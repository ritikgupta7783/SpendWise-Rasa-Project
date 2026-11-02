![alt text](image-5.png)

---

![alt text](image-1.png)

---

![alt text](image-2.png)

---

![alt text](image-3.png)

---

![alt text](image-4.png)

---

![alt text](image.png)

---


# SpendWise — AI-Powered Student Expense Tracker

**A conversational expense-tracking application built using the Rasa Framework, Python, MongoDB Atlas, Flask, and HTML/CSS/JavaScript.**

SpendWise is a personal finance management chatbot that helps users record daily expenses, monitor spending, view category-wise summaries, and manage budgets through natural language conversations.

Instead of manually entering every transaction into a spreadsheet, users can simply tell SpendWise what they spent.

For example:

- "I spent 200 on food."
- "I spent 500 on shopping."
- "How much have I spent?"
- "Show my recent expenses."
- "Set a monthly food budget of 3000."
- "Show my category-wise spending."

SpendWise uses **Rasa Open Source** to understand user messages and manage conversations. Python custom actions handle application logic, while MongoDB Atlas stores financial records.

---

## 1. Project Overview

### What is SpendWise?

SpendWise is a conversational student expense tracker designed to make personal expense management simple.

The application combines a chatbot with a financial dashboard.

Users can:

1. Add expenses using natural language.
2. Calculate their total spending.
3. View category-wise expense summaries.
4. View recent transactions.
5. Set monthly category budgets.
6. Check their existing budget limits.
7. Interact with an AI-style conversational interface.

### Main Objectives

- Understand how conversational AI works using Rasa.
- Implement Natural Language Understanding (NLU).
- Identify user intents and extract entities.
- Manage conversational context using slots.
- Control conversation flows using stories and rules.
- Connect Rasa with Python custom actions.
- Store and retrieve financial data using MongoDB Atlas.
- Integrate the chatbot with a web-based dashboard.

---

## 2. Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.10 | Main programming language |
| Rasa Open Source 3.6.21 | Conversational AI framework |
| Rasa SDK 3.6.2 | Development of custom actions |
| MongoDB Atlas | Cloud database |
| PyMongo | Python–MongoDB connection |
| Flask | Backend API |
| Flask-CORS | Cross-origin communication |
| HTML5 | Frontend structure |
| CSS3 | Frontend styling |
| JavaScript | Frontend interactions |
| Chart.js | Financial data visualization |
| python-dotenv | Environment variable management |

### Why Rasa?

Rasa was selected because it provides a framework for building conversational assistants without requiring an external LLM API for basic intent classification and dialogue management.

It provides two important capabilities:

- **Natural Language Understanding (NLU):** Understands what the user wants and extracts useful information.
- **Dialogue Management:** Determines how the chatbot should respond based on the conversation.

Rasa also allows developers to write custom Python actions to connect the chatbot with external systems such as databases and APIs.

---

## 3. Understanding the Rasa Framework

This is the most important part of the project.

Rasa is not simply a chatbot that matches keywords and returns predefined messages. It uses trained NLU models and dialogue policies to understand messages and determine the next action.

SpendWise uses several important Rasa components.

### 3.1 Intents

An intent represents the purpose or intention behind a user's message.

For example:

| User Message | Detected Intent |
|---|---|
| Hi | `greet` |
| Hello SpendWise | `greet` |
| I spent 200 on food | `add_expense` |
| How much have I spent? | `check_total` |
| Show my expenses | `show_history` |
| Show category summary | `category_summary` |
| Set a budget | `set_budget` |
| Check my budget | `check_budget` |
| Bye | `goodbye` |

SpendWise defines these intents inside:

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
    - I spent 200 on food
    - I purchased something for 500
    - Add 300 to shopping
    - I paid 150 for lunch

- intent: check_total
  examples: |
    - How much have I spent?
    - Tell me my total expenses
    - What is my total spending?
```

**How does this work?**

When the user sends a message, Rasa processes the text and predicts the most likely intent using its trained NLU pipeline.

For example:

Input:

`I spent 200 on food`

Predicted intent:

`add_expense`

The intent tells SpendWise that the user wants to record an expense.

### 3.2 Entities

Entities are important pieces of information extracted from user messages.

In SpendWise, two important entities are:

- `amount`: The amount of money spent.
- `category`: The category of the expense.

Example:

Input:

`I spent 500 on shopping`

Extracted information:

```yaml
intent: add_expense

entities:
  - entity: amount
    value: 500

  - entity: category
    value: shopping
```

Rasa uses annotated training examples to learn entity extraction.

Example:

```yaml
- intent: add_expense
  examples: |
    - I spent [200](amount) on [food](category)
    - I paid [500](amount) for [shopping](category)
    - Add [300](amount) to [travel](category)
```

**Difference between intent and entity:**

- Intent tells us what the user wants to do.
- Entity tells us the information needed to perform that task.

For example, `add_expense` is the intent, while `500` and `shopping` are entities.

### 3.3 Slots

Slots are used to store information during a conversation.

Think of slots as the chatbot's temporary memory.

SpendWise defines slots such as:

- `amount`
- `category`
- `description`

Example:

The user says:

`I spent 500`

The chatbot may identify the amount but not the category.

The conversation can then request the missing category.

The amount can be stored in the `amount` slot while the chatbot waits for the remaining information.

Example domain configuration:

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
```

Slots help preserve information across multiple messages.

### 3.4 Domain

The `domain.yml` file acts as the configuration and vocabulary of the assistant.

It tells Rasa which components exist in the application.

The domain contains:

- Intents
- Entities
- Slots
- Responses
- Custom actions

For example:

```yaml
intents:
  - greet
  - goodbye
  - add_expense
  - check_total
  - show_history

entities:
  - amount
  - category

actions:
  - action_add_expense
  - action_check_total
  - action_show_history
```

The domain connects the NLU configuration with the dialogue management system.

### 3.5 Responses

Responses are predefined messages that the chatbot can send to users.

They are defined inside `domain.yml`.

Example:

```yaml
responses:

  utter_greet:
    - text: "Hello! Welcome to SpendWise."

  utter_goodbye:
    - text: "Goodbye! Keep tracking your expenses."

  utter_help:
    - text: "You can add expenses, check totals and manage budgets."
```

Rasa can use these responses directly without executing custom Python code.

### 3.6 Stories

Stories represent example conversation paths.

They teach Rasa how conversations can proceed.

Example from `data/stories.yml`:

```yaml
stories:

- story: greeting
  steps:
    - intent: greet
    - action: utter_greet

- story: add expense
  steps:
    - intent: add_expense
    - action: action_add_expense

- story: check total
  steps:
    - intent: check_total
    - action: action_check_total
```

**Why are stories important?**

They provide examples of expected conversational behavior.

Rasa uses these examples to train its dialogue management policies.

### 3.7 Rules

Rules define conversation paths that should always follow a predictable pattern.

For example, a greeting should always receive a greeting response.

Example from `data/rules.yml`:

```yaml
rules:

- rule: Respond to greeting
  steps:
    - intent: greet
    - action: utter_greet

- rule: Respond to goodbye
  steps:
    - intent: goodbye
    - action: utter_goodbye
```

**Difference between stories and rules:**

| Stories | Rules |
|---|---|
| Represent example conversation paths | Define predictable conversation behavior |
| Help train dialogue policies | Enforce specified conversational patterns |
| Can represent multiple-step conversations | Usually represent fixed behavior |

### 3.8 Custom Actions

Custom actions are one of the most powerful features of Rasa.

They allow the chatbot to execute actual Python code instead of only returning predefined text.

SpendWise uses custom actions to communicate with MongoDB.

Custom actions are implemented in:

`actions/actions.py`

Some implemented actions include:

| Action | Purpose |
|---|---|
| `action_add_expense` | Save an expense |
| `action_check_total` | Calculate total spending |
| `action_category_summary` | Retrieve category-wise spending |
| `action_show_history` | Retrieve recent transactions |
| `action_delete_expense` | Handle expense deletion |
| `action_set_budget` | Save a category budget |
| `action_check_budget` | Retrieve saved budgets |

Example of a custom action:

```python
from rasa_sdk import Action
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from database.db import add_expense


class ActionAddExpense(Action):

    def name(self):
        return "action_add_expense"

    def run(self, dispatcher, tracker, domain):

        amount = tracker.get_slot("amount")
        category = tracker.get_slot("category")

        if amount is None or category is None:

            dispatcher.utter_message(
                text="Please provide both the expense amount and category."
            )

            return []

        try:

            add_expense(
                amount=float(amount),
                category=category,
                description=""
            )

            dispatcher.utter_message(
                text=f"Successfully saved ₹{amount} under {category}!"
            )

        except Exception:

            dispatcher.utter_message(
                text="Sorry, I couldn't save your expense. Please try again."
            )

        return [
            SlotSet("amount", None),
            SlotSet("category", None)
        ]
```

**What happens here?**

1. Rasa detects the `add_expense` intent.
2. Rasa extracts the amount and category.
3. The values are available through the tracker slots.
4. The custom action reads the slots.
5. The `add_expense()` database function is called.
6. MongoDB stores the transaction.
7. The chatbot confirms the operation.

This is how SpendWise connects conversational AI with real application functionality.

### 3.9 NLU Pipeline

The NLU pipeline is defined in `config.yml`.

It describes the components used to process user messages.

SpendWise uses components such as:

```yaml
pipeline:
  - name: WhitespaceTokenizer

  - name: RegexFeaturizer

  - name: LexicalSyntacticFeaturizer

  - name: CountVectorsFeaturizer

  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 4

  - name: DIETClassifier
    epochs: 100
    constrain_similarities: true

  - name: EntitySynonymMapper

  - name: FallbackClassifier
    threshold: 0.30
    ambiguity_threshold: 0.10
```

Important components:

**WhitespaceTokenizer**

Splits sentences into individual tokens.

**RegexFeaturizer**

Extracts useful features based on regular-expression patterns.

**CountVectorsFeaturizer**

Converts text into numerical features that the machine-learning model can process.

**DIETClassifier**

A machine-learning component that performs intent classification and entity extraction.

**EntitySynonymMapper**

Maps known synonyms to consistent entity values when synonyms are configured.

**FallbackClassifier**

Helps detect messages for which the intent prediction is uncertain.

### 3.10 Policies

Dialogue policies determine which action Rasa should execute next.

SpendWise uses:

```yaml
policies:

  - name: MemoizationPolicy
    max_history: 5

  - name: RulePolicy

  - name: TEDPolicy
    max_history: 5
    epochs: 100
    constrain_similarities: true
```

**MemoizationPolicy**

Checks whether the current conversation matches a previously learned story.

**RulePolicy**

Handles the behavior defined by rules.

**TEDPolicy**

Uses a machine-learning approach to predict the next action based on conversation context.

---

## 4. How SpendWise Works Internally

Consider this example:

User:

`I spent 400 on food`

The application processes the message through the following stages.

```text
                USER MESSAGE
                     |
                     v
              WEB FRONTEND
                     |
                     v
                FLASK API
                     |
                     v
                RASA SERVER
                     |
                     v
             NLU PROCESSING
                     |
             +-------+-------+
             |               |
             v               v
          INTENT           ENTITIES
        add_expense     amount = 400
                       category = food
             |               |
             +-------+-------+
                     |
                     v
              DIALOGUE MANAGER
                     |
                     v
             CUSTOM ACTION
           action_add_expense
                     |
                     v
              PYTHON FUNCTION
                 PyMongo
                     |
                     v
               MONGODB ATLAS
                     |
                     v
              SAVE TRANSACTION
                     |
                     v
              BOT CONFIRMATION
                     |
                     v
              FLASK API RESPONSE
                     |
                     v
                WEB FRONTEND
```

The chatbot responds:

`Successfully saved ₹400 under food!`

The dashboard can then retrieve the updated financial information from the backend.

---

## 5. Project Architecture

SpendWise uses a modular architecture.

Each component has a specific responsibility.

| Component | Responsibility |
|---|---|
| Frontend | Displays dashboard and chatbot |
| Flask backend | Provides APIs to the frontend |
| Rasa server | Handles user messages |
| Rasa NLU | Detects intents and entities |
| Dialogue manager | Selects the next action |
| Action server | Executes custom Python actions |
| Database module | Handles MongoDB operations |
| MongoDB Atlas | Stores expenses and budgets |

### Why separate the Action Server?

Rasa runs custom actions through a separate Rasa SDK action server.

This separates conversational processing from business logic.

The Rasa server handles the conversation, while the action server executes Python operations.

The action endpoint is configured in:

`endpoints.yml`

```yaml
action_endpoint:
  url: "http://localhost:5055/webhook"
```

---

## 6. Database Design

SpendWise uses MongoDB Atlas as its cloud database.

PyMongo is used to connect Python code to MongoDB.

The database name is:

`spendwise_db`

The application uses two main collections.

### Expenses Collection

Stores individual expense records.

Example:

```json
{
  "_id": "MongoDB ObjectId",
  "amount": 400,
  "category": "Food",
  "description": "Lunch",
  "date": "2026-11-03",
  "created_at": "MongoDB Date"
}
```

### Budgets Collection

Stores category-wise budget limits.

Example:

```json
{
  "category": "Food",
  "monthly_limit": 3000
}
```

Collections are created automatically when documents are inserted if they do not already exist.

### Database Module

Database operations are implemented in:

`database/db.py`

The module contains functions for:

- Connecting to MongoDB Atlas.
- Adding expenses.
- Retrieving expenses.
- Calculating total spending.
- Calculating category-wise summaries.
- Deleting expenses.
- Updating expenses.
- Saving budgets.
- Retrieving budgets.

The database layer is separate from the Rasa action layer. This makes the code easier to understand, maintain, and extend.

---

## 7. Project Folder Structure

```text
SpendWise-Rasa-Project/
│
├── actions/
│   ├── __init__.py
│   └── actions.py
│
├── database/
│   ├── __init__.py
│   └── db.py
│
├── data/
│   ├── nlu.yml
│   ├── stories.yml
│   └── rules.yml
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── app.py
│
├── config.yml
├── credentials.yml
├── domain.yml
├── endpoints.yml
│
├── requirements.txt
├── README.md
├── .gitignore
└── .env.example
```

### Explanation of Important Files

| File | Description |
|---|---|
| `app.py` | Flask backend and API routes |
| `config.yml` | Rasa NLU pipeline and dialogue policies |
| `domain.yml` | Intents, entities, slots, responses and actions |
| `credentials.yml` | Rasa input channel configuration |
| `endpoints.yml` | Custom action server configuration |
| `data/nlu.yml` | Intent and entity training examples |
| `data/stories.yml` | Example conversational stories |
| `data/rules.yml` | Fixed conversation rules |
| `actions/actions.py` | Custom Python actions |
| `database/db.py` | MongoDB operations |
| `frontend/index.html` | Dashboard structure |
| `frontend/style.css` | Dashboard styling |
| `frontend/script.js` | Frontend logic and API integration |
| `requirements.txt` | Python dependencies |
| `.env` | Local environment variables and database credentials |

---

## 8. Installation and Setup

### Prerequisites

Install the following:

- Python 3.10.11
- Git
- Visual Studio Code
- MongoDB Atlas account
- Modern web browser

Rasa 3.6.21 is used in this project with Python 3.10.

### Step 1: Clone the Repository

```bash
git clone https://github.com/ritikgupta7783/SpendWise-Rasa-Project.git

cd SpendWise-Rasa-Project
```

### Step 2: Create a Virtual Environment

```bash
python -m venv rasa_venv
```

Activate it on Windows PowerShell:

```powershell
.\rasa_venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
python -m pip install --upgrade pip

pip install -r requirements.txt
```

If you need to reproduce the original environment, use the compatible versions listed in the project requirements.

### Step 4: Configure MongoDB Atlas

1. Create a MongoDB Atlas account.
2. Create a cluster.
3. Create a database user with appropriate database permissions.
4. Add your current IP address to Network Access.
5. Obtain the MongoDB connection string.
6. Create a `.env` file in the project root.

Example `.env`:

```env
MONGODB_URI="mongodb+srv://USERNAME:PASSWORD@YOUR_CLUSTER.mongodb.net/?retryWrites=true&w=majority"

DATABASE_NAME="spendwise_db"
```

Replace the placeholders with your own credentials.

Do not upload `.env` to GitHub.

If your password contains special characters, URL-encode them in the connection string.

### Step 5: Test the Database Connection

```bash
python -m database.db
```

Expected output:

```text
Successfully connected to MongoDB Atlas!
Database: spendwise_db
```

### Step 6: Train the Rasa Model

```bash
rasa train
```

Rasa reads the training data and configuration files, trains the NLU and dialogue models, and saves a trained model inside the `models/` directory.

To validate training data:

```bash
rasa data validate
```

To inspect the trained model interactively:

```bash
rasa shell
```

---

## 9. Running the Application

SpendWise uses separate processes for the Rasa server, custom action server, Flask backend, and frontend.

Open four separate terminals from the project folder.

### Terminal 1: Start the Rasa Action Server

```powershell
rasa run actions
```

The action server runs on:

`http://localhost:5055`

It loads the Python custom actions.

### Terminal 2: Start the Rasa Server

```powershell
rasa run --enable-api --cors "*" --port 5005 --credentials credentials.yml
```

The Rasa server runs on:

`http://localhost:5005`

It receives chatbot messages and manages conversations.

### Terminal 3: Start Flask

```powershell
python app.py
```

The Flask backend runs on:

`http://localhost:5000`

It provides APIs to the frontend and communicates with Rasa.

### Terminal 4: Start the Frontend

```powershell
python -m http.server 5500 --directory frontend
```

Open the application in your browser:

`http://localhost:5500`

Keep the four terminals running while using the application.

---

## 10. API Integration

The frontend communicates with Flask using HTTP requests.

Flask provides an interface between the web application and the backend services.

The current frontend uses these API routes:

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/dashboard` | GET | Dashboard statistics |
| `/api/expenses?limit=10` | GET | Recent transactions |
| `/api/categories` | GET | Category-wise analytics |
| `/api/budgets` | GET | Budget information |
| `/api/chat` | POST | Send chatbot messages |

Example chatbot request:

```json
{
  "sender": "spendwise_web_user",
  "message": "I spent 300 on food"
}
```

Example direct Rasa REST request:

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

Rasa processes the message and returns the bot response.

---

## 11. Testing the Chatbot

Try the following messages after starting all the servers.

| Test | Message |
|---|---|
| Greeting | Hi |
| Add expense | I spent 400 on food |
| Add shopping expense | I spent 500 on shopping |
| Check total | How much have I spent? |
| View history | Show my recent expenses |
| Category summary | Show my category-wise expenses |
| Set budget | Set my food budget to 3000 |
| Check budget | Show my budget |
| Help | Help me |
| Goodbye | Bye |

The chatbot should identify the appropriate intent, extract the available entities, execute the relevant action, and return a response.

---

## 12. Important Rasa Commands

| Command | Purpose |
|---|---|
| `rasa init` | Create a starter Rasa project |
| `rasa train` | Train the assistant |
| `rasa shell` | Test the assistant in the terminal |
| `rasa run` | Start the Rasa server |
| `rasa run actions` | Start the custom action server |
| `rasa data validate` | Validate training data |
| `rasa visualize` | Visualize conversation stories |
| `rasa interactive` | Improve training data interactively |
| `rasa test` | Run model and conversation tests |
| `rasa --version` | Check the installed Rasa version |

---

## 13. Error Handling and Troubleshooting

### MongoDB Connection Error

Possible causes:

- Incorrect connection string.
- Incorrect database username or password.
- IP address not allowed in Atlas Network Access.
- Network connectivity problems.
- Cluster unavailable.

Check the `.env` file and MongoDB Atlas configuration.

### Rasa Action Server Not Running

If custom actions fail, verify that the action server is running on port `5055`.

Also check the action endpoint in `endpoints.yml`.

### 404 or 405 Errors

Make sure the correct API is being used.

The Rasa REST webhook expects a POST request, not a normal browser GET request.

Correct endpoint:

`http://localhost:5005/webhooks/rest/webhook`

### Chatbot Does Not Recognize a Message

Check:

- Whether the intent exists in `data/nlu.yml`.
- Whether the training examples cover different ways of expressing the intent.
- Whether the model has been retrained.
- Whether the correct trained model is loaded.

After changing NLU training examples, run:

```bash
rasa train
```

### Frontend Does Not Load Data

Verify that:

- Flask is running.
- Rasa is running.
- The action server is running.
- The frontend is using the correct API URL.
- Browser developer tools do not show network or JavaScript errors.

---

## 14. Current Limitations

SpendWise is an educational prototype and has some limitations.

1. The current application is designed for a single user.
2. Entity extraction depends on the training examples and configured NLU pipeline.
3. The application does not currently provide full multi-user authentication.
4. Advanced financial reporting is limited.
5. Some expense operations may require more conversational steps.
6. Budget functionality can be extended to provide detailed monthly utilization and alerts.
7. Database availability depends on internet connectivity and MongoDB Atlas access.
8. A production deployment would require stronger security, validation, monitoring, and access control.

---

## 15. Future Improvements

Possible improvements include:

- Multi-user registration and authentication.
- More advanced expense entity extraction.
- Conversational forms for missing information.
- Confirmation before deleting transactions.
- Automatic monthly budget calculations.
- Budget warning notifications.
- Monthly and yearly spending charts.
- Export expenses to CSV or PDF.
- Persistent Rasa conversation tracker storage.
- Improved fallback and clarification behavior.
- Deployment to a cloud platform.
- Mobile-friendly dashboard and progressive web application.

---

## 16. Learning Outcomes

Through this project, the following concepts can be understood practically:

- Conversational AI development using Rasa.
- Intent classification and entity extraction.
- Slot-based conversation context.
- Rasa domain configuration.
- Stories and rules for dialogue management.
- Custom action development using Rasa SDK.
- NLU pipeline and machine-learning-based classification.
- Integration of Rasa with Flask.
- Python database operations using PyMongo.
- MongoDB Atlas cloud database integration.
- Frontend and backend communication through REST APIs.

The main learning objective is to understand how a conversational AI framework can be connected to real-world application logic and external databases.

---

## 17. Author

**Ritik Kumar Gupta**

Computer Science and Engineering  
National Institute of Technology, Silchar

GitHub: https://github.com/ritikgupta7783

Project Repository: https://github.com/ritikgupta7783/SpendWise-Rasa-Project

---

## License

This project is developed for educational and academic purposes.

