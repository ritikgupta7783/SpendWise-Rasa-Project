
import os
from datetime import date
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import json

from flask import Flask, request, jsonify
from flask_cors import CORS

from database.db import (
    get_all_expenses,
    get_total_expenses,
    get_category_summary,
    get_all_budgets
)


# --------------------------------------------------
# 1. FLASK APPLICATION CONFIGURATION
# --------------------------------------------------

app = Flask(__name__)

CORS(app)

RASA_URL = os.getenv(
    "RASA_URL",
    "http://localhost:5005/webhooks/rest/webhook"
)


# --------------------------------------------------
# 2. HOME ROUTE
# --------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "application": "SpendWise",
        "message": "SpendWise API is running!",
        "version": "1.0"
    })


# --------------------------------------------------
# 3. DASHBOARD STATISTICS
# --------------------------------------------------

@app.route("/api/dashboard", methods=["GET"])
def dashboard():

    try:
        expenses = get_all_expenses(limit=10000)
        total = get_total_expenses()

        today = date.today()
        current_month = today.strftime("%Y-%m")

        monthly_expenses = [
            expense for expense in expenses
            if str(expense.get("date", "")).startswith(current_month)
        ]

        monthly_total = sum(
            float(expense.get("amount", 0))
            for expense in monthly_expenses
        )

        return jsonify({
            "success": True,
            "total_expenses": total,
            "monthly_expenses": round(monthly_total, 2),
            "total_transactions": len(expenses),
            "currency": "INR"
        })

    except Exception as error:
        app.logger.exception("Dashboard error")

        return jsonify({
            "success": False,
            "message": "Unable to load dashboard",
            "error": str(error)
        }), 500


# --------------------------------------------------
# 4. GET ALL EXPENSES
# --------------------------------------------------

@app.route("/api/expenses", methods=["GET"])
def expenses():

    try:
        limit = request.args.get("limit", default=100, type=int)
        limit = max(1, min(limit, 10000))

        records = get_all_expenses(limit=limit)

        return jsonify({
            "success": True,
            "count": len(records),
            "expenses": records
        })

    except Exception as error:
        app.logger.exception("Expense retrieval error")

        return jsonify({
            "success": False,
            "message": "Unable to retrieve expenses",
            "error": str(error)
        }), 500


# --------------------------------------------------
# 5. CATEGORY-WISE ANALYTICS
# --------------------------------------------------

@app.route("/api/categories", methods=["GET"])
def categories():

    try:
        summary = get_category_summary()

        result = []

        for item in summary:
            result.append({
                "category": item.get("_id"),
                "total": float(item.get("total", 0)),
                "count": int(item.get("count", 0))
            })

        return jsonify({
            "success": True,
            "categories": result
        })

    except Exception as error:
        app.logger.exception("Category analytics error")

        return jsonify({
            "success": False,
            "message": "Unable to load category analytics",
            "error": str(error)
        }), 500


# --------------------------------------------------
# 6. BUDGET INFORMATION
# --------------------------------------------------

@app.route("/api/budgets", methods=["GET"])
def budgets():

    try:
        budget_records = get_all_budgets()

        expenses = get_all_expenses(limit=10000)

        current_month = date.today().strftime("%Y-%m")

        result = []

        for budget in budget_records:

            category = budget.get("category", "")

            monthly_spent = sum(
                float(expense.get("amount", 0))
                for expense in expenses
                if expense.get("category", "").lower()
                == category.lower()
                and str(expense.get("date", "")).startswith(current_month)
            )

            monthly_limit = float(
                budget.get("monthly_limit", 0)
            )

            result.append({
                "category": category,
                "monthly_limit": monthly_limit,
                "spent": round(monthly_spent, 2),
                "remaining": round(
                    monthly_limit - monthly_spent, 2
                ),
                "percentage_used": round(
                    (monthly_spent / monthly_limit) * 100, 2
                ) if monthly_limit > 0 else 0
            })

        return jsonify({
            "success": True,
            "budgets": result
        })

    except Exception as error:
        app.logger.exception("Budget retrieval error")

        return jsonify({
            "success": False,
            "message": "Unable to retrieve budgets",
            "error": str(error)
        }), 500


# --------------------------------------------------
# 7. RASA CHATBOT API
# --------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def chat():

    try:
        data = request.get_json(silent=True) or {}

        message = data.get("message", "").strip()

        sender_id = data.get("sender", "spendwise_web_user")

        if not message:
            return jsonify({
                "success": False,
                "message": "Please enter a message."
            }), 400

        payload = {
            "sender": sender_id,
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

        for item in rasa_response:
            if item.get("text"):
                messages.append(item["text"])

        return jsonify({
            "success": True,
            "sender": sender_id,
            "responses": messages
        })

    except HTTPError as error:
        return jsonify({
            "success": False,
            "message": "Rasa server returned an error.",
            "status": error.code
        }), 502

    except (URLError, TimeoutError):
        return jsonify({
            "success": False,
            "message": "Cannot connect to Rasa. Make sure the Rasa server is running on port 5005."
        }), 503

    except Exception as error:
        app.logger.exception("Chat error")

        return jsonify({
            "success": False,
            "message": "Chat request failed.",
            "error": str(error)
        }), 500


# --------------------------------------------------
# 8. HEALTH CHECK
# --------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "success": True,
        "flask": "running",
        "rasa_url": RASA_URL,
        "application": "SpendWise"
    })


# --------------------------------------------------
# 9. START FLASK SERVER
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 45)
    print("       SPENDWISE BACKEND SERVER")
    print("=" * 45)

    print("Flask server: http://localhost:5000")
    print("Rasa server:", RASA_URL)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
