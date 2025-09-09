import json
import os
from datetime import date, timedelta, datetime

# The name of the file where we'll save our data
DATA_FILE = "budget_data.json"

# --- Functions for Saving and Loading Data ---
def load_data():
    """Loads budget data from the JSON file. If no file exists, it starts a new setup."""
    if not os.path.exists(DATA_FILE):
        return setup_new_cycle()
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("Error reading the data file. It might be corrupted. Starting a new cycle.")
            return setup_new_cycle()

def save_data(data):
    """Saves the given data to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    print("Data saved successfully.")

# --- Core Application Functions ---
def setup_new_cycle(savings=0.0):
    """Sets up a new budget cycle. Asks for income and start date."""
    print("\n--- Setting Up New Budget Cycle ---")
    
    # Add savings from the previous month
    if savings > 0:
        print(f"Carrying over savings of ${savings:.2f}")

    while True:
        try:
            income_str = input("Enter your total income for this cycle: ")
            initial_income = float(income_str) + savings
            break
        except ValueError:
            print("Invalid amount. Please enter a number.")
    
    while True:
        try:
            start_date_str = input(f"Enter the start date (YYYY-MM-DD), or press Enter for today ({date.today().isoformat()}): ")
            if not start_date_str:
                start_date = date.today()
            else:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            break
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            
    # The cycle ends 30 days after it starts
    end_date = start_date + timedelta(days=30)
    
    data = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "initial_income": initial_income,
        "transactions": [
            {"type": "income", "amount": initial_income, "desc": "Initial Income"}
        ]
    }
    save_data(data)
    print(f"New cycle started! It will end on {end_date.isoformat()}.")
    return data

def add_transaction(data, trans_type):
    """Adds an expense or extra income to the transactions list."""
    try:
        amount = float(input(f"Enter the {trans_type} amount: $"))
        desc = input(f"Enter a short description for this {trans_type}: ")
        
        transaction = {"type": trans_type, "amount": amount, "desc": desc}
        data["transactions"].append(transaction)
        save_data(data)
    except ValueError:
        print("Invalid amount. Please enter a number.")

def view_summary(data):
    """Displays a summary of the current cycle."""
    print("\n--- Current Cycle Summary ---")
    print(f"Cycle: {data['start_date']} to {data['end_date']}")
    
    total_income = 0
    total_expense = 0
    
    for trans in data["transactions"]:
        if trans["type"] == "income":
            total_income += trans["amount"]
        else:
            total_expense += trans["amount"]
            
    remaining_balance = total_income - total_expense
    
    print(f"\nTotal Income:  ${total_income:.2f}")
    print(f"Total Expense: ${total_expense:.2f}")
    print("-------------------------")
    print(f"Balance Left:  ${remaining_balance:.2f}")
    
    print("\n--- All Transactions ---")
    for trans in data["transactions"]:
        print(f"- {trans['desc']} ({trans['type']}): ${trans['amount']:.2f}")
    print("-------------------------")

# --- Main Program Logic ---
def main():
    """The main function that runs the application."""
    data = load_data()
    
    # Check if the current cycle has ended
    today = date.today()
    end_date = date.fromisoformat(data["end_date"])

    if today > end_date:
        print("\nYour budget cycle has ended!")
        view_summary(data)
        
        # Calculate savings
        total_income = sum(t['amount'] for t in data['transactions'] if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in data['transactions'] if t['type'] == 'expense')
        savings = total_income - total_expense
        
        print(f"\nYou saved ${savings:.2f} this cycle!")
        
        if input("Would you like to start the next cycle? (yes/no): ").lower() == 'yes':
            data = setup_new_cycle(savings)
        else:
            print("Goodbye!")
            return

    # If the cycle is ongoing, show the menu
    while True:
        print("\n--- Pay-Cycle Finance Tracker ---")
        print(f"Current cycle ends on: {data['end_date']}")
        print("1. Add Expense")
        print("2. Add Extra Income")
        print("3. View Current Summary")
        print("4. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            add_transaction(data, "expense")
        elif choice == '2':
            add_transaction(data, "income")
        elif choice == '3':
            view_summary(data)
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

# This line ensures the main() function runs when you execute the script
if __name__ == "__main__":
    main()