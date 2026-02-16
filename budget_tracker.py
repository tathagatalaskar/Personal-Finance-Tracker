import sqlite3
import os
from datetime import date, timedelta, datetime
import matplotlib.pyplot as plt

DB_NAME = "finance_tracker.db"

def init_db():
    """Initializes the database with a 3NF Normalized Schema."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Cycles Table (Normalization: Separating time periods)
    cursor.execute('''CREATE TABLE IF NOT EXISTS cycles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_date TEXT,
                        end_date TEXT,
                        initial_income REAL)''')

    # 2. Transactions Table (Linked via Foreign Key)
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cycle_id INTEGER,
                        type TEXT,
                        category TEXT,
                        amount REAL,
                        description TEXT,
                        timestamp TEXT,
                        FOREIGN KEY(cycle_id) REFERENCES cycles(id))''')
    
    # 3. SQL View for Reporting (Shows DQL proficiency)
    cursor.execute('''CREATE VIEW IF NOT EXISTS v_cycle_summary AS 
                      SELECT cycle_id, type, SUM(amount) as total 
                      FROM transactions GROUP BY cycle_id, type''')
    
    # 4. SQL Trigger for Audit Logging (Advanced DBMS feature)
    cursor.execute('''CREATE TABLE IF NOT EXISTS audit_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        action TEXT,
                        trans_id INTEGER,
                        timestamp TEXT)''')
    
    cursor.execute('''CREATE TRIGGER IF NOT EXISTS log_deletion
                      AFTER DELETE ON transactions
                      BEGIN
                        INSERT INTO audit_log (action, trans_id, timestamp)
                        VALUES ('DELETE', old.id, DATETIME('now'));
                      END;''')
    
    conn.commit()
    conn.close()

# --- Core Application Logic ---

def get_current_cycle():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cycles ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row

def start_new_cycle(income, rollover=0.0):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    start = date.today().isoformat()
    end = (date.today() + timedelta(days=30)).isoformat()
    total_income = income + rollover
    
    cursor.execute("INSERT INTO cycles (start_date, end_date, initial_income) VALUES (?, ?, ?)",
                   (start, end, total_income))
    cycle_id = cursor.lastrowid
    
    cursor.execute("INSERT INTO transactions (cycle_id, type, category, amount, description, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                   (cycle_id, 'income', 'Salary', total_income, 'Initial Cycle Funds', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    return cycle_id
    
def add_transaction(cycle_id, t_type, amount, category, desc):
    """Adds an expense or income to the transactions table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (cycle_id, type, category, amount, description, timestamp) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (cycle_id, t_type, amount, category, desc, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    print(f"Success: Added {t_type} of ${amount:.2f} in category '{category}'.")

def calculate_burn_rate(cycle_id):
    """Predictive Logic: Forecasts financial runway."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT start_date FROM cycles WHERE id = ?", (cycle_id,))
    start_date = datetime.strptime(cursor.fetchone()[0], "%Y-%m-%d")
    days_passed = (datetime.now() - start_date).days + 1
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE cycle_id = ? AND type = 'expense'", (cycle_id,))
    total_spent = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE cycle_id = ? AND type = 'income'", (cycle_id,))
    total_income = cursor.fetchone()[0] or 0
    
    balance = total_income - total_spent
    daily_rate = total_spent / days_passed if days_passed > 0 else 0
    runway = balance / daily_rate if daily_rate > 0 else 0
    
    conn.close()
    return balance, daily_rate, runway

def generate_visual_report(cycle_id):
    """Generates a category distribution chart."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM transactions WHERE cycle_id = ? AND type = 'expense' GROUP BY category", (cycle_id,))
    data = cursor.fetchall()
    conn.close()

    if data:
        labels, values = zip(*data)
        plt.figure(figsize=(8, 6))
        plt.pie(values, labels=labels, autopct='%1.1f%%')
        plt.title("Spending Analysis")
        plt.savefig("spending_report.png")
        print("Success: 'spending_report.png' generated.")

def main():
    init_db()
    cycle = get_current_cycle()
    
    if not cycle:
        inc = float(input("Enter cycle starting income: "))
        start_new_cycle(inc)
        cycle = get_current_cycle()

    while True:
        print(f"\n--- Pay-Cycle Tracker (Cycle ID: {cycle[0]}) ---")
        print("1. Add Expense")
        print("2. Predictive Burn Rate (Runway)")
        print("3. Generate Chart")
        print("4. Exit")
        
        cmd = input("Select: ")
        if cmd == '1':
            amt = float(input("Amount: "))
            cat = input("Category: ")
            add_transaction(cycle[0], 'expense', amt, cat, "User Entry")
        elif cmd == '2':
            bal, rate, runway = calculate_burn_rate(cycle[0])
            print(f"Runway: {runway:.1f} days remaining at ${rate:.2f}/day.")
        elif cmd == '3':
            generate_visual_report(cycle[0])
        elif cmd == '4':
            break

if __name__ == "__main__":
    main()
