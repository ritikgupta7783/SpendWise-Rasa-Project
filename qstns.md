# SPENDWISE
# Complete Project Study Guide & Interview Preparation Handbook

**Understanding Rasa Framework, Conversational AI, Python Backend, MongoDB Atlas and Full-Stack Integration**

**Project Developer:** Ritik Kumar Gupta  
**Scholar ID:** 2312065  
**Branch:** Computer Science and Engineering  
**Institute:** National Institute of Technology Silchar  
**Project:** SpendWise — Conversational Expense Tracker  
**Rasa Version:** 3.6.21  
**Python Version:** 3.10.11  

**GitHub Repository:**  
https://github.com/ritikgupta7783/SpendWise-Rasa-Project

---

# PAGE 1 — PROJECT INTRODUCTION AND PROBLEM STATEMENT

## 1.1 What is SpendWise?

SpendWise is a web-based personal expense tracking application integrated with a conversational chatbot built using the Rasa Framework.

Its main purpose is to make expense tracking easier through natural language conversations.

Instead of manually filling out an expense form, users can simply type messages such as:

- I spent 400 on food.
- I paid 250 for transport.
- How much have I spent?
- Show my recent expenses.
- Show my category-wise spending.
- Set my food budget to 3000.
- Check my budget.

The chatbot understands the user's intention, extracts the relevant information, executes the appropriate Python action and communicates with MongoDB Atlas to store or retrieve financial information.

A web dashboard displays the stored information through financial summary cards, category-wise charts, transaction history and budget information.

## 1.2 What Problem Does It Solve?

Traditional expense trackers require users to manually enter details for every transaction.

For example, recording a lunch expense may require:

| Field | Value |
|---|---|
| Amount | ₹400 |
| Category | Food |
| Description | Lunch |
| Date | 03 November 2026 |

The user must navigate through multiple fields.

SpendWise introduces a conversational alternative.

The user simply types:

"I spent 400 on food."

The chatbot extracts:

```text
Amount   = 400
Category = Food
```

It then saves the transaction.

The objective is to demonstrate how conversational AI can connect natural language understanding with a real-world software application.

## 1.3 Main Features

| Feature | Description |
|---|---|
| Expense recording | Add expenses through chatbot messages |
| Total spending | Calculate total recorded expenses |
| Category summary | Group expenses by category |
| Expense history | Retrieve recent transactions |
| Budget management | Save monthly category limits |
| Budget overview | Retrieve configured budget limits |
| Web dashboard | Display financial information |
| AI-style chat interface | Communicate with the Rasa assistant |

## 1.4 Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10.11 | Backend programming |
| Rasa 3.6.21 | Conversational AI |
| Rasa SDK 3.6.2 | Custom actions |
| MongoDB Atlas | Cloud database |
| PyMongo | Database connectivity |
| Flask 3.1.3 | Backend APIs |
| Flask-CORS 6.0.5 | Cross-origin communication |
| HTML5 | Frontend structure |
| CSS3 | Dashboard design |
| JavaScript | Frontend functionality |
| Chart.js | Financial visualization |

## 1.5 Why Did I Choose Rasa?

The assignment required the implementation of a chatbot using the Rasa Framework.

Rasa was selected because it provides:

1. Natural Language Understanding.
2. Intent classification.
3. Entity extraction.
4. Dialogue management.
5. Conversation tracking through slots and trackers.
6. Stories and rules.
7. Custom Python actions.
8. Integration with external databases and APIs.

An important design decision was to use classic Rasa Open Source 3.6.21.

The project demonstrates traditional Rasa concepts rather than depending on a generative AI API.

---

# PAGE 2 — UNDERSTANDING RASA FROM ZERO

## 2.1 What is Rasa?

Rasa is an open-source framework for developing conversational AI assistants.

It allows developers to build chatbots that can understand user messages, maintain conversation context, choose actions and communicate with external systems.

Think of Rasa as the brain of SpendWise.

When a user sends a message, Rasa performs several tasks:

1. Receives the message.
2. Processes the text.
3. Predicts the user's intention.
4. Extracts important information.
5. Updates conversation state.
6. Decides the next action.
7. Executes a response or custom action.

Rasa has two major conceptual parts:

### A. Natural Language Understanding (NLU)

NLU tries to understand what the user means.

Example:

User:

"I spent 500 on shopping."

NLU identifies:

```text
Intent: add_expense

Entities:
amount   = 500
category = shopping
```

### B. Dialogue Management

Dialogue management decides what the assistant should do next.

For example:

```text
Intent detected: add_expense

Next action:
action_add_expense
```

The custom action then saves the transaction.

## 2.2 NLU vs Dialogue Management

| NLU | Dialogue Management |
|---|---|
| Understands the message | Decides the next step |
| Predicts intents | Selects actions |
| Extracts entities | Uses conversation context |
| Processes language | Controls the conversation |

A useful interview explanation:

"NLU determines what the user wants and extracts relevant information. Dialogue management decides how the chatbot should respond or which action should execute."

## 2.3 What Happens Internally?

Consider:

"I spent 400 on food."

```text
              USER MESSAGE
                    |
                    v
                RASA NLU
                    |
          +---------+---------+
          |                   |
          v                   v
       INTENT               ENTITIES
    add_expense          amount = 400
                         category = food
          |                   |
          +---------+---------+
                    |
                    v
             DIALOGUE MANAGER
                    |
                    v
             CUSTOM ACTION
                    |
                    v
               PYTHON CODE
                    |
                    v
              MONGODB ATLAS
                    |
                    v
              BOT RESPONSE
```

This entire process demonstrates the connection between language understanding and application logic.

## 2.4 Important Rasa Terminology

| Concept | Simple Meaning |
|---|---|
| Intent | What the user wants |
| Entity | Important information in a message |
| Slot | Stored conversation information |
| Domain | Defines chatbot capabilities |
| Response | Predefined chatbot message |
| Story | Example conversation path |
| Rule | Fixed conversational behavior |
| Action | Operation executed by Rasa |
| Tracker | Stores conversation history and state |
| Policy | Determines the next action |
| Channel | Method through which users communicate |

Remember these concepts because they are frequently asked in Rasa interviews and academic demonstrations.

---

# PAGE 3 — INTENTS AND ENTITIES

## 3.1 What is an Intent?

An intent represents the purpose behind a user's message.

Different sentences can express the same intention.

For example:

- Hi.
- Hello.
- Hey there.
- Good morning.

All can represent:

`greet`

Similarly:

- How much have I spent?
- Show my total expenses.
- What is my total spending?
- Calculate my expenditure.

All can represent:

`check_total`

Rasa learns these patterns from labeled training examples.

## 3.2 Intents Implemented in SpendWise

Your `data/nlu.yml` contains ten primary user-facing intents.

| Intent | Purpose | Example |
|---|---|---|
| greet | Greeting | Hi |
| goodbye | Ending conversation | Bye |
| add_expense | Adding expense | I spent 400 on food |
| check_total | Calculating total | How much have I spent? |
| category_summary | Category breakdown | Show expenses by category |
| show_history | Expense history | Show my recent expenses |
| delete_expense | Deletion request | Delete my last expense |
| set_budget | Saving budget | Set food budget to 3000 |
| check_budget | Reviewing budget | Show my budget |
| bot_help | Help | What can you do? |

The domain also declares `nlu_fallback`.

It is used when Rasa cannot confidently understand the user message.

## 3.3 How Intent Training Works

The training data is stored in:

`data/nlu.yml`

Example:

```yaml
version: "3.1"

nlu:

- intent: greet
  examples: |
    - hi
    - hello
    - hey
    - good morning

- intent: add_expense
  examples: |
    - I spent [200](amount) on [food](category)
    - Add [500](amount) for [shopping](category)
    - I paid [150](amount) for [transport](category)

- intent: check_total
  examples: |
    - How much have I spent?
    - Show my total expenses
    - What is my total spending?
```

The annotated values teach Rasa that the messages contain entities.

## 3.4 What are Entities?

An entity is a meaningful piece of information extracted from a user message.

For SpendWise:

- `amount`
- `category`

Example:

Input:

"I spent 600 on travel."

Entity output:

```json
{
  "amount": 600,
  "category": "travel"
}
```

Intent:

```text
add_expense
```

## 3.5 Intent vs Entity

This is a common interview question.

Consider:

"I spent 500 on shopping."

The intent is `add_expense`.

The entities are:

- Amount: 500
- Category: shopping

The intent explains the user's objective.

Entities provide the values needed to complete that objective.

## 3.6 Entity Annotation

Rasa uses annotation syntax in training examples.

```yaml
- intent: add_expense
  examples: |
    - I spent [500](amount) on [shopping](category)
```

Here:

`[500](amount)` means that 500 is an amount entity.

`[shopping](category)` means that shopping is a category entity.

## 3.7 Why Are Entities Important?

Without entity extraction, the chatbot would know that the user wants to add an expense but would not know which amount or category to save.

Entity extraction converts natural language into structured information.

This is what allows Rasa to connect user messages to database operations.

---

# PAGE 4 — SLOTS, DOMAIN AND RESPONSES

## 4.1 What are Slots?

Slots are used to store information during a conversation.

Think of slots as temporary conversational memory.

SpendWise defines three slots:

1. amount
2. category
3. description

Example:

User:

"I spent 500 on food."

Rasa extracts:

```text
amount = 500
category = food
```

These values are made available through slots.

The custom action can retrieve them using the tracker.

Example:

```python
amount = tracker.get_slot("amount")
category = tracker.get_slot("category")
```

## 4.2 How Are Slots Configured?

Slots are defined in `domain.yml`.

Example:

```yaml
slots:

  amount:
    type: float
    influence_conversation: false
    mappings:
      - type: from_entity
        entity: amount

  category:
    type: text
    influence_conversation: false
    mappings:
      - type: from_entity
        entity: category

  description:
    type: text
    influence_conversation: false
    mappings:
      - type: custom
```

### Understanding the Configuration

`type: float`

Stores numerical values.

`type: text`

Stores text values.

`influence_conversation: false`

Means the slot value itself is not used as a direct feature for dialogue prediction.

`from_entity`

Automatically fills a slot from a matching extracted entity.

`custom`

The value is expected to be set through custom logic or another supported mechanism.

## 4.3 What is a Tracker?

The tracker maintains conversation state.

It records information such as:

- User messages.
- Predicted intents.
- Extracted entities.
- Slot values.
- Actions executed.
- Bot responses.

For example:

```python
amount = tracker.get_slot("amount")
```

The tracker lets a custom action access information from the conversation.

### Difference Between Tracker and Slot

A slot stores a particular piece of information.

A tracker stores the broader conversation history and state, including slot values.

## 4.4 What is Domain.yml?

The domain describes everything the assistant knows how to handle.

It declares:

- Intents.
- Entities.
- Slots.
- Responses.
- Custom actions.

Example:

```yaml
version: "3.1"

intents:
  - greet
  - add_expense
  - check_total

entities:
  - amount
  - category

actions:
  - action_add_expense
  - action_check_total
```

The domain is the central configuration describing the assistant's vocabulary and capabilities.

## 4.5 What are Responses?

Responses are predefined messages returned by the assistant.

Examples from SpendWise:

- `utter_greet`
- `utter_goodbye`
- `utter_help`
- `utter_ask_amount`
- `utter_ask_category`
- `utter_expense_added`
- `utter_fallback`

Example:

```yaml
responses:

  utter_greet:
    - text: "Hello! Welcome to SpendWise."

  utter_goodbye:
    - text: "Goodbye! Keep tracking your expenses."

  utter_fallback:
    - text: "Sorry, I didn't understand that."
```

### Response vs Custom Action

A response only returns a message.

A custom action can execute Python logic, query MongoDB, update records and return a result.

For example:

`utter_greet` sends a predefined greeting.

`action_add_expense` executes actual expense-saving logic.

This distinction is particularly important during interviews.

---

# PAGE 5 — STORIES, RULES AND DIALOGUE POLICIES

## 5.1 What are Stories?

Stories are examples of how conversations should proceed.

They teach the dialogue manager possible sequences of intents and actions.

SpendWise has ten story paths covering its major operations.

Example from `data/stories.yml`:

```yaml
stories:

- story: greet user
  steps:
    - intent: greet
    - action: utter_greet

- story: add a new expense
  steps:
    - intent: add_expense
    - action: action_add_expense

- story: check total spending
  steps:
    - intent: check_total
    - action: action_check_total
```

### How Does This Work?

User says:

"How much have I spent?"

NLU predicts:

`check_total`

The dialogue manager identifies the expected next action:

`action_check_total`

That action retrieves the total from MongoDB.

## 5.2 What are Rules?

Rules define specific behavior that should be followed consistently.

SpendWise has three rules:

1. Greeting.
2. Goodbye.
3. Help.

Example:

```yaml
rules:

- rule: Respond to greeting
  steps:
    - intent: greet
    - action: utter_greet

- rule: Show help
  steps:
    - intent: bot_help
    - action: utter_help
```

## 5.3 Stories vs Rules

| Stories | Rules |
|---|---|
| Represent example conversation flows | Specify fixed behavior |
| Used to train dialogue prediction | Enforce defined paths |
| Can represent multiple-step interactions | Commonly used for predictable responses |

A simple analogy:

A story teaches the assistant how a conversation might proceed.

A rule tells the assistant what it must do for a specified situation.

## 5.4 What are Dialogue Policies?

Dialogue policies determine the next action based on the conversation state.

SpendWise uses three policies.

### A. MemoizationPolicy

It remembers previously learned conversation paths.

If the current conversation matches a known story, the policy can reuse the learned action sequence.

Configuration:

```yaml
- name: MemoizationPolicy
  max_history: 5
```

### B. RulePolicy

It handles the rules defined in `data/rules.yml`.

For example:

`greet → utter_greet`

### C. TEDPolicy

TED stands for Transformer Embedding Dialogue.

It is a machine-learning-based dialogue policy that predicts the next action using conversation context.

SpendWise configuration:

```yaml
- name: TEDPolicy
  max_history: 5
  epochs: 100
  constrain_similarities: true
```

### What is Max History?

It controls how much recent conversation history is considered by the policy.

A value of five means it considers up to five preceding dialogue states in the configured history.

## 5.5 How Does Rasa Select an Action?

Rasa evaluates the current conversation state using its dialogue policies.

The policies contribute predictions, and the dialogue manager selects the next action according to the learned and configured behavior.

For example:

```text
User message
     |
     v
Intent prediction
     |
     v
Current tracker state
     |
     v
Dialogue policies
     |
     v
Next action
```

This is the basis of Rasa's dialogue management.

---

# PAGE 6 — NLU PIPELINE AND DIET CLASSIFIER

This is one of the most important technical sections for a Rasa interview.

## 6.1 What is an NLU Pipeline?

An NLU pipeline is a sequence of components that process user messages.

Each component performs a specific task.

The pipeline is configured in:

`config.yml`

SpendWise uses:

1. WhitespaceTokenizer
2. RegexFeaturizer
3. LexicalSyntacticFeaturizer
4. CountVectorsFeaturizer
5. Character-level CountVectorsFeaturizer
6. DIETClassifier
7. EntitySynonymMapper
8. FallbackClassifier

## 6.2 WhitespaceTokenizer

It separates text into tokens based on whitespace.

Example:

Input:

"I spent 500 on food"

Output:

```text
["I", "spent", "500", "on", "food"]
```

Tokenization is an important first step in text processing.

## 6.3 RegexFeaturizer

It uses regular-expression patterns to identify useful text patterns.

For example, a regex can help identify numbers or other structured text patterns when corresponding patterns are configured.

In SpendWise, it is included as part of the NLU pipeline.

Do not claim that a particular amount-extraction regex is configured unless it exists in your actual training data.

## 6.4 LexicalSyntacticFeaturizer

It extracts lexical and syntactic features from tokens.

These features can help the model understand the structure of user messages.

## 6.5 CountVectorsFeaturizer

It converts textual information into numerical feature vectors.

Machine-learning models require numerical representations rather than raw strings.

Example:

Words and their frequencies are represented as numerical features.

### Word-Based Features

A vectorizer represents word-level patterns.

### Character-Based Features

SpendWise also uses:

```yaml
- name: CountVectorsFeaturizer
  analyzer: char_wb
  min_ngram: 1
  max_ngram: 4
```

This generates character n-gram features within word boundaries.

Character n-grams can help represent spelling variations and partial word patterns.

## 6.6 What is DIETClassifier?

DIET stands for Dual Intent and Entity Transformer.

It is a Rasa component that performs:

1. Intent classification.
2. Entity extraction.

This means the same model can learn what the user wants and identify important information inside the message.

SpendWise uses:

```yaml
- name: DIETClassifier
  epochs: 100
  constrain_similarities: true
```

### Understanding Intent Classification

Suppose training data contains:

"I spent money on food."

"I purchased lunch."

"Record my food expense."

The model learns patterns associated with the `add_expense` intent.

When a new message arrives, the classifier predicts the most likely intent.

### Understanding Entity Extraction

The model also learns to recognize annotated entities.

For example:

"I spent 500 on shopping."

It identifies:

- amount = 500
- category = shopping

### What are Epochs?

An epoch is one complete pass through the training dataset during model training.

SpendWise uses 100 epochs in its configured DIETClassifier.

More epochs do not automatically guarantee better performance.

The correct configuration depends on the dataset and evaluation results.

## 6.7 EntitySynonymMapper

It maps configured synonyms to canonical entity values.

For example, if synonyms are configured:

```yaml
- synonym: Food
  examples: |
    - food
    - meals
    - dining
```

The mapper can normalize matching extracted values to:

`Food`

Important: The component is present in SpendWise, but only configured synonym groups are actually used.

## 6.8 FallbackClassifier

FallbackClassifier helps detect uncertain predictions.

SpendWise configuration:

```yaml
- name: FallbackClassifier
  threshold: 0.30
  ambiguity_threshold: 0.10
```

Threshold controls when an intent prediction is considered too uncertain.

Ambiguity threshold concerns how close the top intent predictions are.

A fallback mechanism helps reduce the chance of treating unclear messages as confidently understood.

---

# PAGE 7 — CUSTOM ACTIONS AND RASA SDK

## 7.1 What are Custom Actions?

Custom actions allow Rasa to execute external Python code.

They are especially useful when a chatbot needs to:

- Access databases.
- Call APIs.
- Perform calculations.
- Validate information.
- Execute application-specific business logic.

SpendWise uses custom actions to communicate with MongoDB through Python functions.

## 7.2 Why Rasa SDK?

Rasa SDK provides classes and interfaces for defining custom actions.

Important classes used in SpendWise:

```python
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
```

### Action

Base class for defining custom actions.

### Tracker

Provides access to conversation state, slots and message information.

### CollectingDispatcher

Used to send messages from a custom action to the user.

### SlotSet

Used to update or clear a slot.

## 7.3 Understanding the Action Structure

Every custom action implements a `name()` method and a `run()` method.

Example:

```python
class ActionCheckTotal(Action):

    def name(self):
        return "action_check_total"

    def run(self, dispatcher, tracker, domain):

        total = get_total_expenses()

        dispatcher.utter_message(
            text=f"Your total recorded spending is ₹{total:.2f}."
        )

        return []
```

### What Happens?

1. Rasa selects the custom action.
2. The action's `run()` method is called.
3. The database function retrieves the total.
4. The dispatcher sends the response.
5. The action returns events, if necessary.

## 7.4 Seven Registered Actions in SpendWise

### 1. action_add_expense

Purpose: Insert a new expense.

It reads:

```python
amount = tracker.get_slot("amount")
category = tracker.get_slot("category")
```

It checks whether both fields are available.

It then calls:

```python
add_expense(
    amount=amount,
    category=category,
    description=description
)
```

After successful processing, it returns a confirmation.

It also clears the used slots through SlotSet events.

### 2. action_check_total

Calls:

```python
get_total_expenses()
```

Retrieves the sum of all recorded expense amounts.

### 3. action_category_summary

Calls:

```python
get_category_summary()
```

Returns each category's total spending and transaction count.

### 4. action_show_history

Calls:

```python
get_all_expenses(limit=10)
```

Displays up to ten recent transactions.

### 5. action_delete_expense

Currently a placeholder.

It informs the user that deletion requires selecting a specific transaction.

Actual deletion through the chatbot is not implemented.

### 6. action_set_budget

Reads the amount and category slots and calls:

```python
set_budget(category, amount)
```

It stores the monthly category budget.

### 7. action_check_budget

Calls:

```python
get_all_budgets()
```

Displays configured monthly category limits.

The chatbot's current budget response lists limits; the dashboard separately calculates current-month usage.

## 7.5 How Is the Action Server Connected?

The custom action server is configured in:

`endpoints.yml`

```yaml
action_endpoint:
  url: "http://localhost:5055/webhook"
```

The Rasa server sends custom action requests to this endpoint.

The action server executes the requested Python action and returns events and responses.

This separation allows Rasa conversation processing and external Python logic to run as separate services.

---

# PAGE 8 — MONGODB ATLAS AND PYTHON DATABASE INTEGRATION

## 8.1 Why MongoDB?

MongoDB is a document-oriented NoSQL database.

It stores information in BSON documents, which are similar to JSON objects.

It is suitable for an application like SpendWise because expense transactions can be represented naturally as documents.

## 8.2 Why MongoDB Atlas?

MongoDB Atlas is MongoDB's managed cloud database service.

It removes the need to manage a database server manually on the local computer.

SpendWise uses Atlas to persist financial records.

## 8.3 Why PyMongo?

PyMongo is the official Python driver for MongoDB.

It allows Python code to perform database operations.

Examples:

- Insert documents.
- Retrieve records.
- Update documents.
- Delete documents.
- Execute aggregation queries.

## 8.4 Database Structure

Database:

`spendwise_db`

Collections:

1. expenses
2. budgets

### Expenses Collection

Example:

```json
{
  "_id": "ObjectId",
  "amount": 400,
  "category": "Food",
  "description": "Lunch",
  "date": "2026-11-03",
  "created_at": "MongoDB Date"
}
```

### Budgets Collection

Example:

```json
{
  "category": "Food",
  "monthly_limit": 3000,
  "updated_at": "MongoDB Date"
}
```

## 8.5 CRUD Operations

CRUD means:

- Create
- Read
- Update
- Delete

### Create

Insert a new expense:

```python
expenses_collection.insert_one(expense)
```

### Read

Retrieve expenses:

```python
expenses_collection.find()
```

### Update

Update an expense amount:

```python
expenses_collection.update_one(
    {"_id": object_id},
    {"$set": {"amount": float(new_amount)}}
)
```

### Delete

Delete a transaction using its ObjectId:

```python
expenses_collection.delete_one(
    {"_id": object_id}
)
```

The database module contains these lower-level functions.

However, the chatbot's delete action is currently only a placeholder.

## 8.6 What is Aggregation?

Aggregation allows MongoDB to process documents and calculate grouped results.

SpendWise uses aggregation for total expenses and category-wise summaries.

Example total aggregation:

```python
result = expenses_collection.aggregate([
    {
        "$group": {
            "_id": None,
            "total": {
                "$sum": "$amount"
            }
        }
    }
])
```

### Explanation

`$group` groups documents.

`_id: None` places every expense into one group.

`$sum` adds the values of the amount field.

This calculates the total spending.

### Category-Wise Aggregation

```python
result = expenses_collection.aggregate([
    {
        "$group": {
            "_id": "$category",
            "total": {
                "$sum": "$amount"
            },
            "count": {
                "$sum": 1
            }
        }
    }
])
```

This groups records by category and calculates:

- Total amount.
- Number of transactions.

Example result:

| Category | Total | Transactions |
|---|---:|---:|
| Food | ₹800 | 2 |
| Shopping | ₹500 | 1 |
| Travel | ₹300 | 1 |

## 8.7 Environment Variables

Database credentials must not be hardcoded in Python source code.

SpendWise uses a local `.env` file.

Example:

```env
MONGODB_URI="mongodb+srv://USERNAME:PASSWORD@YOUR_CLUSTER.mongodb.net/?retryWrites=true&w=majority"

DATABASE_NAME="spendwise_db"
```

The Python module loads these variables using:

```python
from dotenv import load_dotenv

load_dotenv()
```

This separates application configuration from source code.

Never commit `.env` to GitHub.

---

# PAGE 9 — FLASK BACKEND AND FRONTEND INTEGRATION

## 9.1 Why Flask?

Rasa provides the conversational engine, but SpendWise also needs an HTTP API for its web dashboard.

Flask is used to create that backend API.

It connects the frontend with the database and Rasa server.

## 9.2 Architecture

```text
             FRONTEND
         HTML + CSS + JS
                 |
                 v
             FLASK API
              PORT 5000
                 |
       +---------+---------+
       |                   |
       v                   v
   RASA SERVER        DATABASE API
    PORT 5005              |
       |                   |
       v                   |
  ACTION SERVER            |
    PORT 5055              |
       |                   |
       +---------+---------+
                 |
                 v
           MONGODB ATLAS
```

## 9.3 Important Flask APIs

The backend file is:

`app.py`

It defines the following routes.

| Route | Method | Function |
|---|---|---|
| / | GET | API home |
| /api/health | GET | Backend health check |
| /api/dashboard | GET | Dashboard statistics |
| /api/expenses | GET | Expense history |
| /api/categories | GET | Category information |
| /api/budgets | GET | Budget details |
| /api/chat | POST | Forward chatbot messages |

## 9.4 Chat Integration

The frontend sends a message to:

`POST /api/chat`

Example payload:

```json
{
  "sender": "spendwise_web_user",
  "message": "I spent 400 on food"
}
```

Flask forwards the message to:

`http://localhost:5005/webhooks/rest/webhook`

Rasa returns a response.

Flask then sends the result back to JavaScript.

JavaScript displays it in the chatbot interface.

## 9.5 What is CORS?

CORS means Cross-Origin Resource Sharing.

It is a browser security mechanism governing requests made between different origins.

SpendWise uses:

```python
from flask_cors import CORS

CORS(app)
```

This allows the frontend running on port 5500 to communicate with Flask on port 5000.

For a production deployment, CORS should be restricted to the actual application domain.

## 9.6 Frontend Responsibilities

### HTML

Defines dashboard structure.

### CSS

Controls design, layout, colors and responsiveness.

### JavaScript

Handles:

- API requests.
- Dashboard updates.
- Chat messages.
- Chart creation.
- Transaction display.
- Budget display.

## 9.7 Chart.js

Chart.js is used to display category-wise expense distribution.

The project creates a doughnut chart.

Example:

```javascript
new Chart(ctx, {
    type: "doughnut",

    data: {
        labels: ["Food", "Shopping"],

        datasets: [{
            data: [800, 500]
        }]
    }
});
```

The actual data is obtained dynamically from the Flask categories API.

---

# PAGE 10 — DEVELOPMENT CHALLENGES AND TROUBLESHOOTING

Understanding the challenges faced during development is important for an interview.

## 10.1 Python Compatibility

Initial Python version:

3.12.4

The selected Rasa version required a compatible Python environment.

Solution:

- Installed Python 3.10.11.
- Created a virtual environment.
- Installed Rasa 3.6.21 and Rasa SDK 3.6.2.

This prevented dependency conflicts with the system Python installation.

## 10.2 MongoDB AutoReconnect

The original cluster intermittently returned:

```text
pymongo.errors.AutoReconnect
```

It also reported:

```text
ReplicaSetNoPrimary
```

This indicated that the driver could not establish a usable replica-set connection.

Network checks were performed using:

```powershell
Test-NetConnection HOSTNAME -Port 27017
```

A fresh free-tier Atlas cluster was created.

Its connection string was updated in `.env`.

The new database connection was tested successfully.

## 10.3 Invalid MongoDB URI

An initial test returned:

```text
Invalid URI host: your_new_cluster_host
```

Cause:

A placeholder hostname was accidentally left in the connection string.

Solution:

The actual hostname provided by MongoDB Atlas was used.

## 10.4 Rasa REST Webhook 405 Error

Opening the webhook directly in the browser returned:

```text
405 Method Not Allowed
```

Why?

The browser sends GET when opening a URL.

Rasa's REST webhook expects POST with a JSON payload.

Correct testing method:

```powershell
$body = @{
    sender = "spendwise_test"
    message = "hi"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:5005/webhooks/rest/webhook" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

This successfully returned the configured greeting.

## 10.5 Flask Returned 404

The Flask chat API initially received:

```text
404 Not Found
```

The REST input channel had to be registered through:

`credentials.yml`

Configuration:

```yaml
rest:
```

Rasa was restarted with the credentials file.

The direct REST webhook test then succeeded, followed by a successful Flask chat API test.

## 10.6 Missing Amount or Category

Some expense messages were not understood completely.

For example:

"I shop and spend 300."

The action returned:

"Please provide both the expense amount and category."

Reason:

The custom action requires both amount and category slots.

The current implementation does not have a complete conversational form that gathers missing values over multiple turns.

This remains an improvement opportunity.

---

# PAGE 11 — TESTING, LIMITATIONS AND FUTURE IMPROVEMENTS

## 11.1 Functional Testing

The following tests were performed during development.

| Test | Input / Operation | Observed Result |
|---|---|---|
| Greeting | hi | Greeting returned |
| Expense recording | I spent 400 on food | Saved successfully |
| Database connection | Python database test | Successful |
| Insert operation | ₹300 Shopping test expense | Inserted ID returned |
| Total calculation | Database aggregation | ₹300 returned after test insert |
| REST webhook | POST with hi | Greeting returned |
| Flask dashboard | GET /api/dashboard | HTTP 200 |
| Expense API | GET /api/expenses | HTTP 200 |
| Category API | GET /api/categories | HTTP 200 |
| Budget API | GET /api/budgets | HTTP 200 |
| Flask chatbot | POST /api/chat | HTTP 200 |

These are functional tests.

No formal intent accuracy, entity extraction F1 score, latency benchmark or large-scale NLU evaluation has been conducted.

Do not present these tests as proof of a particular percentage accuracy.

## 11.2 Current Limitations

### 1. Single-User Application

The current database design does not maintain separate user accounts.

### 2. No Authentication

Login, registration and user authentication are not implemented.

### 3. Expense Deletion

The chatbot has a registered deletion intent and action, but the action currently returns a placeholder response.

### 4. Multi-Turn Expense Collection

The current expense action needs both amount and category.

A complete Rasa form-based conversation is not implemented.

### 5. Budget Management

The chatbot can set and list budget limits.

The dashboard calculates current-month spending and remaining budget, but advanced conversational budget analysis is not implemented.

### 6. Evaluation

The system has been functionally tested, but a held-out dataset has not been used to calculate formal accuracy or F1 metrics.

## 11.3 Future Improvements

Possible improvements include:

1. User authentication and authorization.
2. Multi-user expense separation.
3. Rasa forms for collecting missing information.
4. Safe transaction selection and deletion.
5. Monthly budget alerts.
6. Export to CSV and PDF.
7. Persistent Rasa tracker storage.
8. More training examples.
9. Formal NLU evaluation.
10. Deployment to a cloud environment.
11. Hindi and multilingual support.

These features are proposed improvements, not claims about current functionality.

---

# PAGE 12 — COMPLETE INTERVIEW PREPARATION

This section contains likely questions an interviewer or professor may ask about the SpendWise project.

## A. Project-Level Questions

### Q1. Explain your project in one minute.

**Answer:**

"SpendWise is a conversational personal expense tracker developed using Rasa Open Source. It allows users to record expenses, check total spending, view category-wise summaries and manage budget limits through natural language messages. Rasa performs intent classification and entity extraction, while custom Python actions connect the chatbot to MongoDB Atlas through PyMongo. I also integrated Flask APIs and developed a web dashboard using HTML, CSS and JavaScript."

### Q2. Why did you choose this project?

"Expense tracking is a practical problem. I wanted to demonstrate how a conversational interface can simplify traditional application workflows. It also allowed me to explore Rasa concepts and integrate a conversational AI framework with a real database-backed application."

### Q3. What was your biggest technical challenge?

"Python compatibility and MongoDB Atlas connectivity were major challenges. I created a Python 3.10 virtual environment for classic Rasa 3.6 and configured a new MongoDB Atlas cluster after experiencing intermittent connection failures."

### Q4. Is your application an LLM chatbot?

"No. It uses Rasa Open Source with the DIETClassifier for intent classification and entity extraction, along with Rasa dialogue policies. It does not depend on GPT, Gemini or another external LLM API."

## B. Rasa Questions

### Q5. What is Rasa?

Rasa is an open-source conversational AI framework used to develop assistants that understand natural language and manage conversations.

### Q6. What is NLU?

Natural Language Understanding identifies the user's intention and extracts relevant entities from a message.

### Q7. What is an intent?

An intent represents the purpose behind the user's message.

Example:

"I spent 500 on food" → `add_expense`.

### Q8. What is an entity?

An entity is a meaningful value extracted from the message.

Example:

`500` → amount.

`food` → category.

### Q9. What is the difference between an intent and entity?

Intent identifies what the user wants to do.

Entity identifies the information needed to perform it.

### Q10. What is a slot?

A slot stores information within the conversation.

SpendWise uses amount, category and description slots.

### Q11. What is a tracker?

A tracker maintains the conversation state, including messages, events, slot values and actions.

### Q12. What is domain.yml?

It defines intents, entities, slots, responses and custom actions known to the assistant.

### Q13. What are stories?

Stories are example conversation paths used to train dialogue management.

### Q14. What are rules?

Rules define specific conversation behaviors that should consistently occur.

### Q15. What is DIETClassifier?

DIET stands for Dual Intent and Entity Transformer.

It is a Rasa component used for intent classification and entity extraction.

### Q16. What is TEDPolicy?

TEDPolicy is a machine-learning dialogue policy that predicts the next action using conversation context.

### Q17. What is MemoizationPolicy?

It remembers previously trained conversation paths and can reuse them when a similar conversation occurs.

### Q18. What is RulePolicy?

It handles conversation behavior explicitly defined in rules.yml.

### Q19. What is FallbackClassifier?

It helps identify uncertain or ambiguous intent predictions so the assistant can handle unclear messages.

### Q20. What are custom actions?

Custom actions allow Rasa to execute external Python code, such as inserting transactions into MongoDB.

## C. Backend Questions

### Q21. Why did you use Flask?

"Rasa handles conversations, but the web dashboard also requires APIs for accessing financial statistics, expenses and budgets. Flask provides those APIs and forwards chat messages to Rasa."

### Q22. Why do you need PyMongo?

PyMongo is the Python driver used to communicate with MongoDB.

### Q23. Why MongoDB instead of a relational database?

MongoDB stores records as flexible documents. Expense data naturally maps to documents containing amount, category, description and date.

### Q24. What is MongoDB aggregation?

Aggregation is a database processing framework that allows operations such as grouping, counting, filtering and summing documents.

SpendWise uses it to calculate total spending and category-wise summaries.

### Q25. What is CRUD?

CRUD stands for Create, Read, Update and Delete.

These represent the four basic database operations.

### Q26. Why do you use .env?

To store configuration such as the MongoDB URI separately from application source code.

This reduces the risk of exposing credentials in GitHub.

## D. Integration Questions

### Q27. How does the frontend communicate with Rasa?

"The frontend sends a message to the Flask chat API. Flask forwards it to the Rasa REST webhook through an HTTP POST request. Rasa returns a response, and Flask passes it back to JavaScript."

### Q28. Why are there four terminals?

The application runs four separate processes:

| Process | Port |
|---|---|
| Rasa action server | 5055 |
| Rasa server | 5005 |
| Flask backend | 5000 |
| Frontend static server | 5500 |

### Q29. Why is the action server separate from Rasa?

It separates conversation management from external Python business logic.

The Rasa server determines which action should run, and the Rasa SDK action server executes it.

### Q30. What happens when MongoDB becomes unavailable?

Database operations can fail with connection errors. The database module checks the connection and attempts to reconnect. If the database is still unavailable, the operation should return an error rather than silently claiming success.

## E. Practical Demonstration Questions

An interviewer may ask you to demonstrate:

1. Add ₹400 under Food.
2. Add ₹500 under Shopping.
3. Ask for total spending.
4. View category-wise expenses.
5. Show recent transactions.
6. Set a monthly budget.
7. View saved budgets.
8. Show how the frontend dashboard updates.
9. Explain the NLU result and extracted entities.

Always demonstrate a workflow that has actually been tested.

---

# FINAL REVISION CHECKLIST

Before presenting the project, make sure you can explain:

- [ ] What problem SpendWise solves.
- [ ] Why Rasa was chosen.
- [ ] Difference between NLU and dialogue management.
- [ ] All ten primary user-facing intents.
- [ ] Amount and category entities.
- [ ] Amount, category and description slots.
- [ ] Domain.yml.
- [ ] Stories and rules.
- [ ] NLU pipeline.
- [ ] DIETClassifier.
- [ ] MemoizationPolicy.
- [ ] RulePolicy.
- [ ] TEDPolicy.
- [ ] Custom action architecture.
- [ ] Rasa SDK.
- [ ] MongoDB Atlas.
- [ ] PyMongo and aggregation.
- [ ] Flask APIs.
- [ ] REST webhook.
- [ ] Complete expense recording workflow.
- [ ] Current implementation limitations.
- [ ] Development challenges.

## FINAL PROJECT SUMMARY

SpendWise demonstrates the practical use of the Rasa Framework for developing a database-connected conversational application.

The project combines NLU, intent classification, entity extraction, slot management, dialogue policies, stories, rules and Python custom actions.

The assistant uses MongoDB Atlas to save and retrieve financial data. Flask exposes backend APIs, and a web dashboard provides a visual interface for reviewing spending.

The most important learning from this project is understanding how a conversational AI framework can translate ordinary user messages into structured information, execute application logic, communicate with databases and return meaningful responses.

**Project Repository:**  
https://github.com/ritikgupta7783/SpendWise-Rasa-Project

**Developer:** Ritik Kumar Gupta  
**National Institute of Technology Silchar**

---

**END OF HANDBOOK**