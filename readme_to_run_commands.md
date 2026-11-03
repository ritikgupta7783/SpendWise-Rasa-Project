# SpendWise — How to Run the Project

A conversational personal expense tracker built using Rasa Open Source, Python, Flask and MongoDB Atlas.

**Developer:** Ritik Kumar Gupta  
**Scholar ID:** 2312065  
**Institute:** National Institute of Technology Silchar

**GitHub:** https://github.com/ritikgupta7783/SpendWise-Rasa-Project

---

# 1. Prerequisites

Before running SpendWise, make sure the following are installed:

| Software | Version |
|---|---|
| Python | 3.10.11 |
| Rasa Open Source | 3.6.21 |
| Rasa SDK | 3.6.2 |
| VS Code | Latest |
| MongoDB Atlas | Cloud database |
| Git | Latest |

The project was developed and tested on Windows using PowerShell.

**Important:** This project uses Python 3.10.11 because the selected Rasa 3.6 environment requires a compatible Python version.

# 2. Open the Project in VS Code

Open PowerShell and execute:

```powershell
cd "D:\Rasa SpendWise"
code .
```

Alternatively, open the `Rasa SpendWise` folder directly from VS Code.

Open the integrated terminal:

`Ctrl + `` (backtick)

# 3. Activate the Virtual Environment

The project uses an existing Python virtual environment named `rasa_venv`.

Run:

```powershell
.\rasa_venv\Scripts\Activate.ps1
```

Your terminal should display:

```text
(rasa_venv) PS D:\Rasa SpendWise>
```

Verify Python:

```powershell
python --version
```

Expected:

```text
Python 3.10.11
```

**Why is this necessary?**

A virtual environment isolates the project's Python dependencies from the system Python installation.

It ensures that Rasa, Flask, PyMongo and other packages use the versions installed for SpendWise.

# 4. Configure MongoDB Atlas

SpendWise uses MongoDB Atlas to store expense and budget information.

Before running the application, create a local `.env` file in the project root.

Example:

```env
MONGODB_URI="mongodb+srv://USERNAME:PASSWORD@YOUR_CLUSTER.mongodb.net/?retryWrites=true&w=majority"

DATABASE_NAME="spendwise_db"
```

Replace the placeholders with your own MongoDB Atlas credentials and cluster hostname.

**Never upload `.env` to GitHub.**

The `.gitignore` file should exclude it.

The database connection is managed through:

```text
database/db.py
```

# 5. Start the Application — Four Terminals Required

SpendWise uses four separate running processes.

**Important:** Open four terminals in VS Code. Start one process in each terminal and leave all four running.

## Terminal 1 — Rasa Action Server

Open the first terminal.

Run:

```powershell
cd "D:\Rasa SpendWise"

.\rasa_venv\Scripts\Activate.ps1

rasa run actions
```

Expected output:

```text
Action endpoint is up and running
http://0.0.0.0:5055

Successfully connected to MongoDB Atlas!
Database: spendwise_db
```

### Why do we need this?

The action server executes custom Python actions.

For example, when a user sends:

`I spent 400 on food`

Rasa selects `action_add_expense`.

The action server executes that Python code, which calls the database module and saves the expense in MongoDB Atlas.

The action server runs on port **5055**.

Keep this terminal running.

---

## Terminal 2 — Rasa Server

Open the second terminal.

Run:

```powershell
cd "D:\Rasa SpendWise"

.\rasa_venv\Scripts\Activate.ps1

rasa run --enable-api --cors "*" --port 5005 --credentials credentials.yml
```

Expected output:

```text
Rasa server is up and running.
```

### Why do we need this?

This is the main conversational AI server.

It:

- Receives user messages.
- Processes messages using the NLU pipeline.
- Identifies intents.
- Extracts entities.
- Updates slots.
- Manages conversations.
- Selects custom actions.
- Returns chatbot responses.

The server exposes the REST webhook at:

```text
http://localhost:5005/webhooks/rest/webhook
```

The `--enable-api` option enables the Rasa HTTP API.

The `--cors "*"` option enables cross-origin requests for development.

The `--credentials credentials.yml` option loads the configured REST input channel.

Keep this terminal running.

---

## Terminal 3 — Flask Backend

Open the third terminal.

Run:

```powershell
cd "D:\Rasa SpendWise"

.\rasa_venv\Scripts\Activate.ps1

python app.py
```

Expected output should show Flask running on:

```text
http://127.0.0.1:5000
```

### Why do we need this?

Flask acts as the backend API layer.

It connects the web dashboard to the database and Rasa.

It provides these endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Backend health check |
| `/api/dashboard` | GET | Dashboard statistics |
| `/api/expenses` | GET | Expense history |
| `/api/categories` | GET | Category-wise spending |
| `/api/budgets` | GET | Budget information |
| `/api/chat` | POST | Send messages to Rasa |

For chatbot messages, Flask forwards the request to the Rasa REST webhook.

Keep this terminal running.

---

## Terminal 4 — Frontend Server

Open the fourth terminal.

Run:

```powershell
cd "D:\Rasa SpendWise"

.\rasa_venv\Scripts\Activate.ps1

python -m http.server 5500 --directory frontend
```

Expected output:

```text
Serving HTTP on :: port 5500
```

### Why do we need this?

This command starts a simple local HTTP server to serve the frontend files.

It serves:

- `index.html`
- `style.css`
- `script.js`

The browser loads the frontend from this server.

Keep this terminal running.

# 6. Open SpendWise in Your Browser

Once all four terminals are running, open:

**http://localhost:5500**

This is the main SpendWise application.

The frontend communicates with Flask, Flask communicates with Rasa, and Rasa invokes the custom action server when an action is required.

# 7. Architecture and Communication Flow

```mermaid
flowchart TD
    A["User opens SpendWise"] --> B["Frontend: HTML, CSS, JavaScript"]
    B --> C["Flask Backend: Port 5000"]

    C --> D["Rasa REST Webhook: Port 5005"]

    D --> E["NLU Pipeline"]
    E --> F["Intent Classification"]
    E --> G["Entity Extraction"]

    F --> H["Dialogue Management"]
    G --> H

    H --> I["Rasa Action Server: Port 5055"]
    I --> J["Custom Python Actions"]
    J --> K["PyMongo Database Module"]
    K --> L[("MongoDB Atlas")]

    L --> K
    K --> J
    J --> H
    H --> D
    D --> C
    C --> B
```

### Example: Adding an Expense

User enters:

```text
I spent 400 on food
```

The following process occurs:

1. Frontend sends the message to Flask.
2. Flask forwards it to the Rasa REST webhook.
3. Rasa identifies the `add_expense` intent.
4. Rasa extracts `amount = 400`.
5. Rasa extracts `category = food`.
6. Rasa updates the corresponding slots.
7. Dialogue management selects `action_add_expense`.
8. The action server executes the Python custom action.
9. The database module uses PyMongo to insert the transaction.
10. MongoDB Atlas stores the expense.
11. Rasa returns a confirmation.
12. Flask sends the response to the frontend.
13. The chat interface displays the response.

Expected chatbot response:

```text
Successfully saved ₹400 under food!
```

# 8. Testing the Application

After starting all four terminals, test the following operations.

| Test | Message | Expected Behaviour |
|---|---|---|
| Greeting | `hi` | Greeting response |
| Add expense | `I spent 400 on food` | Saves expense |
| Add expense | `I spent 500 on shopping` | Saves expense |
| Check total | `How much have I spent?` | Returns total |
| Category summary | `Show my category-wise expenses` | Returns category totals |
| Expense history | `Show my recent expenses` | Displays recent transactions |
| Set budget | `Set my food budget to 3000` | Saves budget limit |
| Check budget | `Check my budget` | Displays saved budget limits |
| Help | `help` | Shows chatbot capabilities |

Some operations require the relevant amount and category information to be extracted from the message.

The chatbot's deletion action is currently a placeholder.

# 9. Test the Rasa REST Webhook Separately

You can test Rasa without opening the frontend.

Open another PowerShell terminal and execute:

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

Expected response:

```text
recipient_id   text
------------   ----
spendwise_test Hello! Welcome to SpendWise...
```

This confirms that the Rasa REST channel is responding.

**Note:** Opening `/webhooks/rest/webhook` directly in a browser may return `405 Method Not Allowed`, because the REST webhook expects POST requests rather than a normal browser GET request.

# 10. Useful Development Commands

## Check Rasa version

```powershell
rasa --version
```

## Check Python version

```powershell
python --version
```

## Validate Rasa training data

```powershell
rasa data validate
```

## Train the Rasa model

```powershell
rasa train
```

Run this after changing NLU training data, stories, rules or relevant model configuration.

## Test through Rasa shell

```powershell
rasa shell
```

## Test database connectivity

```powershell
python -m database.db
```

## Compile Python files

```powershell
python -m py_compile database/db.py actions/actions.py app.py
```

# 11. Common Problems and Solutions

### Problem 1: Rasa command not recognized

Cause: The virtual environment may not be activated.

Solution:

```powershell
.\rasa_venv\Scripts\Activate.ps1
```

### Problem 2: MongoDB AutoReconnect

Cause: MongoDB Atlas connection interruption or network connectivity issues.

Check:

- MongoDB Atlas cluster status.
- Network Access settings.
- Connection string in `.env`.
- Database user credentials.
- Internet connectivity.

Do not expose your MongoDB URI or password when sharing logs.

### Problem 3: 405 Method Not Allowed

Cause: The REST webhook was accessed through GET.

Solution: Use POST with a JSON payload as demonstrated in Section 9.

### Problem 4: Flask returns 404

Check:

- Flask server is running.
- Correct endpoint is being called.
- Flask route exists in `app.py`.
- Rasa REST channel is configured in `credentials.yml`.

### Problem 5: Chatbot cannot save an expense

Check:

- Rasa server is running.
- Action server is running.
- MongoDB connection is successful.
- Amount and category entities are extracted correctly.
- The action is registered in `domain.yml`.

### Problem 6: Frontend is not loading

Check whether Terminal 4 is running.

Open:

```text
http://localhost:5500
```

Also verify that `frontend/index.html` exists.

# 12. Project Structure

```text
Rasa SpendWise/
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
├── .env
│
├── rasa_venv/
├── models/
├── temp/
└── pip-cache/
```

### Important Files

| File | Responsibility |
|---|---|
| `config.yml` | NLU pipeline and dialogue policies |
| `domain.yml` | Intents, entities, slots, responses and actions |
| `data/nlu.yml` | Intent and entity training examples |
| `data/stories.yml` | Conversation stories |
| `data/rules.yml` | Dialogue rules |
| `actions/actions.py` | Custom Python actions |
| `database/db.py` | MongoDB operations |
| `endpoints.yml` | Rasa action server connection |
| `credentials.yml` | Rasa input channel configuration |
| `app.py` | Flask backend APIs |
| `frontend/index.html` | Dashboard structure |
| `frontend/style.css` | Dashboard styling |
| `frontend/script.js` | Frontend logic and API communication |

# 13. Important Notes

- All four services must remain running while using the complete application.
- The Rasa model is already stored in the `models/` directory. You do not need to train it every time.
- If you modify NLU data, stories, rules or configuration, train the model again using `rasa train`.
- If you modify custom action or database code, restart the action server.
- If you modify Flask code, restart Flask.
- If you modify frontend files, refresh the browser.
- Keep MongoDB credentials in `.env`.
- Never upload `.env` or `rasa_venv/` to GitHub.
- The current application is a local development setup, not a deployed production service.

# 14. Current Implementation Status

## Implemented

- Rasa NLU pipeline.
- Ten primary user-facing intents.
- Amount and category entities.
- Slot configuration.
- Stories and rules.
- MemoizationPolicy, RulePolicy and TEDPolicy.
- Seven registered custom actions.
- MongoDB Atlas connection.
- Expense insertion and retrieval.
- Total expense calculation.
- Category-wise aggregation.
- Budget storage and retrieval.
- Flask backend APIs.
- Rasa REST integration.
- Web dashboard and chat interface.

## Current Limitations

- Single-user prototype.
- No authentication or login system.
- Expense deletion action is a placeholder.
- Complete multi-turn form-based slot filling is not implemented.
- No formal NLU accuracy or F1 benchmark has been conducted.

---

# 15. Developer Information

**Project:** SpendWise — Conversational Expense Tracker

**Developer:** Ritik Kumar Gupta

**Scholar ID:** 2312065

**Branch:** Computer Science and Engineering

**Institute:** National Institute of Technology Silchar

**GitHub Repository:**

https://github.com/ritikgupta7783/SpendWise-Rasa-Project

---

<p align="center">
  <strong>SpendWise — Track Smarter. Spend Better.</strong>
</p>

<p align="center">
  Built with Python, Rasa, Flask and MongoDB Atlas.
</p>
