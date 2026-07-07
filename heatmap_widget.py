"""
heatmap_widget.py — Embedded matplotlib keyboard heatmap for PyQt6
"""

import numpy as np
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy

from theme import BG, BG2, BORDER, TEXT, TEXT2, TEXT3, HEATMAP_COLORS

CMAP = LinearSegmentedColormap.from_list("kt", HEATMAP_COLORS)

# row, col_offset, display_label, internal_key, width_multiplier
LAYOUT = [
    # ESC row
    [("escape","ESC",1),("`","` ",1),("1","1",1),("2","2",1),("3","3",1),
     ("4","4",1),("5","5",1),("6","6",1),("7","7",1),("8","8",1),
     ("9","9",1),("0","0",1),("-","-",1),("=","=",1),("backspace","⌫",1.5)],
    # QWERTY
    [("tab","TAB",1.5),("q","Q",1),("w","W",1),("e","E",1),("r","R",1),
     ("t","T",1),("y","Y",1),("u","U",1),("i","I",1),("o","O",1),
     ("p","P",1),("[","[",1),("]","]",1),("\\","\\",1.5)],
    # ASDF
    [("caps_lock","CAPS",1.8),("a","A",1),("s","S",1),("d","D",1),("f","F",1),
     ("g","G",1),("h","H",1),("j","J",1),("k","K",1),("l","L",1),
     (";",";",1),("'","'",1),("enter","↵",1.7)],
    # ZXCV
    [("shift","SHIFT",2.2),("z","Z",1),("x","X",1),("c","C",1),("v","V",1),
     ("b","B",1),("n","N",1),("m","M",1),(",",",",1),(".",".",1),
     ("/","/",1),("shift_r","SHIFT",2.3)],
    # Space row
    [("ctrl","CTRL",1.5),("cmd","WIN",1.2),("alt","ALT",1.2),
     ("space","SPACE",5.5),("alt_r","ALT",1.2),("ctrl_r","CTRL",1.5)],
]
MOUSE_LAYOUT = [
    # ikey, label, x, y, w, h
    ("m_scroll_up", "SCR-UP", 17.6, 4.1, 0.8, 0.8),
    ("m_scroll_down", "SCR-DN", 17.6, 2.1, 0.8, 0.8),
    ("m_forward", "FWD", 15.5, 2.1, 0.9, 0.8),
    ("m_back", "BACK", 15.5, 1.1, 0.9, 0.8),
    ("m_left", "L-CLK", 16.5, 3.0, 1.0, 1.0),
    ("m_middle", "M-CLK", 17.6, 3.0, 0.8, 1.0),
    ("m_right", "R-CLK", 18.5, 3.0, 1.0, 1.0),
]

KEY_H = 0.80
KEY_W_UNIT = 0.95
GAP = 0.05
ROW_H = 1.0


class HeatmapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.counts = {}
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.fig, self.ax = plt.subplots(figsize=(14, 4))
        self.fig.patch.set_facecolor(BG)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.canvas)
        self._draw()

    def update_counts(self, counts: dict):
        self.counts = counts
        self._draw()

    def _draw(self):
        self.ax.clear()
        self.ax.set_facecolor(BG)
        self.fig.patch.set_facecolor(BG)

        max_count = max(self.counts.values()) if self.counts else 1

        num_rows = len(LAYOUT)

        # Draw Keyboard keys
        for row_idx, row_keys in enumerate(LAYOUT):
            y = (num_rows - row_idx - 1) * ROW_H
            x = 0.0
            for ikey, label, width_mult in row_keys:
                w = KEY_W_UNIT * width_mult
                count = self.counts.get(ikey, 0)
                heat = count / max_count
                color = CMAP(heat)
                border_color = "#58a6ff" if count > 0 else BORDER

                rect = mpatches.FancyBboxPatch(
                    (x + GAP/2, y + GAP/2),
                    w - GAP, KEY_H - GAP,
                    boxstyle="round,pad=0.04",
                    linewidth=0.8,
                    edgecolor=border_color,
                    facecolor=color,
                    zorder=2,
                )
                self.ax.add_patch(rect)

                cx = x + w / 2
                cy = y + KEY_H / 2

                # Key label
                self.ax.text(
                    cx, cy + 0.10, label,
                    ha="center", va="center",
                    fontsize=6.5,
                    color=TEXT if heat > 0.25 else TEXT3,
                    fontfamily="monospace",
                    fontweight="bold",
                    zorder=3,
                )
                # Count below label
                if count > 0:
                    self.ax.text(
                        cx, cy - 0.22, str(count),
                        ha="center", va="center",
                        fontsize=5.0,
                        color=TEXT2,
                        fontfamily="monospace",
                        zorder=3,
                    )

                x += w

        # Draw Mouse buttons
        for ikey, label, mx, my, mw, mh in MOUSE_LAYOUT:
            count = self.counts.get(ikey, 0)
            heat = count / max_count
            color = CMAP(heat)
            border_color = "#58a6ff" if count > 0 else BORDER

            rect = mpatches.FancyBboxPatch(
                (mx + GAP/2, my + GAP/2),
                mw - GAP, mh - GAP,
                boxstyle="round,pad=0.04",
                linewidth=0.8,
                edgecolor=border_color,
                facecolor=color,
                zorder=2,
            )
            self.ax.add_patch(rect)

            cx = mx + mw / 2
            cy = my + mh / 2

            self.ax.text(
                cx, cy + 0.10 if mh >= 1.0 else cy + 0.05, label,
                ha="center", va="center",
                fontsize=6.0 if mh < 1.0 else 6.5,
                color=TEXT if heat > 0.25 else TEXT3,
                fontfamily="monospace",
                fontweight="bold",
                zorder=3,
            )
            if count > 0:
                self.ax.text(
                    cx, cy - 0.22 if mh >= 1.0 else cy - 0.18, str(count),
                    ha="center", va="center",
                    fontsize=5.0,
                    color=TEXT2,
                    fontfamily="monospace",
                    zorder=3,
                )

        # Total width including keyboard + mouse
        max_w = 19.8
        self.ax.set_xlim(-0.1, max_w + 0.1)
        self.ax.set_ylim(-0.1, num_rows * ROW_H + 0.1)
        self.ax.axis("off")

        self.fig.tight_layout(pad=0.3)
        self.canvas.draw_idle()
