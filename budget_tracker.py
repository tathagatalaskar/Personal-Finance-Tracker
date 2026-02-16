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
    
    conn.commit()
    conn.close()

# --- Core Logic Functions ---

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
    """Saves a transaction to the DB safely using Parameterized Queries."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (cycle_id, type, category, amount, description, timestamp) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (cycle_id, t_type, amount, category, desc, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    print(f"\n✅ Successfully added {category}: ${amount:,.2f}")

def calculate_burn_rate(cycle_id):
    """Predictive Logic: Forecasts financial runway based on spend velocity."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT start_date FROM cycles WHERE id = ?", (cycle_id,))
    start_str = cursor.fetchone()[0]
    start_date = datetime.strptime(start_str, "%Y-%m-%d")
    
    # Calculate days passed (minimum 1 to avoid division by zero)
    days_passed = (datetime.now() - start_date).days + 1
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE cycle_id = ? AND type = 'expense'", (cycle_id,))
    total_spent = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE cycle_id = ? AND type = 'income'", (cycle_id,))
    total_income = cursor.fetchone()[0] or 0
    
    balance = total_income - total_spent
    daily_rate = total_spent / days_passed
    runway = balance / daily_rate if daily_rate > 0 else 0
    
    conn.close()
    return balance, daily_rate, runway

def generate_visual_report(cycle_id):
    """Generates a category distribution chart with professional validation."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM transactions WHERE cycle_id = ? AND type = 'expense' GROUP BY category", (cycle_id,))
    data = cursor.fetchall()
    conn.close()

    if not data:
        print("\n⚠️ No expenses found! Add some transactions before generating a chart.")
        return

    labels, values = zip(*data)
    plt.figure(figsize=(10, 6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title(f"Spending Distribution (Cycle {cycle_id})")
    plt.axis('equal') 
    plt.savefig("spending_report.png")
    print("\n📈 Success: 'spending_report.png' generated in your project folder.")

# --- Main Interface ---

def main():
    init_db()
    cycle = get_current_cycle()
    
    if not cycle:
        print("Welcome! Let's initialize your first budget cycle.")
        while True:
            try:
                inc = float(input("Enter starting income for this cycle: "))
                if inc < 0: raise ValueError
                break
            except ValueError:
                print("❌ Please enter a valid positive number.")
        
        start_new_cycle(inc)
        cycle = get_current_cycle()

    while True:
        print(f"\n{'='*40}")
        print(f" 💳 PAY-CYCLE TRACKER | ID: {cycle[0]}")
        print(f" 📅 Ends: {cycle[2]}")
        print(f"{'='*40}")
        print("1. 💸 Add Expense")
        print("2. 📊 View Burn Rate & Runway")
        print("3. 🎨 Generate Category Chart")
        print("4. 🚪 Exit")
        
        choice = input("\nSelect an option: ")

        if choice == '1':
            while True:
                try:
                    amt = float(input("Amount: "))
                    if amt <= 0: raise ValueError
                    break
                except ValueError:
                    print("❌ Invalid amount. Enter a positive number.")
            
            print("\nSuggestions: Food, Rent, Transport, Entertainment, Shopping, Health")
            cat = input("Category (or press Enter for 'Misc'): ").strip().title()
            if not cat: cat = "Misc"
            
            add_transaction(cycle[0], 'expense', amt, cat, "User Entry")

        elif choice == '2':
            bal, rate, runway = calculate_burn_rate(cycle[0])
            print(f"\n--- 📈 FINANCIAL FORECAST ---")
            print(f"Current Balance : ${bal:,.2f}")
            print(f"Daily Spend Rate: ${rate:,.2f}/day")
            if rate > 0:
                print(f"Est. Runway    : {runway:.1f} days remaining")
            else:
                print("Est. Runway    : Infinite (No expenses recorded)")

        elif choice == '3':
            generate_visual_report(cycle[0])

        elif choice == '4':
            print("Goodbye! Keeping your finances on track. 🚀")
            break
        else:
            print("❌ Invalid selection. Please choose 1-4.")

if __name__ == "__main__":
    main()
