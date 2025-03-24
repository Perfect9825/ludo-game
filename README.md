# 🎲 Ludo Master Game

A fun and simple **4x4 Ludo game** developed in **Python** using the **Kivy framework**.
It supports Android & iOS packaging using **Buildozer**.

## 🚀 Features:

- Auto-play demo mode (autonomous moves)
- 4 houses: Red, Blue, Green, Yellow
- Clean and scalable UI
- Dynamic dice rolls & token movement
- Game-over detection with winner display
- Modular backend logic
- Test cases to verify backend functionality

## 🛠️ Tech Stack:

- Python 3.x
- Kivy
- Buildozer (for packaging to Android/iOS)
- Threading
- Object-Oriented Programming

## 📂 Project Structure:

/ludo_project
├── .gitignore               # Git ignore rules
├── buildozer.spec           # Buildozer configuration (for packaging)
├── LICENSE                  # MIT License
├── LudoIcon2.png            # App icon
├── LudoSplash2.png          # App splash screen
├── ludo/                    # Backend logic implementation
├── tests/                   # Unit tests
│   ├── __init__.py          # Makes 'tests' a package
│   ├── test_board.py        # Tests for board logic
│   ├── test_tokens.py       # Tests for token movement logic
│   └── test_game.py         # Tests for game flow
└── README.md                # Project documentation
└── main.py                # Frontend logic implementation (Using Kivy framework)

## ⚙️ Running the App:

1. **Install Dependencies:**
   ```bash```
   **pip install kivy**
   **pip install buildozer** # If packaging to Android/iOS

2. **Run the Game:**
   ```bash```
   **python main.py**

3. **📱 Packaging for Android (Optional):**
   ``bash``
   **buildozer init**
   **buildozer -v android debug**

4. **For iOS, configure Xcode & Mac environment and run:**
   ```bash```
   **buildozer -v ios debug**

## 🧪 Running Tests:

Test cases are available to check backend logic functionality.
```bash``` **cd tests** **python -m unittest discover**

## 📄 License:

This project is licensed under the MIT License.
See the [LICENSE](License.txt) file for details.

Copyright (C) 2025 Perfect9825. All rights reserved.

## 🙌 Contribution:

Feel free to fork, raise issues, or submit pull requests to improve the game.