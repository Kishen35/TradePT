// content.js - Ultimate AI Agent v7 (Dynamic Panels + Background Data Persistence)
console.log("Deriv AI Trading Tutor: Ultimate Agent Loaded.");

const state = {
  balance: "0.00",
  currentSymbol: "",
  stakeAmount: "",
  winRate: "68%",
  positions: [],
  recentTrades: [],
  lastTradeDataFetch: 0, // Timestamp of last trade data fetch
  backgroundDataValid: false,
  tradeType: "",
  marketType: "",
  trendType: "unknown",
  parameters: {},
};

class Chatbox {
  // 3. Floating Bubble with Dynamic Chat Interface
  injectFloatingBubble() {
    if (document.getElementById("deriv-ai-bubble-container")) return;

    const container = document.createElement("div");
    container.id = "deriv-ai-bubble-container";
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
            </div>

            <div class="chat-input-area">
                <input type="text" id="user-input" placeholder="Ask AI anything...">
                <button id="send-msg">Send</button>
            </div>
        </div>
    `;
    document.body.appendChild(container);

    const trigger = document.getElementById("ai-bubble-trigger");
    const popup = document.getElementById("ai-insights-popup");
    const closeBtn = document.getElementById("close-popup");

    trigger.onclick = () => {
      popup.style.display = popup.style.display === "none" ? "flex" : "none";
    };

    closeBtn.onclick = (e) => {
      e.stopPropagation();
      popup.style.display = "none";
    };

    document.getElementById("send-msg").onclick = this.sendMessage.bind(this);
    document.getElementById("user-input").addEventListener("keydown", (e) => {
      if (e.key === "Enter") this.sendMessage();
    });
  }

  async sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (!text) return;

    this.addMessage("user", text);
    input.value = "";

    // Show typing indicator
    this.addMessage("ai", "🤔 Analyzing your trading data...");

    try {
      // Initialize AI integration if not already done
      if (!window.aiIntegration) {
        window.aiIntegration = new AIIntegration();
      }

      // Categorize message for better context
      const messageType = window.aiIntegration.categorizeMessage(text);

      // Get AI response with full trading context
      const aiResponse = await window.aiIntegration.sendMessageToAI(
        text,
        messageType,
      );

      // Remove typing indicator and add real response
      const chatMessages = document.getElementById("chat-messages");
      const lastMessage = chatMessages.lastElementChild;
      if (lastMessage && lastMessage.textContent.includes("Analyzing")) {
        lastMessage.remove();
      }

      this.addMessage("ai", aiResponse);
    } catch (error) {
      console.error("AI chat error:", error);
      // Remove typing indicator
      const chatMessages = document.getElementById("chat-messages");
      const lastMessage = chatMessages.lastElementChild;
      if (lastMessage && lastMessage.textContent.includes("Analyzing")) {
        lastMessage.remove();
      }

      // Error message (Fallback removed)
      this.addMessage(
        "ai",
        "I apologize, but I am unable to connect to the AI service at the moment. Please check your connection or configuration.",
      );
    }
  }

  formatMessage(text) {
    if (!text) return "";

    // 1. Escape HTML
    let formatted = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");

    // 2. Bold (**text**)
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    // 3. Italics (*text*)
    formatted = formatted.replace(/\*(.*?)\*/g, "<em>$1</em>");

    // 4. Newlines
    formatted = formatted.replace(/\n/g, "<br>");

    return formatted;
  }

  addMessage(sender, text) {
    const chatMessages = document.getElementById("chat-messages");
    const msg = document.createElement("div");
    msg.className = `message ${sender}`;
    msg.innerHTML = this.formatMessage(text); // Use innerHTML with formatted text
    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // 4. In-Line Button Injection (Maintaining perfect alignment)
  injectInlineButtons() {
    // Buy Advice
    const buyButtonSelectors = [
      "#dt_purchase_multup_button",
      ".trade-container__fieldset button.btn-purchase--multiplier",
      "button.btn-purchase",
    ];
    buyButtonSelectors.forEach((selector) => {
      const buyBtn = document.querySelector(selector);
      if (
        buyBtn &&
        buyBtn.offsetWidth > 0 &&
        !buyBtn.parentElement.querySelector(".ai-advice-btn.purchase-advice")
      ) {
        const adviceBtn = document.createElement("button");
        adviceBtn.className = "ai-advice-btn purchase-advice";
        adviceBtn.innerText = "AI Analysis";
        adviceBtn.onclick = (e) => {
          e.preventDefault();
          this.showDecisionOverlay("purchase");
        };
        buyBtn.parentNode.insertBefore(adviceBtn, buyBtn.nextSibling);
      }
    });

    // Close/Sell Advice - Enhanced to detect both Close and Sell buttons
    // Method 1: Find buttons by text content (Close)
    const closeButtons = document.querySelectorAll(
      'button[id^="dc_contract_card_"][id$="_button"], .dc-table__cell button.dc-btn--secondary',
    );
    closeButtons.forEach((btn) => {
      if (btn.innerText.toLowerCase() !== "close") return;
      if (btn.parentElement.classList.contains("ai-button-container")) return;
      const container = document.createElement("div");
      container.className = "ai-button-container";
      btn.parentNode.insertBefore(container, btn);
      container.appendChild(btn);
      const adviceBtn = document.createElement("button");
      adviceBtn.className = "ai-advice-btn close-advice";
      adviceBtn.innerText = "AI";
      adviceBtn.onclick = (e) => {
        e.preventDefault();
        this.showDecisionOverlay("close");
      };
      container.appendChild(adviceBtn);
    });

    // Method 2: Find Sell buttons using the specific selector pattern
    const sellButtons = document.querySelectorAll(
      '[id^="dc_contract_card_"] > div > div > button',
    );
    sellButtons.forEach((btn) => {
      // Check if it's a Sell button by text content
      if (btn.innerText.toLowerCase() !== "sell") return;
      if (btn.parentElement.classList.contains("ai-button-container")) return;

      console.log("Found Sell button:", btn.id, btn.innerText);

      const container = document.createElement("div");
      container.className = "ai-button-container";
      btn.parentNode.insertBefore(container, btn);
      container.appendChild(btn);
      const adviceBtn = document.createElement("button");
      adviceBtn.className = "ai-advice-btn close-advice";
      adviceBtn.innerText = "AI";
      adviceBtn.onclick = (e) => {
        e.preventDefault();
        this.showDecisionOverlay("close");
      };
      container.appendChild(adviceBtn);
    });

    // Method 3: Generic approach for any Close/Sell buttons we might have missed
    const allButtons = document.querySelectorAll("button");
    allButtons.forEach((btn) => {
      const buttonText = btn.innerText.toLowerCase();
      if (
        (buttonText === "close" || buttonText === "sell") &&
        btn.offsetWidth > 0 &&
        !btn.parentElement.classList.contains("ai-button-container") &&
        !btn.classList.contains("ai-advice-btn")
      ) {
        console.log(
          "Found additional Close/Sell button:",
          btn.className,
          btn.innerText,
        );

        const container = document.createElement("div");
        container.className = "ai-button-container";
        btn.parentNode.insertBefore(container, btn);
        container.appendChild(btn);
        const adviceBtn = document.createElement("button");
        adviceBtn.className = "ai-advice-btn close-advice";
        adviceBtn.innerText = "AI";
        adviceBtn.onclick = (e) => {
          e.preventDefault();
          this.showDecisionOverlay("close");
        };
        container.appendChild(adviceBtn);
      }
    });
  }

  // 5. Decision Overlay
  async showDecisionOverlay(type) {
    let overlay = document.getElementById("ai-decision-overlay");
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.id = "ai-decision-overlay";
      document.body.appendChild(overlay);
    }

    // Show loading state first
    overlay.innerHTML = `
        <div class="overlay-content">
            <div class="overlay-header"><span>AI Trade Assistant</span><button onclick="document.getElementById('ai-decision-overlay').style.display='none'">×</button></div>
            <div class="overlay-body">
                <div class="advice-status loading">🤔 Analyzing your trade...</div>
                <p>Checking market conditions and your trading context...</p>
                <div class="advice-details">
                    <div><strong>Balance:</strong> ${state.balance}</div>
                    <div><strong>Symbol:</strong> ${state.currentSymbol || "Not selected"}</div>
                    <div><strong>Win Rate:</strong> ${state.winRate}</div>
                </div>
            </div>
            <div class="overlay-footer">
                <button onclick="document.getElementById('ai-decision-overlay').style.display='none'">Cancel</button>
            </div>
        </div>
    `;
    overlay.style.display = "flex";

    try {
      // Refresh scraped data before analysis
      scraper.scrapeContext();

      if (!window.aiIntegration) {
        window.aiIntegration = new AIIntegration();
      }

      const context = {
        symbol: state.currentSymbol,
        balance: state.balance,
        stake: state.stakeAmount,
        trade_type: state.tradeType || null,
        market_type: state.marketType || state.currentSymbol,
        trend_type: state.trendType || "unknown",
        parameters: Object.keys(state.parameters || {}).length > 0 ? state.parameters : null,
      };

      if (type === "close" && state.positions.length > 0) {
        const pos = state.positions[0];
        const pnlStr = typeof pos.pnl === "string" ? pos.pnl.replace(/[^0-9.-]/g, "") : pos.pnl;
        context.pnl = parseFloat(pnlStr) || 0;
        context.symbol = pos.symbol || state.currentSymbol;
        context.entry_price = null;
        context.current_price = null;
        context.duration_minutes = null;
      }

      const aiResult = await window.aiIntegration.callEducationAnalyze(
        type,
        context);
      const aiText = aiResult.text;
      const recommendedModuleId = aiResult.recommended_module_id;

      // Determine advice status based on AI response
      const adviceStatus = this.determineAdviceStatus(aiText, type);

      // Update overlay with AI analysis
      overlay.innerHTML = `
            <div class="overlay-content">
                <div class="overlay-header"><span>AI Trade Assistant</span><button onclick="document.getElementById('ai-decision-overlay').style.display='none'">×</button></div>
                <div class="overlay-body">
                    <div class="advice-status ${adviceStatus.class}">${adviceStatus.icon} ${adviceStatus.text}</div>
                    <p class="ai-analysis">${this.formatMessage(aiText)}</p>
                    <div class="advice-details">
                        <div><strong>Balance:</strong> ${state.balance}</div>
                        <div><strong>Symbol:</strong> ${state.currentSymbol || "Not selected"}</div>
                        <div><strong>Win Rate:</strong> ${state.winRate}</div>
                        ${state.positions.length > 0 ? `<div><strong>Open Positions:</strong> ${state.positions.length}</div>` : ""}
                    </div>
                </div>
                <div class="overlay-footer">
                    <button onclick="document.getElementById('ai-decision-overlay').style.display='none'">Got it</button>
                    <button id="learn-more-btn" style="background: #242828; margin-left: 10px;">Learn more</button>
                </div>
            </div>
        `;

      // Log analysis to chatbot history
      this.addMessage("ai", `📊 **AI ${type === "purchase" ? "Buy" : "Close"} Analysis** (${state.currentSymbol || "Unknown"}):\n\n${aiText}`);

      // Set up "Learn more" button — navigate to specific module quiz
      document.getElementById("learn-more-btn").onclick = () => {
        overlay.style.display = "none";
        this.navigateToEducation(recommendedModuleId);
      };
    } catch (error) {
      console.error("AI analysis failed:", error);

      // Error state (Fallback removed)
      overlay.innerHTML = `
            <div class="overlay-content">
                <div class="overlay-header"><span>AI Trade Assistant</span><button onclick="document.getElementById('ai-decision-overlay').style.display='none'">×</button></div>
                <div class="overlay-body">
                    <div class="advice-status warning">⚠️ Service Unavailable</div>
                    <p>Unable to generate AI analysis at this time. Please check your configuration.</p>
                </div>
                <div class="overlay-footer">
                    <button onclick="document.getElementById('ai-decision-overlay').style.display='none'">Close</button>
                </div>
            </div>
        `;
    }
  }

  // Helper function to determine advice status from AI response
  determineAdviceStatus(aiResponse, type) {
    const response = aiResponse.toLowerCase();

    // Look for positive/negative indicators in AI response
    const positiveWords = [
      "good",
      "safe",
      "recommend",
      "favorable",
      "positive",
      "go ahead",
      "yes",
    ];
    const negativeWords = [
      "avoid",
      "risky",
      "dangerous",
      "not recommended",
      "wait",
      "no",
      "caution",
    ];
    const cautionWords = [
      "careful",
      "consider",
      "monitor",
      "watch",
      "moderate",
    ];

    const hasPositive = positiveWords.some((word) => response.includes(word));
    const hasNegative = negativeWords.some((word) => response.includes(word));
    const hasCaution = cautionWords.some((word) => response.includes(word));

    if (hasNegative) {
      return { class: "warning", icon: "⚠️", text: "Exercise Caution" };
    } else if (hasCaution) {
      return { class: "neutral", icon: "🤔", text: "Consider Carefully" };
    } else if (hasPositive) {
      return {
        class: "good",
        icon: "✅",
        text: type === "purchase" ? "Good to Trade" : "Safe to Close",
      };
    } else {
      return { class: "neutral", icon: "💡", text: "Review Analysis" };
    }
  }

  // 6. Navigate to education dashboard (with sign-in check)
  navigateToEducation(moduleId) {
    // Use chrome.storage.local (works across all extension contexts/domains)
    chrome.storage.local.get("user_session", (data) => {
      const session = data.user_session;

      if (session && session.id) {
        // User is signed in — open education dashboard with specific module quiz
        const encoded = btoa(encodeURIComponent(JSON.stringify(session)));
        let url = `http://localhost:8000/static/trading_edu.html?session=${encoded}`;
        if (moduleId) url += `&module=${moduleId}`;
        window.open(url, "_blank");
      } else {
        // Not signed in — show sign-in prompt overlay
        let signInOverlay = document.getElementById("ai-signin-overlay");
        if (!signInOverlay) {
          signInOverlay = document.createElement("div");
          signInOverlay.id = "ai-signin-overlay";
          document.body.appendChild(signInOverlay);
        }
        signInOverlay.innerHTML = `
          <div class="overlay-content">
            <div class="overlay-header"><span>Sign In Required</span><button onclick="document.getElementById('ai-signin-overlay').style.display='none'">×</button></div>
            <div class="overlay-body" style="text-align:center;">
              <div style="font-size:36px; margin-bottom:12px;">🔐</div>
              <p>Sign in to access your personalized learning dashboard and track your progress.</p>
            </div>
            <div class="overlay-footer" style="justify-content:center; gap:10px;">
              <button onclick="document.getElementById('ai-signin-overlay').style.display='none'" style="background:#242828;">Cancel</button>
              <button id="ai-signin-btn" style="background:#ff444f;">Sign In</button>
            </div>
          </div>
        `;
        signInOverlay.style.display = "flex";
        document.getElementById("ai-signin-btn").onclick = () => {
          signInOverlay.style.display = "none";
          // Open login page in extension popup
          chrome.runtime.sendMessage({ action: "openPopup" });
        };
      }
    });
  }

  // 7. Open chat with contextual prefilled message
  openChatWithPrefill(actionType) {
    const trigger = document.getElementById("ai-bubble-trigger");
    const popup = document.getElementById("ai-insights-popup");
    const input = document.getElementById("user-input");

    // Open chat if closed
    if (popup.style.display === "none") trigger.click();

    // Generate contextual message based on action type and current data
    let prefilledMessage = "";
    if (actionType === "close" && state.currentSymbol) {
      prefilledMessage = `Should I close my current position?`;
    } else if (actionType === "purchase" && state.currentSymbol) {
      prefilledMessage = `Is now a good time to buy ${state.currentSymbol}?`;
    } else {
      prefilledMessage = `What's your advice on my current trading situation?`;
    }

    // Prefill the input and focus
    input.value = prefilledMessage;
    input.focus();
  }
}

class Scraper {
  constructor() {
    this.updater = new Updater();
  }

  // 1. Enhanced Context Scraper with Live Data (using innerHTML)
  scrapeContext() {
    // Account Balance - Multiple selectors for reliability
    const balanceEl =
      document.querySelector("#dt_core_account-info_acc-info") ||
      document.querySelector(".acc-info__balance");
    if (balanceEl) {
      // Use innerHTML to capture nested elements, then extract text
      const balanceHTML = balanceEl.innerHTML;
      state.balance =
        balanceEl.innerText.trim() || extractTextFromHTML(balanceHTML);
    }

    // Current Trading Symbol - Enhanced selectors with innerHTML
    const symbolEl =
      document.querySelector(".cq-symbol-select-btn .cq-symbol") ||
      document.querySelector(".cq-symbol-info .cq-symbol") ||
      document.querySelector('[data-testid="dt_symbol_info_name"]') ||
      document.querySelector(".cq-symbol-select-btn .cq-symbol-name");
    if (symbolEl) {
      const symbolHTML = symbolEl.innerHTML;
      state.currentSymbol =
        extractTextFromHTML(symbolHTML) || symbolEl.innerText.trim();
    }

    // Stake Amount
    const stakeInput = document.querySelector("#dt_amount_input");
    if (stakeInput) {
      state.stakeAmount = stakeInput.value;
    }

    // Trade Type (e.g. Accumulators, Multipliers)
    const tradeTypeEl =
      document.querySelector('[class*="learn-about"] .dc-text') ||
      document.querySelector(".trade-type-selector .dc-text") ||
      document.querySelector('[data-testid*="trade-type"]') ||
      document.querySelector(".dc-dropdown__display");
    if (tradeTypeEl) {
      state.tradeType = tradeTypeEl.innerText?.trim() || "";
    }

    // Market type = current symbol (e.g. Volatility 100 Index)
    state.marketType = state.currentSymbol || "";

    // Trend from price change (e.g. +0.641 or -0.62)
    const priceChangeEl =
      document.querySelector('[class*="price-change"]') ||
      document.querySelector('[class*="change--"]') ||
      document.querySelector(".cq-chart-price__value--profit") ||
      document.querySelector(".cq-chart-price__value--loss");
    if (priceChangeEl) {
      const changeText = priceChangeEl.innerText || "";
      state.trendType = changeText.includes("-") ? "down" : changeText.includes("+") ? "up" : "sideways";
    }

    // Parameters (Accumulators: growth rate, take profit)
    const growthRateEl = document.querySelector('[class*="growth-rate"] .dc-dropdown__display');
    const takeProfitEl =
      document.querySelector("#dc_take_profit_input") ||
      document.querySelector('[class*="take-profit"] input');
    state.parameters = {};
    if (growthRateEl) state.parameters.growth_rate = growthRateEl.innerText?.trim();
    if (takeProfitEl?.value) state.parameters.take_profit = takeProfitEl.value;

    // Scrape Live Positions
    this.scrapeLivePositions();

    // Scrape Recent Trades (for performance panel)
    this.scrapeRecentTrades();

    this.updater.updateDynamicPanels();
  }

  // 1a. Live Position Scraper (using correct Deriv selectors)
  scrapeLivePositions() {
    state.positions = []; // Reset positions array

    // Use the specific selector for position symbols
    const symbolElements = document.querySelectorAll(
      "#dc-contract_card_underlying_label > span",
    );

    console.log("Found symbol elements:", symbolElements.length);

    if (symbolElements.length === 0) {
      console.log(
        "No positions found with #dc-contract_card_underlying_label > span selector",
      );
      // Try alternative approaches
      const contractCards = document.querySelectorAll(".dc-contract-card");
      console.log("Found contract cards as fallback:", contractCards.length);
    }

    symbolElements.forEach((symbolEl, index) => {
      try {
        // Get the symbol from the specific selector
        const symbol =
          extractTextFromHTML(symbolEl.innerHTML) || symbolEl.innerText.trim();

        // Find the parent contract card to get P&L and other data
        const contractCard = symbolEl.closest(".dc-contract-card");

        if (contractCard) {
          // Look for P&L using the correct profit/loss selectors
          // Try profit selector first
          let pnlEl = contractCard.querySelector(
            ".dc-contract-card-item__total-profit-loss .dc-contract-card-item__body--profit > span",
          );
          let isProfit = true;

          // If no profit found, try loss selector
          if (!pnlEl) {
            pnlEl = contractCard.querySelector(
              ".dc-contract-card-item__total-profit-loss .dc-contract-card-item__body--loss > span",
            );
            isProfit = false;
          }

          // Fallback to generic selectors if specific ones don't work
          if (!pnlEl) {
            pnlEl =
              contractCard.querySelector(".dc-contract-card__profit-loss") ||
              contractCard.querySelector('[class*="profit"]') ||
              contractCard.querySelector('[class*="pnl"]');
          }

          const typeEl = contractCard.querySelector(".dc-contract-card__type");

          console.log(`Position ${index}:`, {
            symbol: symbol,
            pnlHTML: pnlEl ? pnlEl.innerHTML : "not found",
            isProfit: isProfit,
            typeHTML: typeEl ? typeEl.innerHTML : "not found",
          });

          if (symbol && pnlEl) {
            const pnlText =
              extractTextFromHTML(pnlEl.innerHTML) || pnlEl.innerText.trim();

            const position = {
              symbol: symbol,
              pnl: pnlText,
              type: typeEl
                ? extractTextFromHTML(typeEl.innerHTML) ||
                typeEl.innerText.trim()
                : "Unknown",
              isProfit: isProfit,
            };
            state.positions.push(position);
            console.log("Added position:", position);
          }
        } else {
          console.log(`No parent contract card found for symbol: ${symbol}`);
        }
      } catch (error) {
        console.log("Error scraping position:", error);
      }
    });

    console.log("Total positions found:", state.positions.length);

    // Update the positions panel with live data
    this.updater.updatePositionsPanel();
  }

  // 1d. Recent Trades Scraper (for profit page only)
  scrapeRecentTrades() {
    const url = window.location.href;

    // Only scrape on profit page (not statement page - that's just trade history without P&L)
    if (!url.includes("/reports/profit")) {
      return;
    }

    console.log("Scraping recent trades on profit page...");

    // Look for trade rows - they have IDs like dt_reports_contract_305945452408
    const tradeRows = document.querySelectorAll('[id^="dt_reports_contract_"]');

    console.log("Found trade rows:", tradeRows.length);

    // Get last 5 trades (or fewer if less available)
    const last5Trades = Array.from(tradeRows).slice(0, 5);

    // Reset trades array only if we found new data
    if (last5Trades.length > 0) {
      state.recentTrades = [];
    }

    last5Trades.forEach((row, index) => {
      try {
        // Profit page selectors only
        const pnlEl = row.querySelector(".table__cell.profit_loss > span");
        const isProfit =
          row.querySelector(".table__cell.profit_loss .amount--profit") !==
          null;

        console.log(`Trade ${index}:`, {
          pnlHTML: pnlEl ? pnlEl.innerHTML : "not found",
          isProfit: isProfit,
          rowId: row.id,
        });

        if (pnlEl) {
          const pnlText =
            extractTextFromHTML(pnlEl.innerHTML) || pnlEl.innerText.trim();

          const trade = {
            pnl: pnlText,
            isProfit: isProfit,
            result: isProfit ? "W" : "L", // W for Win, L for Loss
          };

          state.recentTrades.push(trade);
          console.log("Added trade:", trade);
        }
      } catch (error) {
        console.log("Error scraping trade row:", error);
      }
    });

    console.log("Total trades found:", state.recentTrades.length);

    // Update timestamp and save to persistence if we got new data
    if (state.recentTrades.length > 0) {
      state.lastTradeDataFetch = Date.now();
      state.backgroundDataValid = true;
      this.updater.saveDataToPersistence();
    }

    // Update the performance panel
    this.updater.updatePerformancePanel();
  }
}

class Updater {
  // 0. Background Data Persistence System
  loadPersistedData() {
    try {
      const savedData = localStorage.getItem("deriv-ai-tutor-data");
      if (savedData) {
        const parsed = JSON.parse(savedData);
        // Only load trade data if it's less than 5 minutes old
        const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;

        if (
          parsed.lastTradeDataFetch &&
          parsed.lastTradeDataFetch > fiveMinutesAgo
        ) {
          state.recentTrades = parsed.recentTrades || [];
          state.winRate = parsed.winRate || "68%";
          state.lastTradeDataFetch = parsed.lastTradeDataFetch;
          state.backgroundDataValid = true;
          console.log("Loaded persisted trade data:", {
            trades: state.recentTrades.length,
            winRate: state.winRate,
            age:
              Math.round((Date.now() - state.lastTradeDataFetch) / 1000) +
              "s ago",
          });
        }
      }
    } catch (error) {
      console.log("Error loading persisted data:", error);
    }
  }

  saveDataToPersistence() {
    try {
      const dataToSave = {
        recentTrades: state.recentTrades,
        winRate: state.winRate,
        lastTradeDataFetch: state.lastTradeDataFetch,
      };
      localStorage.setItem("deriv-ai-tutor-data", JSON.stringify(dataToSave));
      console.log("Saved data to persistence:", {
        trades: state.recentTrades.length,
        winRate: state.winRate,
      });
    } catch (error) {
      console.log("Error saving data to persistence:", error);
    }
  }

  // 1e. Update Performance Panel with Live Data
  updatePerformancePanel() {
    const perfContainer = document.querySelector("#panel-performance");
    if (!perfContainer) return;

    // Calculate total profit from recent trades
    let totalProfit = 0;
    state.recentTrades.forEach((trade) => {
      const amount = parseFloat(trade.pnl.replace(/[^\d.-]/g, ""));
      if (!isNaN(amount)) {
        totalProfit += trade.isProfit ? Math.abs(amount) : -Math.abs(amount);
      }
    });

    // Generate W-L pattern from recent trades
    const tradePattern =
      state.recentTrades.map((trade) => trade.result).join("-") || "No data";

    // Update the performance panel content
    const totalProfitEl = perfContainer.querySelector(
      ".stat-row:first-of-type strong",
    );
    const last5TradesEl = perfContainer.querySelector(
      ".stat-row:last-of-type strong",
    );

    if (totalProfitEl && state.recentTrades.length > 0) {
      const profitColor = totalProfit >= 0 ? "#4bb543" : "#ff444f";
      const profitSign = totalProfit >= 0 ? "+" : "";
      totalProfitEl.innerHTML = `<span style="color: ${profitColor};">${profitSign}${totalProfit.toFixed(2)} USD</span>`;
    }

    if (last5TradesEl && state.recentTrades.length > 0) {
      last5TradesEl.innerText = tradePattern;
    }

    // Update win rate in Smart Insights panel
    this.updateSmartInsights();

    console.log("Updated performance panel:", {
      totalProfit: totalProfit.toFixed(2),
      tradePattern: tradePattern,
    });
  }

  // 1f. Update Smart Insights Panel with Dynamic Win Rate
  async updateSmartInsights() {
    const insightsContainer = document.querySelector("#panel-insights");
    if (!insightsContainer) return;

    // Calculate win rate from recent trades
    let calculatedWinRate = "68%"; // Default fallback

    if (state.recentTrades.length > 0) {
      const wins = state.recentTrades.filter((trade) => trade.isProfit).length;
      const totalTrades = state.recentTrades.length;
      const winRatePercent = Math.round((wins / totalTrades) * 100);
      calculatedWinRate = `${winRatePercent}%`;

      console.log("Calculated win rate:", {
        wins: wins,
        totalTrades: totalTrades,
        winRate: calculatedWinRate,
      });
    }

    // Update state
    state.winRate = calculatedWinRate;

    // Update the win rate in the insights panel
    const winRateEl = insightsContainer.querySelector(
      ".stat-row:first-of-type strong",
    );
    if (winRateEl) {
      // Color code the win rate
      const winRateNum = parseInt(calculatedWinRate);
      let winRateColor = "#4bb543"; // Green for good win rate
      if (winRateNum < 50) {
        winRateColor = "#ff4757"; // Red for poor win rate
      } else if (winRateNum < 65) {
        winRateColor = "#ffa502"; // Orange for average win rate
      }

      winRateEl.textContent = calculatedWinRate;
      winRateEl.style.color = winRateColor;
    }

    // Try to get AI insights if available
    try {
      if (!window.aiIntegration) {
        window.aiIntegration = new AIIntegration();
      }

      const insights = await window.aiIntegration.getTradingInsights();

      if (insights && insights.insights.length > 0) {
        // Update insights panel with AI-generated insights
        this.updateInsightsPanelWithAI(insights);
      }
    } catch (error) {
      console.log("Could not fetch AI insights, using fallback:", error);
      // Continue with basic insights
    }
  }

  // Update insights panel with AI-generated insights
  updateInsightsPanelWithAI(insights) {
    const insightsContainer = document.querySelector("#panel-insights");
    if (!insightsContainer) return;

    // Find or create insights list
    let insightsList = insightsContainer.querySelector(".ai-insights-list");
    if (!insightsList) {
      insightsList = document.createElement("div");
      insightsList.className = "ai-insights-list";
      insightsContainer.appendChild(insightsList);
    }

    // Clear existing insights
    insightsList.innerHTML = "";

    // Add top 3 insights
    const topInsights = insights.insights.slice(0, 3);
    topInsights.forEach((insight) => {
      const insightEl = document.createElement("div");
      insightEl.className = `insight-item ${insight.priority}`;

      const icon =
        insight.type === "strength"
          ? "✅"
          : insight.type === "weakness"
            ? "⚠️"
            : "💡";

      insightEl.innerHTML = `
            <span class="insight-icon">${icon}</span>
            <span class="insight-text">${insight.message}</span>
        `;

      insightsList.appendChild(insightEl);
    });

    // Add lesson suggestion if available
    if (insights.suggested_lesson) {
      const lessonEl = document.createElement("div");
      lessonEl.className = "suggested-lesson";
      lessonEl.innerHTML = `
            <strong>📚 Suggested Lesson:</strong>
            <span>${insights.suggested_lesson}</span>
        `;
      insightsList.appendChild(lessonEl);
    }
  }

  // 1c. Update Positions Panel with Live Data
  updatePositionsPanel() {
    const positionsContainer = document.querySelector("#panel-positions");
    if (!positionsContainer) return;

    // Find the content area (skip the h4 header)
    const existingItems = positionsContainer.querySelectorAll(".pos-item");
    existingItems.forEach((item) => item.remove());

    if (state.positions.length === 0) {
      // Show placeholder if no positions found
      const placeholder = document.createElement("div");
      placeholder.className = "pos-item";
      placeholder.innerHTML =
        '<span style="color: #999;">No open positions detected</span>';
      positionsContainer.appendChild(placeholder);
      return;
    }

    // Add live positions
    state.positions.forEach((position) => {
      const posItem = document.createElement("div");
      posItem.className = "pos-item";

      // Use the isProfit flag we set during scraping for accurate color coding
      const pnlColor = position.isProfit ? "#4bb543" : "#ff444f";

      posItem.innerHTML = `${position.symbol}: <span style="color: ${pnlColor};">${position.pnl}</span>`;
      positionsContainer.appendChild(posItem);
    });
  }

  // 2. Dynamic Panel Logic
  updateDynamicPanels() {
    const url = window.location.href;
    const posPanel = document.getElementById("panel-positions");
    const perfPanel = document.getElementById("panel-performance");

    // Hide Positions Panel completely - no longer needed
    if (posPanel) posPanel.style.display = "none";

    // Show Performance Panel persistently when we have trade data (from background persistence)
    if (perfPanel) {
      if (state.backgroundDataValid && state.recentTrades.length > 0) {
        perfPanel.style.display = "block";
        // Update the panel with current data
        this.updatePerformancePanel();
      } else {
        perfPanel.style.display = "none";
      }
    }
  }
}

const extractTextFromHTML = (html) => {
  if (!html) return "";
  // Create a temporary div to parse HTML and extract text
  const tempDiv = document.createElement("div");
  tempDiv.innerHTML = html;
  return tempDiv.innerText.trim();
};

const backgroundDataFetcher = (scraper, updater) => {
  const url = window.location.href;

  // Only fetch from profit page (not statement page)
  if (url.includes("/reports/profit")) {
    const timeSinceLastFetch = Date.now() - state.lastTradeDataFetch;
    const oneMinute = 60 * 1000;

    // Only fetch if it's been more than 1 minute since last fetch
    if (timeSinceLastFetch > oneMinute) {
      console.log("Background fetching trade data from profit page...");
      scraper.scrapeRecentTrades();
    }
  }

  // Always update Smart Insights if we have background data
  if (state.backgroundDataValid && state.recentTrades.length > 0) {
    updater.updateSmartInsights();
  }
};

/** Main Code */
const chatbot = new Chatbox();
const scraper = new Scraper();
const updater = new Updater();

chrome.runtime.onMessage.addListener((message) => {
  if (message.type === "user_session_data") {
    // To handle storing user session data from background script
    console.log("User Session Data Received:", message.payload);
    localStorage.setItem("user_session_data", JSON.stringify(message.payload));
  }

  if (message.type === 'user_registration_data') {
    // To handle populating and showing up trading strategy page
    console.log("User Registration Data Received:", message.payload);
    togglePocketPTStrategy();
  }
});

// --- PocketPT Dashboard Integration ---
function injectPocketPTTab() {
  if (document.getElementById('pocketpt-nav-tab')) return;

  const menuLinks = document.querySelector('.header__menu-links');
  if (!menuLinks) return;

  const tabWrapper = document.createElement('span');
  tabWrapper.id = 'pocketpt-nav-tab';
  // Initially no active wrapper unless it's the active view
  tabWrapper.className = '';

  const tabLink = document.createElement('a');
  tabLink.className = 'header__menu-link pocketpt-tab';
  tabLink.href = '#';
  tabLink.innerHTML = `
    <span class="dc-text header__menu-link-text" title="PocketPT">
      <span class="pocketpt-tab-icon">Pocket<span style="color:#ff444f">PT</span></span>
    </span>
  `;

  tabLink.onclick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    togglePocketPTDashboard(true);
  };

  tabWrapper.appendChild(tabLink);
  const reportsTab = document.getElementById('dt_reports_tab');
  if (reportsTab && reportsTab.parentElement) {
    menuLinks.insertBefore(tabWrapper, reportsTab.parentElement);
  } else {
    menuLinks.appendChild(tabWrapper);
  }

  // Add listeners to other tabs to hide PocketPT when clicked
  menuLinks.querySelectorAll('a').forEach(link => {
    if (!link.classList.contains('pocketpt-tab')) {
      link.addEventListener('click', () => togglePocketPTDashboard(false));
    }
  });

  // Also listen to the parent items/containers for clicks that might trigger dropdowns
  menuLinks.querySelectorAll('.header__menu-link-wrapper').forEach(wrapper => {
    if (!wrapper.contains(document.querySelector('.pocketpt-tab'))) {
      wrapper.addEventListener('click', () => togglePocketPTDashboard(false));
    }
  });

  // Listen for logo/hub clicks outside the menu links
  const hubLogo = document.querySelector('.header__logo-wrapper') || document.querySelector('.header__menu-item--logo') || document.querySelector('.header__menu-item');
  if (hubLogo) {
    hubLogo.addEventListener('click', () => togglePocketPTDashboard(false));
  }

  // Detect clicks on the main header area to hide dashboard
  const header = document.querySelector('header');
  if (header) {
    header.addEventListener('click', (e) => {
      if (!e.target.closest('#pocketpt-nav-tab')) {
        togglePocketPTDashboard(false);
      }
    });
  }
}

function togglePocketPTDashboard(show) {
  let iframe = document.getElementById('pocketpt-dashboard-overlay');
  const tabWrapper = document.getElementById('pocketpt-nav-tab');
  const tab = document.querySelector('.pocketpt-tab');

  if (show) {
    if (!iframe) {
      iframe = document.createElement('iframe');
      iframe.id = 'pocketpt-dashboard-overlay';
      iframe.src = chrome.runtime.getURL('views/trading_edu.html');
      Object.assign(iframe.style, {
        position: 'fixed',
        top: '48px',
        left: '0',
        width: '100vw',
        height: 'calc(100vh - 48px)',
        border: 'none',
        zIndex: '99', // Significantly lowered to stay behind Deriv's dropdowns (usually 100-1000+)
        background: '#f2f3f4',
        display: 'block'
      });
      document.body.appendChild(iframe);
    } else {
      iframe.style.display = 'block';
    }

    // Set active state
    if (tabWrapper) tabWrapper.className = 'header__menu-link--active__link-wrapper';
    if (tab) tab.classList.add('active');

    // Remove active state from other tabs
    const menuLinks = document.querySelector('.header__menu-links');
    if (menuLinks) {
      menuLinks.querySelectorAll('.header__menu-link--active__link-wrapper').forEach(wrapper => {
        if (wrapper.id !== 'pocketpt-nav-tab') {
          wrapper.className = '';
        }
      });
    }
  } else {
    // Hide iframe
    if (iframe) iframe.style.display = 'none';

    // Remove active state
    if (tabWrapper) tabWrapper.className = '';
    if (tab) tab.classList.remove('active');

    // Note: Deriv's own routing will naturally set the other tabs to active when clicked
  }
}

// --- PocketPT Trading Strategy Page Display
function togglePocketPTStrategy() {
  let iframe = document.getElementById('pocketpt-strategy-overlay');
  let backBtn = document.getElementById('pocketpt-strategy-back-btn');

  if (!iframe) {
    // Create iframe
    iframe = document.createElement('iframe');
    iframe.id = 'pocketpt-strategy-overlay';
    iframe.src = chrome.runtime.getURL('views/trading_strategy.html');

    // FULL SCREEN STYLE
    Object.assign(iframe.style, {
      position: 'fixed',
      top: '48px',
      left: '0',
      width: '100vw',
      height: 'calc(100vh - 48px - 36px)', // ✅ spaces added
      border: 'none',
      zIndex: '999999',
      background: '#fff',
      display: 'block'
    });

    document.body.appendChild(iframe);

    // Create Back Button
    backBtn = document.createElement('button');
    backBtn.id = 'pocketpt-strategy-back-btn';
    backBtn.innerText = '← Back';

    Object.assign(backBtn.style, {
      position: 'fixed',
      bottom: '50px',
      left: '20px',
      zIndex: '1000000',
      padding: '10px 16px',
      fontSize: '14px',
      cursor: 'pointer',
      borderRadius: '6px',
      border: 'none',
      background: '#000',
      color: '#fff'
    });

    backBtn.onclick = () => {
      iframe.remove();
      backBtn.remove();
    };

    document.body.appendChild(backBtn);

  } else {
    // If already exists, remove both
    iframe.remove();
    if (backBtn) backBtn.remove();
  }
}

// Init
function init() {
  // Load any persisted data first
  updater.loadPersistedData();

  chatbot.injectFloatingBubble();

  injectPocketPTTab();

  // Listen for browser back/forward navigation
  window.addEventListener('popstate', () => {
    togglePocketPTDashboard(false);
  });

  // Main scraping interval (every 6 seconds)
  setInterval(() => {
    scraper.scrapeContext();
    chatbot.injectInlineButtons();
    injectPocketPTTab(); // Ensure tab stays there during SPA navigation
  }, 6000); // 6 seconds

  // Background data fetcher (every 30 seconds)
  setInterval(() => {
    backgroundDataFetcher(scraper, updater);
  }, 30000); // 30 seconds
}
setTimeout(init, 3000);
