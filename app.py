
import os
import json
import logging

from datetime import date, datetime, timedelta
from collections import defaultdict
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from flask import Flask, request, jsonify
from flask_cors import CORS

from bson import ObjectId
from bson.errors import InvalidId

from database.db import (
    connect_database,
    get_all_expenses,
    get_total_expenses,
    get_category_summary,
    get_all_budgets,
    get_budget_status,
    get_expenses_filtered,
    get_highest_expense,
    get_average_expense,
    add_expense,
    update_expense,
    delete_expense,
    get_total_by_date_range
)


# ==================================================
# 1. APPLICATION CONFIGURATION
# ==================================================

app = Flask(__name__)

app.config["JSON_SORT_KEYS"] = False

logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# Configure allowed frontend origins.
# Add your deployed frontend URL to FRONTEND_ORIGINS when needed.
allowed_origins = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5500,http://127.0.0.1:5500"
).split(",")

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [origin.strip() for origin in allowed_origins]
        }
    }
)

RASA_URL = os.getenv(
    "RASA_URL",
    "http://localhost:5005/webhooks/rest/webhook"
)

RASA_STATUS_URL = os.getenv(
    "RASA_STATUS_URL",
    "http://localhost:5005/status"
)

MAX_EXPENSE_LIMIT = 10000


# ==================================================
# 2. COMMON HELPER FUNCTIONS
# ==================================================

def error_response(message, status_code=500):
    """Return a consistent API error response."""

    return jsonify({
        "success": False,
        "message": message
    }), status_code


def validate_date(value):
    """Validate YYYY-MM-DD date strings."""

    if not value:
        return None

    try:
        return date.fromisoformat(value).isoformat()
    except (ValueError, TypeError):
        raise ValueError("Dates must use YYYY-MM-DD format.")


def validate_amount(value):
    """Validate a positive numeric amount."""

    try:
        amount = float(value)
    except (ValueError, TypeError):
        raise ValueError("Amount must be a valid number.")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    return amount


def get_json_body():
    """Safely retrieve JSON request data."""

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        raise ValueError("A valid JSON object is required.")

    return data


# ==================================================
# 3. HOME ROUTE
# ==================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "success": True,
        "application": "SpendWise",
        "message": "SpendWise API is running!",
        "version": "2.0"
    })


# ==================================================
# 4. DASHBOARD STATISTICS
# ==================================================

@app.route("/api/dashboard", methods=["GET"])
def dashboard():

    try:
        # Retrieve all expenses for accurate transaction counts.
        expenses = get_all_expenses(limit=None)

        total = get_total_expenses()

        today = date.today()
        month_start = today.replace(day=1).isoformat()

        if today.month == 12:
            next_month = date(today.year + 1, 1, 1)
        else:
            next_month = date(today.year, today.month + 1, 1)

        month_end = next_month.isoformat()

        monthly_total = get_total_by_date_range(
            month_start,
            month_end
        )

        budgets = get_all_budgets()

        return jsonify({
            "success": True,
            "total_expenses": round(float(total), 2),
            "monthly_expenses": round(float(monthly_total), 2),
            "total_transactions": len(expenses),
            "budget_count": len(budgets),
            "currency": "INR"
        })

    except Exception:
        app.logger.exception("Dashboard error")
        return error_response("Unable to load dashboard statistics.")


# ==================================================
# 5. EXPENSE RETRIEVAL AND FILTERING
# ==================================================

@app.route("/api/expenses", methods=["GET"])
def expenses():

    try:
        limit = request.args.get(
            "limit",
            default=100,
            type=int
        )

        limit = max(1, min(limit, MAX_EXPENSE_LIMIT))

        category = request.args.get("category")

        start_date = validate_date(
            request.args.get("start_date")
        )

        end_date = validate_date(
            request.args.get("end_date")
        )

        if start_date and end_date and start_date > end_date:
            return error_response(
                "Start date cannot be after end date.",
                400
            )

        records = get_expenses_filtered(
            category=category,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

        return jsonify({
            "success": True,
            "count": len(records),
            "expenses": records
        })

    except ValueError as error:
        return error_response(str(error), 400)

    except Exception:
        app.logger.exception("Expense retrieval error")
        return error_response("Unable to retrieve expenses.")


# ==================================================
# 6. ADD EXPENSE THROUGH API
# ==================================================

@app.route("/api/expenses", methods=["POST"])
def create_expense():

    try:
        data = get_json_body()

        amount = validate_amount(data.get("amount"))

        category = data.get("category")

        if not category or not str(category).strip():
            return error_response(
                "Expense category is required.",
                400
            )

        description = data.get("description", "")

        if not isinstance(description, str):
            return error_response(
                "Description must be text.",
                400
            )

        expense = add_expense(
            amount=amount,
            category=category,
            description=description
        )

        return jsonify({
            "success": True,
            "message": "Expense added successfully.",
            "expense": expense
        }), 201

    except ValueError as error:
        return error_response(str(error), 400)

    except Exception:
        app.logger.exception("Add expense API error")
        return error_response("Unable to save expense.")


# ==================================================
# 7. UPDATE EXPENSE
# ==================================================

@app.route("/api/expenses/<expense_id>", methods=["PUT"])
def edit_expense(expense_id):

    try:
        data = get_json_body()

        if not ObjectId.is_valid(expense_id):
            return error_response(
                "Invalid expense ID.",
                400
            )

        amount = None

        if "amount" in data:
            amount = validate_amount(data["amount"])

        category = data.get("category")
        description = data.get("description")

        if category is not None:
            if not isinstance(category, str) or not category.strip():
                return error_response(
                    "Category must be valid text.",
                    400
                )

        if description is not None:
            if not isinstance(description, str):
                return error_response(
                    "Description must be text.",
                    400
                )

        if not any(
            key in data
            for key in ("amount", "category", "description")
        ):
            return error_response(
                "Provide at least one field to update.",
                400
            )

        updated = update_expense(
            expense_id=expense_id,
            amount=amount,
            category=category,
            description=description
        )

        if not updated:
            return error_response(
                "Expense not found or no changes made.",
                404
            )

        return jsonify({
            "success": True,
            "message": "Expense updated successfully."
        })

    except ValueError as error:
        return error_response(str(error), 400)

    except Exception:
        app.logger.exception("Update expense error")
        return error_response("Unable to update expense.")


# ==================================================
# 8. DELETE EXPENSE
# ==================================================

@app.route("/api/expenses/<expense_id>", methods=["DELETE"])
def remove_expense(expense_id):

    try:
        if not ObjectId.is_valid(expense_id):
            return error_response(
                "Invalid expense ID.",
                400
            )

        deleted = delete_expense(expense_id)

        if not deleted:
            return error_response(
                "Expense not found.",
                404
            )

        return jsonify({
            "success": True,
            "message": "Expense deleted successfully."
        })

    except Exception:
        app.logger.exception("Delete expense error")
        return error_response("Unable to delete expense.")


# ==================================================
# 9. CATEGORY-WISE ANALYTICS
# ==================================================

@app.route("/api/categories", methods=["GET"])
def categories():

    try:
        summary = get_category_summary()

        result = []

        for item in summary:

            category = item.get("category") or "Other"

            result.append({
                "category": category,
                "total": round(
                    float(item.get("total", 0)),
                    2
                ),
                "count": int(item.get("count", 0))
            })

        result.sort(
            key=lambda item: item["total"],
            reverse=True
        )

        return jsonify({
            "success": True,
            "categories": result
        })

    except Exception:
        app.logger.exception("Category analytics error")
        return error_response("Unable to load category analytics.")


# ==================================================
# 10. ADVANCED EXPENSE ANALYTICS
# ==================================================

@app.route("/api/analytics/highest", methods=["GET"])
def highest_expense():

    try:
        expense = get_highest_expense()

        return jsonify({
            "success": True,
            "expense": expense
        })

    except Exception:
        app.logger.exception("Highest expense error")
        return error_response("Unable to retrieve highest expense.")


@app.route("/api/analytics/average", methods=["GET"])
def average_expense():

    try:
        average = get_average_expense()

        return jsonify({
            "success": True,
            "average_expense": round(float(average), 2),
            "currency": "INR"
        })

    except Exception:
        app.logger.exception("Average expense error")
        return error_response("Unable to calculate average expense.")


# ==================================================
# 11. SPENDING TRENDS
# ==================================================

@app.route("/api/analytics/trends", methods=["GET"])
def spending_trends():

    try:
        period = request.args.get(
            "period",
            default="daily"
        ).lower()

        if period not in ("daily", "monthly"):
            return error_response(
                "Period must be daily or monthly.",
                400
            )

        expenses = get_all_expenses(limit=None)

        trends = defaultdict(float)

        for expense in expenses:

            expense_date = str(expense.get("date", ""))

            if len(expense_date) < 7:
                continue

            if period == "daily":
                key = expense_date[:10]
            else:
                key = expense_date[:7]

            trends[key] += float(expense.get("amount", 0))

        result = [
            {
                "period": key,
                "total": round(value, 2)
            }
            for key, value in sorted(trends.items())
        ]

        return jsonify({
            "success": True,
            "period": period,
            "trends": result
        })

    except Exception:
        app.logger.exception("Spending trends error")
        return error_response("Unable to calculate spending trends.")


# ==================================================
# 12. BUDGET INFORMATION
# ==================================================

@app.route("/api/budgets", methods=["GET"])
def budgets():

    try:
        category = request.args.get("category")

        if category:
            result = get_budget_status(category=category)
        else:
            result = get_budget_status()

        return jsonify({
            "success": True,
            "budgets": result,
            "count": len(result)
        })

    except Exception:
        app.logger.exception("Budget retrieval error")
        return error_response("Unable to retrieve budgets.")


# ==================================================
# 13. RASA CHATBOT INTEGRATION
# ==================================================

@app.route("/api/chat", methods=["POST"])
def chat():

    try:
        data = get_json_body()

        message = data.get("message")

        sender_id = data.get(
            "sender",
            "spendwise_web_user"
        )

        if not isinstance(message, str):
            return error_response(
                "Message must be text.",
                400
            )

        message = message.strip()

        if not message:
            return error_response(
                "Please enter a message.",
                400
            )

        if not isinstance(sender_id, str) or not sender_id.strip():
            return error_response(
                "Invalid sender ID.",
                400
            )

        payload = {
            "sender": sender_id.strip(),
            "message": message
        }

        encoded_data = json.dumps(payload).encode("utf-8")

        rasa_request = Request(
            RASA_URL,
            data=encoded_data,
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urlopen(rasa_request, timeout=60) as response:

            rasa_response = json.loads(
                response.read().decode("utf-8")
            )

        messages = []

        if isinstance(rasa_response, list):

            for item in rasa_response:
                if isinstance(item, dict) and item.get("text"):
                    messages.append(item["text"])

        return jsonify({
            "success": True,
            "sender": sender_id.strip(),
            "responses": messages,
            "message_count": len(messages)
        })

    except ValueError as error:
        return error_response(str(error), 400)

    except HTTPError as error:

        app.logger.error(
            "Rasa HTTP error: %s",
            error.code
        )

        return jsonify({
            "success": False,
            "message": "Rasa server returned an error.",
            "status": error.code
        }), 502

    except (URLError, TimeoutError):
        app.logger.exception("Rasa connection error")

        return jsonify({
            "success": False,
            "message": "Cannot connect to Rasa. Check whether port 5005 is running."
        }), 503

    except Exception:
        app.logger.exception("Chat API error")
        return error_response("Chat request failed.")


# ==================================================
# 14. APPLICATION HEALTH MONITORING
# ==================================================

@app.route("/api/health", methods=["GET"])
def health():

    mongodb_status = "connected"
    rasa_status = "connected"

    # Test MongoDB.
    try:
        get_total_expenses()
    except Exception:
        mongodb_status = "disconnected"
        app.logger.exception("MongoDB health check failed")

    # Test Rasa.
    try:
        rasa_request = Request(
            RASA_STATUS_URL,
            headers={"Accept": "application/json"}
        )

        with urlopen(rasa_request, timeout=5) as response:
            if response.status != 200:
                rasa_status = "disconnected"

    except Exception:
        rasa_status = "disconnected"
        app.logger.exception("Rasa health check failed")

    overall_status = (
        "healthy"
        if mongodb_status == "connected"
        and rasa_status == "connected"
        else "degraded"
    )

    return jsonify({
        "success": True,
        "application": "SpendWise",
        "status": overall_status,
        "services": {
            "flask": "running",
            "mongodb": mongodb_status,
            "rasa": rasa_status
        }
    })


# ==================================================
# 15. START FLASK SERVER
# ==================================================

if __name__ == "__main__":

    print("=" * 50)
    print("           SPENDWISE BACKEND SERVER")
    print("=" * 50)

    print("Flask URL:", "http://localhost:5000")
    print("Rasa URL:", RASA_URL)
    print("MongoDB database configured through .env")

    # Verify MongoDB before starting Flask.
    try:
        connect_database()
        print("MongoDB startup check: SUCCESS")

    except Exception:
        print("MongoDB startup check: FAILED")
        print("Check your .env and MongoDB Atlas Network Access.")
        raise

    print("=" * 50)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
