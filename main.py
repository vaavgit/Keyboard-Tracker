"""
main.py — KeyTracker Desktop App
Run: python main.py
"""

import sys
import os
import json
import time
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTabWidget, QListWidget,
    QListWidgetItem, QSplitter, QFrame, QScrollArea, QGridLayout,
    QSizePolicy, QMessageBox, QProgressBar, QTextEdit,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QFont, QColor, QPalette

from engine import TrackerEngine, GAMING_KEYS
from theme import QSS, BG, BG2, BG3, BORDER, TEXT, TEXT2, TEXT3, ACCENT, ACCENT2, ACCENT3, WARN
from heatmap_widget import HeatmapWidget


# ── Stat card widget ───────────────────────────────────────────────────────────
class StatCard(QFrame):
    def __init__(self, label: str, value: str = "—", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {BG2}; border: 1px solid {BORDER}; border-radius: 10px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        self.val_label = QLabel(value)
        self.val_label.setObjectName("stat_value")
        self.val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_label = QLabel(label.upper())
        self.lbl_label.setObjectName("stat_label")
        self.lbl_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.val_label)
        layout.addWidget(self.lbl_label)

    def set_value(self, v: str):
        self.val_label.setText(v)

    def set_color(self, color: str):
        self.val_label.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")


# ── Gaming key bar ─────────────────────────────────────────────────────────────
class GamingBar(QFrame):
    def __init__(self, key_label: str, key: str, parent=None):
        super().__init__(parent)
        self.key = key
        self.setStyleSheet(f"background: transparent; border: none;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(10)

        lbl = QLabel(f"<b>{key_label}</b>")
        lbl.setFixedWidth(48)
        lbl.setStyleSheet(f"color: {TEXT}; font-family: monospace; font-size: 12px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(14)
        self.bar.setStyleSheet(f"""
            QProgressBar {{ background: {BG3}; border: none; border-radius: 7px; }}
            QProgressBar::chunk {{ background: {ACCENT}; border-radius: 7px; }}
        """)

        self.count_lbl = QLabel("0")
        self.count_lbl.setFixedWidth(52)
        self.count_lbl.setStyleSheet(f"color: {TEXT2}; font-family: monospace; font-size: 12px;")
        self.count_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(lbl)
        layout.addWidget(self.bar, 1)
        layout.addWidget(self.count_lbl)

    def update(self, count: int, max_count: int):
        pct = int(count / max_count * 100) if max_count > 0 else 0
        self.bar.setValue(pct)
        self.count_lbl.setText(f"{count:,}")


# ── Sessions list item ─────────────────────────────────────────────────────────
def make_session_item(session: dict) -> QListWidgetItem:
    name = session.get("session_name", "Unknown")
    date = session.get("date", "")
    total = session.get("total_keypresses", 0)
    total_mouse = session.get("total_mouse", 0)
    kpm = session.get("avg_kpm", 0)
    duration = session.get("duration_seconds", 0)
    m, s = divmod(int(duration), 60)

    text = f"{name}\n{date}  ·  {total:,} keys  ·  {total_mouse:,} mouse  ·  {kpm} avg KPM  ·  {m:02d}:{s:02d}"
    item = QListWidgetItem(text)
    item.setData(Qt.ItemDataRole.UserRole, session)
    return item


# ── Main Window ────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = TrackerEngine()
        self.engine.on_keypress = self._on_keypress
        self.engine.on_session_saved = self._on_session_saved

        self.setWindowTitle("KeyTracker")
        self.setMinimumSize(1000, 680)
        self.resize(1180, 740)

        # Typing test state variables
        self.typing_test_active = False
        self.typing_elapsed_seconds = 0
        self.typing_test_timer = QTimer()
        self.typing_test_timer.setInterval(100) # Tick every 100ms
        self.typing_test_timer.timeout.connect(self._typing_test_tick)

        self._build_ui()
        self._setup_timer()

        # Refresh sessions list on start
        self._refresh_sessions()

    # ── UI Build ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        root.addWidget(self._build_header())

        # Tab area
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        root.addWidget(self.tabs, 1)

        self.tabs.addTab(self._build_live_tab(), "  Live  ")
        self.tabs.addTab(self._build_typing_tab(), "  Typing Test  ")
        self.tabs.addTab(self._build_sessions_tab(), "  Sessions  ")
        self.tabs.addTab(self._build_compare_tab(), "  Compare  ")

    def _build_header(self):
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet(f"background-color: {BG2}; border-bottom: 1px solid {BORDER};")
        h = QHBoxLayout(header)
        h.setContentsMargins(24, 0, 24, 0)

        # Logo / title
        title = QLabel("⌨  KeyTracker")
        title.setStyleSheet(f"color: {TEXT}; font-size: 18px; font-weight: bold; letter-spacing: 1px;")
        h.addWidget(title)

        h.addStretch()

        # Status pill
        self.status_pill = QLabel("● IDLE")
        self.status_pill.setObjectName("session_status")
        self.status_pill.setStyleSheet(f"color: {TEXT3}; background: {BG3}; border: 1px solid {BORDER};")
        h.addWidget(self.status_pill)

        return header

    def _build_live_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # ── Session control row ────────────────────────────────────────────────
        ctrl = QHBoxLayout()
        ctrl.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Session name  (e.g. Match 1 Ranked)...")
        self.name_input.setFixedHeight(38)
        ctrl.addWidget(self.name_input, 1)

        self.btn_start = QPushButton("▶  Start")
        self.btn_start.setObjectName("btn_start")
        self.btn_start.setFixedHeight(38)
        self.btn_start.clicked.connect(self._start_session)
        ctrl.addWidget(self.btn_start)

        self.btn_stop = QPushButton("■  Stop & Save")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.setFixedHeight(38)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_session)
        ctrl.addWidget(self.btn_stop)

        layout.addLayout(ctrl)

        # ── Stat cards row ─────────────────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)
        self.card_total = StatCard("Total Keys", "0")
        self.card_mouse = StatCard("Total Mouse", "0")
        self.card_kpm   = StatCard("KPM (now)", "0")
        self.card_avg   = StatCard("Avg KPM", "0")
        self.card_time  = StatCard("Session Time", "00:00:00")
        for c in [self.card_total, self.card_mouse, self.card_kpm, self.card_avg, self.card_time]:
            cards_row.addWidget(c)
        layout.addLayout(cards_row)

        # ── Heatmap ────────────────────────────────────────────────────────────
        hm_frame = QFrame()
        hm_frame.setStyleSheet(f"background: {BG2}; border: 1px solid {BORDER}; border-radius: 10px;")
        hm_layout = QVBoxLayout(hm_frame)
        hm_layout.setContentsMargins(12, 10, 12, 10)

        hm_title = QLabel("Keyboard Heatmap")
        hm_title.setStyleSheet(f"color: {TEXT2}; font-size: 11px; letter-spacing: 1px; border: none; background: transparent;")
        hm_layout.addWidget(hm_title)

        self.heatmap = HeatmapWidget()
        self.heatmap.setMinimumHeight(180)
        hm_layout.addWidget(self.heatmap, 1)
        layout.addWidget(hm_frame, 1)

        # ── Bottom: top keys + gaming panel ───────────────────────────────────
        bottom = QHBoxLayout()
        bottom.setSpacing(12)

        # Top keys
        top_frame = QFrame()
        top_frame.setStyleSheet(f"background: {BG2}; border: 1px solid {BORDER}; border-radius: 10px;")
        top_frame.setMinimumWidth(220)
        top_layout = QVBoxLayout(top_frame)
        top_layout.setContentsMargins(14, 12, 14, 12)
        top_layout.setSpacing(6)

        tl = QLabel("Top Keys")
        tl.setStyleSheet(f"color: {TEXT2}; font-size: 11px; letter-spacing: 1px; border: none; background: transparent;")
        top_layout.addWidget(tl)

        self.top_labels = []
        for _ in range(10):
            lbl = QLabel("—")
            lbl.setStyleSheet(f"color: {TEXT}; font-family: monospace; font-size: 12px; border: none; background: transparent;")
            top_layout.addWidget(lbl)
            self.top_labels.append(lbl)
        top_layout.addStretch()
        bottom.addWidget(top_frame)

        # Gaming panel
        gaming_frame = QFrame()
        gaming_frame.setStyleSheet(f"background: {BG2}; border: 1px solid {BORDER}; border-radius: 10px;")
        gaming_layout = QVBoxLayout(gaming_frame)
        gaming_layout.setContentsMargins(14, 12, 14, 12)
        gaming_layout.setSpacing(4)

        gl = QLabel("Gaming Keys")
        gl.setStyleSheet(f"color: {TEXT2}; font-size: 11px; letter-spacing: 1px; border: none; background: transparent;")
        gaming_layout.addWidget(gl)

        GAMING_DISPLAY = [
            ("W  Forward",  "w"),  ("A  Left",     "a"),
            ("S  Back",     "s"),  ("D  Right",    "d"),
            ("SPACE  Jump", "space"), ("SHIFT Sprint","shift"),
            ("CTRL Crouch", "ctrl"), ("R  Reload",  "r"),
            ("F  Interact", "f"),  ("Q",           "q"),
            ("E",           "e"),  ("1","1"),("2","2"),("3","3"),("4","4"),("5","5"),
        ]
        self.gaming_bars: dict[str, GamingBar] = {}
        for label, key in GAMING_DISPLAY:
            bar = GamingBar(label, key)
            gaming_layout.addWidget(bar)
            self.gaming_bars[key] = bar

        # Strafe ratio label
        self.strafe_label = QLabel("")
        self.strafe_label.setStyleSheet(f"color: {ACCENT}; font-size: 11px; font-family: monospace; border: none; background: transparent;")
        self.strafe_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gaming_layout.addWidget(self.strafe_label)

        bottom.addWidget(gaming_frame, 1)
        layout.addLayout(bottom)

        return w

    def _build_sessions_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        hdr = QHBoxLayout()
        lbl = QLabel("Saved Sessions")
        lbl.setStyleSheet(f"color: {TEXT2}; font-size: 11px; letter-spacing: 1px;")
        hdr.addWidget(lbl)
        hdr.addStretch()
        btn_refresh = QPushButton("↻  Refresh")
        btn_refresh.setFixedHeight(32)
        btn_refresh.clicked.connect(self._refresh_sessions)
        hdr.addWidget(btn_refresh)
        layout.addLayout(hdr)

        self.session_list = QListWidget()
        self.session_list.setFont(QFont("Segoe UI", 12))
        self.session_list.itemClicked.connect(self._on_session_clicked)
        layout.addWidget(self.session_list, 1)

        # Detail panel
        self.session_detail = QLabel("Select a session to see details.")
        self.session_detail.setStyleSheet(
            f"background: {BG2}; border: 1px solid {BORDER}; border-radius: 10px;"
            f"color: {TEXT2}; padding: 16px; font-family: monospace; font-size: 12px;"
        )
        self.session_detail.setWordWrap(True)
        self.session_detail.setMinimumHeight(120)
        layout.addWidget(self.session_detail)

        return w

    def _build_compare_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        info = QLabel("Select two sessions from the lists below to compare them side by side.")
        info.setStyleSheet(f"color: {TEXT2}; font-size: 12px;")
        layout.addWidget(info)

        lists_row = QHBoxLayout()
        lists_row.setSpacing(16)

        for side in ["A", "B"]:
            col = QVBoxLayout()
            lbl = QLabel(f"Session {side}")
            lbl.setStyleSheet(f"color: {TEXT2}; font-size: 11px; letter-spacing: 1px;")
            col.addWidget(lbl)
            lst = QListWidget()
            lst.setFont(QFont("Segoe UI", 11))
            setattr(self, f"cmp_list_{side.lower()}", lst)
            col.addWidget(lst)
            lists_row.addLayout(col)

        layout.addLayout(lists_row, 1)

        btn_cmp = QPushButton("Compare Selected Sessions")
        btn_cmp.setFixedHeight(38)
        btn_cmp.clicked.connect(self._do_compare)
        layout.addWidget(btn_cmp)

        self.cmp_result = QLabel("")
        self.cmp_result.setStyleSheet(
            f"background: {BG2}; border: 1px solid {BORDER}; border-radius: 10px;"
            f"color: {TEXT}; padding: 16px; font-family: monospace; font-size: 12px;"
        )
        self.cmp_result.setWordWrap(True)
        self.cmp_result.setMinimumHeight(160)
        layout.addWidget(self.cmp_result)

        return w

    # ── Timer (live updates) ───────────────────────────────────────────────────

    def _setup_timer(self):
        self.timer = QTimer()
        self.timer.setInterval(500)   # update every 500ms
        self.timer.timeout.connect(self._tick)
        self.timer.start()

    def _tick(self):
        if not self.engine.running:
            return

        counts = self.engine.get_counts_copy()
        total_kb = self.engine.total_keys()
        total_m = self.engine.total_mouse()
        kpm    = self.engine.kpm_now()
        avg    = self.engine.avg_kpm()
        elapsed = self.engine.elapsed_str()

        # Stat cards
        self.card_total.set_value(f"{total_kb:,}")
        self.card_mouse.set_value(f"{total_m:,}")
        self.card_kpm.set_value(str(kpm))
        self.card_avg.set_value(str(avg))
        self.card_time.set_value(elapsed)

        # Heatmap (throttle: update every 2s to avoid lag)
        if not hasattr(self, "_hm_tick"):
            self._hm_tick = 0
        self._hm_tick += 1
        if self._hm_tick % 4 == 0:
            self.heatmap.update_counts(counts)

        # Top keys
        top = self.engine.top_keys(10)
        for i, lbl in enumerate(self.top_labels):
            if i < len(top):
                k, v = top[i]
                bar_len = int(v / (top[0][1] or 1) * 12)
                bar = "█" * bar_len
                lbl.setText(f"{k.upper():>8}  {bar} {v:,}")
            else:
                lbl.setText("—")

        # Gaming bars
        gaming = self.engine.gaming_stats()
        gmax = max(gaming.values()) if gaming else 1
        for key, bar_widget in self.gaming_bars.items():
            bar_widget.update(gaming.get(key, 0), gmax)

        # Strafe ratio
        lp, rp = self.engine.strafe_ratio()
        if lp is not None:
            self.strafe_label.setText(f"Strafe  ←{lp}%  /  {rp}%→")
        else:
            self.strafe_label.setText("")

    # ── Session controls ───────────────────────────────────────────────────────

    def _start_session(self):
        name = self.name_input.text().strip()
        if not name:
            name = f"Session {datetime.now().strftime('%H:%M')}"
        self.engine.start(name)
        self.heatmap.update_counts({})
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.name_input.setEnabled(False)
        self.status_pill.setText("● RECORDING")
        self.status_pill.setStyleSheet(f"color: {ACCENT2}; background: #1a3a1a; border: 1px solid {ACCENT2};")
        self._hm_tick = 0

    def _stop_session(self):
        result = self.engine.stop()
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.name_input.setEnabled(True)
        self.status_pill.setText("● IDLE")
        self.status_pill.setStyleSheet(f"color: {TEXT3}; background: {BG3}; border: 1px solid {BORDER};")

        # Final heatmap update
        if result:
            self.heatmap.update_counts(result.get("counts", {}))
            self._refresh_sessions()

    # ── Key press callback (from engine thread) ────────────────────────────────

    def _on_keypress(self, key: str, count: int):
        pass  # tick handles updates

    def _on_session_saved(self, payload: dict):
        pass  # refresh handled in stop

    # ── Sessions tab ───────────────────────────────────────────────────────────

    def _refresh_sessions(self):
        sessions = TrackerEngine.list_sessions()
        self.session_list.clear()
        self.cmp_list_a.clear()
        self.cmp_list_b.clear()
        for s in sessions:
            item = make_session_item(s)
            self.session_list.addItem(item)
            self.cmp_list_a.addItem(make_session_item(s))
            self.cmp_list_b.addItem(make_session_item(s))

    def _on_session_clicked(self, item: QListWidgetItem):
        s = item.data(Qt.ItemDataRole.UserRole)
        counts = s.get("counts", {})
        # Filter out mouse keys for Top 5 keyboard keys
        kb_counts = {k: v for k, v in counts.items() if not k.startswith("m_")}
        top5 = sorted(kb_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_str = "  ".join(f"{k.upper()}:{v}" for k, v in top5)

        wasd = {k: counts.get(k, 0) for k in ["w","a","s","d","space"]}
        a, d = wasd["a"], wasd["d"]
        strafing = a + d
        strafe_str = f"←{int(a/strafing*100)}% / {int(d/strafing*100)}%→" if strafing else "n/a"

        detail = (
            f"📌  {s.get('session_name', '—')}\n"
            f"📅  {s.get('date', '—')}\n"
            f"⏱   Duration: {int(s.get('duration_seconds', 0))}s  "
            f"   Keyboard Total: {s.get('total_keypresses', 0):,} keys  "
            f"   Mouse Total: {s.get('total_mouse', 0):,} clicks\n"
            f"📈  Avg KPM: {s.get('avg_kpm', 0)}\n\n"
            f"Top 5 Keys:  {top_str}\n"
            f"WASD:  W={wasd['w']}  A={wasd['a']}  S={wasd['s']}  D={wasd['d']}  "
            f"Space={wasd['space']}    Strafe: {strafe_str}"
        )
        self.session_detail.setText(detail)

    # ── Compare tab ────────────────────────────────────────────────────────────

    def _do_compare(self):
        a_items = self.cmp_list_a.selectedItems()
        b_items = self.cmp_list_b.selectedItems()
        if not a_items or not b_items:
            self.cmp_result.setText("Please select one session in each list.")
            return

        s1 = a_items[0].data(Qt.ItemDataRole.UserRole)
        s2 = b_items[0].data(Qt.ItemDataRole.UserRole)
        c1, c2 = s1.get("counts", {}), s2.get("counts", {})

        all_keys = sorted(
            set(list(c1.keys()) + list(c2.keys())),
            key=lambda k: c1.get(k, 0) + c2.get(k, 0),
            reverse=True
        )[:16]

        lines = [
            f"A: {s1['session_name']}  ({s1['total_keypresses']:,} keys, {s1.get('total_mouse', 0):,} mouse, {s1['avg_kpm']} avg KPM)",
            f"B: {s2['session_name']}  ({s2['total_keypresses']:,} keys, {s2.get('total_mouse', 0):,} mouse, {s2['avg_kpm']} avg KPM)",
            "",
            f"{'KEY':>10}   {'A':>8}   {'B':>8}   {'DIFF':>8}   TREND",
            "─" * 52,
        ]
        for k in all_keys:
            a_v = c1.get(k, 0)
            b_v = c2.get(k, 0)
            diff = b_v - a_v
            trend = "▲" if diff > 0 else ("▼" if diff < 0 else "─")
            lines.append(f"{k.upper():>10}   {a_v:>8,}   {b_v:>8,}   {diff:>+8,}   {trend}")

        lines.append("─" * 52)
        t1, t2 = s1["total_keypresses"], s2["total_keypresses"]
        lines.append(f"{'KEYS TOT':>10}   {t1:>8,}   {t2:>8,}   {t2-t1:>+8,}")
        m1, m2 = s1.get("total_mouse", 0), s2.get("total_mouse", 0)
        lines.append(f"{'MOUSE TOT':>10}   {m1:>8,}   {m2:>8,}   {m2-m1:>+8,}")

        self.cmp_result.setText("\n".join(lines))

    # ── Typing Speed & Accuracy Test ───────────────────────────────────────────

    # ── Typing Speed & Accuracy Test ───────────────────────────────────────────

    def _build_typing_tab(self):
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Splitter to divide left (test) and right (history)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # ── Left pane: Test Panel ──
        test_panel = QFrame()
        test_panel.setStyleSheet("background: transparent; border: none;")
        test_layout = QVBoxLayout(test_panel)
        test_layout.setContentsMargins(0, 0, 0, 0)
        test_layout.setSpacing(16)

        # Instruction
        inst = QLabel("<b>Typing Speed & Accuracy Test</b><br>"
                      "<span style='color: #8b949e;'>Type the prompt paragraph displayed below. "
                      "Keystrokes will be highlighted in real-time. The test will auto-complete when finished.</span>")
        inst.setWordWrap(True)
        inst.setStyleSheet("font-size: 13px; border: none; background: transparent;")
        test_layout.addWidget(inst)

        # Control Row
        ctrl = QHBoxLayout()
        ctrl.setSpacing(10)
        
        self.btn_typing_start = QPushButton("Start Test")
        self.btn_typing_start.setObjectName("btn_typing_start") # Reuses high-contrast green styling
        self.btn_typing_start.setFixedHeight(38)
        self.btn_typing_start.clicked.connect(self._start_typing_test)
        ctrl.addWidget(self.btn_typing_start)

        self.btn_typing_stop = QPushButton("Stop Test")
        self.btn_typing_stop.setObjectName("btn_typing_stop") # Reuses high-contrast red styling
        self.btn_typing_stop.setFixedHeight(38)
        self.btn_typing_stop.setEnabled(False)
        self.btn_typing_stop.clicked.connect(self._stop_typing_test)
        ctrl.addWidget(self.btn_typing_stop)
        
        ctrl.addStretch()
        test_layout.addLayout(ctrl)

        # Stats Row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)
        
        self.card_typing_wpm = StatCard("WPM", "0")
        self.card_typing_acc = StatCard("Accuracy", "100%")
        self.card_typing_time = StatCard("Elapsed Time", "00:00")
        self.card_typing_words = StatCard("Typed Chars", "0 / 0")
        
        for card in [self.card_typing_wpm, self.card_typing_acc, self.card_typing_time, self.card_typing_words]:
            stats_row.addWidget(card)
        test_layout.addLayout(stats_row)

        # Prompt Display Area
        self.prompt_display_frame = QFrame()
        self.prompt_display_frame.setStyleSheet(f"background: {BG2}; border: 1px solid {BORDER}; border-radius: 8px;")
        prompt_disp_layout = QVBoxLayout(self.prompt_display_frame)
        prompt_disp_layout.setContentsMargins(16, 16, 16, 16)

        self.prompt_display = QLabel("Click 'Start Test' above to load a typing prompt...")
        self.prompt_display.setWordWrap(True)
        self.prompt_display.setStyleSheet(f"""
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 15px;
            color: {TEXT2};
            background: transparent;
            border: none;
            line-height: 1.5;
        """)
        prompt_disp_layout.addWidget(self.prompt_display)
        test_layout.addWidget(self.prompt_display_frame)

        # Text input area
        self.typing_input = QTextEdit()
        self.typing_input.setPlaceholderText("Once the test starts, type here...")
        self.typing_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: {BG2};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 15px;
                color: {TEXT};
            }}
            QTextEdit:focus {{
                border-color: {ACCENT};
            }}
        """)
        self.typing_input.setEnabled(False)
        self.typing_input.textChanged.connect(self._on_typing_text_changed)
        test_layout.addWidget(self.typing_input, 1)

        splitter.addWidget(test_panel)

        # ── Right pane: History Panel ──
        history_panel = QFrame()
        history_panel.setStyleSheet(f"background-color: {BG2}; border-left: 1px solid {BORDER};")
        history_layout = QVBoxLayout(history_panel)
        history_layout.setContentsMargins(16, 0, 0, 0)
        history_layout.setSpacing(12)

        history_title = QLabel("RECENT TEST RUNS")
        history_title.setStyleSheet(f"color: {TEXT2}; font-size: 11px; letter-spacing: 1px; font-weight: bold;")
        history_layout.addWidget(history_title)

        self.typing_history_list = QListWidget()
        self.typing_history_list.setStyleSheet(f"background-color: {BG3}; border: 1px solid {BORDER}; border-radius: 8px;")
        self.typing_history_list.setFont(QFont("Segoe UI", 10))
        history_layout.addWidget(self.typing_history_list, 1)

        btn_clear_history = QPushButton("Clear History")
        btn_clear_history.setFixedHeight(32)
        btn_clear_history.clicked.connect(self._clear_typing_history)
        history_layout.addWidget(btn_clear_history)

        splitter.addWidget(history_panel)
        
        # Set initial splitter sizes (75% left, 25% right)
        splitter.setSizes([750, 250])

        return w

    # Paragraphs to select for typing tests
    TYPING_PARAGRAPHS = [
        "The quick brown fox jumps over the lazy dog. This classic pangram contains every letter of the English alphabet, making it a perfect quick test for keyboard speed and finger flexibility.",
        "Programming is the art of telling another human what one wants the computer to do. Code should be written to be read by humans, and only incidentally for computers to execute.",
        "Typography is the art and technique of arranging type to make written language legible, readable, and appealing when displayed. The arrangement of type involves selecting typefaces, point sizes, line lengths, and line-spacing.",
        "A keyboard is one of the primary input devices used with a computer. Similar to an electric typewriter, a keyboard is composed of buttons that create letters, numbers, and symbols, as well as perform other functions.",
        "The mouse is a handheld pointing device that detects two-dimensional motion relative to a surface. This motion is typically translated into the motion of a pointer on a display, allowing smooth control of the user interface."
    ]

    def _start_typing_test(self):
        import random
        self.current_paragraph = random.choice(self.TYPING_PARAGRAPHS)
        self.typing_test_active = True
        self.typing_elapsed_seconds = 0
        self.typing_input.setEnabled(True)
        self.typing_input.clear()
        self.typing_input.setFocus()
        
        self.btn_typing_start.setEnabled(False)
        self.btn_typing_stop.setEnabled(True)
        
        # Reset stats UI
        self.card_typing_wpm.set_value("0")
        self.card_typing_acc.set_value("100%")
        self.card_typing_time.set_value("00:00")
        self.card_typing_words.set_value(f"0 / {len(self.current_paragraph)}")
        
        # Set initial un-typed paragraph (all gray)
        self.prompt_display.setText(self.current_paragraph)

        self.typing_start_time = time.time()
        self.typing_test_timer.start()

    def _stop_typing_test(self):
        if not self.typing_test_active:
            return
        
        self.typing_test_active = False
        self.typing_test_timer.stop()
        self.typing_input.setEnabled(False)
        self.btn_typing_start.setEnabled(True)
        self.btn_typing_stop.setEnabled(False)

        # Save final result to history
        wpm = self.card_typing_wpm.val_label.text()
        acc = self.card_typing_acc.val_label.text()
        dur = self.card_typing_time.val_label.text()
        chars = self.card_typing_words.val_label.text()
        
        time_str = datetime.now().strftime("%H:%M")
        history_text = f"🕒 {time_str}  ·  {wpm} WPM  ·  {acc} Acc  ·  {dur}  ·  {chars.split(' ')[0]} chars"
        self.typing_history_list.insertItem(0, QListWidgetItem(history_text))

    def _typing_test_tick(self):
        if not self.typing_test_active:
            return
        self.typing_elapsed_seconds = time.time() - self.typing_start_time
        mins, secs = divmod(int(self.typing_elapsed_seconds), 60)
        self.card_typing_time.set_value(f"{mins:02d}:{secs:02d}")
        
        # Recalculate stats on tick to keep WPM moving as time flows
        self._update_typing_stats()

    def _on_typing_text_changed(self):
        if not self.typing_test_active:
            return
        self._update_typing_stats()

    def _update_typing_stats(self):
        text = self.typing_input.toPlainText()
        target = self.current_paragraph
        
        # Block additional characters beyond target length
        if len(text) > len(target):
            text = text[:len(target)]
            self.typing_input.blockSignals(True)
            self.typing_input.setPlainText(text)
            cursor = self.typing_input.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.typing_input.setTextCursor(cursor)
            self.typing_input.blockSignals(False)

        if not text:
            self.card_typing_wpm.set_value("0")
            self.card_typing_acc.set_value("100%")
            self.card_typing_words.set_value(f"0 / {len(target)}")
            self.prompt_display.setText(target)
            return

        # Compare character by character
        html = []
        correct_chars = 0
        total_typed = len(text)
        
        for i, char in enumerate(target):
            if i < total_typed:
                if text[i] == char:
                    # Correct character: green
                    html.append(f'<span style="color: {ACCENT2}; font-weight: bold;">{char}</span>')
                    correct_chars += 1
                else:
                    # Incorrect character: red underlined
                    disp_char = "_" if char == " " else char
                    html.append(f'<span style="color: {ACCENT3}; font-weight: bold; text-decoration: underline;">{disp_char}</span>')
            else:
                # Untyped character: gray
                html.append(f'<span style="color: {TEXT2};">{char}</span>')

        self.prompt_display.setText("".join(html))

        # Speed (WPM) = (correct characters / 5.0) / elapsed_minutes
        elapsed_mins = max(self.typing_elapsed_seconds / 60.0, 0.001)
        wpm = int((correct_chars / 5.0) / elapsed_mins)

        # Accuracy
        acc = int((correct_chars / total_typed) * 100) if total_typed > 0 else 100

        self.card_typing_wpm.set_value(str(wpm))
        self.card_typing_acc.set_value(f"{acc}%")
        self.card_typing_words.set_value(f"{total_typed} / {len(target)}")

        # Auto-stop when completed
        if total_typed >= len(target):
            self._stop_typing_test()

    def _clear_typing_history(self):
        self.typing_history_list.clear()


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    app.setApplicationName("KeyTracker")

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
