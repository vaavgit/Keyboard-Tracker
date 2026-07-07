# Contributing to KeyTracker

Thank you for your interest in contributing to KeyTracker! We welcome all types of contributions, including bug reports, feature requests, documentation updates, and code contributions.

## How to Contribute

### 1. Reporting Bugs
- Search existing issues to see if the bug has already been reported.
- If not, open a new issue with a clear description, steps to reproduce, and screenshots if applicable.

### 2. Suggesting Enhancements
- Open an issue explaining the feature request, why it would be useful, and how it should work.

### 3. Code Contributions
- **Fork** the repository and clone it locally.
- Set up a virtual environment and install dependencies from `requirements.txt`.
- Create a new branch for your feature or bugfix:
  ```bash
  git checkout -b feature/amazing-feature
  ```
- Write clean, formatted, and readable Python code.
- Ensure the app runs correctly by executing:
  ```bash
  python main.py
  ```
- Verify that PyInstaller builds successfully:
  ```bash
  pyinstaller KeyTracker.spec
  ```
- Commit your changes and push to your fork.
- Open a Pull Request from your fork to our `main` branch.

Thank you for helping make KeyTracker better!
