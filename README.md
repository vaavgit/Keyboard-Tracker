# KeyTracker 🎮⌨️

A lightweight, offline desktop application that tracks keyboard analytics, builds live heatmaps, and monitors keypress speed. 

It is written in Python using **PyQt6** for the UI, **matplotlib** for the heatmap visualizations, and **pynput** for global keyboard and mouse tracking.

---

## Why I Built This

I wanted a keyboard heatmap and speed tracker to analyze my gaming sessions and coding sprints. Almost every tool available online either required an account, had excessive bloat, or raised privacy concerns by running background telemetry. 

KeyTracker is **100% local**. It runs entirely on your machine, makes zero network requests, and saves session logs as raw JSON files in a local directory.

---

## Features

- 🔥 **Real-Time Heatmap**: A visual map showing keyboard frequency that updates dynamically as you type.
- ⚡ **KPM (Keys Per Minute) Tracker**: Monitors typing speed peaks and averages over the course of a session.
- 🎮 **Gaming Dashboard**: Specially monitors gaming layouts (WASD, Space, Shift, Ctrl, Q/E/R/F) and calculates key ratios (like your A/D strafe ratio).
- 📂 **Session History**: Save sessions and load them later to review your statistics.
- ⚖️ **Comparison Tool**: Load any two saved sessions side-by-side to compare metrics (KPM, total keystrokes, distribution).

---

## Getting Started

### Prerequisites
Make sure you have Python 3.10+ installed.

### 1. Installation
Clone the repository and install the dependencies from the root directory:
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

### 3. Packaging into a Standalone Executable
If you want to compile KeyTracker into a single standalone executable (e.g. an `.exe` file on Windows), you can use PyInstaller with the provided `.spec` file:
```bash
# Install pyinstaller if you don't have it
pip install pyinstaller

# Build the executable
pyinstaller KeyTracker.spec
```
The compiled executable will be located in the `dist/` directory.

---

## Project Structure

- `main.py`: The entry point and PyQT6 UI layout/interactions.
- `engine.py`: Background thread listener that hooks keyboard/mouse inputs and emits updates.
- `heatmap_widget.py`: Custom matplotlib canvas that plots the keyboard layout.
- `theme.py`: Custom stylesheet and color palettes for the dark minimal UI.
- `requirements.txt`: Python package dependencies.
- `KeyTracker.spec`: Config file for building a standalone app with PyInstaller.

---

## License

This project is open-source. Feel free to fork, modify, and use it however you'd like.
