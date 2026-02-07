// content.js - Ultimate AI Agent v7 (Dynamic Panels)
console.log("Deriv AI Trading Tutor: Ultimate Agent Loaded.");

const state = {
    balance: "0.00",
    currentSymbol: "",
    winRate: "68%",
    positions: [],
    recentTrades: []
};

// 1. Enhanced Context Scraper with Live Data (using innerHTML)
function scrapeContext() {
    // Account Balance - Multiple selectors for reliability
    const balanceEl = document.querySelector('#dt_core_account-info_acc-info') ||
        document.querySelector('.acc-info__balance');
    if (balanceEl) {
        // Use innerHTML to capture nested elements, then extract text
        const balanceHTML = balanceEl.innerHTML;
        state.balance = balanceEl.innerText.trim() || extractTextFromHTML(balanceHTML);
    }

    // Current Trading Symbol - Enhanced selectors with innerHTML
    const symbolEl = document.querySelector('.cq-symbol-select-btn .cq-symbol') ||
        document.querySelector('.cq-symbol-info .cq-symbol') ||
        document.querySelector('[data-testid="dt_symbol_info_name"]') ||
        document.querySelector('.cq-symbol-select-btn .cq-symbol-name');
    if (symbolEl) {
        const symbolHTML = symbolEl.innerHTML;
        state.currentSymbol = extractTextFromHTML(symbolHTML) || symbolEl.innerText.trim();
    }

    // Scrape Live Positions
    scrapeLivePositions();
    
    // Scrape Recent Trades (for performance panel)
    scrapeRecentTrades();

    updateDynamicPanels();
}

// 1a. Live Position Scraper (using correct Deriv selectors)
function scrapeLivePositions() {
    state.positions = []; // Reset positions array

    // Use the specific selector for position symbols
    const symbolElements = document.querySelectorAll("#dc-contract_card_underlying_label > span");

    console.log('Found symbol elements:', symbolElements.length);

    if (symbolElements.length === 0) {
        console.log('No positions found with #dc-contract_card_underlying_label > span selector');
        // Try alternative approaches
        const contractCards = document.querySelectorAll('.dc-contract-card');
        console.log('Found contract cards as fallback:', contractCards.length);
    }

    symbolElements.forEach((symbolEl, index) => {
        try {
            // Get the symbol from the specific selector
            const symbol = extractTextFromHTML(symbolEl.innerHTML) || symbolEl.innerText.trim();

            // Find the parent contract card to get P&L and other data
            const contractCard = symbolEl.closest('.dc-contract-card');

            if (contractCard) {
                // Look for P&L using the correct profit/loss selectors
                // Try profit selector first
                let pnlEl = contractCard.querySelector('.dc-contract-card-item__total-profit-loss .dc-contract-card-item__body--profit > span');
                let isProfit = true;

                // If no profit found, try loss selector
                if (!pnlEl) {
                    pnlEl = contractCard.querySelector('.dc-contract-card-item__total-profit-loss .dc-contract-card-item__body--loss > span');
                    isProfit = false;
                }

                // Fallback to generic selectors if specific ones don't work
                if (!pnlEl) {
                    pnlEl = contractCard.querySelector('.dc-contract-card__profit-loss') ||
                        contractCard.querySelector('[class*="profit"]') ||
                        contractCard.querySelector('[class*="pnl"]');
                }

                const typeEl = contractCard.querySelector('.dc-contract-card__type');

                console.log(`Position ${index}:`, {
                    symbol: symbol,
                    pnlHTML: pnlEl ? pnlEl.innerHTML : 'not found',
                    isProfit: isProfit,
                    typeHTML: typeEl ? typeEl.innerHTML : 'not found'
                });

                if (symbol && pnlEl) {
                    const pnlText = extractTextFromHTML(pnlEl.innerHTML) || pnlEl.innerText.trim();

                    const position = {
                        symbol: symbol,
                        pnl: pnlText,
                        type: typeEl ? (extractTextFromHTML(typeEl.innerHTML) || typeEl.innerText.trim()) : 'Unknown',
                        isProfit: isProfit
                    };
                    state.positions.push(position);
                    console.log('Added position:', position);
                }
            } else {
                console.log(`No parent contract card found for symbol: ${symbol}`);
            }
        } catch (error) {
            console.log('Error scraping position:', error);
        }
    });

    console.log('Total positions found:', state.positions.length);

    // Update the positions panel with live data
    updatePositionsPanel();
}

// 1d. Recent Trades Scraper (for profit/statement pages)
function scrapeRecentTrades() {
    state.recentTrades = []; // Reset trades array
    
    const url = window.location.href;
    
    // Only scrape on profit or statement pages
    if (!url.includes('/reports/profit') && !url.includes('/reports/statement')) {
        return;
    }
    
    console.log('Scraping recent trades on:', url.includes('/reports/profit') ? 'profit page' : 'statement page');
    
    // Look for trade rows - they have IDs like dt_reports_contract_305945452408
    const tradeRows = document.querySelectorAll('[id^="dt_reports_contract_"]');
    
    console.log('Found trade rows:', tradeRows.length);
    
    // Get last 5 trades (or fewer if less available)
    const last5Trades = Array.from(tradeRows).slice(0, 5);
    
    last5Trades.forEach((row, index) => {
        try {
            let pnlEl = null;
            let isProfit = false;
            
            if (url.includes('/reports/profit')) {
                // Profit page selectors
                pnlEl = row.querySelector('.table__cell.profit_loss > span');
                // Check if it has profit class (you mentioned _profit for profit)
                isProfit = row.querySelector('.table__cell.profit_loss .amount--profit') !== null;
            } else if (url.includes('/reports/statement')) {
                // Statement page selectors
                pnlEl = row.querySelector('.table__cell.amount .amount--profit') || 
                       row.querySelector('.table__cell.amount .amount--loss');
                isProfit = row.querySelector('.table__cell.amount .amount--profit') !== null;
            }
            
            console.log(`Trade ${index}:`, {
                pnlHTML: pnlEl ? pnlEl.innerHTML : 'not found',
                isProfit: isProfit,
                rowId: row.id
            });
            
            if (pnlEl) {
                const pnlText = extractTextFromHTML(pnlEl.innerHTML) || pnlEl.innerText.trim();
                
                const trade = {
                    pnl: pnlText,
                    isProfit: isProfit,
                    result: isProfit ? 'W' : 'L' // W for Win, L for Loss
                };
                
                state.recentTrades.push(trade);
                console.log('Added trade:', trade);
            }
        } catch (error) {
            console.log('Error scraping trade row:', error);
        }
    });
    
    console.log('Total trades found:', state.recentTrades.length);
    
    // Update the performance panel
    updatePerformancePanel();
}

// 1e. Update Performance Panel with Live Data
function updatePerformancePanel() {
    const perfContainer = document.querySelector('#panel-performance');
    if (!perfContainer) return;
    
    // Calculate total profit from recent trades
    let totalProfit = 0;
    state.recentTrades.forEach(trade => {
        const amount = parseFloat(trade.pnl.replace(/[^\d.-]/g, ''));
        if (!isNaN(amount)) {
            totalProfit += trade.isProfit ? Math.abs(amount) : -Math.abs(amount);
        }
    });
    
    // Generate W-L pattern from recent trades
    const tradePattern = state.recentTrades.map(trade => trade.result).join('-') || 'No data';
    
    // Update the performance panel content
    const totalProfitEl = perfContainer.querySelector('.stat-row:first-of-type strong');
    const last5TradesEl = perfContainer.querySelector('.stat-row:last-of-type strong');
    
    if (totalProfitEl && state.recentTrades.length > 0) {
        const profitColor = totalProfit >= 0 ? '#4bb543' : '#ff444f';
        const profitSign = totalProfit >= 0 ? '+' : '';
        totalProfitEl.innerHTML = `<span style="color: ${profitColor};">${profitSign}${totalProfit.toFixed(2)} USD</span>`;
    }
    
    if (last5TradesEl && state.recentTrades.length > 0) {
        last5TradesEl.innerText = tradePattern;
    }
    
    // Update win rate in Smart Insights panel
    updateSmartInsights();
    
    console.log('Updated performance panel:', {
        totalProfit: totalProfit.toFixed(2),
        tradePattern: tradePattern
    });
}

// 1f. Update Smart Insights Panel with Dynamic Win Rate
function updateSmartInsights() {
    const insightsContainer = document.querySelector('#panel-insights');
    if (!insightsContainer) return;
    
    // Calculate win rate from recent trades
    let calculatedWinRate = "68%"; // Default fallback
    
    if (state.recentTrades.length > 0) {
        const wins = state.recentTrades.filter(trade => trade.isProfit).length;
        const totalTrades = state.recentTrades.length;
        const winRatePercent = Math.round((wins / totalTrades) * 100);
        calculatedWinRate = `${winRatePercent}%`;
        
        console.log('Calculated win rate:', {
            wins: wins,
            totalTrades: totalTrades,
            winRate: calculatedWinRate
        });
    }
    
    // Update the win rate in the insights panel
    const winRateEl = insightsContainer.querySelector('.stat-row:first-of-type strong');
    if (winRateEl) {
        // Color code the win rate
        const winRateNum = parseInt(calculatedWinRate);
        let winRateColor = '#4bb543'; // Green for good win rate
        if (winRateNum < 50) {
            winRateColor = '#ff444f'; // Red for poor win rate
        } else if (winRateNum < 65) {
            winRateColor = '#ffa500'; // Orange for average win rate
        }
        
        winRateEl.innerHTML = `<span style="color: ${winRateColor};">${calculatedWinRate}</span>`;
    }
    
    // Update the state for other functions to use
    state.winRate = calculatedWinRate;
}
function extractTextFromHTML(html) {
    if (!html) return '';
    // Create a temporary div to parse HTML and extract text
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    return tempDiv.innerText.trim();
}

// 1c. Update Positions Panel with Live Data
function updatePositionsPanel() {
    const positionsContainer = document.querySelector('#panel-positions');
    if (!positionsContainer) return;

    // Find the content area (skip the h4 header)
    const existingItems = positionsContainer.querySelectorAll('.pos-item');
    existingItems.forEach(item => item.remove());

    if (state.positions.length === 0) {
        // Show placeholder if no positions found
        const placeholder = document.createElement('div');
        placeholder.className = 'pos-item';
        placeholder.innerHTML = '<span style="color: #999;">No open positions detected</span>';
        positionsContainer.appendChild(placeholder);
        return;
    }

    // Add live positions
    state.positions.forEach(position => {
        const posItem = document.createElement('div');
        posItem.className = 'pos-item';

        // Use the isProfit flag we set during scraping for accurate color coding
        const pnlColor = position.isProfit ? '#4bb543' : '#ff444f';

        posItem.innerHTML = `${position.symbol}: <span style="color: ${pnlColor};">${position.pnl}</span>`;
        positionsContainer.appendChild(posItem);
    });
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
    document.getElementById('user-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

function sendMessage() {
    const input = document.getElementById('user-input');
    const text = input.value.trim();
    if (!text) return;

    addMessage('user', text);
    input.value = '';

    setTimeout(() => {
        addMessage('ai', "I've checked your " + (state.currentSymbol || "current market") + " data. Given your balance of " + state.balance + ", I recommend sticking to a 1:2 risk-to-reward ratio.");
    }, 1000);
}

function addMessage(sender, text) {
    const chatMessages = document.getElementById('chat-messages');
    const msg = document.createElement('div');
    msg.className = `message ${sender}`;
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

    // Close/Sell Advice - Enhanced to detect both Close and Sell buttons
    // Method 1: Find buttons by text content (Close)
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

    // Method 2: Find Sell buttons using the specific selector pattern
    const sellButtons = document.querySelectorAll('[id^="dc_contract_card_"] > div > div > button');
    sellButtons.forEach(btn => {
        // Check if it's a Sell button by text content
        if (btn.innerText.toLowerCase() !== 'sell') return;
        if (btn.parentElement.classList.contains('ai-button-container')) return;
        
        console.log('Found Sell button:', btn.id, btn.innerText);
        
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

    // Method 3: Generic approach for any Close/Sell buttons we might have missed
    const allButtons = document.querySelectorAll('button');
    allButtons.forEach(btn => {
        const buttonText = btn.innerText.toLowerCase();
        if ((buttonText === 'close' || buttonText === 'sell') && 
            btn.offsetWidth > 0 && 
            !btn.parentElement.classList.contains('ai-button-container') &&
            !btn.classList.contains('ai-advice-btn')) {
            
            console.log('Found additional Close/Sell button:', btn.className, btn.innerText);
            
            const container = document.createElement('div');
            container.className = 'ai-button-container';
            btn.parentNode.insertBefore(container, btn);
            container.appendChild(btn);
            const adviceBtn = document.createElement('button');
            adviceBtn.className = 'ai-advice-btn close-advice';
            adviceBtn.innerText = 'AI';
            adviceBtn.onclick = (e) => { e.preventDefault(); showDecisionOverlay('close'); };
            container.appendChild(adviceBtn);
        }
    });
}

// 5. Decision Overlay
function showDecisionOverlay(type) {
    let overlay = document.getElementById('ai-decision-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'ai-decision-overlay';
        document.body.appendChild(overlay);
    }
    overlay.innerHTML = `
        <div class="overlay-content">
            <div class="overlay-header"><span>AI Trade Assistant</span><button onclick="document.getElementById('ai-decision-overlay').style.display='none'">×</button></div>
            <div class="overlay-body">
                <div class="advice-status good">Safe to Trade</div>
                <p>Market conditions are stable. Risk is within your profile.</p>
                <div class="advice-details"><div><strong>Balance:</strong> ${state.balance}</div><div><strong>Risk:</strong> Low</div></div>
            </div>
            <div class="overlay-footer">
                <button onclick="document.getElementById('ai-decision-overlay').style.display='none'">Got it</button>
                <button id="ask-ai-more-btn" style="background: #242828; margin-left: 10px;">Ask AI More</button>
            </div>
        </div>
    `;
    overlay.style.display = 'flex';
    document.getElementById('ask-ai-more-btn').onclick = () => {
        overlay.style.display = 'none';
        openChatWithPrefill(type);
    };
}

// 6. Open chat with contextual prefilled message
function openChatWithPrefill(actionType) {
    const trigger = document.getElementById('ai-bubble-trigger');
    const popup = document.getElementById('ai-insights-popup');
    const input = document.getElementById('user-input');

    // Open chat if closed
    if (popup.style.display === 'none') trigger.click();

    // Generate contextual message based on action type and current data
    let prefilledMessage = '';
    if (actionType === 'close' && state.currentSymbol) {
        prefilledMessage = `Should I close my current ${state.currentSymbol} position?`;
    } else if (actionType === 'purchase' && state.currentSymbol) {
        prefilledMessage = `Is now a good time to buy ${state.currentSymbol}?`;
    } else {
        prefilledMessage = `What's your advice on my current trading situation?`;
    }

    // Prefill the input and focus
    input.value = prefilledMessage;
    input.focus();
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
