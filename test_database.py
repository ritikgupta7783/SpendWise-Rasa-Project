
from database.db import (
    connect_database,
    add_expense,
    get_all_expenses,
    get_total_expenses,
    get_category_summary,
    close_database
)

if connect_database():

    print("\n--- ADD EXPENSE ---")

    expense_id = add_expense(
        amount=200,
        category="Food",
        description="Lunch"
    )

    print("Inserted Expense ID:", expense_id)

    print("\n--- ALL EXPENSES ---")

    expenses = get_all_expenses()

    for expense in expenses:
        print(expense)

    print("\n--- TOTAL EXPENSES ---")

    print("Total: ₹", get_total_expenses())

    print("\n--- CATEGORY SUMMARY ---")

    for item in get_category_summary():
        print(item)

    close_database()
