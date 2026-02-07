// content.js - Ultimate AI Agent v7 (Dynamic Panels)
console.log("Deriv AI Trading Tutor: Ultimate Agent Loaded.");

// Backend API Configuration
const API_BASE_URL = "http://localhost:8000";
let sessionId = null;  // For chat continuity

const state = {
    balance: "0.00",
    currentSymbol: "",
    winRate: "68%",
    positions: [],
    recentTrades: []
};

// 1. Context Scraper
function scrapeContext() {
    const balanceEl = document.querySelector('.acc-info__balance') || document.querySelector('#dt_core_account-info_acc-info');
    if (balanceEl) state.balance = balanceEl.innerText.trim();

    const symbolEl = document.querySelector('.cq-symbol-select-btn .cq-symbol-name');
    if (symbolEl) state.currentSymbol = symbolEl.innerText.trim();
    
    updateDynamicPanels();
}

// 2. Dynamic Panel Logic
function updateDynamicPanels() {
    const url = window.location.href;
    const posPanel = document.getElementById('panel-positions');
    const perfPanel = document.getElementById('panel-performance');

    // Toggle Positions Panel
    if (url.includes('/dtrader') || url.includes('/reports/positions')) {
        if (posPanel) posPanel.style.display = 'block';
    } else {
        if (posPanel) posPanel.style.display = 'none';
    }

    // Toggle Performance Panel
    if (url.includes('/reports/profit') || url.includes('/reports/statement')) {
        if (perfPanel) perfPanel.style.display = 'block';
    } else {
        if (perfPanel) perfPanel.style.display = 'none';
    }
}

// 3. Floating Bubble with Dynamic Chat Interface
function injectFloatingBubble() {
    if (document.getElementById('deriv-ai-bubble-container')) return;

    const container = document.createElement('div');
    container.id = 'deriv-ai-bubble-container';
    container.innerHTML = `
        <div id="ai-bubble-trigger">
            <span class="bubble-icon">AI</span>
            <span class="bubble-text">Smart Insights</span>
        </div>
        <div id="ai-insights-popup" style="display: none;">
            <div class="popup-header">
                <span>AI Trading Tutor</span>
                <button id="close-popup">×</button>
            </div>
            <div class="popup-scroll-area">
                <!-- 1. Always Visible: Insights Panel -->
                <div class="panel-section" id="panel-insights">
                    <h4>Smart Insights</h4>
                    <div class="stat-row"><span>Win Rate:</span> <strong>${state.winRate}</strong></div>
                    <div class="stat-row"><span>Risk Level:</span> <strong style="color: #4bb543;">Low</strong></div>
                </div>

                <!-- 2. Contextual: Current Positions (DTrader/Positions only) -->
                <div class="panel-section" id="panel-positions" style="display: none;">
                    <h4>Current Positions</h4>
                    <div class="pos-item">AUD/JPY: <span style="color: #4bb543;">+3.56 USD</span></div>
                    <div class="pos-item">Volatility 100: <span style="color: #ff444f;">-1.20 USD</span></div>
                </div>

                <!-- 3. Contextual: Recent Performance (Profit/Statement only) -->
                <div class="panel-section" id="panel-performance" style="display: none;">
                    <h4>Recent Performance</h4>
                    <div class="stat-row"><span>Total Profit:</span> <strong style="color: #4bb543;">+125.40 USD</strong></div>
                    <div class="stat-row"><span>Last 5 Trades:</span> <strong>W-W-L-W-W</strong></div>
                </div>

                <!-- 4. Chat Messages Area -->
                <div id="chat-messages">
                    <div class="message ai">
                        Hello! I've analyzed your current view. How can I help you with your strategy today?
                    </div>
                </div>
                
                <!-- 5. Interactive Lesson Block (appears in chat flow) -->
                <div class="lesson-block">
                    <strong>Recommended Lesson</strong>
                    <p>Mastering Multipliers & Risk Management</p>
                    <button class="lesson-btn">Start 2-min Lesson</button>
                </div>
            </div>

            <div class="chat-input-area">
                <input type="text" id="user-input" placeholder="Ask AI anything...">
                <button id="send-msg">Send</button>
            </div>
        </div>
    `;
    document.body.appendChild(container);

    const trigger = document.getElementById('ai-bubble-trigger');
    const popup = document.getElementById('ai-insights-popup');
    const closeBtn = document.getElementById('close-popup');

    trigger.onclick = () => {
        popup.style.display = popup.style.display === 'none' ? 'flex' : 'none';
    };

    closeBtn.onclick = (e) => {
        e.stopPropagation();
        popup.style.display = 'none';
    };

    document.getElementById('send-msg').onclick = sendMessage;
    document.getElementById('user-input').onkeypress = (e) => {
        if (e.key === 'Enter') sendMessage();
    };
}

async function sendMessage() {
    const input = document.getElementById('user-input');
    const text = input.value.trim();
    if (!text) return;

    addMessage('user', text);
    input.value = '';

    // Show typing indicator
    const typingId = 'typing-' + Date.now();
    addMessage('ai', '...', typingId);

    try {
        const response = await fetch(`${API_BASE_URL}/ai/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: 1,
                message: text,
                session_id: sessionId,
                user_context: {
                    experience_level: "beginner",
                    preferred_assets: [state.currentSymbol || "EURUSD"],
                    market_context: `Balance: ${state.balance}, Symbol: ${state.currentSymbol}`
                }
            })
        });

        const data = await response.json();
        sessionId = data.session_id;  // Save for chat continuity

        // Remove typing indicator and show response
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();

        addMessage('ai', data.response || "Sorry, I couldn't process that. Please try again.");
    } catch (error) {
        console.error('AI Chat Error:', error);
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();
        addMessage('ai', "Connection error. Make sure the backend server is running on localhost:8000");
    }
}

function addMessage(sender, text, id = null) {
    const chatMessages = document.getElementById('chat-messages');
    const msg = document.createElement('div');
    msg.className = `message ${sender}`;
    if (id) msg.id = id;
    msg.innerText = text;
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 4. In-Line Button Injection (Maintaining perfect alignment)
function injectInlineButtons() {
    // Buy Advice
    const buyButtonSelectors = ['#dt_purchase_multup_button', '.trade-container__fieldset button.btn-purchase--multiplier', 'button.btn-purchase'];
    buyButtonSelectors.forEach(selector => {
        const buyBtn = document.querySelector(selector);
        if (buyBtn && buyBtn.offsetWidth > 0 && !buyBtn.parentElement.querySelector('.ai-advice-btn.purchase-advice')) {
            const adviceBtn = document.createElement('button');
            adviceBtn.className = 'ai-advice-btn purchase-advice';
            adviceBtn.innerText = 'AI Analysis';
            adviceBtn.onclick = (e) => { e.preventDefault(); showDecisionOverlay('purchase'); };
            buyBtn.parentNode.insertBefore(adviceBtn, buyBtn.nextSibling);
        }
    });

    // Close Advice
    const closeButtons = document.querySelectorAll('button[id^="dc_contract_card_"][id$="_button"], .dc-table__cell button.dc-btn--secondary');
    closeButtons.forEach(btn => {
        if (btn.innerText.toLowerCase() !== 'close') return;
        if (btn.parentElement.classList.contains('ai-button-container')) return;
        const container = document.createElement('div');
        container.className = 'ai-button-container';
        btn.parentNode.insertBefore(container, btn);
        container.appendChild(btn);
        const adviceBtn = document.createElement('button');
        adviceBtn.className = 'ai-advice-btn close-advice';
        adviceBtn.innerText = 'AI';
        adviceBtn.onclick = (e) => { e.preventDefault(); showDecisionOverlay('close'); };
        container.appendChild(adviceBtn);
    });
}

// 5. Decision Overlay
async function showDecisionOverlay(type) {
    let overlay = document.getElementById('ai-decision-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'ai-decision-overlay';
        document.body.appendChild(overlay);
    }

    // Show loading state first
    overlay.innerHTML = `
        <div class="overlay-content">
            <div class="overlay-header"><span>AI Trade Assistant</span><button onclick="document.getElementById('ai-decision-overlay').style.display='none'">×</button></div>
            <div class="overlay-body">
                <div class="advice-status">Analyzing...</div>
                <p>Getting AI insights for ${state.currentSymbol || 'your trade'}...</p>
            </div>
        </div>
    `;
    overlay.style.display = 'flex';

    try {
        // Call the backend for real analysis
        const response = await fetch(`${API_BASE_URL}/ai/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: 1,
                message: type === 'purchase'
                    ? `Should I buy ${state.currentSymbol || 'this asset'} now? My balance is ${state.balance}. Give me a short analysis with buy/sell recommendation.`
                    : `Should I close my ${state.currentSymbol || 'current'} position now? My balance is ${state.balance}. Give me a short analysis.`,
                session_id: sessionId,
                user_context: {
                    experience_level: "beginner",
                    preferred_assets: [state.currentSymbol || "EURUSD"]
                }
            })
        });

        const data = await response.json();
        sessionId = data.session_id;

        // Parse AI response to determine if safe or risky
        const aiResponse = data.response || "Unable to analyze. Please try again.";
        const isPositive = aiResponse.toLowerCase().includes('safe') ||
                          aiResponse.toLowerCase().includes('favorable') ||
                          aiResponse.toLowerCase().includes('good') ||
                          !aiResponse.toLowerCase().includes('risk') ||
                          !aiResponse.toLowerCase().includes('caution');

        overlay.innerHTML = `
            <div class="overlay-content">
                <div class="overlay-header"><span>AI Trade Assistant</span><button onclick="document.getElementById('ai-decision-overlay').style.display='none'">×</button></div>
                <div class="overlay-body">
                    <div class="advice-status ${isPositive ? 'good' : 'warning'}">${isPositive ? 'Analysis Complete' : 'Review Recommended'}</div>
                    <p>${aiResponse}</p>
                    <div class="advice-details"><div><strong>Balance:</strong> ${state.balance}</div><div><strong>Symbol:</strong> ${state.currentSymbol || 'N/A'}</div></div>
                </div>
                <div class="overlay-footer">
                    <button onclick="document.getElementById('ai-decision-overlay').style.display='none'">Got it</button>
                    <button id="ask-ai-more-btn" style="background: #242828; margin-left: 10px;">Ask AI More</button>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('AI Analysis Error:', error);
        overlay.innerHTML = `
            <div class="overlay-content">
                <div class="overlay-header"><span>AI Trade Assistant</span><button onclick="document.getElementById('ai-decision-overlay').style.display='none'">×</button></div>
                <div class="overlay-body">
                    <div class="advice-status warning">Connection Error</div>
                    <p>Could not connect to AI backend. Make sure server is running on localhost:8000</p>
                    <div class="advice-details"><div><strong>Balance:</strong> ${state.balance}</div></div>
                </div>
                <div class="overlay-footer">
                    <button onclick="document.getElementById('ai-decision-overlay').style.display='none'">Close</button>
                </div>
            </div>
        `;
    }

    // Re-attach event listener for "Ask AI More" button
    const askMoreBtn = document.getElementById('ask-ai-more-btn');
    if (askMoreBtn) {
        askMoreBtn.onclick = () => {
            overlay.style.display = 'none';
            const trigger = document.getElementById('ai-bubble-trigger');
            if (document.getElementById('ai-insights-popup').style.display === 'none') trigger.click();
        };
    }
}

// Init
function init() {
    injectFloatingBubble();
    setInterval(() => {
        scrapeContext();
        injectInlineButtons();
    }, 2000);
}
setTimeout(init, 3000);
