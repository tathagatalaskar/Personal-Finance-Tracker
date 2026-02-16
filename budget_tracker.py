import sqlite3
import os
from datetime import date, timedelta, datetime
import matplotlib.pyplot as plt

DB_NAME = "finance_tracker.db"

def init_db():
    """Initializes the database with a 3NF Normalized Schema."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Cycles Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS cycles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_date TEXT,
                        end_date TEXT,
                        initial_income REAL)''')

    # 2. Transactions Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cycle_id INTEGER,
                        type TEXT,
                        category TEXT,
                        amount REAL,
                        description TEXT,
                        timestamp TEXT,
                        FOREIGN KEY(cycle_id) REFERENCES cycles(id))''')
    
    # 3. SQL View for Summaries
    cursor.execute('''CREATE VIEW IF NOT EXISTS v_cycle_summary AS 
                      SELECT cycle_id, type, SUM(amount) as total 
                      FROM transactions GROUP BY cycle_id, type''')
    
    conn.commit()
    conn.close()

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
    """Saves a transaction to the DB safely."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (cycle_id, type, category, amount, description, timestamp) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (cycle_id, t_type, amount, category, desc, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    print(f"\n✅ Successfully added {category}: ${amount:.2f}")

def calculate_burn_rate(cycle_id):
    """Calculates runway using: Balance / (Total Spent / Days Passed)"""
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
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM transactions WHERE cycle_id = ? AND type = 'expense' GROUP BY category", (cycle_id,))
    data = cursor.fetchall()
    conn.close()

    if not data:
        print("\n⚠️ No expenses found to graph!")
        return

    labels, values = zip(*data)
    plt.figure(figsize=(10, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("Spending Breakdown by Category")
    plt.axis('equal') 
    plt.savefig("spending_report.png")
    print("\n📈 Graph generated: Open 'spending_report.png' to view.")

def main():
    init_db()
    cycle = get_current_cycle()
    
    if not cycle:
        print("Welcome! Let's set up your first budget cycle.")
        while True:
            try:
                inc = float(input("Enter your starting income for this cycle: "))
                break
            except ValueError:
                print("Invalid input. Please enter a number (e.g., 1500.50)")
        
        start_new_cycle(inc)
        cycle = get_current_cycle()

    while True:
        print(f"\n{'='*30}")
        print(f" PAY-CYCLE TRACKER (ID: {cycle[0]})")
        print(f" Cycle Ends: {cycle[2]}")
        print(f"{'='*30}")
        print("1. 💸 Add Expense")
        print("2. 📊 View Burn Rate & Runway")
        print("3. 🎨 Generate Spending Chart")
        print("4. 🚪 Exit")
        
        choice = input("\nChoose an option: ")

        if choice == '1':
            while True:
                try:
                    amt = float(input("Amount spent: "))
                    break
                except ValueError:
                    print("Please enter a valid number for the amount.")
            
            print("\nCommon categories: Food, Rent, Transport, Entertainment, Shopping")
            cat = input("Category (or press enter for 'Miscellaneous'): ").strip()
            if not cat: cat = "Miscellaneous"
            
            add_transaction(cycle[0], 'expense', amt, cat, "User Entry")

        elif choice == '2':
            bal, rate, runway = calculate_burn_rate(cycle[0])
            print(f"\n--- Financial Health ---")
            print(f"Current Balance: ${bal:.2f}")
            print(f"Daily Spend Rate: ${rate:.2f}/day")
            if rate > 0:
                print(f"Estimated Runway: {runway:.1f} days remaining")
            else:
                print("Estimated Runway: Infinite (No expenses recorded yet!)")

        elif choice == '3':
            generate_visual_report(cycle[0])

        elif choice == '4':
            print("Goodbye! Stay within budget.")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
