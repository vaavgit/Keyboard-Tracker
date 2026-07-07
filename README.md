# KeyTracker 🎮⌨️🖱️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.4.0+-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Made with ❤️](https://img.shields.io/badge/Made%20with-%E2%9D%A4%EF%B8%8F-red.svg)](https://github.com/vaavgit/Keyboard-Tracker)

> **A lightweight, local-only desktop application that tracks keyboard analytics, monitors mouse activity, builds live heatmaps, and measures typing speed and accuracy.**

KeyTracker is 100% offline, privacy-focused, and designed for gamers, developers, and anyone who wants deep insights into their input behavior.

---

## ✨ Features

### 🔥 **Real-Time Keyboard Heatmap**
- Visual map showing keypress frequency across your entire keyboard
- Live updates as you type
- Color-coded intensity visualization

### ⚡ **Interactive Typing Speed Test**
- Measure **WPM** (Words Per Minute) and **Accuracy**
- Real-time character feedback (green for correct, red for incorrect)
- Multiple practice paragraphs
- Auto-completion when test finishes
- Progression history tracking

### 🖱️ **Mouse Click Tracker**
- Captures left, right, middle, and side button clicks
- Tracks scroll wheel interactions
- Comprehensive click statistics

### 🎮 **Gaming Dashboard**
- Dedicated monitoring for gaming keys (WASD, Space, Shift, Ctrl)
- **Strafe Ratio Analysis** - Calculate left/right movement distribution (A/D ratio)
- Number key tracking (1-5)
- Perfect for analyzing gaming performance

### 📊 **Session Management**
- Save and load tracking sessions as JSON
- View detailed session statistics
- Compare two sessions side-by-side
- Export data for analysis

### 🔐 **100% Offline & Private**
- Zero network requests
- All data stored locally
- No telemetry, no tracking, no logins required
- Full control over your data

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Windows, macOS, or Linux**

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/vaavgit/Keyboard-Tracker.git
cd Keyboard-Tracker
```

#### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run the Application
```bash
python main.py
```

---

## 📦 Build Standalone Executable

### Create a Single .EXE File (Windows)
```bash
pip install pyinstaller
pyinstaller KeyTracker.spec
```

The compiled executable will be in the `dist/` directory. You can run it without Python installed!

---

## 📖 How to Use

### **Live Tab** - Track Your Activity
1. Enter a session name (e.g., "Gaming Session 1", "Coding Marathon")
2. Click **Start** to begin tracking
3. Your keyboard heatmap, click counts, and stats update in real-time
4. Click **Stop & Save** when done
5. Session is automatically saved as JSON

### **Typing Test Tab** - Measure Your Speed
1. Click **Start Test**
2. Read the displayed paragraph
3. Type it in the text box
4. Watch real-time accuracy feedback (green = correct, red = mistakes)
5. Test auto-completes when finished
6. Check your **WPM** and **Accuracy** in the stats cards
7. History of all test runs appears on the right

### **Sessions Tab** - View Saved Data
- Browse all saved sessions
- Click a session to see detailed statistics
- Compare top keys, WASD distribution, and strafe ratios

### **Compare Tab** - Side-by-Side Analysis
- Select two sessions from the left and right lists
- Click **Compare Selected Sessions**
- View a detailed diff of key distribution, mouse clicks, and KPM

---

## 🎯 Use Cases

**For Gamers:**
- Analyze your gaming performance
- Track WASD key distribution for movement patterns
- Monitor mouse click frequency
- Improve reaction time through typing speed tests

**For Developers:**
- Track your coding speed and efficiency
- Analyze keyboard patterns and hot keys
- Measure productivity in different coding sessions

**For Typists:**
- Measure WPM improvement over time
- Practice typing accuracy
- Build consistent touch typing habits

**For Anyone:**
- Private keyboard analytics
- No cloud storage or tracking
- Completely offline operation

---

## 📁 Project Structure

```
Keyboard-Tracker/
├── main.py                 # Main UI and window management
├── engine.py              # Core tracking engine & background thread
├── heatmap_widget.py      # Keyboard heatmap visualization
├── theme.py               # Dark theme and color constants
├── KeyTracker.spec        # PyInstaller configuration
├── requirements.txt       # Python dependencies
├── LICENSE                # MIT License
├── README.md              # This file
└── sessions/              # Auto-created directory for saved JSON data
```

---

## 🛠️ Technical Details

### Dependencies
- **pynput** - System-wide keyboard and mouse event hooks
- **PyQt6** - Cross-platform desktop GUI framework
- **matplotlib** - Heatmap visualization
- **numpy** - Data processing

### Architecture
- **Multithreaded**: Background listener thread captures input without blocking UI
- **Thread-safe**: Locks protect shared state between UI and tracking threads
- **Low overhead**: Minimal CPU/memory usage
- **Zero network**: Completely self-contained

---

## 🔐 Privacy & Security

✅ **Completely Offline**
- No internet connection required
- No cloud storage
- No telemetry or tracking

✅ **Full Data Control**
- All session data stored locally in `sessions/` directory
- Data remains on your computer
- Export sessions as JSON anytime

✅ **Open Source**
- Transparent code you can audit
- MIT License - free for personal and commercial use

---

## 🐛 Troubleshooting

### Issue: Permission Denied on macOS/Linux
Solution: Grant accessibility permissions
```bash
# macOS: System Preferences → Security & Privacy → Accessibility
# Linux: May need sudo for keyboard hooking
```

### Issue: ImportError for pynput
Solution: Reinstall dependencies
```bash
pip install --upgrade pynput
```

### Issue: KeyTracker won't start
Solution: Ensure Python 3.10+ is installed
```bash
python --version
```

---

## 📝 License

This project is open-source under the **MIT License**. See [LICENSE](LICENSE) for details.

You're free to:
- ✅ Use for personal or commercial purposes
- ✅ Modify and redistribute
- ✅ Fork and create derivatives
- ✅ Use privately or publicly

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. **Fork** the repository
2. **Create a branch** for your feature (`git checkout -b feature/amazing-feature`)
3. **Make your changes** and commit (`git commit -m 'Add amazing feature'`)
4. **Push to your branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request** with a clear description

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 💡 Ideas for Future Features

- [ ] Dark/Light theme toggle
- [ ] Custom keyboard layouts
- [ ] Audio alerts for typing tests
- [ ] Export to CSV
- [ ] Advanced analytics dashboard
- [ ] Multiplayer comparisons
- [ ] Integration with fitness trackers
- [ ] Mobile companion app

---

## 📞 Support & Feedback

- **Found a bug?** [Open an Issue](https://github.com/vaavgit/Keyboard-Tracker/issues)
- **Have a feature request?** [Create a Discussion](https://github.com/vaavgit/Keyboard-Tracker/discussions)
- **Want to contribute?** Check out [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 🎖️ Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- Input hooking via [pynput](https://github.com/moses-palmer/pynput)
- Visualization with [matplotlib](https://matplotlib.org/)

---

## 📊 Stats

- ⌨️ Tracks every keystroke
- 🖱️ Monitors all mouse interactions
- 📈 Real-time performance metrics
- 💾 Persistent session storage

---

**Made with ❤️ by [@vaavgit](https://github.com/vaavgit)**

⭐ **If you find KeyTracker useful, please give it a star!** ⭐
