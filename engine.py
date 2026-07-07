"""
engine.py — Keyboard tracking engine (no UI dependency)
Runs a background thread that listens for keypresses via pynput.
Emits signals via callbacks so the UI can update live.
"""

from sys import path
import time
import threading
import json
import os
from collections import defaultdict
from datetime import datetime
from pynput import keyboard as kb, mouse


SESSIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)

GAMING_KEYS = ["w", "a", "s", "d", "space", "shift", "ctrl", "q", "e", "r", "f",
               "1", "2", "3", "4", "5"]


def key_name(key):
    try:
        c = key.char
        if c is None:
            raise AttributeError 
        # Normalize control characters (e.g. Ctrl+A -> \x01 -> 'a')
        if len(c) == 1 and 1 <= ord(c) <= 26:
            c = chr(ord(c) + 96)
        return c.lower()
    except AttributeError:
        name = str(key).replace("Key.", "").lower()
        # Normalize special keys to match heatmap layout names
        if name == "esc":
            return "escape"
        elif name in ("ctrl_l", "ctrl"):
            return "ctrl"
        elif name in ("alt_l", "alt"):
            return "alt"
        elif name in ("cmd_l", "cmd"):
            return "cmd"
        elif name in ("shift_l", "shift"):
            return "shift"
        return name



def mouse_button_name(button):
    try:
        name = button.name.lower()
    except AttributeError:
        name = str(button).replace("Button.", "").lower()
    
    if name in ("left", "button.left"):
        return "m_left"
    elif name in ("right", "button.right"):
        return "m_right"
    elif name in ("middle", "button.middle"):
        return "m_middle"
    elif name in ("x1", "button.x1"):
        return "m_back"
    elif name in ("x2", "button.x2"):
        return "m_forward"
    return f"m_{name}"


class TrackerEngine:
    def __init__(self):
        self.session_name = ""
        self.running = False
        self.start_time = None
        self.keyboard_counts = defaultdict(int)
        self.mouse_counts = defaultdict(int)
        self.timestamps = []          # for KPM
        self.pressed_keys = set()
        self._kb_listener = None
        self._mouse_listener = None
        self._lock = threading.Lock()

        # Callbacks set by UI
        self.on_keypress = None       # called on every tracked press
        self.on_session_saved = None  # called after save

    # ── Public API ─────────────────────────────────────────────────────────────

    def start(self, name: str):
        if self.running:
            return
        self.session_name = name or f"Session_{datetime.now().strftime('%H%M%S')}"
        self.start_time = time.time()
        with self._lock:
            self.keyboard_counts = defaultdict(int)
            self.mouse_counts = defaultdict(int)
            self.timestamps = []
            self.pressed_keys = set()
        self.running = True
        self._start_listener()

    def stop(self) -> dict | None:
        if not self.running:
            return None
        self.running = False
        if self._kb_listener:
            self._kb_listener.stop()
            self._kb_listener = None
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        return self.save()

    def save(self) -> dict:
        secs = self.elapsed_seconds()
        total_kb = self.total_keys()
        total_m = self.total_mouse()
        with self._lock:
            kb_dict = dict(self.keyboard_counts)
            m_dict = dict(self.mouse_counts)
            combined = dict(self.keyboard_counts)
            combined.update(self.mouse_counts)
        payload = {
            "session_name": self.session_name,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": round(secs, 1),
            "total_keypresses": total_kb,
            "total_mouse": total_m,
            "avg_kpm": round((total_kb / secs) * 60, 1) if secs > 0 else 0,
            "counts": combined,
            "keyboard_counts": kb_dict,
            "mouse_counts": m_dict,
        }
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = self.session_name
        for char in '<>:"/\\|?*':
            safe = safe.replace(char, "-")
        safe = safe.replace(" ", "_")
        path = os.path.join(SESSIONS_DIR, f"{ts}_{safe}.json")
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        payload["_path"] = path
        if self.on_session_saved:
            self.on_session_saved(payload)
        return payload

    # ── Stats helpers ──────────────────────────────────────────────────────────

    def get_counts_copy(self) -> dict:
        with self._lock:
            combined = dict(self.keyboard_counts)
            combined.update(self.mouse_counts)
            return combined

    def total_keys(self) -> int:
        with self._lock:
            return sum(self.keyboard_counts.values())

    def total_mouse(self) -> int:
        with self._lock:
            return sum(self.mouse_counts.values())

    def total(self) -> int:
        return self.total_keys()

    def elapsed_seconds(self) -> float:
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time

    def elapsed_str(self) -> str:
        s = int(self.elapsed_seconds())
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def kpm_now(self) -> int:
        now = time.time()
        with self._lock:
            self.timestamps = [t for t in self.timestamps if now - t <= 60]
            return len(self.timestamps)

    def avg_kpm(self) -> int:
        secs = self.elapsed_seconds()
        if secs <= 0:
            return 0
        return int((self.total_keys() / secs) * 60)

    def top_keys(self, n=15):
        with self._lock:
            return sorted(self.keyboard_counts.items(), key=lambda x: x[1], reverse=True)[:n]

    def gaming_stats(self) -> dict:
        with self._lock:
            return {k: self.keyboard_counts.get(k, 0) for k in GAMING_KEYS}

    def strafe_ratio(self):
        with self._lock:
            a = self.keyboard_counts.get("a", 0)
            d = self.keyboard_counts.get("d", 0)
        total = a + d
        if total == 0:
            return None, None
        return round(a / total * 100), round(d / total * 100)

    # ── Internal ───────────────────────────────────────────────────────────────

    def _start_listener(self):
        def on_press(key):
            if not self.running:
                return False
            k = key_name(key)
            with self._lock:
                if k in self.pressed_keys:
                    return
                self.pressed_keys.add(k)
                self.keyboard_counts[k] += 1
                self.timestamps.append(time.time())
            if self.on_keypress:
                self.on_keypress(k, self.keyboard_counts[k])

        def on_release(key):
            if not self.running:
                return False
            k = key_name(key)
            with self._lock:
                self.pressed_keys.discard(k)

        def on_click(x, y, button, pressed):
            if not self.running:
                return False
            if pressed:
                btn = mouse_button_name(button)
                with self._lock:
                    self.mouse_counts[btn] += 1
                if self.on_keypress:
                    self.on_keypress(btn, self.mouse_counts[btn])

        def on_scroll(x, y, dx, dy):
            if not self.running:
                return False
            scr = []
            if dy > 0:
                scr.append("m_scroll_up")
            elif dy < 0:
                scr.append("m_scroll_down")
            if dx > 0:
                scr.append("m_scroll_right")
            elif dx < 0:
                scr.append("m_scroll_left")
            
            if scr:
                with self._lock:
                    for s in scr:
                        self.mouse_counts[s] += 1
                if self.on_keypress:
                    self.on_keypress(scr[0], self.mouse_counts[scr[0]])

        self._kb_listener = kb.Listener(on_press=on_press, on_release=on_release)
        self._kb_listener.daemon = True
        self._kb_listener.start()

        self._mouse_listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
        self._mouse_listener.daemon = True
        self._mouse_listener.start()

    # ── Session file utils ─────────────────────────────────────────────────────

    @staticmethod
    def list_sessions() -> list[dict]:
        sessions = []
        for fname in sorted(os.listdir(SESSIONS_DIR), reverse=True):
            if fname.endswith(".json"):
                path = os.path.join(SESSIONS_DIR, fname)
                try:
                    with open(path) as f:
                        data = json.load(f)
                    data["_path"] = path
                    data["_file"] = fname
                    sessions.append(data)
                except Exception:
                    pass
        return sessions

    @staticmethod
    def load_session(path: str) -> dict:
        with open(path) as f:
            return json.load(f)

