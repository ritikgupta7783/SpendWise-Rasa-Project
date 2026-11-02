
import os
import time
from datetime import datetime, date
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pymongo import MongoClient, DESCENDING
from pymongo.errors import (
    AutoReconnect,
    ConnectionFailure,
    ServerSelectionTimeoutError,
    PyMongoError
)
from bson import ObjectId
from bson.errors import InvalidId


# --------------------------------------------------
# 1. ENVIRONMENT CONFIGURATION
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "spendwise_db")


# --------------------------------------------------
# 2. DATABASE GLOBAL VARIABLES
# --------------------------------------------------

client = None
db = None

expenses_collection = None
budgets_collection = None


# --------------------------------------------------
# 3. DATABASE CONNECTION
# --------------------------------------------------

def connect_database():
    global client, db
    global expenses_collection, budgets_collection

    if not MONGODB_URI:
        raise ValueError("MONGODB_URI is missing from .env")

    try:
        # Close an old client before creating another one.
        if client is not None:
            client.close()

        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000,
            retryReads=True,
            retryWrites=True,
            appname="SpendWise"
        )

        # Verify the actual connection.
        client.admin.command("ping")

        db = client[DATABASE_NAME]

        expenses_collection = db["expenses"]
        budgets_collection = db["budgets"]

        print("Successfully connected to MongoDB Atlas!")
        print("Database:", DATABASE_NAME)

        return True

    except Exception as error:
        print("MongoDB connection failed:", error)

        if client is not None:
            client.close()

        client = None
        db = None
        expenses_collection = None
        budgets_collection = None

        return False


# --------------------------------------------------
# 4. ENSURE DATABASE CONNECTION
# --------------------------------------------------

def ensure_connection():
    global client

    try:
        if client is None:
            return connect_database()

        client.admin.command("ping")
        return True

    except (AutoReconnect, ConnectionFailure,
            ServerSelectionTimeoutError, PyMongoError):

        print("MongoDB connection interrupted. Reconnecting...")

        return connect_database()


# --------------------------------------------------
# 5. ADD EXPENSE
# --------------------------------------------------

def add_expense(amount, category, description="", expense_date=None):

    if not ensure_connection():
        raise ConnectionFailure("Could not connect to MongoDB Atlas")

    if amount is None or float(amount) <= 0:
        raise ValueError("Expense amount must be greater than zero")

    if not category:
        raise ValueError("Expense category is required")

    if expense_date is None:
        expense_date = date.today()

    if isinstance(expense_date, datetime):
        expense_date = expense_date.date()

    if isinstance(expense_date, date):
        expense_date = expense_date.isoformat()

    expense = {
        "amount": float(amount),
        "category": str(category).strip().title(),
        "description": str(description).strip(),
        "date": expense_date,
        "created_at": datetime.utcnow()
    }

    result = expenses_collection.insert_one(expense)

    return str(result.inserted_id)


# --------------------------------------------------
# 6. GET ALL EXPENSES
# --------------------------------------------------

def get_all_expenses(limit=50):

    if not ensure_connection():
        raise ConnectionFailure("Database unavailable")

    expenses = list(
        expenses_collection.find()
        .sort("created_at", DESCENDING)
        .limit(limit)
    )

    for expense in expenses:
        expense["_id"] = str(expense["_id"])

    return expenses


# --------------------------------------------------
# 7. GET TOTAL EXPENSES
# --------------------------------------------------

def get_total_expenses():

    if not ensure_connection():
        raise ConnectionFailure("Database unavailable")

    result = list(
        expenses_collection.aggregate([
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$amount"}
                }
            }
        ])
    )

    if not result:
        return 0.0

    return float(result[0]["total"])


# --------------------------------------------------
# 8. CATEGORY-WISE SUMMARY
# --------------------------------------------------

def get_category_summary():

    if not ensure_connection():
        raise ConnectionFailure("Database unavailable")

    result = list(
        expenses_collection.aggregate([
            {
                "$group": {
                    "_id": "$category",
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"total": -1}
            }
        ])
    )

    return result


# --------------------------------------------------
# 9. DELETE EXPENSE
# --------------------------------------------------

def delete_expense(expense_id):

    if not ensure_connection():
        raise ConnectionFailure("Database unavailable")

    try:
        object_id = ObjectId(expense_id)
    except (InvalidId, TypeError):
        return False

    result = expenses_collection.delete_one(
        {"_id": object_id}
    )

    return result.deleted_count > 0


# --------------------------------------------------
# 10. UPDATE EXPENSE
# --------------------------------------------------

def update_expense(expense_id, new_amount):

    if not ensure_connection():
        raise ConnectionFailure("Database unavailable")

    if float(new_amount) <= 0:
        raise ValueError("Amount must be greater than zero")

    try:
        object_id = ObjectId(expense_id)
    except (InvalidId, TypeError):
        return False

    result = expenses_collection.update_one(
        {"_id": object_id},
        {"$set": {"amount": float(new_amount)}}
    )

    return result.modified_count > 0


# --------------------------------------------------
# 11. SET MONTHLY BUDGET
# --------------------------------------------------

def set_budget(category, monthly_limit):

    if not ensure_connection():
        raise ConnectionFailure("Database unavailable")

    if not category:
        raise ValueError("Budget category is required")

    if float(monthly_limit) <= 0:
        raise ValueError("Budget must be greater than zero")

    budgets_collection.update_one(
        {"category": str(category).strip().title()},
        {
            "$set": {
                "monthly_limit": float(monthly_limit),
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )

    return True


# --------------------------------------------------
# 12. GET ALL BUDGETS
# --------------------------------------------------

def get_all_budgets():

    if not ensure_connection():
        raise ConnectionFailure("Database unavailable")

    budgets = list(budgets_collection.find())

    for budget in budgets:
        budget["_id"] = str(budget["_id"])

    return budgets


# --------------------------------------------------
# 13. CLOSE DATABASE
# --------------------------------------------------

def close_database():

    global client, db
    global expenses_collection, budgets_collection

    if client is not None:
        client.close()

    client = None
    db = None
    expenses_collection = None
    budgets_collection = None

    print("MongoDB connection closed.")


# --------------------------------------------------
# 14. DIRECT DATABASE TEST
# --------------------------------------------------

if __name__ == "__main__":

    try:
        if connect_database():
            print("\n--- CONNECTION TEST SUCCESSFUL ---")

            print("\n--- TOTAL EXPENSES ---")
            print("Total: ₹", get_total_expenses())

            print("\n--- RECENT EXPENSES ---")

            for expense in get_all_expenses(limit=5):
                print(expense)

    except Exception as error:
        print("Database test failed:", error)

    finally:
        close_database()
