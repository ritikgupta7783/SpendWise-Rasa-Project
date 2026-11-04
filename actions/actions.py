
from datetime import date, timedelta

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from database.db import (
    add_expense,
    get_all_expenses,
    get_total_expenses,
    get_category_total,
    get_category_summary,
    get_total_by_date_range,
    get_expenses_filtered,
    get_highest_expense,
    get_average_expense,
    delete_expense,
    set_budget,
    get_all_budgets,
    get_budget_status,
    normalize_category,
    _date_range,
)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def get_value(tracker, entity_name, slot_name=None):
    """
    Get the latest entity value from the user's message.
    If it is not present, use the stored slot value.
    """

    entities = tracker.latest_message.get("entities", [])

    for entity in reversed(entities):
        if entity.get("entity") == entity_name:
            return entity.get("value")

    if slot_name:
        return tracker.get_slot(slot_name)

    return None


def format_currency(amount):
    """Format an amount in Indian Rupees."""

    return f"₹{float(amount):,.2f}"


def format_expense(expense):
    """Format one expense for chatbot responses."""

    return (
        f"{format_currency(expense.get('amount', 0))} "
        f"on {expense.get('category', 'Other')} "
        f"({expense.get('description') or 'No description'}) "
        f"on {expense.get('date', 'Unknown date')}"
    )


def get_period_dates(period):
    """Convert a supported date period into a date range."""

    start, end = _date_range(period)
    return start, end


# --------------------------------------------------
# 1. ADD EXPENSE
# --------------------------------------------------

class ActionAddExpense(Action):

    def name(self):
        return "action_add_expense"

    def run(self, dispatcher, tracker, domain):

        amount = get_value(tracker, "amount", "amount")
        category = get_value(tracker, "category", "category")
        description = tracker.get_slot("description") or ""

        if amount is None:
            dispatcher.utter_message(
                text="How much did you spend? Please provide the amount."
            )
            return []

        if category is None:
            dispatcher.utter_message(
                text=f"You spent {format_currency(amount)}. "
                     "Which category should I save it under?"
            )

            return [
                SlotSet("amount", float(amount)),
                SlotSet("category", None)
            ]

        try:
            expense = add_expense(
                amount=float(amount),
                category=category,
                description=description
            )

            dispatcher.utter_message(
                text=(
                    f"Expense added successfully! "
                    f"{format_currency(expense['amount'])} "
                    f"spent on {expense['category']}."
                )
            )

            return [
                SlotSet("amount", None),
                SlotSet("category", None),
                SlotSet("description", None)
            ]

        except Exception as error:
            print(f"Add expense error: {error}")

            dispatcher.utter_message(
                text="Sorry, I could not save your expense. "
                     "Please check the database connection."
            )

            return []


# --------------------------------------------------
# 2. COMPLETE EXPENSE
# --------------------------------------------------

class ActionCompleteExpense(Action):

    def name(self):
        return "action_complete_expense"

    def run(self, dispatcher, tracker, domain):

        amount = tracker.get_slot("amount")
        category = get_value(tracker, "category", "category")
        description = tracker.get_slot("description") or ""

        if amount is None:
            dispatcher.utter_message(
                text="Please provide the expense amount first."
            )
            return []

        if category is None:
            dispatcher.utter_message(
                text="Please tell me the expense category."
            )
            return []

        try:
            expense = add_expense(
                amount=float(amount),
                category=category,
                description=description
            )

            dispatcher.utter_message(
                text=(
                    f"Done! I saved {format_currency(expense['amount'])} "
                    f"under {expense['category']}."
                )
            )

            return [
                SlotSet("amount", None),
                SlotSet("category", None),
                SlotSet("description", None)
            ]

        except Exception as error:
            print(f"Complete expense error: {error}")

            dispatcher.utter_message(
                text="I could not save that expense. Please try again."
            )

            return []


# --------------------------------------------------
# 3. CHECK TOTAL EXPENSES
# --------------------------------------------------

class ActionCheckTotal(Action):

    def name(self):
        return "action_check_total"

    def run(self, dispatcher, tracker, domain):

        try:
            total = get_total_expenses()

            dispatcher.utter_message(
                text=f"Your total recorded spending is {format_currency(total)}."
            )

        except Exception as error:
            print(f"Total expense error: {error}")

            dispatcher.utter_message(
                text="I could not calculate your total spending."
            )

        return []


# --------------------------------------------------
# 4. CHECK CATEGORY TOTAL
# --------------------------------------------------

class ActionCheckCategoryTotal(Action):

    def name(self):
        return "action_check_category_total"

    def run(self, dispatcher, tracker, domain):

        category = get_value(tracker, "category", "category")

        if not category:
            dispatcher.utter_message(
                text="Which category would you like me to check?"
            )
            return []

        try:
            normalized = normalize_category(category)
            total = get_category_total(normalized)

            dispatcher.utter_message(
                text=(
                    f"You have spent {format_currency(total)} "
                    f"on {normalized}."
                )
            )

            return [SlotSet("category", normalized)]

        except Exception as error:
            print(f"Category total error: {error}")

            dispatcher.utter_message(
                text="I could not calculate spending for that category."
            )

            return []


# --------------------------------------------------
# 5. CATEGORY-WISE SUMMARY
# --------------------------------------------------

class ActionCategorySummary(Action):

    def name(self):
        return "action_category_summary"

    def run(self, dispatcher, tracker, domain):

        try:
            summary = get_category_summary()

            if not summary:
                dispatcher.utter_message(
                    text="You have not recorded any expenses yet."
                )
                return []

            message = "Here is your category-wise spending:\n\n"

            for item in summary:
                message += (
                    f"• {item['category']}: "
                    f"{format_currency(item['total'])} "
                    f"({item['count']} transactions)\n"
                )

            dispatcher.utter_message(text=message)

        except Exception as error:
            print(f"Category summary error: {error}")

            dispatcher.utter_message(
                text="I could not generate your category summary."
            )

        return []


# --------------------------------------------------
# 6. SHOW EXPENSE HISTORY
# --------------------------------------------------

class ActionShowHistory(Action):

    def name(self):
        return "action_show_history"

    def run(self, dispatcher, tracker, domain):

        try:
            expenses = get_all_expenses(limit=10)

            if not expenses:
                dispatcher.utter_message(
                    text="You have not recorded any expenses yet."
                )
                return []

            message = "Here are your 10 most recent expenses:\n\n"

            for index, expense in enumerate(expenses, start=1):
                message += (
                    f"{index}. {format_expense(expense)}\n"
                )

            dispatcher.utter_message(text=message)

        except Exception as error:
            print(f"History error: {error}")

            dispatcher.utter_message(
                text="I could not retrieve your expense history."
            )

        return []


# --------------------------------------------------
# 7. CHECK SPENDING BY DATE
# --------------------------------------------------

class ActionCheckDateTotal(Action):

    def name(self):
        return "action_check_date_total"

    def run(self, dispatcher, tracker, domain):

        period = get_value(tracker, "date_period", "date_period")

        if not period:
            dispatcher.utter_message(
                text="Please specify a period, such as today, "
                     "yesterday, this month, or last month."
            )
            return []

        try:
            start_date, end_date = get_period_dates(period)

            total = get_total_by_date_range(
                start_date,
                end_date
            )

            dispatcher.utter_message(
                text=(
                    f"Your spending for {period} is "
                    f"{format_currency(total)}."
                )
            )

        except ValueError:
            dispatcher.utter_message(
                text="I currently support today, yesterday, this week, "
                     "last week, this month, last month, this year, "
                     "and last year."
            )

        except Exception as error:
            print(f"Date total error: {error}")

            dispatcher.utter_message(
                text="I could not calculate spending for that period."
            )

        return []


# --------------------------------------------------
# 8. FILTERED EXPENSE HISTORY
# --------------------------------------------------

class ActionFilteredHistory(Action):

    def name(self):
        return "action_filtered_history"

    def run(self, dispatcher, tracker, domain):

        category = get_value(tracker, "category", "category")
        period = get_value(tracker, "date_period", "date_period")

        try:
            start_date = None
            end_date = None

            if period:
                start_date, end_date = get_period_dates(period)

            expenses = get_expenses_filtered(
                category=category,
                start_date=start_date,
                end_date=end_date,
                limit=20
            )

            if not expenses:
                dispatcher.utter_message(
                    text="I could not find any expenses matching those filters."
                )
                return []

            message = "Here are the matching expenses:\n\n"

            for index, expense in enumerate(expenses, start=1):
                message += (
                    f"{index}. {format_expense(expense)}\n"
                )

            dispatcher.utter_message(text=message)

        except ValueError:
            dispatcher.utter_message(
                text="I could not understand that date period."
            )

        except Exception as error:
            print(f"Filtered history error: {error}")

            dispatcher.utter_message(
                text="I could not retrieve the filtered expense history."
            )

        return []


# --------------------------------------------------
# 9. HIGHEST EXPENSE
# --------------------------------------------------

class ActionHighestExpense(Action):

    def name(self):
        return "action_highest_expense"

    def run(self, dispatcher, tracker, domain):

        try:
            expense = get_highest_expense()

            if not expense:
                dispatcher.utter_message(
                    text="You have not recorded any expenses yet."
                )
                return []

            dispatcher.utter_message(
                text=(
                    "Your highest recorded expense is "
                    f"{format_expense(expense)}."
                )
            )

        except Exception as error:
            print(f"Highest expense error: {error}")

            dispatcher.utter_message(
                text="I could not find your highest expense."
            )

        return []


# --------------------------------------------------
# 10. AVERAGE EXPENSE
# --------------------------------------------------

class ActionAverageExpense(Action):

    def name(self):
        return "action_average_expense"

    def run(self, dispatcher, tracker, domain):

        try:
            average = get_average_expense()

            dispatcher.utter_message(
                text=(
                    f"Your average expense per transaction is "
                    f"{format_currency(average)}."
                )
            )

        except Exception as error:
            print(f"Average expense error: {error}")

            dispatcher.utter_message(
                text="I could not calculate your average expense."
            )

        return []


# --------------------------------------------------
# 11. FOLLOW-UP CATEGORY QUESTION
# --------------------------------------------------

class ActionFollowupCategory(Action):

    def name(self):
        return "action_followup_category"

    def run(self, dispatcher, tracker, domain):

        category = get_value(tracker, "category", "category")

        if not category:
            dispatcher.utter_message(
                text="Which category would you like me to check?"
            )
            return []

        try:
            normalized = normalize_category(category)
            total = get_category_total(normalized)

            dispatcher.utter_message(
                text=(
                    f"You have spent {format_currency(total)} "
                    f"on {normalized}."
                )
            )

            return [SlotSet("category", normalized)]

        except Exception as error:
            print(f"Follow-up category error: {error}")

            dispatcher.utter_message(
                text="I could not retrieve that category's spending."
            )

            return []


# --------------------------------------------------
# 12. SET BUDGET
# --------------------------------------------------

class ActionSetBudget(Action):

    def name(self):
        return "action_set_budget"

    def run(self, dispatcher, tracker, domain):

        category = get_value(tracker, "category", "category")
        amount = get_value(tracker, "amount", "amount")

        if not category:
            dispatcher.utter_message(
                text="Which category would you like to set a budget for?"
            )
            return []

        if amount is None:
            dispatcher.utter_message(
                text="What budget amount would you like to set?"
            )
            return []

        try:
            budget = set_budget(category, float(amount))

            dispatcher.utter_message(
                text=(
                    f"Your monthly budget for {budget['category']} "
                    f"has been set to {format_currency(budget['amount'])}."
                )
            )

            return [
                SlotSet("amount", None),
                SlotSet("category", None)
            ]

        except Exception as error:
            print(f"Set budget error: {error}")

            dispatcher.utter_message(
                text="I could not save your budget. Please try again."
            )

            return []


# --------------------------------------------------
# 13. CHECK BUDGET
# --------------------------------------------------

class ActionCheckBudget(Action):

    def name(self):
        return "action_check_budget"

    def run(self, dispatcher, tracker, domain):

        category = get_value(tracker, "category", "category")

        try:
            statuses = get_budget_status(category)

            if not statuses:
                if category:
                    message = (
                        f"You have not set a budget for "
                        f"{normalize_category(category)} yet."
                    )
                else:
                    message = "You have not configured any budgets yet."

                dispatcher.utter_message(text=message)
                return []

            message = "Here is your monthly budget status:\n\n"

            for item in statuses:
                message += (
                    f"• {item['category']}\n"
                    f"  Budget: {format_currency(item['budget'])}\n"
                    f"  Spent: {format_currency(item['spent'])}\n"
                    f"  Remaining: {format_currency(item['remaining'])}\n"
                    f"  Used: {item['percentage_used']:.1f}%\n\n"
                )

            dispatcher.utter_message(text=message)

        except Exception as error:
            print(f"Check budget error: {error}")

            dispatcher.utter_message(
                text="I could not retrieve your budget status."
            )

        return []


# --------------------------------------------------
# 14. DELETE EXPENSE
# --------------------------------------------------

class ActionDeleteExpense(Action):

    def name(self):
        return "action_delete_expense"

    def run(self, dispatcher, tracker, domain):

        try:
            expenses = get_all_expenses(limit=5)

            if not expenses:
                dispatcher.utter_message(
                    text="There are no expenses available to delete."
                )
                return []

            message = (
                "I found your five most recent expenses:\n\n"
            )

            for index, expense in enumerate(expenses, start=1):
                message += (
                    f"{index}. {format_expense(expense)}\n"
                    f"   ID: {expense['_id']}\n"
                )

            message += (
                "\nFor safety, no expense has been deleted. "
                "Use the expense ID with the dashboard's delete option "
                "to remove a specific transaction."
            )

            dispatcher.utter_message(text=message)

        except Exception as error:
            print(f"Delete expense error: {error}")

            dispatcher.utter_message(
                text="I could not retrieve expenses for deletion."
            )

        return []
