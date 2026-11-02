
const API_URL = "http://localhost:5000/api";

let categoryChart = null;


// --------------------------------------------------
// 1. FORMAT CURRENCY
// --------------------------------------------------

function formatCurrency(amount) {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2
    }).format(Number(amount) || 0);
}


// --------------------------------------------------
// 2. API REQUEST HELPER
// --------------------------------------------------

async function fetchAPI(endpoint) {
    const response = await fetch(`${API_URL}${endpoint}`);

    if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
    }

    const result = await response.json();

    if (!result.success) {
        throw new Error(result.message || "Unable to load data");
    }

    return result;
}


// --------------------------------------------------
// 3. LOAD DASHBOARD STATISTICS
// --------------------------------------------------

async function loadDashboard() {
    try {
        const data = await fetchAPI("/dashboard");

        document.getElementById("totalExpenses").textContent =
            formatCurrency(data.total_expenses);

        document.getElementById("monthlyExpenses").textContent =
            formatCurrency(data.monthly_expenses);

        document.getElementById("totalTransactions").textContent =
            data.total_transactions;

        document.getElementById("summaryTotal").textContent =
            formatCurrency(data.total_expenses);

        document.getElementById("summaryMonthly").textContent =
            formatCurrency(data.monthly_expenses);

        document.getElementById("summaryTransactions").textContent =
            data.total_transactions;

    } catch (error) {
        console.error("Dashboard error:", error);
        showToast("Unable to load dashboard statistics.");
    }
}


// --------------------------------------------------
// 4. LOAD TRANSACTIONS
// --------------------------------------------------

async function loadExpenses() {
    const tbody = document.getElementById("transactionsBody");

    try {
        const data = await fetchAPI("/expenses?limit=10");

        if (!data.expenses.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="empty-state">
                        No expenses recorded yet.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = data.expenses.map(expense => `
            <tr>
                <td>${escapeHTML(expense.description || "Expense")}</td>

                <td>
                    <span class="category-badge">
                        ${escapeHTML(expense.category || "Other")}
                    </span>
                </td>

                <td>${escapeHTML(expense.date || "—")}</td>

                <td class="amount">
                    -${formatCurrency(expense.amount)}
                </td>
            </tr>
        `).join("");

    } catch (error) {
        console.error("Expense error:", error);

        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-state">
                    Could not load transactions.
                </td>
            </tr>
        `;
    }
}


// --------------------------------------------------
// 5. LOAD CATEGORY ANALYTICS
// --------------------------------------------------

async function loadCategories() {
    try {
        const data = await fetchAPI("/categories");

        const labels = data.categories.map(item => item.category);

        const values = data.categories.map(item => item.total);

        const ctx = document.getElementById("categoryChart");

        if (categoryChart) {
            categoryChart.destroy();
        }

        if (labels.length === 0) {
            ctx.parentElement.innerHTML = `
                <p class="empty-state">
                    Add expenses to see your category breakdown.
                </p>
            `;
            return;
        }

        categoryChart = new Chart(ctx, {
            type: "doughnut",

            data: {
                labels: labels,

                datasets: [{
                    data: values,

                    backgroundColor: [
                        "#8b7cff",
                        "#53a5ff",
                        "#35d39a",
                        "#ffae70",
                        "#e878b5",
                        "#64c9d9",
                        "#b5a0ff"
                    ],

                    borderWidth: 2,
                    borderColor: "#151f35",
                    hoverOffset: 8
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                cutout: "68%",

                plugins: {
                    legend: {
                        position: "bottom",

                        labels: {
                            color: "#b4bfd3",
                            padding: 16,
                            usePointStyle: true,
                            font: {
                                size: 10
                            }
                        }
                    },

                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${formatCurrency(context.raw)}`;
                            }
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error("Category error:", error);
        showToast("Unable to load category analytics.");
    }
}


// --------------------------------------------------
// 6. LOAD BUDGETS
// --------------------------------------------------

async function loadBudgets() {
    const budgetList = document.getElementById("budgetList");

    try {
        const data = await fetchAPI("/budgets");

        const budgets = data.budgets;

        document.getElementById("budgetCount").textContent =
            budgets.length;

        document.getElementById("summaryBudgets").textContent =
            budgets.length;

        if (!budgets.length) {
            budgetList.innerHTML = `
                <p class="empty-state">
                    No budgets created yet. Ask the AI assistant to set a budget.
                </p>
            `;
            return;
        }

        budgetList.innerHTML = budgets.map(budget => {
            const percentage = Math.min(
                Math.max(Number(budget.percentage_used) || 0, 0),
                100
            );

            const exceeded = budget.spent > budget.monthly_limit;

            return `
                <div class="budget-item">

                    <div class="budget-info">
                        <strong>${escapeHTML(budget.category)}</strong>

                        <span>
                            ${formatCurrency(budget.spent)}
                            / ${formatCurrency(budget.monthly_limit)}
                        </span>
                    </div>

                    <div class="progress-track">
                        <div
                            class="progress-fill"
                            style="width: ${percentage}%; background:
                            ${exceeded ? '#ff7373' : ''}"
                        ></div>
                    </div>

                    <div class="budget-details">
                        ${exceeded
                            ? `Over budget by ${formatCurrency(budget.spent - budget.monthly_limit)}`
                            : `${formatCurrency(budget.remaining)} remaining`
                        }
                    </div>

                </div>
            `;
        }).join("");

    } catch (error) {
        console.error("Budget error:", error);

        budgetList.innerHTML = `
            <p class="empty-state">Unable to load budgets.</p>
        `;
    }
}


// --------------------------------------------------
// 7. HTML ESCAPE HELPER
// --------------------------------------------------

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[char]);
}


// --------------------------------------------------
// 8. CHATBOT OPEN AND CLOSE
// --------------------------------------------------

function openChat() {
    document.getElementById("chatWidget").classList.add("open");

    document.getElementById("floatingChat").style.display = "none";

    document.getElementById("chatInput").focus();
}

function closeChat() {
    document.getElementById("chatWidget").classList.remove("open");

    document.getElementById("floatingChat").style.display = "block";
}


// --------------------------------------------------
// 9. ADD CHAT MESSAGE TO UI
// --------------------------------------------------

function addMessage(message, sender) {
    const messages = document.getElementById("chatMessages");

    const element = document.createElement("div");

    element.className =
        sender === "user" ? "user-message" : "bot-message";

    // textContent prevents HTML injection from chatbot responses.
    element.textContent = message;

    messages.appendChild(element);

    messages.scrollTop = messages.scrollHeight;

    return element;
}


// --------------------------------------------------
// 10. SEND MESSAGE TO RASA THROUGH FLASK
// --------------------------------------------------

async function sendMessage(message) {
    if (!message.trim()) return;

    openChat();

    addMessage(message, "user");

    const input = document.getElementById("chatInput");
    const button = document.getElementById("sendButton");

    input.value = "";
    button.disabled = true;

    const loading = addMessage("SpendWise is thinking...", "bot");

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                sender: "spendwise_web_user",
                message: message
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Chat request failed");
        }

        loading.remove();

        if (data.responses && data.responses.length) {
            data.responses.forEach(reply => {
                addMessage(reply, "bot");
            });
        } else {
            addMessage(
                "I received your message, but have no response to show.",
                "bot"
            );
        }

        // Refresh dashboard after possible expense or budget changes.
        await Promise.all([
            loadDashboard(),
            loadExpenses(),
            loadCategories(),
            loadBudgets()
        ]);

    } catch (error) {
        loading.remove();

        console.error("Chat error:", error);

        addMessage(
            "Sorry, I couldn't connect to SpendWise. Please try again.",
            "bot"
        );

    } finally {
        button.disabled = false;
        input.focus();
    }
}


// --------------------------------------------------
// 11. CHAT FORM SUBMISSION
// --------------------------------------------------

document.getElementById("chatForm").addEventListener(
    "submit",
    function(event) {
        event.preventDefault();

        const input = document.getElementById("chatInput");

        const message = input.value.trim();

        if (message) {
            sendMessage(message);
        }
    }
);


// --------------------------------------------------
// 12. QUICK CHAT SUGGESTIONS
// --------------------------------------------------

function sendSuggestion(message) {
    sendMessage(message);
}


// --------------------------------------------------
// 13. TOAST NOTIFICATION
// --------------------------------------------------

function showToast(message) {
    const toast = document.createElement("div");

    toast.textContent = message;

    toast.style.cssText = `
        position: fixed;
        bottom: 25px;
        left: 50%;
        transform: translateX(-50%);
        background: #26334c;
        color: white;
        padding: 13px 20px;
        border: 1px solid #485875;
        border-radius: 9px;
        font-size: 12px;
        z-index: 999;
    `;

    document.body.appendChild(toast);

    setTimeout(() => toast.remove(), 3500);
}


// --------------------------------------------------
// 14. INITIALIZE APPLICATION
// --------------------------------------------------

async function initializeSpendWise() {
    await Promise.all([
        loadDashboard(),
        loadExpenses(),
        loadCategories(),
        loadBudgets()
    ]);
}

document.addEventListener("DOMContentLoaded", initializeSpendWise);
