// ══════════════════════════════════════════════════════════════
// Mock state object for standalone usage (when no Chrome extension)
// ══════════════════════════════════════════════════════════════
if (typeof state === 'undefined') {
    window.state = {
        balance: null,
        currentSymbol: null,
        winRate: null,
        positions: [],
        recentTrades: []
    };
    console.log('💡 Running in standalone mode (no Chrome extension detected)');
}

// ══════════════════════════════════════════════════════════════
// Initialize AI Integration
// ══════════════════════════════════════════════════════════════
let aiIntegration;

document.addEventListener('DOMContentLoaded', () => {
    // Initialize AI Integration
    if (window.AIIntegration) {
        aiIntegration = new AIIntegration();
        console.log('✅ AI Integration initialized');
        console.log('📡 Backend URL:', aiIntegration.backendUrl);
    } else {
        console.warn('⚠️ AI Integration module not found - check that ai-integration.js is loaded');
    }

    loadScenario(0);

    // Default to manual entry for autopsy
    showManualEntry();
});

// ══════════════════════════════════════════════════════════════
// State
// ══════════════════════════════════════════════════════════════
let xp = 240, streak = 3;
let currentScenario = 0, scenarioAnswered = false;
let score = 0, totalAnswered = 0;

// ══════════════════════════════════════════════════════════════
// Tabs (Fixed to work with new navigation structure)
// ══════════════════════════════════════════════════════════════
function switchTab(tab) {
    document.querySelectorAll('.tab-page').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');
    const idx = ['learn', 'tutor', 'autopsy', 'leaderboard'].indexOf(tab);
    document.querySelectorAll('.nav-tab')[idx]?.classList.add('active');
}

// ══════════════════════════════════════════════════════════════
// Scenarios Modal Functions (Not in top navigation, triggered from Learn tab)
// ══════════════════════════════════════════════════════════════
function openScenarios() {
    document.getElementById('scenarios-modal').style.display = 'flex';
    loadScenario(currentScenario);
}

function closeScenarios() {
    document.getElementById('scenarios-modal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('scenarios-modal');
    if (event.target === modal) {
        closeScenarios();
    }
}

// ══════════════════════════════════════════════════════════════
// XP & Toast
// ══════════════════════════════════════════════════════════════
function addXP(amount, reason) {
    xp += amount;
    document.getElementById('xpCount').textContent = xp;
    document.getElementById('xpAmount').textContent = '+' + amount + ' XP';
    document.getElementById('xpReason').textContent = reason;
    const t = document.getElementById('xpToast');
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2800);
}

function showToast(msg) {
    document.getElementById('xpReason').textContent = msg;
    document.getElementById('xpAmount').textContent = '💡';
    const t = document.getElementById('xpToast');
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2500);
}

// ══════════════════════════════════════════════════════════════
// Scenarios (unchanged - still using hardcoded data)
// ══════════════════════════════════════════════════════════════
const scenarios = [
    {
        chip: 'GOLD / XAU', chipClass: 'chip-default',
        contextText: `Gold has been climbing for 3 consecutive days after the US Federal Reserve signalled it would keep interest rates unchanged. The US Dollar Index (DXY) has weakened, and there's rising geopolitical tension in the Middle East. Gold is currently sitting just below a key resistance level at $2,380.`,
        marketData: [{ label: 'XAU/USD', val: '$2,374.20', cls: 'up' }, { label: '3-Day Change', val: '+1.8%', cls: 'up' }, { label: 'RSI (14)', val: '68.4', cls: 'neutral' }, { label: 'DXY', val: '102.1 ↓', cls: 'down' }],
        question: 'Given these conditions, a trader wants to go <em>LONG on Gold</em>. Which is the strongest reason to support that decision?',
        choices: [{ l: 'A', t: 'Gold has gone up 3 days in a row, so it will keep going up.' }, { l: 'B', t: 'Weak Dollar + stable rates + geopolitical uncertainty = classic safe-haven demand for Gold.' }, { l: 'C', t: "RSI is near 70 which means it's about to shoot up even higher." }, { l: 'D', t: "Gold always goes up, it's the safest trade." }],
        correct: 1,
        explanation: `<strong>B is correct</strong> — a great example of <span class="hl">macro confluence</span>.<br><br>When the US Dollar weakens, Gold typically rises because it's priced in USD. Add <strong>stable/low interest rates</strong> and <strong>geopolitical risk</strong> and you have three independent reasons aligning.<br><br><strong>Why the others are wrong:</strong><br>• <strong>A</strong> is <span class="hl">recency bias</span> — past movement doesn't predict future movement on its own.<br>• <strong>C</strong> is backwards — RSI near 70 signals <em>overbought</em>, a caution signal.<br>• <strong>D</strong> is a dangerous myth.`,
        followups: ['What is RSI overbought?', 'How does DXY affect Gold?', 'What is safe-haven demand?']
    },
    {
        chip: 'VOLATILITY 75', chipClass: 'chip-teal',
        contextText: `You're trading Volatility 75 Index on Deriv. The market has been ranging between 8,200 and 8,500 for the past 4 hours. You spot what looks like a breakout above 8,500 — but the candle that broke out was a very small-bodied candle with a long wick. Volume (pip movement) is lower than the previous candles.`,
        marketData: [{ label: 'V75 Price', val: '8,518', cls: 'up' }, { label: 'Range High', val: '8,500', cls: 'neutral' }, { label: 'Candle Body', val: 'Small', cls: 'down' }, { label: 'RSI (14)', val: '62.1', cls: 'neutral' }],
        question: 'You see price break above the range. Should you immediately <em>enter a LONG trade</em>?',
        choices: [{ l: 'A', t: 'Yes! Breakout confirmed — enter immediately for maximum profit.' }, { l: 'B', t: 'Wait for a candle close above 8,500 AND a retest of that level before entering.' }, { l: 'C', t: 'No — RSI at 62 means the move is already over.' }, { l: 'D', t: 'Enter a SHORT trade — the small wick candle signals a reversal.' }],
        correct: 1,
        explanation: `<strong>B is the disciplined answer</strong> — this separates profitable traders from impulsive ones.<br><br>Small candle body + long wick + low volatility = classic signs of a <span class="hl">false breakout</span>. Synthetic indices frequently "poke" above resistance to trigger stops before reversing.<br><br><strong>The correct process:</strong><br>1. Wait for a <strong>full candle close</strong> above 8,500<br>2. Wait for a <strong>retest</strong> — price returns to 8,500, holds as support, then bounces<br>3. <em>Then</em> enter with stop below the retest candle`,
        followups: ['What is a false breakout?', 'How do I spot a retest?', 'What candle body size matters?']
    },
    {
        chip: 'PSYCHOLOGY', chipClass: 'chip-red',
        contextText: `You just took a loss of $50 on a V75 trade. You were certain about your setup but the market moved against you. You still have $200 in your account. You're feeling frustrated and want to "make it back quickly." You spot another trade that looks okay but not perfect — your usual rules say to skip it.`,
        marketData: [{ label: 'Account', val: '$200', cls: 'neutral' }, { label: 'Just Lost', val: '-$50', cls: 'down' }, { label: 'Account Down', val: '-25%', cls: 'down' }, { label: 'Setup Quality', val: 'Below avg', cls: 'down' }],
        question: 'You break your rules and enter the trade anyway. What are you experiencing?',
        choices: [{ l: 'A', t: 'Smart trading — catching up losses is part of trading strategy.' }, { l: 'B', t: 'Revenge trading driven by emotional bias — one of the most common causes of blown accounts.' }, { l: 'C', t: 'FOMO — fear of missing a potential winning trade.' }, { l: 'D', t: 'Confirmation bias — the market always gives you a chance to recover.' }],
        correct: 1,
        explanation: `<strong>B — Revenge trading.</strong> Recognising it is the most important skill you'll develop.<br><br><span class="hl">Revenge trading</span> happens when <strong>emotion overrides your system</strong>. Your brain wants to restore what it lost immediately.<br><br><strong>What actually happens:</strong><br>• Below-average setup → higher chance of another loss<br>• Another loss → frustration doubles → bigger "recovery" bets<br>• This spiral has blown more accounts than bad analysis<br><br><strong>Professional response:</strong> Close the platform. Walk away 30 minutes.`,
        followups: ['How do I stop revenge trading?', 'What is FOMO in trading?', 'How do I build discipline?']
    },
    {
        chip: 'RISK MANAGEMENT', chipClass: 'chip-default',
        contextText: `You have a $500 trading account. You've identified a solid setup on EUR/USD. Entry: 1.0850, stop-loss: 1.0820 (30 pips), take-profit: 1.0920 (70 pips). You want to risk 10% of your account on this trade.`,
        marketData: [{ label: 'Account Size', val: '$500', cls: 'neutral' }, { label: 'Stop Distance', val: '30 pips', cls: 'neutral' }, { label: 'TP Distance', val: '70 pips', cls: 'neutral' }, { label: 'Risk:Reward', val: '1:2.33', cls: 'up' }],
        question: 'Risking 10% ($50) per trade on this setup — is this <em>good risk management</em>?',
        choices: [{ l: 'A', t: "Yes — a 1:2.33 RR ratio means you'll be profitable long-term." }, { l: 'B', t: 'Yes — you need to risk more to make more with a small account.' }, { l: 'C', t: 'No — 10% per trade is far too high. 3 consecutive losses wipes 27% of your account.' }, { l: 'D', t: "Doesn't matter — risk management only matters for large accounts." }],
        correct: 2,
        explanation: `<strong>C is correct.</strong> The R:R is great — but the <span class="hl">position sizing is dangerous</span>.<br><br>At 10% risk per trade:<br>• 3 losses in a row = account down <strong>27%</strong><br>• 5 losses in a row = account down <strong>41%</strong><br><br><strong>Professional standard: 1–2% per trade</strong><br>At 1% ($5/trade), 10 consecutive losses = only -10% — manageable and recoverable.<br><br><span class="hl">Survival first, profit second.</span>`,
        followups: ['What is the 1% rule?', 'How do I calculate position size?', 'What is a drawdown?']
    }
];

function loadScenario(idx) {
    const s = scenarios[idx];
    scenarioAnswered = false;
    document.getElementById('qNum').textContent = idx + 1;
    document.getElementById('scenarioChip').textContent = s.chip;
    document.getElementById('scenarioChip').className = 'chip ' + s.chipClass;
    document.getElementById('scenarioContextText').textContent = s.contextText;
    document.getElementById('marketDataRow').innerHTML = s.marketData.map(d => `
    <div class="market-datum">
      <div class="datum-label">${d.label}</div>
      <div class="datum-val ${d.cls}">${d.val}</div>
    </div>`).join('');
    document.getElementById('scenarioQuestion').innerHTML = s.question;
    document.getElementById('choiceGrid').innerHTML = s.choices.map((c, i) => `
    <button class="choice-btn" onclick="selectChoice(${i})" id="choice-${i}">
      <span class="choice-label">${c.l}</span>${c.t}
    </button>`).join('');
    document.getElementById('aiExplain').classList.remove('visible');
    document.getElementById('scenarioScore').textContent = totalAnswered > 0 ? `${score}/${totalAnswered} correct` : '';
}

function selectChoice(idx) {
    if (scenarioAnswered) return;
    scenarioAnswered = true; totalAnswered++;
    const s = scenarios[currentScenario];
    const btns = document.querySelectorAll('.choice-btn');
    btns.forEach((b, i) => { b.disabled = true; if (i === s.correct) b.classList.add('reveal-correct'); });
    const isCorrect = idx === s.correct;
    btns[idx].classList.remove('reveal-correct');
    btns[idx].classList.add(isCorrect ? 'selected-correct' : 'selected-wrong');
    if (isCorrect) { score++; addXP(20, 'Correct answer!'); } else { addXP(5, 'Good try — lesson learned!'); }
    document.getElementById('scenarioScore').textContent = `${score}/${totalAnswered} correct`;
    document.getElementById('aiExplainText').innerHTML = s.explanation;
    document.getElementById('aiFollowup').innerHTML = s.followups.map(f =>
        `<div class="followup-pill" onclick="closeScenarios();switchTab('tutor');askTutor('${f}')">${f}</div>`).join('');
    document.getElementById('aiExplain').classList.add('visible');
}

function nextScenario() { currentScenario = (currentScenario + 1) % scenarios.length; loadScenario(currentScenario); }
function prevScenario() { currentScenario = (currentScenario - 1 + scenarios.length) % scenarios.length; loadScenario(currentScenario); }

// ══════════════════════════════════════════════════════════════
// AI Tutor - COMPLETELY UNTOUCHED
// ══════════════════════════════════════════════════════════════
function askTutor(q) {
    switchTab('tutor');
    document.getElementById('tutorInput').value = q;
    setTimeout(sendTutorMsg, 100);
}

async function sendTutorMsg() {
    const input = document.getElementById('tutorInput');
    const msg = input.value.trim();
    if (!msg) return;

    input.value = '';
    document.getElementById('sendBtn').disabled = true;

    const msgs = document.getElementById('tutorMessages');

    // Add user message
    msgs.innerHTML += `
    <div class="msg user">
      <div class="msg-av user">👤</div>
      <div class="bubble">${escapeHtml(msg)}</div>
    </div>`;

    // Add typing indicator
    const tid = 'typing-' + Date.now();
    msgs.innerHTML += `
    <div class="msg ai" id="${tid}">
      <div class="msg-av ai">🤖</div>
      <div class="bubble">
        <div class="typing-row">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>
    </div>`;

    msgs.scrollTop = msgs.scrollHeight;

    try {
        // Check if AI Integration is initialized
        if (!aiIntegration) {
            throw new Error('AI Integration not initialized. Make sure ai-integration.js is loaded.');
        }

        // Categorize message for better context
        const messageType = aiIntegration.categorizeMessage(msg);

        // Get AI response with full context
        const response = await aiIntegration.sendMessageToAI(msg, messageType);

        // Remove typing indicator and add AI response
        document.getElementById(tid).remove();
        msgs.innerHTML += `
      <div class="msg ai">
        <div class="msg-av ai">🤖</div>
        <div class="bubble">${formatMd(response)}</div>
      </div>`;

    } catch (error) {
        console.error('Tutor API error:', error);

        // Determine the type of error for better user feedback
        let errorMessage = 'I\'m having trouble connecting right now.';
        let errorDetails = '';

        if (error.message.includes('not initialized')) {
            errorMessage = 'AI Integration module not loaded.';
            errorDetails = 'Make sure ai-integration.js is in the same folder as this HTML file.';
        } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            errorMessage = 'Cannot connect to backend server.';
            errorDetails = `Make sure your backend is running on ${aiIntegration?.backendUrl || 'http://localhost:8000'}`;
        } else if (error.message.includes('404')) {
            errorMessage = 'Backend endpoint not found.';
            errorDetails = 'Check that your backend has the /ai/chat endpoint configured.';
        } else if (error.message.includes('500')) {
            errorMessage = 'Backend server error.';
            errorDetails = 'Check your backend logs for details.';
        } else {
            errorDetails = error.message;
        }

        // Remove typing indicator and show error message
        document.getElementById(tid).remove();
        msgs.innerHTML += `
      <div class="msg ai">
        <div class="msg-av ai">⚠️</div>
        <div class="bubble">
          <strong>${errorMessage}</strong><br><br>
          ${errorDetails}
          <div style="font-size:11px;color:var(--txt-muted);margin-top:12px;padding-top:8px;border-top:1px solid var(--border);">
            <strong>Troubleshooting:</strong><br>
            1. Check that ai-integration.js is loaded<br>
            2. Verify backend is running: <code style="background:rgba(0,0,0,0.1);padding:2px 4px;border-radius:3px;">${aiIntegration?.backendUrl || 'http://localhost:8000'}</code><br>
            3. Open browser console (F12) for detailed errors
          </div>
        </div>
      </div>`;
    }

    msgs.scrollTop = msgs.scrollHeight;
    document.getElementById('sendBtn').disabled = false;
    input.focus();
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Helper function to format markdown
function formatMd(text) {
    return text
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/`(.+?)`/g, '<code>$1</code>')
        .replace(/^• (.+)/gm, '<div style="padding-left:12px;margin:2px 0">• $1</div>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');
}

function learnConcept(concept) {
    askTutor(`Explain ${concept} to me, using synthetic indices as examples where possible`);
    addXP(5, 'Started a new concept!');
}

// ══════════════════════════════════════════════════════════════
// Trade Autopsy - Integrated with Deriv API
// ══════════════════════════════════════════════════════════════

// Global state for trades
let pastTradesData = [];
let selectedTradeIds = new Set();

// Toggle between past trades and manual entry
function showPastTrades() {
    document.getElementById('pastTradesSection').style.display = 'block';
    document.getElementById('manualEntrySection').style.display = 'none';
    document.getElementById('btnPastTrades').className = 'btn-primary';
    document.getElementById('btnManualEntry').className = 'btn-secondary';
    document.getElementById('autopsyResult').classList.remove('visible');

    // Auto-fetch trades if not loaded
    if (pastTradesData.length === 0) {
        fetchPastTrades();
    }
}

function showManualEntry() {
    document.getElementById('pastTradesSection').style.display = 'none';
    document.getElementById('manualEntrySection').style.display = 'block';
    document.getElementById('btnPastTrades').className = 'btn-secondary';
    document.getElementById('btnManualEntry').className = 'btn-primary';
    document.getElementById('autopsyResult').classList.remove('visible');
}

// Fetch past trades from Deriv via backend
async function fetchPastTrades() {
    const limit = parseInt(document.getElementById('tradeLimit').value);

    // Show loading
    document.getElementById('tradesLoading').style.display = 'block';
    document.getElementById('tradesTableContainer').style.display = 'none';
    document.getElementById('tradesError').style.display = 'none';

    try {
        if (!aiIntegration) {
            throw new Error('AI Integration not initialized');
        }

        const response = await fetch(`${aiIntegration.backendUrl}/deriv/profit-table?limit=${limit}&sort=DESC`);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Failed to fetch trades: ${response.status}`);
        }

        const data = await response.json();
        pastTradesData = data.transactions || [];

        if (pastTradesData.length === 0) {
            showTradesError('No Trades Found', 'No trading history available in your Deriv account.');
            return;
        }

        renderTradesTable(pastTradesData);

    } catch (error) {
        console.error('Failed to fetch past trades:', error);

        let errorTitle = 'Connection Error';
        let errorMessage = error.message;

        if (error.message.includes('not initialized')) {
            errorTitle = 'AI Integration Not Found';
            errorMessage = 'Make sure ai-integration.js is loaded.';
        } else if (error.message.includes('Failed to fetch')) {
            errorTitle = 'Backend Not Available';
            errorMessage = `Cannot connect to ${aiIntegration?.backendUrl || 'backend'}. Make sure your backend server is running.`;
        } else if (error.message.includes('NetworkError')) {
            errorTitle = 'Network Error';
            errorMessage = 'Check your internet connection and backend server status.';
        }

        showTradesError(errorTitle, errorMessage);
    }
}

// Render trades table
function renderTradesTable(trades) {
    const tbody = document.getElementById('tradesTableBody');
    tbody.innerHTML = '';

    trades.forEach((trade, index) => {
        const buyTime = new Date(trade.buy_time * 1000).toLocaleString();
        const duration = trade.duration ? formatDuration(trade.duration) : 'N/A';
        const profitLoss = parseFloat(trade.profit_loss || 0);
        const isWin = profitLoss >= 0;

        const row = document.createElement('tr');
        row.style.borderBottom = '1px solid var(--border)';
        row.style.transition = 'background 0.2s';
        row.style.cursor = 'pointer';

        row.innerHTML = `
      <td style="padding:12px;">
        <input type="checkbox" class="trade-checkbox" data-index="${index}" 
               onchange="updateSelectedTrades()" style="cursor:pointer;">
      </td>
      <td style="padding:12px;font-size:13px;">${trade.contract_type || 'N/A'}</td>
      <td style="padding:12px;font-size:13px;font-weight:500;">${trade.symbol || 'N/A'}</td>
      <td style="padding:12px;font-size:12px;color:var(--txt-muted);">${buyTime}</td>
      <td style="padding:12px;font-size:13px;">$${parseFloat(trade.buy_price || 0).toFixed(2)}</td>
      <td style="padding:12px;font-size:12px;color:var(--txt-muted);">${duration}</td>
      <td style="padding:12px;font-size:14px;font-weight:600;color:${isWin ? 'var(--profit)' : 'var(--loss)'};">
        ${isWin ? '+' : ''}$${profitLoss.toFixed(2)}
      </td>
    `;

        // Click row to toggle checkbox
        row.onclick = (e) => {
            if (e.target.type !== 'checkbox') {
                const checkbox = row.querySelector('.trade-checkbox');
                checkbox.checked = !checkbox.checked;
                updateSelectedTrades();
            }
        };

        tbody.appendChild(row);
    });

    document.getElementById('tradesLoading').style.display = 'none';
    document.getElementById('tradesTableContainer').style.display = 'block';
    selectedTradeIds.clear();
    updateSelectedTrades();
}

// Format duration
function formatDuration(seconds) {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
}

// Update selected trades count
function updateSelectedTrades() {
    const checkboxes = document.querySelectorAll('.trade-checkbox:checked');
    selectedTradeIds.clear();
    checkboxes.forEach(cb => selectedTradeIds.add(parseInt(cb.dataset.index)));

    document.getElementById('selectedCount').textContent = selectedTradeIds.size;
    document.getElementById('btnAnalyzeSelected').disabled = selectedTradeIds.size === 0;
}

// Toggle select all
function toggleSelectAll() {
    const selectAll = document.getElementById('selectAll').checked;
    document.querySelectorAll('.trade-checkbox').forEach(cb => {
        cb.checked = selectAll;
    });
    updateSelectedTrades();
}

// Show error state
function showTradesError(title, message) {
    document.getElementById('tradesLoading').style.display = 'none';
    document.getElementById('tradesTableContainer').style.display = 'none';
    document.getElementById('tradesError').style.display = 'block';
    document.getElementById('errorTitle').textContent = title;
    document.getElementById('errorMessage').textContent = message;
}

// Analyze selected trades with AI
async function analyzeSelectedTrades() {
    if (selectedTradeIds.size === 0) return;

    const selectedTrades = Array.from(selectedTradeIds).map(index => pastTradesData[index]);

    // Show loading
    const resultEl = document.getElementById('autopsyResult');
    resultEl.classList.add('visible');
    document.getElementById('verdictIcon').textContent = '🔬';
    document.getElementById('verdictLabel').textContent = 'Analyzing...';
    document.getElementById('verdictLabel').className = 'verdict-title';
    document.getElementById('verdictSub').textContent = `Analyzing ${selectedTrades.length} trade(s)...`;
    document.getElementById('autopsyLessons').innerHTML = `
    <div style="color:var(--txt-muted);font-size:12px;padding:20px;text-align:center;">
      <div class="typing-row" style="justify-content:center;">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>`;
    document.getElementById('autopsyNextStep').innerHTML = '';
    document.getElementById('autopsyActions').innerHTML = '';

    try {
        // Build detailed analysis request
        const tradesText = selectedTrades.map((trade, i) => {
            const profitLoss = parseFloat(trade.profit_loss || 0);
            const buyPrice = parseFloat(trade.buy_price || 0);
            const sellPrice = parseFloat(trade.sell_price || 0);

            return `
Trade ${i + 1}:
- Contract: ${trade.contract_type || 'Unknown'}
- Symbol: ${trade.symbol || 'Unknown'}
- Buy Price: $${buyPrice.toFixed(2)}
- Sell Price: $${sellPrice.toFixed(2)}
- Stake: $${buyPrice.toFixed(2)}
- P/L: $${profitLoss.toFixed(2)} (${profitLoss >= 0 ? 'WIN' : 'LOSS'})
- Duration: ${formatDuration(trade.duration || 0)}
- Buy Time: ${new Date(trade.buy_time * 1000).toLocaleString()}
${trade.sell_time ? `- Sell Time: ${new Date(trade.sell_time * 1000).toLocaleString()}` : ''}
      `.trim();
        }).join('\n\n');

        const analysisMessage = `Analyze these ${selectedTrades.length} trades from my Deriv trading history:

${tradesText}

Please provide:
1. **Overall Performance Summary**: Win rate, total P/L, average trade duration
2. **Pattern Detection**: 
   - Are there signs of revenge trading after losses?
   - Overtrading patterns?
   - Time-of-day patterns (when do I win/lose most)?
   - Symbol preferences and performance per symbol
3. **What I'm Doing Well**: Specific strengths in my trading
4. **Key Areas for Improvement**: Critical weaknesses to address
5. **Actionable Recommendations**: Specific, concrete steps to improve
6. **Suggested Learning Topics**: Concepts I should study based on my mistakes

Format your response with clear sections and be specific with numbers and examples from the trades.`;

        const response = await aiIntegration.sendMessageToAI(analysisMessage, 'analysis');

        // Calculate aggregate stats
        const totalPL = selectedTrades.reduce((sum, t) => sum + parseFloat(t.profit_loss || 0), 0);
        const wins = selectedTrades.filter(t => parseFloat(t.profit_loss || 0) >= 0).length;
        const losses = selectedTrades.length - wins;
        const winRate = ((wins / selectedTrades.length) * 100).toFixed(1);
        const avgWin = wins > 0 ? selectedTrades
            .filter(t => parseFloat(t.profit_loss || 0) >= 0)
            .reduce((sum, t) => sum + parseFloat(t.profit_loss || 0), 0) / wins : 0;
        const avgLoss = losses > 0 ? selectedTrades
            .filter(t => parseFloat(t.profit_loss || 0) < 0)
            .reduce((sum, t) => sum + parseFloat(t.profit_loss || 0), 0) / losses : 0;

        // Render results
        document.getElementById('verdictIcon').textContent = totalPL >= 0 ? '✅' : '📉';
        document.getElementById('verdictLabel').textContent = `${selectedTrades.length} Trades Analyzed`;
        document.getElementById('verdictLabel').className = 'verdict-title ' + (totalPL >= 0 ? 'win' : 'loss');
        document.getElementById('verdictSub').textContent =
            `Win Rate: ${winRate}% (${wins}W/${losses}L) | Total P/L: ${totalPL >= 0 ? '+' : ''}$${totalPL.toFixed(2)} | Avg Win: $${avgWin.toFixed(2)} | Avg Loss: $${avgLoss.toFixed(2)}`;

        document.getElementById('autopsyLessons').innerHTML = `
      <div class="lesson-row">
        <div class="lesson-badge">🤖</div>
        <div class="lesson-text"><strong>AI Analysis:</strong><br>${formatMd(response)}</div>
      </div>`;

        document.getElementById('autopsyNextStep').innerHTML =
            `<span style="color:var(--info);font-weight:600;">Next: </span>Review the patterns identified and ask your tutor for specific guidance on improvement areas.`;

        document.getElementById('autopsyActions').innerHTML = `
      <button class="followup-pill" onclick="switchTab('tutor');askTutor('Based on my recent ${selectedTrades.length} trades analysis, what specific habits should I change?')">Ask tutor about habits →</button>
      <button class="followup-pill" onclick="openScenarios()">Practice scenario →</button>`;

        addXP(20, `Analyzed ${selectedTrades.length} trades!`);
        resultEl.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (error) {
        console.error('Analysis failed:', error);
        showAnalysisError(error);
    }
}

// Manual autopsy
async function runManualAutopsy() {
    const instrument = document.getElementById('tradeInstrument').value;
    const dir = document.getElementById('tradeDir').value;
    const entry = parseFloat(document.getElementById('tradeEntry').value) || 0;
    const exitP = parseFloat(document.getElementById('tradeExit').value) || 0;
    const sl = parseFloat(document.getElementById('tradeSL').value) || 0;
    const tp = parseFloat(document.getElementById('tradeTP').value) || 0;
    const result = parseFloat(document.getElementById('tradeResult').value) || 0;
    const level = document.getElementById('traderLevel').value.toLowerCase();
    const thoughts = document.getElementById('tradeThoughts').value;

    // Validate required fields
    if (!entry || !exitP) {
        alert('Please enter at least Entry Price and Exit Price');
        return;
    }

    // Show loading state
    const resultEl = document.getElementById('autopsyResult');
    resultEl.classList.add('visible');
    document.getElementById('verdictIcon').textContent = '🔬';
    document.getElementById('verdictLabel').textContent = 'Analysing...';
    document.getElementById('verdictLabel').className = 'verdict-title';
    document.getElementById('verdictSub').textContent = 'Please wait while we analyse your trade';
    document.getElementById('autopsyLessons').innerHTML = `
    <div style="color:var(--txt-muted);font-size:12px;padding:20px;text-align:center;">
      <div class="typing-row" style="justify-content:center;">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>`;
    document.getElementById('autopsyNextStep').innerHTML = '';
    document.getElementById('autopsyActions').innerHTML = '';

    try {
        if (!aiIntegration) {
            throw new Error('AI Integration not initialized. Make sure ai-integration.js is loaded.');
        }

        // Calculate R:R and other metrics
        const rr = sl && tp ? Math.abs(tp - entry) / Math.abs(entry - sl) : null;
        const hitSL = sl && ((dir.includes('BUY') && exitP <= sl) || (dir.includes('SELL') && exitP >= sl));
        const hitTP = tp && ((dir.includes('BUY') && exitP >= tp) || (dir.includes('SELL') && exitP <= tp));

        // Prepare autopsy request
        const autopsyMessage = `Analyse this ${level} trader's manual trade entry:
      
**Trade Details:**
- Instrument: ${instrument}
- Direction: ${dir}
- Entry Price: ${entry}
- Exit Price: ${exitP}
- Stop Loss: ${sl || 'Not set'}
- Take Profit: ${tp || 'Not set'}
- Result: $${result}
- Risk:Reward Ratio: ${rr ? `1:${rr.toFixed(2)}` : 'Not calculated (no SL/TP)'}
${hitSL ? '- **Hit Stop Loss**: Yes' : ''}
${hitTP ? '- **Hit Take Profit**: Yes' : ''}
${thoughts ? `- Trader's thoughts: "${thoughts}"` : ''}

**Analysis Required:**
1. **Trade Execution Quality**: Was this a good setup? Did they follow proper risk management?
2. **Psychology Check**: Any signs of emotional trading, FOMO, revenge trading, or overconfidence?
3. **Key Lesson**: What's the ONE most important takeaway from this trade?
4. **Specific Improvements**: Concrete actions to take on the next trade
5. **Suggested Concept**: What trading concept should they study based on this trade?

Be specific, actionable, and educational. Use numbers from the trade data.`;

        // Get AI analysis
        const response = await aiIntegration.sendMessageToAI(autopsyMessage, 'analysis');

        // Parse and render the response
        renderAutopsyFromText(response, instrument, dir, result, entry, exitP, sl, tp, rr);

    } catch (error) {
        console.error('Autopsy API failed:', error);
        showAnalysisError(error);
    }

    addXP(15, 'Trade analysed!');
    resultEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderAutopsyFromText(aiResponse, instrument, dir, result, entry, exitP, sl, tp, rr) {
    const isWin = result > 0;

    // Set verdict
    document.getElementById('verdictIcon').textContent = isWin ? '✅' : '📉';
    document.getElementById('verdictLabel').textContent = isWin ? 'Winning Trade' : 'Losing Trade';
    document.getElementById('verdictLabel').className = 'verdict-title ' + (isWin ? 'win' : 'loss');
    document.getElementById('verdictSub').textContent =
        `${instrument} ${dir} | ${result >= 0 ? '+' : ''}$${result.toFixed(2)} | ${rr ? 'R:R 1:' + rr.toFixed(2) : 'No R:R set'}`;

    // Render AI analysis
    document.getElementById('autopsyLessons').innerHTML = `
    <div class="lesson-row">
      <div class="lesson-badge">🤖</div>
      <div class="lesson-text"><strong>AI Analysis:</strong><br>${formatMd(aiResponse)}</div>
    </div>`;

    // Set next steps
    document.getElementById('autopsyNextStep').innerHTML =
        `<span style="color:var(--info);font-weight:600;">Next: </span>Review the analysis above and implement the specific improvements suggested.`;

    document.getElementById('autopsyActions').innerHTML = `
    <button class="followup-pill" onclick="switchTab('tutor');askTutor('Based on my last ${instrument} trade, what should I focus on improving?')">Ask tutor →</button>
    <button class="followup-pill" onclick="openScenarios()">Practice scenario →</button>`;
}

function showAnalysisError(error) {
    let errorTitle = 'Analysis Failed';
    let errorMessage = 'Unable to analyze trades';

    if (error.message.includes('not initialized')) {
        errorTitle = 'AI Not Available';
        errorMessage = 'AI Integration module not loaded. Make sure ai-integration.js is in the same folder.';
    } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        errorTitle = 'Connection Failed';
        errorMessage = `Cannot connect to backend server at ${aiIntegration?.backendUrl || 'http://localhost:8000'}. Make sure it's running.`;
    } else if (error.message.includes('404')) {
        errorTitle = 'Endpoint Not Found';
        errorMessage = 'The /ai/chat endpoint was not found on your backend. Check your API configuration.';
    } else if (error.message.includes('500')) {
        errorTitle = 'Server Error';
        errorMessage = 'Backend server encountered an error. Check your backend logs.';
    } else {
        errorMessage = error.message;
    }

    document.getElementById('verdictIcon').textContent = '⚠️';
    document.getElementById('verdictLabel').textContent = errorTitle;
    document.getElementById('verdictLabel').className = 'verdict-title loss';
    document.getElementById('verdictSub').textContent = errorMessage;
    document.getElementById('autopsyLessons').innerHTML = `
    <div class="lesson-row">
      <div class="lesson-badge">ℹ️</div>
      <div class="lesson-text">
        <strong>Error Details:</strong> ${errorMessage}<br><br>
        <strong>Troubleshooting:</strong><br>
        1. Ensure ai-integration.js is loaded (check browser console)<br>
        2. Verify backend is running: <code style="background:rgba(0,0,0,0.1);padding:2px 4px;border-radius:3px;">${aiIntegration?.backendUrl || 'http://localhost:8000'}</code><br>
        3. Test backend with curl or browser: <code style="background:rgba(0,0,0,0.1);padding:2px 4px;border-radius:3px;">${aiIntegration?.backendUrl || 'http://localhost:8000'}/deriv/profit-table?limit=10</code>
      </div>
    </div>`;
    document.getElementById('autopsyNextStep').innerHTML = '';
    document.getElementById('autopsyActions').innerHTML = '';
}


// ══════════════════════════════════════════════════════════════
// Click Event Listeners Bindings
// ══════════════════════════════════════════════════════════════
document.getElementById('learn-nav-tab').addEventListener('click', () => switchTab('learn'));
document.getElementById('tutor-nav-tab').addEventListener('click', () => switchTab('tutor'));
document.getElementById('autopsy-nav-tab').addEventListener('click', () => switchTab('autopsy'));
document.getElementById('leaderboard-nav-tab').addEventListener('click', () => switchTab('leaderboard'));
document.getElementById('streak-keep-it-going').addEventListener('click', () => openScenarios);
document.getElementById('learning-section-link').addEventListener('click', () => showToast('Rebuilding curriculum from your trades...'));
document.getElementById('path-grid-card-active').addEventListener('click', () => openScenarios);
document.getElementById('rsi-concept-card').addEventListener('click', () => learnConcept('RSI'));
document.getElementById('support-concept-card').addEventListener('click', () => learnConcept('Support & Resistance'));
document.getElementById('macd-concept-card').addEventListener('click', () => learnConcept('MACD'));
document.getElementById('stop-concept-card').addEventListener('click', () => learnConcept('Stop Loss Placement'));
document.getElementById('candle-concept-card').addEventListener('click', () => learnConcept('Candlestick Patterns'));
document.getElementById('risk-concept-card').addEventListener('click', () => learnConcept('Risk:Reward'));
document.getElementById('tutor-pill-link').addEventListener('click', () => { switchTab('tutor'); askTutor('Why do I keep closing trades too early?') });
document.getElementById('close-modal-scenario').addEventListener('click', () => closeScenarios);
document.getElementById('btn-previous').addEventListener('click', () => prevScenario);
document.getElementById('btn-next-scenario').addEventListener('click', () => nextScenario);
document.getElementById('tutorInput').addEventListener('keydown', (event) => { if (event.key === 'Enter') sendTutorMsg() });
document.getElementById('sendBtn').addEventListener('click', () => sendTutorMsg);
document.getElementById('btnPastTrades').addEventListener('click', () => showPastTrades);
document.getElementById('btnManualEntry').addEventListener('click', () => showManualEntry);
document.getElementById('fetch-past-trades').addEventListener('click', () => fetchPastTrades);
document.getElementById('btnAnalyzeSelected').addEventListener('click', () => analyzeSelectedTrades);
document.getElementById('btn-autopsy-run').addEventListener('click', () => runManualAutopsy);
document.getElementById('selectAll').addEventListener('click', () => toggleSelectAll);