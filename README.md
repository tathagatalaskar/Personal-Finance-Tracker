# 💸 Pay-Cycle Finance Tracker (Pro)

> **A Smart Financial Forecasting Tool built with Python & SQLite**

Most budget apps fail because they strictly follow calendar months.
This tool is built for the real world—tracking your money from **paycheck to paycheck**.

It doesn't just record what you spent — it uses a **Predictive Burn-Rate Algorithm** to calculate exactly how many days your money will last.

---

## 🎯 Why This Project Matters

For recruiters evaluating technical depth, this project demonstrates:

* ✅ **DBMS Mastery:**
  Uses a **3NF Normalized SQLite Database** with optimized **SQL Views** for structured reporting.

* 📈 **Financial Intelligence:**
  Implements a **Daily Spend Velocity Algorithm** to forecast your *Financial Runway*.

* 🔐 **Professional Integrity:**
  Includes **Input Validation** and **Parameterized Queries** to prevent SQL injection and crashes.

* 📊 **Data Visualization:**
  Converts raw SQL data into visual spending distribution charts using **Matplotlib**.

---

## 🚀 How to Run (Step-by-Step)

Follow these steps to set up the project locally.
This will **wipe any old versions** and start fresh.

---

### 1️⃣ Download & Clean Slate

Open your **Terminal (Mac/Linux)** or **Command Prompt (Windows)** and run:

```bash
# Remove old folder (if exists)
rm -rf Personal-Finance-Tracker

# Clone fresh copy from GitHub
git clone https://github.com/tathagatalaskar/Personal-Finance-Tracker.git

# Navigate into project folder
cd Personal-Finance-Tracker
```

---

### 2️⃣ Install Required Libraries

Install dependencies (mainly for chart visualization):

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Launch the Application

Start the tracker:

```bash
python3 budget_tracker.py
```

---

## 📊 Features (For Interviewers)

### 🔥 Predictive Burn Rate

Uses financial forecasting logic:

```
Runway = Balance / DailySpendRate
```

Predicts how long your current balance will sustain your spending habits.

---

### 🗄️ Audit-Ready Database

* SQLite backend
* Persistent `.db` file created locally
* Data separated cleanly from application logic

---

### 📈 Visual Insights

* Automatically generates `spending_report.png`
* Pie chart visualization of category-wise spending
* Helps identify financial leakage

---

## 🛠️ Tech Stack

| Component     | Technology                           |
| ------------- | ------------------------------------ |
| Language      | Python 3.x                           |
| Database      | SQLite3 (Relational DB)              |
| Analytics     | Python Datetime + Linear Forecasting |
| Visualization | Matplotlib                           |

---

## 📂 Project Structure

```
Personal-Finance-Tracker/
│
├── budget_tracker.py
├── requirements.txt
├── spending_report.png
├── finance.db
└── README.md
```

---

## 👨‍💻 Author

**Tathagata Laskar**
Computer Science Student
UID: 24BCS11358

Specialization: **Database Management & Predictive Logic**

📧 Email: [tathagata.laskar24@gmail.com](mailto:tathagata.laskar24@gmail.com)

---

