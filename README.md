# Pay-Cycle Personal Finance Tracker

A command-line application built with Python to help users manage their finances based on their personal pay cycle rather than a standard calendar month. This tool provides persistent data storage and automatically rolls over savings to the next cycle.

![Demo GIF of the application in use](link_to_your_gif_or_screenshot.gif)

## 🌟 Key Features

- **Cycle-Based Tracking:** Define your budget from one payday to the next (e.g., 15th of the month to the 15th of the next).
- **Data Persistence:** User data is saved to a local `budget_data.json` file, so progress is never lost.
- **Automated Savings Rollover:** Automatically calculates savings at the end of a cycle and adds it to the next month's income.
- **Dynamic Transaction Logging:** Add expenses and extra income on the fly.
- **Smart Date Handling:** Utilizes Python's `datetime` module to correctly calculate cycle end-dates, immune to month lengths and leap years.
- **User-Friendly Interface:** A simple, menu-driven command-line interface makes it easy to use.

## 🛠️ Tech Stack

- **Language:** Python
- **Core Libraries:** `datetime`, `json`, `os`

## 🚀 How to Run

1.  Ensure you have Python 3 installed.
2.  Clone this repository or download the `budget_tracker.py` file.
3.  Open your terminal, navigate to the project directory, and run the command:
    ```bash
    python budget_tracker.py
    ```
4.  The application will start and guide you through the setup.
