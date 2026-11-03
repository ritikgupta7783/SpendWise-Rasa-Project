"use strict";

// ==========================================
// SPENDWISE CONFIGURATION
// ==========================================

const API_URL = "http://localhost:5000/api";
const CHAT_TIMEOUT_MS = 30000;
const EASE = "cubic-bezier(0.22, 1, 0.36, 1)";

const MOBILE_QUERY = window.matchMedia("(max-width: 750px)");
const REDUCED_MOTION = window.matchMedia("(prefers-reduced-motion: reduce)");

let categoryChart = null;
let chatAnimation = null;
let lastChatPosition = null;
let lastChatSize = null;
let chatBusy = false;
let toastElement = null;
let toastTimer = null;

let chatWidget;
let chatHeader;
let floatingChat;


// ==========================================
// 1. HELPERS
// ==========================================

function formatCurrency(amount) {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2
    }).format(Number(amount) || 0);
}

function formatDate(value) {
    if (!value) return "—";

    let date;
    const dateOnly = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(value));

    if (dateOnly) {
        // Build a local date so "2026-11-03" never shifts to the previous day.
        date = new Date(+dateOnly[1], +dateOnly[2] - 1, +dateOnly[3]);
    } else {
        date = new Date(value);
    }

    if (Number.isNaN(date.getTime())) return String(value);

    return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric"
    });
}

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[char]);
}

function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
}

function showToast(message) {
    // One toast at a time, so several failed requests do not stack on top of each other.
    if (!toastElement) {
        toastElement = document.createElement("div");
        toastElement.setAttribute("role", "status");
        toastElement.style.cssText = `
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
            z-index: 9999;
            max-width: calc(100vw - 32px);
            text-align: center;
        `;
        document.body.appendChild(toastElement);
    }

    toastElement.textContent = message;
    toastElement.hidden = false;

    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { toastElement.hidden = true; }, 3500);
}


// ==========================================
// 2. API REQUEST HELPER
// ==========================================

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


// ==========================================
// 3. DASHBOARD STATISTICS
// ==========================================

async function loadDashboard() {
    try {
        const data = await fetchAPI("/dashboard");

        const total = formatCurrency(data.total_expenses);
        const monthly = formatCurrency(data.monthly_expenses);
        const count = data.total_transactions ?? 0;

        setText("totalExpenses", total);
        setText("monthlyExpenses", monthly);
        setText("totalTransactions", count);

        setText("summaryTotal", total);
        setText("summaryMonthly", monthly);
        setText("summaryTransactions", count);

    } catch (error) {
        console.error("Dashboard error:", error);
        showToast("Unable to load dashboard statistics.");
    }
}


// ==========================================
// 4. TRANSACTIONS
// ==========================================

async function loadExpenses() {
    const tbody = document.getElementById("transactionsBody");

    try {
        const data = await fetchAPI("/expenses?limit=10");
        const expenses = data.expenses || [];

        if (!expenses.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="empty-state">No expenses recorded yet.</td>
                </tr>`;
            return;
        }

        tbody.innerHTML = expenses.map(expense => `
            <tr>
                <td>${escapeHTML(expense.description || "Expense")}</td>
                <td>
                    <span class="category-badge">${escapeHTML(expense.category || "Other")}</span>
                </td>
                <td>${escapeHTML(formatDate(expense.date))}</td>
                <td class="amount">-${escapeHTML(formatCurrency(expense.amount))}</td>
            </tr>
        `).join("");

    } catch (error) {
        console.error("Expense error:", error);

        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-state">Could not load transactions.</td>
            </tr>`;
    }
}


// ==========================================
// 5. CATEGORY ANALYTICS
// ==========================================

const CHART_COLORS = [
    "#8b7cff", "#53a5ff", "#35d39a", "#ffae70",
    "#e878b5", "#64c9d9", "#b5a0ff"
];

async function loadCategories() {
    const canvas = document.getElementById("categoryChart");
    const emptyMessage = document.getElementById("chartEmpty");

    try {
        const data = await fetchAPI("/categories");
        const categories = data.categories || [];

        const labels = categories.map(item => item.category);
        const values = categories.map(item => item.total);

        // No data: show a message instead of an empty canvas.
        if (!labels.length) {
            if (categoryChart) {
                categoryChart.destroy();
                categoryChart = null;
            }
            canvas.hidden = true;
            emptyMessage.hidden = false;
            return;
        }

        canvas.hidden = false;
        emptyMessage.hidden = true;

        if (typeof Chart === "undefined") {
            throw new Error("Chart.js failed to load");
        }

        // Update in place when the chart already exists (no flicker / re-animation).
        if (categoryChart) {
            categoryChart.data.labels = labels;
            categoryChart.data.datasets[0].data = values;
            categoryChart.update();
            return;
        }

        categoryChart = new Chart(canvas, {
            type: "doughnut",

            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: CHART_COLORS,
                    borderWidth: 2,
                    borderColor: "#13171f",       // matches --panel
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
                            font: { size: 11 }
                        }
                    },

                    tooltip: {
                        callbacks: {
                            label: context =>
                                `${context.label}: ${formatCurrency(context.raw)}`
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


// ==========================================
// 6. BUDGETS
// ==========================================

async function loadBudgets() {
    const budgetList = document.getElementById("budgetList");

    try {
        const data = await fetchAPI("/budgets");
        const budgets = data.budgets || [];

        setText("budgetCount", budgets.length);
        setText("summaryBudgets", budgets.length);

        if (!budgets.length) {
            budgetList.innerHTML = `
                <p class="empty-state">
                    No budgets created yet. Ask the AI assistant to set a budget.
                </p>`;
            return;
        }

        budgetList.innerHTML = budgets.map(budget => {
            const spent = Number(budget.spent) || 0;
            const limit = Number(budget.monthly_limit) || 0;

            const used = budget.percentage_used != null
                ? Number(budget.percentage_used)
                : (limit > 0 ? (spent / limit) * 100 : 0);

            const percentage = Math.min(Math.max(used || 0, 0), 100);
            const exceeded = spent > limit;
            const remaining = budget.remaining != null
                ? Number(budget.remaining)
                : limit - spent;

            const state = exceeded ? "over" : (percentage >= 80 ? "warn" : "");

            return `
                <div class="budget-item">
                    <div class="budget-info">
                        <strong>${escapeHTML(budget.category)}</strong>
                        <span>${escapeHTML(formatCurrency(spent))} / ${escapeHTML(formatCurrency(limit))}</span>
                    </div>

                    <div class="progress-track">
                        <div class="progress-fill ${state}" style="width: ${percentage}%"></div>
                    </div>

                    <div class="budget-details ${exceeded ? "over" : ""}">
                        ${exceeded
                            ? `Over budget by ${escapeHTML(formatCurrency(spent - limit))}`
                            : `${escapeHTML(formatCurrency(remaining))} remaining`}
                    </div>
                </div>`;
        }).join("");

    } catch (error) {
        console.error("Budget error:", error);
        budgetList.innerHTML = `<p class="empty-state">Unable to load budgets.</p>`;
    }
}


// ==========================================
// 7. REFRESH DASHBOARD
// ==========================================

async function refreshDashboard() {
    await Promise.all([
        loadDashboard(),
        loadExpenses(),
        loadCategories(),
        loadBudgets()
    ]);
}

async function handleRefreshClick(event) {
    const button = event.currentTarget;
    button.disabled = true;

    try {
        await refreshDashboard();
    } finally {
        button.disabled = false;
    }
}


// ==========================================
// 8. CHATBOT POSITION AND SIZE
// ==========================================

function isChatOpen() {
    return chatWidget.classList.contains("open");
}

function saveChatGeometry() {
    if (!isChatOpen()) return;

    const rect = chatWidget.getBoundingClientRect();

    lastChatPosition = { left: rect.left, top: rect.top };
    lastChatSize = { width: rect.width, height: rect.height };
}

function setChatPosition(left, top) {
    chatWidget.style.left = `${left}px`;
    chatWidget.style.top = `${top}px`;
    chatWidget.style.right = "auto";
    chatWidget.style.bottom = "auto";
}

function cancelChatAnimation() {
    if (chatAnimation) {
        chatAnimation.cancel();
        chatAnimation = null;
    }
    chatWidget.classList.remove("animating");
}

/**
 * Plays a Web Animation on the chat window and then CANCELS it, so no
 * "fill: forwards" effect is left behind overriding the widget's styles.
 * Returns false if the animation was interrupted.
 */
async function playChatAnimation(keyframes, duration) {
    if (REDUCED_MOTION.matches) return true;

    const animation = chatWidget.animate(keyframes, {
        duration,
        easing: EASE,
        fill: "forwards"
    });

    chatAnimation = animation;

    try {
        await animation.finished;
    } catch (error) {
        return false;                       // cancelled by close / re-open
    }

    if (chatAnimation === animation) chatAnimation = null;
    animation.cancel();

    return true;
}

// Transform that squeezes the chat window onto the floating icon.
function transformToIcon(windowRect, iconRect) {
    const x = iconRect.left + iconRect.width / 2 - (windowRect.left + windowRect.width / 2);
    const y = iconRect.top + iconRect.height / 2 - (windowRect.top + windowRect.height / 2);

    return `translate(${x}px, ${y}px) scale(${iconRect.width / windowRect.width}, ${iconRect.height / windowRect.height})`;
}


// ==========================================
// 9. OPEN / CLOSE / MINIMIZE / RESTORE
// ==========================================

function openChat() {
    if (!chatWidget) return;

    // Minimized windows fly back out of the icon.
    if (chatWidget.classList.contains("minimized")) {
        restoreChat();
        return;
    }

    if (isChatOpen()) {
        document.getElementById("chatInput").focus();
        return;
    }

    cancelChatAnimation();

    chatWidget.classList.add("open");
    floatingChat.classList.remove("visible");

    // Measure first, THEN animate (an animation at t=0 would skew the rect).
    saveChatGeometry();

    if (!REDUCED_MOTION.matches) {
        chatWidget.animate(
            [
                { opacity: 0, transform: "translateY(10px) scale(0.98)" },
                { opacity: 1, transform: "none" }
            ],
            { duration: 180, easing: "ease-out" }
        );
    }

    document.getElementById("chatInput").focus();
}

function closeChat() {
    if (!chatWidget) return;

    cancelChatAnimation();

    chatWidget.classList.remove("open", "minimized");
    floatingChat.classList.add("visible");
}

async function minimizeChat() {
    if (!isChatOpen() || chatAnimation) return;

    saveChatGeometry();

    // The icon must be visible before it can be measured.
    floatingChat.classList.add("visible");

    const windowRect = chatWidget.getBoundingClientRect();
    const iconRect = floatingChat.getBoundingClientRect();

    chatWidget.classList.add("animating");

    const finished = await playChatAnimation(
        [
            { transform: "none", opacity: 1, borderRadius: "12px" },
            { transform: transformToIcon(windowRect, iconRect), opacity: 0.2, borderRadius: "50%" }
        ],
        400
    );

    chatWidget.classList.remove("animating");

    if (!finished) return;

    chatWidget.classList.remove("open");
    chatWidget.classList.add("minimized");   // CSS keeps it hidden
}

async function restoreChat() {
    if (chatAnimation) return;

    if (!lastChatPosition || !lastChatSize) {
        chatWidget.classList.remove("minimized");
        openChat();
        return;
    }

    const iconRect = floatingChat.getBoundingClientRect();

    const width = Math.min(lastChatSize.width, window.innerWidth - 16);
    const height = Math.min(lastChatSize.height, window.innerHeight - 16);

    const left = Math.max(8, Math.min(lastChatPosition.left, window.innerWidth - width - 8));
    const top = Math.max(8, Math.min(lastChatPosition.top, window.innerHeight - height - 8));

    chatWidget.style.width = `${width}px`;
    chatWidget.style.height = `${height}px`;
    setChatPosition(left, top);

    chatWidget.classList.remove("minimized");
    chatWidget.classList.add("open", "animating");

    const windowRect = chatWidget.getBoundingClientRect();

    floatingChat.classList.remove("visible");

    const finished = await playChatAnimation(
        [
            { transform: transformToIcon(windowRect, iconRect), opacity: 0.2, borderRadius: "50%" },
            { transform: "none", opacity: 1, borderRadius: "12px" }
        ],
        420
    );

    chatWidget.classList.remove("animating");

    if (!finished) return;

    saveChatGeometry();
    document.getElementById("chatInput").focus();
}

// The floating button opens a closed chat or restores a minimized one.
function handleFloatingClick() {
    if (chatWidget.classList.contains("minimized")) {
        restoreChat();
    } else {
        openChat();
    }
}


// ==========================================
// 10. CHAT MESSAGES
// ==========================================

function addMessage(message, sender) {
    const messages = document.getElementById("chatMessages");
    const element = document.createElement("div");

    element.className = sender === "user" ? "user-message" : "bot-message";
    element.textContent = message;               // safe text insertion

    messages.appendChild(element);
    messages.scrollTop = messages.scrollHeight;

    return element;
}

// Rasa replies can arrive as plain strings or as {text: "..."} objects.
function replyToText(reply) {
    if (typeof reply === "string") return reply;
    if (reply && typeof reply.text === "string") return reply.text;
    return "";
}

async function sendMessage(message) {
    message = String(message || "").trim();

    if (!message || chatBusy) return;

    if (!isChatOpen()) openChat();

    chatBusy = true;
    addMessage(message, "user");

    const input = document.getElementById("chatInput");
    const button = document.getElementById("sendButton");

    input.value = "";
    button.disabled = true;

    const loading = addMessage("SpendWise is thinking...", "bot");

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), CHAT_TIMEOUT_MS);

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                sender: "spendwise_web_user",
                message: message
            }),
            signal: controller.signal
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Chat request failed");
        }

        loading.remove();

        const replies = (data.responses || []).map(replyToText).filter(Boolean);

        if (replies.length) {
            replies.forEach(reply => addMessage(reply, "bot"));
        } else {
            addMessage("I received your message, but have no response to show.", "bot");
        }

        // Expenses or budgets may have changed.
        refreshDashboard();

    } catch (error) {
        loading.remove();
        console.error("Chat error:", error);

        addMessage(
            error.name === "AbortError"
                ? "SpendWise took too long to answer. Please try again."
                : "Sorry, I couldn't connect to SpendWise. Please try again.",
            "bot"
        );

    } finally {
        clearTimeout(timeout);
        chatBusy = false;
        button.disabled = false;
        input.focus();
    }
}

function sendSuggestion(message) {
    sendMessage(message);
}

function initializeChatForm() {
    document.getElementById("chatForm").addEventListener("submit", event => {
        event.preventDefault();
        sendMessage(document.getElementById("chatInput").value);
    });
}


// ==========================================
// 11. DRAG CHATBOT USING ITS HEADER
// ==========================================

function initializeChatDragging() {
    let dragging = false;
    let startX = 0, startY = 0, startLeft = 0, startTop = 0;

    chatHeader.addEventListener("pointerdown", event => {
        if (event.button !== 0) return;
        if (MOBILE_QUERY.matches) return;                 // docked on phones
        if (event.target.closest("button")) return;
        if (!isChatOpen() || chatWidget.classList.contains("animating")) return;

        event.preventDefault();

        const rect = chatWidget.getBoundingClientRect();

        dragging = true;
        startX = event.clientX;
        startY = event.clientY;
        startLeft = rect.left;
        startTop = rect.top;

        setChatPosition(rect.left, rect.top);
        document.body.classList.add("chat-interacting");

        document.addEventListener("pointermove", moveChat);
        document.addEventListener("pointerup", stopDragging);
        document.addEventListener("pointercancel", stopDragging);
    });

    function moveChat(event) {
        if (!dragging) return;

        const width = chatWidget.offsetWidth;
        const height = chatWidget.offsetHeight;

        const left = Math.max(8, Math.min(startLeft + event.clientX - startX, window.innerWidth - width - 8));
        const top = Math.max(8, Math.min(startTop + event.clientY - startY, window.innerHeight - height - 8));

        setChatPosition(left, top);
    }

    function stopDragging() {
        if (!dragging) return;

        dragging = false;
        document.body.classList.remove("chat-interacting");

        document.removeEventListener("pointermove", moveChat);
        document.removeEventListener("pointerup", stopDragging);
        document.removeEventListener("pointercancel", stopDragging);

        saveChatGeometry();
    }
}


// ==========================================
// 12. RESIZE FROM ALL FOUR CORNERS
// ==========================================

function initializeChatResizing() {
    const MIN_WIDTH = 280;
    const MIN_HEIGHT = 260;
    const MARGIN = 8;

    chatWidget.querySelectorAll(".resize-handle").forEach(handle => {
        handle.addEventListener("pointerdown", event => {
            if (event.button !== 0) return;
            if (MOBILE_QUERY.matches) return;
            if (!isChatOpen() || chatWidget.classList.contains("animating")) return;

            event.preventDefault();
            event.stopPropagation();

            const corner = handle.dataset.corner;
            const west = corner.includes("w");
            const north = corner.includes("n");

            const rect = chatWidget.getBoundingClientRect();
            const startX = event.clientX;
            const startY = event.clientY;
            const startWidth = rect.width;
            const startHeight = rect.height;
            const startLeft = rect.left;
            const startTop = rect.top;

            document.body.classList.add("chat-interacting");
            setChatPosition(startLeft, startTop);

            function resizeChat(moveEvent) {
                const dx = moveEvent.clientX - startX;
                const dy = moveEvent.clientY - startY;

                const maxWidth = window.innerWidth - MARGIN * 2;
                const maxHeight = window.innerHeight - MARGIN * 2;

                let width = west ? startWidth - dx : startWidth + dx;
                let height = north ? startHeight - dy : startHeight + dy;

                width = Math.max(Math.min(MIN_WIDTH, maxWidth), Math.min(width, maxWidth));
                height = Math.max(Math.min(MIN_HEIGHT, maxHeight), Math.min(height, maxHeight));

                let left = west ? startLeft + startWidth - width : startLeft;
                let top = north ? startTop + startHeight - height : startTop;

                left = Math.max(MARGIN, Math.min(left, window.innerWidth - width - MARGIN));
                top = Math.max(MARGIN, Math.min(top, window.innerHeight - height - MARGIN));

                chatWidget.style.width = `${width}px`;
                chatWidget.style.height = `${height}px`;
                setChatPosition(left, top);
            }

            function stopResize() {
                document.removeEventListener("pointermove", resizeChat);
                document.removeEventListener("pointerup", stopResize);
                document.removeEventListener("pointercancel", stopResize);

                document.body.classList.remove("chat-interacting");
                saveChatGeometry();
            }

            document.addEventListener("pointermove", resizeChat);
            document.addEventListener("pointerup", stopResize);
            document.addEventListener("pointercancel", stopResize);
        });
    });
}


// ==========================================
// 13. CONTROLS, KEYBOARD AND WINDOW EVENTS
// ==========================================

function initializeChatControls() {
    document.getElementById("minimizeChat").addEventListener("click", minimizeChat);
    document.getElementById("closeChat").addEventListener("click", closeChat);

    // The floating button had no click handler before: it could never reopen the chat.
    floatingChat.addEventListener("click", handleFloatingClick);

    document.querySelectorAll("[data-open-chat]").forEach(element => {
        element.addEventListener("click", openChat);
    });

    document.querySelectorAll("[data-suggestion]").forEach(element => {
        element.addEventListener("click", () => sendSuggestion(element.dataset.suggestion));
    });

    document.getElementById("refreshButton").addEventListener("click", handleRefreshClick);

    document.addEventListener("keydown", event => {
        if (event.key === "Escape" && isChatOpen() && !chatAnimation) {
            minimizeChat();
        }
    });
}

// Keep the chat window inside the screen when the browser is resized.
window.addEventListener("resize", () => {
    if (!chatWidget || !isChatOpen() || MOBILE_QUERY.matches) return;

    const rect = chatWidget.getBoundingClientRect();

    const width = Math.min(rect.width, window.innerWidth - 16);
    const height = Math.min(rect.height, window.innerHeight - 16);

    const left = Math.max(8, Math.min(rect.left, window.innerWidth - width - 8));
    const top = Math.max(8, Math.min(rect.top, window.innerHeight - height - 8));

    chatWidget.style.width = `${width}px`;
    chatWidget.style.height = `${height}px`;
    setChatPosition(left, top);

    saveChatGeometry();
});


// ==========================================
// 14. SIDEBAR ACTIVE LINK (SCROLL SPY)
// ==========================================

function initializeNavigation() {
    const links = document.querySelectorAll(".nav-item[data-section]");
    const sections = ["analytics", "transactions", "budgets"];
    let ticking = false;

    function setActive(id) {
        links.forEach(link => {
            link.classList.toggle("active", link.dataset.section === id);
        });
    }

    function update() {
        ticking = false;

        let current = "dashboard";
        const atBottom =
            window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4;

        sections.forEach(id => {
            const element = document.getElementById(id);
            if (element && element.getBoundingClientRect().top <= 140) current = id;
        });

        if (atBottom) current = "budgets";

        setActive(current);
    }

    window.addEventListener("scroll", () => {
        if (!ticking) {
            ticking = true;
            requestAnimationFrame(update);
        }
    }, { passive: true });

    links.forEach(link => {
        link.addEventListener("click", () => setActive(link.dataset.section));
    });
}


// ==========================================
// 15. INITIALIZE SPENDWISE
// ==========================================

async function initializeSpendWise() {
    chatWidget = document.getElementById("chatWidget");
    chatHeader = document.getElementById("chatHeader");
    floatingChat = document.getElementById("floatingChat");

    initializeChatForm();
    initializeChatDragging();
    initializeChatResizing();
    initializeChatControls();
    initializeNavigation();

    await refreshDashboard();
}

document.addEventListener("DOMContentLoaded", initializeSpendWise);