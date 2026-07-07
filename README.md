# KeyTracker 🎮🖱️⌨️

A lightweight, local-only desktop application that tracks keyboard analytics, monitors mouse activity, builds live heatmaps, and measures typing metrics. 

It is written in Python using **PyQt6** for the UI, **matplotlib** for visualizations, and **pynput** for system-wide keyboard and mouse hooks.

---

## Why I Built This

I wanted a keyboard heatmap, mouse tracking, and speed analysis tool to evaluate my coding speed and gaming sessions. Most telemetry tools require online logins, run suspicious background processes, or send telemetry to external servers. 

KeyTracker is **100% offline**. It captures inputs locally, makes zero network requests, and saves session logs as raw JSON files in a local directory.

---

## Features

- 🔥 **Real-Time Heatmap**: A live visual map showing keypress frequency.
- 🖱️ **Mouse Click Tracker**: Captures and counts left, right, middle, and side button mouse clicks to analyze overall gaming/workday inputs.
- ⚡ **Interactive Typing Test**: Evaluate your WPM (Words Per Minute) and accuracy with an interactive paragraph-matching test. Characters are colored in green or red in real-time as you type, matching standard online speed-testing platforms.
- 🎮 **Gaming Dashboard**: Monitors specific gaming key configurations (WASD, Space, Shift, Ctrl, numbers) and calculates strafe ratios (A/D).
- 📊 **Progression History**: Log and compare test runs over time to watch your typing speed and accuracy climb.
- ⚖️ **Session Comparison**: Load any two saved logs side-by-side to diff key distributions, total keypresses, and mouse clicks.

---

## Getting Started

### Prerequisites
Make sure you have Python 3.10+ installed.

### 1. Installation
Clone the repository and install the dependencies in the root directory:
```bash
# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Running the App
Start the app by running:
```bash
python main.py
```

### 3. Standalone Compilation
To compile KeyTracker into a single standalone executable (e.g., `.exe` on Windows):
```bash
# Install pyinstaller
pip install pyinstaller

# Build the executable
pyinstaller KeyTracker.spec
```
The compiled executable will be located in the `dist/` directory.

---

## Project Structure

- `main.py`: Entry point; defines layout and actions for the PyQt6 UI.
- `engine.py`: Runs a background thread tracking global system inputs (key hooks & mouse clicks).
- `heatmap_widget.py`: Custom matplotlib canvas drawing the keyboard heatmap.
- `theme.py`: Defines color palettes and stylesheet rules for the dark minimal theme.
- `KeyTracker.spec`: Configuration for PyInstaller packaging.

---

## License

This project is open-source. Feel free to fork, modify, and use it however you'd like.
