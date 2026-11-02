
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from database.db import (
    add_expense,
    get_all_expenses,
    get_total_expenses,
    get_category_summary,
    set_budget,
    get_all_budgets
)


class ActionAddExpense(Action):

    def name(self) -> Text:
        return "action_add_expense"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        amount = tracker.get_slot("amount")
        category = tracker.get_slot("category")
        description = tracker.get_slot("description") or ""

        if amount is None or category is None:
            dispatcher.utter_message(
                text="Please provide both the expense amount and category."
            )
            return []

        expense_id = add_expense(
            amount=amount,
            category=category,
            description=description
        )

        if expense_id:
            dispatcher.utter_message(
                text=f"Successfully saved ₹{amount} under {category}!"
            )
        else:
            dispatcher.utter_message(
                text="Sorry, I couldn't save your expense. Please try again."
            )

        return [
            SlotSet("amount", None),
            SlotSet("category", None),
            SlotSet("description", None)
        ]


class ActionCheckTotal(Action):

    def name(self) -> Text:
        return "action_check_total"

    def run(self, dispatcher, tracker, domain):

        total = get_total_expenses()

        dispatcher.utter_message(
            text=f"Your total recorded spending is ₹{total:.2f}."
        )

        return []


class ActionCategorySummary(Action):

    def name(self) -> Text:
        return "action_category_summary"

    def run(self, dispatcher, tracker, domain):

        summary = get_category_summary()

        if not summary:
            dispatcher.utter_message(
                text="You haven't recorded any expenses yet."
            )
            return []

        message = "Your category-wise spending:\n"

        for item in summary:
            message += (
                f"\n{item['_id']}: ₹{item['total']:.2f} "
                f"({item['count']} expenses)"
            )

        dispatcher.utter_message(text=message)

        return []


class ActionShowHistory(Action):

    def name(self) -> Text:
        return "action_show_history"

    def run(self, dispatcher, tracker, domain):

        expenses = get_all_expenses(limit=10)

        if not expenses:
            dispatcher.utter_message(
                text="No expenses recorded yet."
            )
            return []

        message = "Your recent expenses:\n"

        for expense in expenses:
            message += (
                f"\n₹{expense['amount']:.2f} - "
                f"{expense['category']} - "
                f"{expense['description']} - "
                f"{expense['date']}"
            )

        dispatcher.utter_message(text=message)

        return []


class ActionDeleteExpense(Action):

    def name(self) -> Text:
        return "action_delete_expense"

    def run(self, dispatcher, tracker, domain):

        dispatcher.utter_message(
            text="Expense deletion will be available once you select a specific transaction."
        )

        return []


class ActionSetBudget(Action):

    def name(self) -> Text:
        return "action_set_budget"

    def run(self, dispatcher, tracker, domain):

        amount = tracker.get_slot("amount")
        category = tracker.get_slot("category")

        if amount is None or category is None:
            dispatcher.utter_message(
                text="Please provide both a budget amount and category."
            )
            return []

        success = set_budget(category, amount)

        if success:
            dispatcher.utter_message(
                text=f"Your monthly {category} budget is set to ₹{amount}."
            )
        else:
            dispatcher.utter_message(
                text="Sorry, I couldn't save your budget."
            )

        return [
            SlotSet("amount", None),
            SlotSet("category", None)
        ]


class ActionCheckBudget(Action):

    def name(self) -> Text:
        return "action_check_budget"

    def run(self, dispatcher, tracker, domain):

        budgets = get_all_budgets()

        if not budgets:
            dispatcher.utter_message(
                text="You haven't configured any budgets yet."
            )
            return []

        message = "Your budget overview:\n"

        for budget in budgets:
            message += (
                f"\n{budget['category']}: "
                f"₹{budget['monthly_limit']:.2f} monthly limit"
            )

        dispatcher.utter_message(text=message)

        return []
