"""
theme.py — Color palette and stylesheet for KeyTracker UI
"""

# ── Colors ─────────────────────────────────────────────────────────────────────
BG         = "#0d1117"   # main background
BG2        = "#161b22"   # card / panel background
BG3        = "#21262d"   # input / hover background
BORDER     = "#30363d"   # subtle borders
TEXT       = "#e6edf3"   # primary text
TEXT2      = "#8b949e"   # secondary / muted text
TEXT3      = "#484f58"   # disabled / very muted
ACCENT     = "#58a6ff"   # blue accent (primary)
ACCENT2    = "#3fb950"   # green (active / running)
ACCENT3    = "#f78166"   # red / stop
WARN       = "#d29922"   # yellow / warning
HEAT_LOW   = "#0a3060"
HEAT_MID   = "#0066cc"
HEAT_HIGH  = "#ff6600"
HEAT_MAX   = "#ff2200"

# ── Heatmap gradient stops (count → color) ────────────────────────────────────
HEATMAP_COLORS = [BG2, HEAT_LOW, HEAT_MID, "#00aaff", HEAT_HIGH, HEAT_MAX]

# ── Stylesheet ─────────────────────────────────────────────────────────────────
QSS = f"""
QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: 'Segoe UI', 'SF Pro Display', 'Ubuntu', sans-serif;
    font-size: 13px;
}}

QMainWindow {{
    background-color: {BG};
}}

/* ── Buttons ── */
QPushButton {{
    background-color: {BG3};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 18px;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: #2d333b;
    border-color: {ACCENT};
}}
QPushButton:pressed {{
    background-color: {ACCENT};
    color: {BG};
}}
QPushButton#btn_start {{
    background-color: {ACCENT2};
    color: {BG};
    border: none;
    font-weight: bold;
    font-size: 14px;
    padding: 10px 28px;
    border-radius: 8px;
}}
QPushButton#btn_start:hover {{
    background-color: #56d364;
}}
QPushButton#btn_stop {{
    background-color: {ACCENT3};
    color: {BG};
    border: none;
    font-weight: bold;
    font-size: 14px;
    padding: 10px 28px;
    border-radius: 8px;
}}
QPushButton#btn_stop:hover {{
    background-color: #ff8080;
}}
QPushButton#btn_stop:disabled {{
    background-color: {BG3};
    color: {TEXT3};
}}
QPushButton#btn_start:disabled {{
    background-color: {BG3};
    color: {TEXT3};
}}

QPushButton#btn_typing_start {{
    background-color: {ACCENT2};
    color: {BG};
    border: none;
    font-weight: bold;
    font-size: 13px;
    padding: 8px 24px;
    border-radius: 6px;
}}
QPushButton#btn_typing_start:hover {{
    background-color: #56d364;
}}
QPushButton#btn_typing_start:disabled {{
    background-color: {BG3};
    color: {TEXT3};
}}
QPushButton#btn_typing_stop {{
    background-color: {ACCENT3};
    color: {BG};
    border: none;
    font-weight: bold;
    font-size: 13px;
    padding: 8px 24px;
    border-radius: 6px;
}}
QPushButton#btn_typing_stop:hover {{
    background-color: #ff8080;
}}
QPushButton#btn_typing_stop:disabled {{
    background-color: {BG3};
    color: {TEXT3};
}}


/* ── Line Edit ── */
QLineEdit {{
    background-color: {BG3};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 12px;
    color: {TEXT};
    font-size: 13px;
    selection-background-color: {ACCENT};
}}
QLineEdit:focus {{
    border-color: {ACCENT};
}}

/* ── Tab widget ── */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    background-color: {BG2};
}}
QTabBar::tab {{
    background-color: {BG};
    color: {TEXT2};
    padding: 8px 20px;
    border: none;
    font-size: 13px;
}}
QTabBar::tab:selected {{
    color: {TEXT};
    border-bottom: 2px solid {ACCENT};
}}
QTabBar::tab:hover {{
    color: {TEXT};
    background-color: {BG3};
}}

/* ── Scroll area ── */
QScrollArea {{
    border: none;
    background-color: transparent;
}}
QScrollBar:vertical {{
    background: {BG2};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

/* ── Labels ── */
QLabel#stat_value {{
    font-size: 28px;
    font-weight: bold;
    color: {ACCENT};
}}
QLabel#stat_label {{
    font-size: 11px;
    color: {TEXT2};
    letter-spacing: 1px;
}}
QLabel#session_status {{
    font-size: 12px;
    font-weight: bold;
    letter-spacing: 1px;
    padding: 4px 12px;
    border-radius: 4px;
}}

/* ── List widget ── */
QListWidget {{
    background-color: {BG2};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 4px;
}}
QListWidget::item {{
    padding: 10px 12px;
    border-radius: 6px;
    color: {TEXT};
}}
QListWidget::item:selected {{
    background-color: {BG3};
    color: {TEXT};
}}
QListWidget::item:hover {{
    background-color: #1c2128;
}}

/* ── Splitter ── */
QSplitter::handle {{
    background-color: {BORDER};
    width: 1px;
}}

/* ── Tooltip ── */
QToolTip {{
    background-color: {BG3};
    color: {TEXT};
    border: 1px solid {BORDER};
    padding: 4px 8px;
    border-radius: 4px;
}}
"""
