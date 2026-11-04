
import os
from datetime import datetime, date, timedelta
from calendar import monthrange

from dotenv import load_dotenv
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
from bson.errors import InvalidId


# --------------------------------------------------
# 1. ENVIRONMENT CONFIGURATION
# --------------------------------------------------

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "spendwiselatest")

client = None
db = None

expenses_collection = None
budgets_collection = None


# --------------------------------------------------
# 2. CATEGORY NORMALIZATION
# --------------------------------------------------

CATEGORY_ALIASES = {
    "food": "Food",
    "foods": "Food",
    "grocery": "Groceries",
    "groceries": "Groceries",
    "shopping": "Shopping",
    "education": "Education",
    "books": "Education",
    "entertainment": "Entertainment",
    "medical": "Medical",
    "health": "Medical",
    "transport": "Travel",
    "transportation": "Travel",
    "travel": "Travel",
    "travelling": "Travel",
    "fuel": "Fuel",
    "rent": "Rent",
    "utilities": "Utilities",
    "bills": "Utilities",
    "other": "Other",
}


def normalize_category(category):
    """Convert category names into a consistent format."""

    if not category:
        return "Other"

    cleaned = str(category).strip().lower()

    return CATEGORY_ALIASES.get(
        cleaned,
        cleaned.title()
    )


# --------------------------------------------------
# 3. DATABASE CONNECTION
# --------------------------------------------------

def connect_database():
    """Connect to MongoDB Atlas."""

    global client, db
    global expenses_collection, budgets_collection

    if not MONGODB_URI:
        raise ValueError(
            "MONGODB_URI is missing. Check your .env file."
        )

    try:
        new_client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=10000
        )

        # Verify the connection
        new_client.admin.command("ping")

        client = new_client
        db = client[DATABASE_NAME]

        expenses_collection = db["expenses"]
        budgets_collection = db["budgets"]

        print("MongoDB connected successfully!")
        print(f"Database: {DATABASE_NAME}")

        return True

    except Exception as error:
        try:
            new_client.close()
        except Exception:
            pass

        client = None
        db = None
        expenses_collection = None
        budgets_collection = None

        print(f"MongoDB connection failed: {error}")
        raise


def close_database():
    """Close the MongoDB connection."""

    global client, db
    global expenses_collection, budgets_collection

    if client:
        client.close()

    client = None
    db = None
    expenses_collection = None
    budgets_collection = None

    print("MongoDB connection closed.")


def _check_connection():
    """Ensure database connection exists."""

    if expenses_collection is None or budgets_collection is None:
        connect_database()


# --------------------------------------------------
# 4. HELPER FUNCTIONS
# --------------------------------------------------

def _serialize_expense(expense):
    """Convert MongoDB document into JSON-friendly data."""

    if not expense:
        return None

    result = dict(expense)

    if "_id" in result:
        result["_id"] = str(result["_id"])

    return result


def _date_range(period):
    """
    Return start and end dates for a requested period.

    Supported periods:
    today, yesterday, this week, last week,
    this month, last month, this year, last year.
    """

    today = date.today()
    period = (period or "").strip().lower()

    if period == "today":
        start = today
        end = today + timedelta(days=1)

    elif period == "yesterday":
        start = today - timedelta(days=1)
        end = today

    elif period == "this week":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=7)

    elif period == "last week":
        end = today - timedelta(days=today.weekday())
        start = end - timedelta(days=7)

    elif period == "this month":
        start = today.replace(day=1)
        end = (
            start.replace(
                month=start.month + 1
            )
            if start.month < 12
            else date(start.year + 1, 1, 1)
        )

    elif period == "last month":
        end = today.replace(day=1)

        if end.month == 1:
            start = date(end.year - 1, 12, 1)
        else:
            start = date(end.year, end.month - 1, 1)

    elif period == "this year":
        start = date(today.year, 1, 1)
        end = date(today.year + 1, 1, 1)

    elif period == "last year":
        start = date(today.year - 1, 1, 1)
        end = date(today.year, 1, 1)

    else:
        raise ValueError(f"Unsupported date period: {period}")

    return (
        start.isoformat(),
        end.isoformat()
    )


# --------------------------------------------------
# 5. ADD EXPENSE
# --------------------------------------------------

def add_expense(amount, category, description=""):
    """Insert a new expense into MongoDB."""

    _check_connection()

    if amount is None or float(amount) <= 0:
        raise ValueError("Expense amount must be greater than zero.")

    expense = {
        "amount": float(amount),
        "category": normalize_category(category),
        "description": str(description or "").strip(),
        "date": date.today().isoformat(),
        "created_at": datetime.now().isoformat()
    }

    result = expenses_collection.insert_one(expense)

    expense["_id"] = str(result.inserted_id)

    return expense


# --------------------------------------------------
# 6. RETRIEVE EXPENSES
# --------------------------------------------------

def get_all_expenses(limit=None):
    """Retrieve expenses, newest first."""

    _check_connection()

    cursor = expenses_collection.find().sort(
        "created_at",
        DESCENDING
    )

    if limit is not None:
        cursor = cursor.limit(int(limit))

    return [
        _serialize_expense(expense)
        for expense in cursor
    ]


def get_total_expenses():
    """Calculate total spending across all expenses."""

    _check_connection()

    result = expenses_collection.aggregate([
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }
        }
    ])

    result = list(result)

    return float(result[0]["total"]) if result else 0.0


def get_category_total(category):
    """Calculate total spending for one category."""

    _check_connection()

    normalized = normalize_category(category)

    result = expenses_collection.aggregate([
        {
            "$match": {
                "category": normalized
            }
        },
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }
        }
    ])

    result = list(result)

    return float(result[0]["total"]) if result else 0.0


def get_category_summary():
    """Calculate spending totals grouped by category."""

    _check_connection()

    result = expenses_collection.aggregate([
        {
            "$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"},
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {
                "total": -1
            }
        }
    ])

    return [
        {
            "category": item["_id"],
            "total": float(item["total"]),
            "count": int(item["count"])
        }
        for item in result
    ]


# --------------------------------------------------
# 7. DATE-BASED EXPENSE QUERIES
# --------------------------------------------------

def get_total_by_date_range(start_date, end_date):
    """
    Calculate spending between two dates.

    start_date is inclusive.
    end_date is exclusive.
    Dates must use YYYY-MM-DD format.
    """

    _check_connection()

    result = expenses_collection.aggregate([
        {
            "$match": {
                "date": {
                    "$gte": start_date,
                    "$lt": end_date
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }
        }
    ])

    result = list(result)

    return float(result[0]["total"]) if result else 0.0


def get_expenses_filtered(
    category=None,
    start_date=None,
    end_date=None,
    limit=20
):
    """Retrieve expenses using optional filters."""

    _check_connection()

    query = {}

    if category:
        query["category"] = normalize_category(category)

    if start_date or end_date:
        query["date"] = {}

        if start_date:
            query["date"]["$gte"] = start_date

        if end_date:
            query["date"]["$lt"] = end_date

    cursor = expenses_collection.find(query).sort(
        "created_at",
        DESCENDING
    ).limit(int(limit))

    return [
        _serialize_expense(expense)
        for expense in cursor
    ]


# --------------------------------------------------
# 8. EXPENSE ANALYTICS
# --------------------------------------------------

def get_highest_expense():
    """Return the highest expense."""

    _check_connection()

    expense = expenses_collection.find_one(
        {},
        sort=[("amount", DESCENDING)]
    )

    return _serialize_expense(expense)


def get_average_expense():
    """Calculate average expense amount."""

    _check_connection()

    result = expenses_collection.aggregate([
        {
            "$group": {
                "_id": None,
                "average": {"$avg": "$amount"}
            }
        }
    ])

    result = list(result)

    return float(result[0]["average"]) if result else 0.0


# --------------------------------------------------
# 9. DELETE AND UPDATE EXPENSES
# --------------------------------------------------

def delete_expense(expense_id):
    """Delete an expense using its MongoDB ID."""

    _check_connection()

    try:
        object_id = ObjectId(expense_id)
    except (InvalidId, TypeError):
        return False

    result = expenses_collection.delete_one({
        "_id": object_id
    })

    return result.deleted_count > 0


def update_expense(expense_id, amount=None, category=None, description=None):
    """Update selected fields of an expense."""

    _check_connection()

    try:
        object_id = ObjectId(expense_id)
    except (InvalidId, TypeError):
        return False

    updates = {}

    if amount is not None:
        if float(amount) <= 0:
            raise ValueError("Expense amount must be greater than zero.")

        updates["amount"] = float(amount)

    if category is not None:
        updates["category"] = normalize_category(category)

    if description is not None:
        updates["description"] = str(description).strip()

    if not updates:
        return False

    result = expenses_collection.update_one(
        {"_id": object_id},
        {"$set": updates}
    )

    return result.matched_count > 0


# --------------------------------------------------
# 10. BUDGET MANAGEMENT
# --------------------------------------------------

def set_budget(category, amount):
    """Create or update a monthly budget for a category."""

    _check_connection()

    if amount is None or float(amount) <= 0:
        raise ValueError("Budget amount must be greater than zero.")

    normalized = normalize_category(category)

    budget = {
        "category": normalized,
        "amount": float(amount),
        "updated_at": datetime.now().isoformat()
    }

    budgets_collection.update_one(
        {"category": normalized},
        {"$set": budget},
        upsert=True
    )

    return budget


def get_all_budgets():
    """Retrieve all configured budgets."""

    _check_connection()

    return [
        _serialize_expense(budget)
        for budget in budgets_collection.find().sort("category", 1)
    ]


def get_budget_status(category=None):
    """
    Compare monthly spending against configured budgets.

    If category is provided, return its budget status.
    Otherwise, return status for all configured budgets.
    """

    _check_connection()

    budgets = list(budgets_collection.find())

    if category:
        normalized = normalize_category(category)

        budgets = [
            budget for budget in budgets
            if budget.get("category") == normalized
        ]

    today = date.today()
    month_start = today.replace(day=1).isoformat()

    if today.month == 12:
        next_month = date(today.year + 1, 1, 1)
    else:
        next_month = date(today.year, today.month + 1, 1)

    month_end = next_month.isoformat()

    statuses = []

    for budget in budgets:
        budget_category = budget["category"]

        spending = expenses_collection.aggregate([
            {
                "$match": {
                    "category": budget_category,
                    "date": {
                        "$gte": month_start,
                        "$lt": month_end
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$amount"}
                }
            }
        ])

        spending = list(spending)

        spent = (
            float(spending[0]["total"])
            if spending else 0.0
        )

        budget_amount = float(budget["amount"])

        statuses.append({
            "category": budget_category,
            "budget": budget_amount,
            "spent": spent,
            "remaining": budget_amount - spent,
            "percentage_used": (
                spent / budget_amount * 100
            )
        })

    return statuses
