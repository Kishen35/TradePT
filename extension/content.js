// content.js - Ultimate AI Agent v7 (Dynamic Panels + Background Data Persistence)
console.log("Deriv AI Trading Tutor: Ultimate Agent Loaded.");

const state = {
  balance: "0.00",
  currentSymbol: "",
  winRate: "68%",
  positions: [],
  recentTrades: [],
  lastTradeDataFetch: 0, // Timestamp of last trade data fetch
  backgroundDataValid: false,
  // NEW: Trade setup parameters (scraped when user clicks AI Analysis)
  tradeSetup: {
    tradeType: null,
    growthRate: null,
    stake: null,
    takeProfitEnabled: false,
    maxPayout: null,
    maxTicks: null,
  },
  // NEW: Chat session ID for conversation continuity
  sessionId: null,
};

// Backend API URL (change to your deployed URL in production)
const API_BASE_URL = "http://localhost:8000";

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

    // Lesson button handler
    const lessonBtn = document.querySelector(".lesson-btn");
    if (lessonBtn) {
      lessonBtn.onclick = () => this.startLesson();
    }
  }

  // Start a 2-minute lesson
  async startLesson() {
    const lessonBlock = document.querySelector(".lesson-block");
    const originalContent = lessonBlock.innerHTML;

    // Show loading state
    lessonBlock.innerHTML = `
      <strong>Loading Lesson...</strong>
      <p>Generating personalized content for you...</p>
    `;

    try {
      const response = await fetch(`${API_BASE_URL}/ai/lesson`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: "risk management", // Default topic, can be dynamic based on user patterns
          user_level: "beginner",
          user_context: {
            experience_level: "beginner",
            trading_style: "day_trader",
          },
        }),
      });

      const lesson = await response.json();

      // Display the lesson in the chat area (no markdown formatting)
      this.addMessage("ai", `${lesson.title}\n\nLet me teach you about this in 2 minutes!`);

      // Display each section with a small delay for readability
      for (let i = 0; i < lesson.sections.length; i++) {
        const section = lesson.sections[i];
        setTimeout(() => {
          this.addMessage("ai", `${section.heading}\n\n${section.content}`);
        }, (i + 1) * 2000); // 2 seconds apart
      }

      // Display key takeaways at the end
      setTimeout(() => {
        const takeaways = lesson.key_takeaways.map((t, i) => `${i + 1}. ${t}`).join("\n");
        this.addMessage("ai", `Key Takeaways:\n\n${takeaways}`);
      }, (lesson.sections.length + 1) * 2000);

      // Display quiz if available
      if (lesson.quiz && lesson.quiz.length > 0) {
        setTimeout(() => {
          const q = lesson.quiz[0];
          const options = q.options.map((o, i) => `${String.fromCharCode(65 + i)}. ${o}`).join("\n");
          this.addMessage("ai", `Quick Quiz:\n\n${q.question}\n\n${options}\n\n(Think about it! The answer is ${q.correct})`);
        }, (lesson.sections.length + 2) * 2000);
      }

      // Restore lesson block with "completed" state
      lessonBlock.innerHTML = `
        <strong>✅ Lesson Complete!</strong>
        <p>${lesson.title}</p>
        <button class="lesson-btn">Start Another Lesson</button>
      `;

      // Re-attach click handler
      const newBtn = lessonBlock.querySelector(".lesson-btn");
      if (newBtn) {
        newBtn.onclick = () => this.startLesson();
      }

    } catch (error) {
      console.error("Lesson API error:", error);

      // Restore original content on error
      lessonBlock.innerHTML = originalContent;
      lessonBlock.innerHTML = `
        <strong>⚠️ Could not load lesson</strong>
        <p>Please check if the backend server is running.</p>
        <button class="lesson-btn">Try Again</button>
      `;

      const retryBtn = lessonBlock.querySelector(".lesson-btn");
      if (retryBtn) {
        retryBtn.onclick = () => this.startLesson();
      }
    }
  }

  async sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (!text) return;

    this.addMessage("user", text);
    input.value = "";

    // Show typing indicator
    this.addMessage("ai", "Thinking...");

    try {
      const response = await fetch(`${API_BASE_URL}/ai/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          session_id: state.sessionId,
          user_context: {
            experience_level: "beginner",
            trading_style: "day_trader",
            risk_behavior: "conservative",
          },
          market_data: {
            balance: state.balance,
            symbol: state.currentSymbol,
            positions: state.positions,
            winRate: state.winRate,
          },
        }),
      });

      const data = await response.json();

      // Remove typing indicator and show real response
      const chatMessages = document.getElementById("chat-messages");
      const lastMsg = chatMessages.lastElementChild;
      if (lastMsg && lastMsg.innerText === "Thinking...") {
        lastMsg.remove();
      }

      // Save session ID for conversation continuity
      if (data.session_id) {
        state.sessionId = data.session_id;
      }

      this.addMessage("ai", data.response || "Sorry, I couldn't process that. Please try again.");
    } catch (error) {
      console.error("Chat API error:", error);

      // Remove typing indicator
      const chatMessages = document.getElementById("chat-messages");
      const lastMsg = chatMessages.lastElementChild;
      if (lastMsg && lastMsg.innerText === "Thinking...") {
        lastMsg.remove();
      }

      // Show fallback response
      this.addMessage(
        "ai",
        "I'm having trouble connecting to my brain right now. " +
          "Based on your balance of " + state.balance + ", " +
          "I'd recommend keeping your risk per trade below 2%."
      );
    }
  }

  addMessage(sender, text) {
    const chatMessages = document.getElementById("chat-messages");
    const msg = document.createElement("div");
    msg.className = `message ${sender}`;
    msg.innerText = text;
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

  // 5. Decision Overlay - Now calls backend API for real analysis
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
                <div class="advice-status loading" style="background: #666;">Analyzing...</div>
                <p>Checking your trade setup with AI...</p>
                <div class="advice-details"><div><strong>Symbol:</strong> ${state.currentSymbol || "Loading..."}</div><div><strong>Balance:</strong> ${state.balance}</div></div>
            </div>
        </div>
    `;
    overlay.style.display = "flex";

    // Scrape the current trade setup parameters
    scraper.scrapeTradeSetup();

    try {
      const response = await fetch(`${API_BASE_URL}/ai/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          balance: state.balance,
          symbol: state.currentSymbol,
          positions: state.positions,
          recentTrades: state.recentTrades,
          winRate: state.winRate,
          trade_setup: {
            trade_type: state.tradeSetup.tradeType,
            growth_rate: state.tradeSetup.growthRate,
            stake: state.tradeSetup.stake,
            take_profit_enabled: state.tradeSetup.takeProfitEnabled,
            max_payout: state.tradeSetup.maxPayout,
            max_ticks: state.tradeSetup.maxTicks,
          },
          user_preferences: {
            experience_level: "beginner",
            risk_behavior: "conservative",
          },
        }),
      });

      const data = await response.json();

      // Determine status class and text based on AI response
      const isSafe = data.safe_to_trade;
      const statusClass = isSafe ? "good" : "bad";
      const statusText = isSafe ? "Safe to Trade" : "Not Safe to Trade";
      const statusColor = isSafe ? "#4bb543" : "#ff444f";

      // Update overlay with AI analysis result
      overlay.innerHTML = `
          <div class="overlay-content">
              <div class="overlay-header"><span>AI Trade Assistant</span><button onclick="document.getElementById('ai-decision-overlay').style.display='none'">×</button></div>
              <div class="overlay-body">
                  <div class="advice-status ${statusClass}" style="background: ${statusColor};">${statusText}</div>
                  <p>${data.reason || "Analysis complete."}</p>
                  <div class="advice-details">
                      <div><strong>Trade:</strong> ${state.tradeSetup.tradeType || state.currentSymbol || "Unknown"} @ ${state.tradeSetup.stake || "?"} USD</div>
                      <div><strong>Risk Level:</strong> ${data.risk_level || "Unknown"}</div>
                  </div>
                  <p style="margin-top: 10px; font-style: italic; color: #888;"><strong>Tip:</strong> ${data.tip || "Always manage your risk."}</p>
              </div>
              <div class="overlay-footer">
                  <button onclick="document.getElementById('ai-decision-overlay').style.display='none'">Got it</button>
                  <button id="ask-ai-more-btn" style="background: #242828; margin-left: 10px;">Ask AI More</button>
              </div>
          </div>
      `;

      // Store the analysis result for "Ask AI More" context
      state.lastAnalysis = data;

    } catch (error) {
      console.error("AI Analysis error:", error);

      // Show error state
      overlay.innerHTML = `
          <div class="overlay-content">
              <div class="overlay-header"><span>AI Trade Assistant</span><button onclick="document.getElementById('ai-decision-overlay').style.display='none'">×</button></div>
              <div class="overlay-body">
                  <div class="advice-status bad" style="background: #ff444f;">Connection Error</div>
                  <p>Could not connect to AI backend. Is the server running?</p>
                  <div class="advice-details"><div><strong>Balance:</strong> ${state.balance}</div><div><strong>Tip:</strong> Start server with: uvicorn app.main:app --reload</div></div>
              </div>
              <div class="overlay-footer">
                  <button onclick="document.getElementById('ai-decision-overlay').style.display='none'">Got it</button>
                  <button id="ask-ai-more-btn" style="background: #242828; margin-left: 10px;">Ask AI More</button>
              </div>
          </div>
      `;
    }

    // Re-attach the "Ask AI More" button handler
    const askMoreBtn = document.getElementById("ask-ai-more-btn");
    if (askMoreBtn) {
      askMoreBtn.onclick = () => {
        overlay.style.display = "none";
        this.openChatWithPrefill(type);
      };
    }
  }

  // 6. Open chat with contextual prefilled message
  openChatWithPrefill(actionType) {
    const trigger = document.getElementById("ai-bubble-trigger");
    const popup = document.getElementById("ai-insights-popup");
    const input = document.getElementById("user-input");

    // Open chat if closed
    if (popup.style.display === "none") trigger.click();

    // Generate contextual message based on action type, analysis result, and current data
    let prefilledMessage = "";

    // If we have a recent analysis result, reference it
    if (state.lastAnalysis && !state.lastAnalysis.safe_to_trade) {
      prefilledMessage = `Why is it not safe to trade ${state.tradeSetup.tradeType || state.currentSymbol || "right now"}? Please explain in detail.`;
    } else if (actionType === "close" && state.currentSymbol) {
      prefilledMessage = `Should I close my current ${state.currentSymbol} position?`;
    } else if (actionType === "purchase") {
      const tradeInfo = state.tradeSetup.tradeType
        ? `${state.tradeSetup.tradeType} at ${state.tradeSetup.stake || "?"} USD stake`
        : state.currentSymbol;
      prefilledMessage = `Tell me more about this trade setup: ${tradeInfo}. What should I watch out for?`;
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

  // 1c. Trade Setup Scraper (scrapes the trade parameters user selected)
  scrapeTradeSetup() {
    console.log("Scraping trade setup parameters...");

    // Trade Type (Accumulators, Multipliers, Rise/Fall, etc.)
    state.tradeSetup.tradeType = this.getTradeType();

    // Growth Rate (for Accumulators: 1%, 2%, 3%, 4%, 5%)
    state.tradeSetup.growthRate = this.getSelectedGrowthRate();

    // Stake Amount
    state.tradeSetup.stake = this.getStakeAmount();

    // Take Profit enabled?
    state.tradeSetup.takeProfitEnabled = this.isTakeProfitEnabled();

    // Max Payout
    state.tradeSetup.maxPayout = this.getMaxPayout();

    // Max Ticks (for Accumulators)
    state.tradeSetup.maxTicks = this.getMaxTicks();

    console.log("Scraped trade setup:", state.tradeSetup);
  }

  getTradeType() {
    // Try multiple selectors for trade type
    const selectors = [
      '.contract-type-display',
      '.trade-type-header h4',
      '[data-testid="dt_contract_dropdown"] .dc-dropdown__display-text',
      '.contract-type-widget__display',
      '.purchase-container__title',
      // Look for text that says Accumulators, Multipliers, etc.
      '.trade-container__fieldset-header',
    ];

    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el && el.innerText.trim()) {
        return el.innerText.trim();
      }
    }

    // Fallback: Check URL for trade type hints
    const url = window.location.href;
    if (url.includes('accumulator')) return 'Accumulators';
    if (url.includes('multiplier')) return 'Multipliers';
    if (url.includes('rise_fall')) return 'Rise/Fall';

    return null;
  }

  getSelectedGrowthRate() {
    // For Accumulators - find the selected growth rate button
    // Growth rate buttons are typically in a button group with one selected
    const selectors = [
      '.growth-rate button.selected',
      '.growth-rate button[class*="active"]',
      '[class*="growth"] button[class*="selected"]',
      '.trade-params__option--selected',
      // Deriv specific selectors
      '.dc-button-menu__button--active',
    ];

    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el && el.innerText.trim()) {
        return el.innerText.trim();
      }
    }

    // Try to find any button group where one is selected
    const buttonGroups = document.querySelectorAll('.dc-button-menu, .button-group');
    for (const group of buttonGroups) {
      const activeBtn = group.querySelector('.dc-button-menu__button--active, .active, .selected');
      if (activeBtn) {
        const text = activeBtn.innerText.trim();
        if (text.includes('%')) return text;
      }
    }

    return null;
  }

  getStakeAmount() {
    // Find the stake/amount input field
    const selectors = [
      'input[data-testid="dt_amount_input"]',
      '.stake-input input',
      'input[name="stake"]',
      'input[name="amount"]',
      '.trade-container__fieldset input[type="text"]',
      '.dc-input__field',
    ];

    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el && el.value) {
        return el.value;
      }
    }

    // Fallback: Look for a display element with stake value
    const stakeDisplay = document.querySelector('.trade-container__fieldset .dc-input-wrapper input');
    if (stakeDisplay) return stakeDisplay.value;

    return null;
  }

  isTakeProfitEnabled() {
    // Check if take profit checkbox is enabled
    const selectors = [
      'input[type="checkbox"][name*="take_profit"]',
      '.take-profit-checkbox input',
      '#dt_take_profit-checkbox',
      'input[id*="take_profit"]',
    ];

    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el) {
        return el.checked;
      }
    }

    return false;
  }

  getMaxPayout() {
    // Find max payout display value
    const selectors = [
      '.max-payout .value',
      '[class*="payout"] .dc-text',
      '[data-testid="dt_max_payout"]',
      '.trade-container__fieldset-info .trade-container__fieldset-info-value',
    ];

    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el && el.innerText.trim()) {
        return el.innerText.trim();
      }
    }

    // Look for text containing "payout" nearby
    const allText = document.body.innerText;
    const payoutMatch = allText.match(/Max\.?\s*payout[:\s]+([0-9,\.]+\s*USD)/i);
    if (payoutMatch) return payoutMatch[1];

    return null;
  }

  getMaxTicks() {
    // Find max ticks display value (for Accumulators)
    const selectors = [
      '.max-ticks .value',
      '[class*="ticks"] .dc-text',
      '.trade-container__fieldset-info .trade-container__fieldset-info-value',
    ];

    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el && el.innerText.trim() && el.innerText.includes('tick')) {
        return el.innerText.trim();
      }
    }

    // Look for text containing "ticks"
    const allText = document.body.innerText;
    const ticksMatch = allText.match(/Max\.?\s*ticks?[:\s]+(\d+\s*ticks?)/i);
    if (ticksMatch) return ticksMatch[1];

    return null;
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
  updateSmartInsights() {
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

    // Update the win rate in the insights panel
    const winRateEl = insightsContainer.querySelector(
      ".stat-row:first-of-type strong",
    );
    if (winRateEl) {
      // Color code the win rate
      const winRateNum = parseInt(calculatedWinRate);
      let winRateColor = "#4bb543"; // Green for good win rate
      if (winRateNum < 50) {
        winRateColor = "#ff444f"; // Red for poor win rate
      } else if (winRateNum < 65) {
        winRateColor = "#ffa500"; // Orange for average win rate
      }

      winRateEl.innerHTML = `<span style="color: ${winRateColor};">${calculatedWinRate}</span>`;
    }

    // Update the state for other functions to use
    state.winRate = calculatedWinRate;
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

// Init
function init() {
  // Load any persisted data first
  updater.loadPersistedData();

  chatbot.injectFloatingBubble();

  // Main scraping interval (every 6 seconds)
  setInterval(() => {
    scraper.scrapeContext();
    chatbot.injectInlineButtons();
  }, 6000); // 6 seconds

  // Background data fetcher (every 30 seconds)
  setInterval(() => {
    backgroundDataFetcher(scraper, updater);
  }, 30000); // 30 seconds
}
setTimeout(init, 3000);
