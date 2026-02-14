// ── State ──
let chosen = null;
let profileData = { left: null, right: null };
let cardsReady = false;

// ── Claude API helper (via local proxy) ───────────────────────────────────────
// The proxy at /api/claude adds your API key server-side, so it never
// touches the browser. Change PROXY_URL if you deploy elsewhere.

const BACKEND_URL = "http://localhost:8000";
const PROXY_URL = BACKEND_URL + "/api/claude";

// Get user session — check URL param first (passed from extension), then localStorage
function getUserSession() {
  try {
    const params = new URLSearchParams(window.location.search);
    const encoded = params.get('session');

    if (encoded) {
      const decoded = decodeURIComponent(atob(encoded));
      localStorage.setItem('user_session', decoded);

      window.history.replaceState({}

        , '', window.location.pathname);
      return JSON.parse(decoded);
    }

    const raw = localStorage.getItem('user_session');
    return raw ? JSON.parse(raw) : null;
  }

  catch {
    return null;
  }
}

async function callClaude(systemPrompt, userMessage) {
  const response = await fetch(PROXY_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1000,
      system: systemPrompt,
      messages: [{ role: "user", content: userMessage }]
    })
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Proxy error ${response.status}: ${err}`);
  }

  const data = await response.json();
  const raw = data.content.map(b => b.text || "").join("");
  // Strip markdown code fences if the model wraps its JSON
  return raw.replace(/^```json\s*/i, "").replace(/```\s*$/, "").trim();
}


// ── Generate both strategy cards on load ──
async function generateStrategyCards() {
  const systemPrompt = `You are a trading education AI for PocketPT, a retail trading app. 
Generate two contrasting trading strategy profiles in valid JSON only — no extra text, no markdown fences.
The JSON must match this exact shape:
{
  "strategies": [
    {
      "side": "left",
      "icon": "emoji",
      "title": "Strategy Name",
      "subtitle": "Style descriptor · Technique",
      "description": "2 sentences. Second-person, energetic. Include <em> on a key phrase.",
      "traits": [
        { "icon": "emoji", "label": "Trait name", "detail": "one sentence explanation" },
        { "icon": "emoji", "label": "Trait name", "detail": "one sentence explanation" },
        { "icon": "emoji", "label": "Trait name", "detail": "one sentence explanation" },
        { "icon": "emoji", "label": "Trait name", "detail": "one sentence explanation" }
      ],
      "metrics": {
        "winRate": "40–50%",
        "rr": "1:3+",
        "speed": "Fast"
      },
      "psychTags": ["tag1", "tag2", "tag3", "tag4"],
      "colorClass": "red",
      "btnLabel": "Choose [Name] →"
    },
    {
      "side": "right",
      "icon": "emoji",
      "title": "Strategy Name",
      "subtitle": "Style descriptor · Technique",
      "description": "2 sentences. Second-person, calm. Include <em> on a key phrase.",
      "traits": [
        { "icon": "emoji", "label": "Trait name", "detail": "one sentence explanation" },
        { "icon": "emoji", "label": "Trait name", "detail": "one sentence explanation" },
        { "icon": "emoji", "label": "Trait name", "detail": "one sentence explanation" },
        { "icon": "emoji", "label": "Trait name", "detail": "one sentence explanation" }
      ],
      "metrics": {
        "winRate": "60–70%",
        "rr": "1:1.5",
        "speed": "Slow"
      },
      "psychTags": ["tag1", "tag2", "tag3", "tag4"],
      "colorClass": "teal",
      "btnLabel": "Choose [Name] →"
    }
  ]
}
Strategy A (left/red) should be a high-energy, trend-following style (momentum, breakouts, fast decisions).
Strategy B (right/teal) should be a patient, analytical style (mean reversion, counter-trend, careful entries).
Keep descriptions punchy and authentic to retail traders. Vary the exact framing each time.`;

  try {
    const raw = await callClaude(systemPrompt, "Generate two trading strategy profiles for PocketPT onboarding.");
    const parsed = JSON.parse(raw);
    parsed.strategies.forEach(s => { profileData[s.side] = s; });
    renderCards();
    cardsReady = true;
  } catch (err) {
    showCardError('left', err);
    showCardError('right', err);
  }
}

function showCardError(side, err) {
  document.getElementById('body-' + side).innerHTML = `
    <div class="error-msg">
      <strong>Failed to load profile.</strong> ${err.message}<br>
      <button class="btn-ghost" style="margin-top:10px;font-size:12px" id='btnGhostRetry">↻ Retry</button>
    </div>`;
}

function renderCards() {
  ['left', 'right'].forEach(side => {
    const p = profileData[side];
    if (!p) return;
    const colorClass = p.colorClass || (side === 'left' ? 'red' : 'teal');

    // Hero
    document.getElementById('hero-' + side + '-content').innerHTML = `
      <div class="card-icon">${p.icon}</div>
      <div class="card-title">${p.title}</div>
      <div class="card-subtitle">${p.subtitle}</div>`;

    // Body
    document.getElementById('body-' + side).innerHTML = `
      <p class="card-desc">${p.description}</p>
      <div class="trait-list">
        ${p.traits.map(t => `
          <div class="trait-row">
            <div class="trait-icon">${t.icon}</div>
            <div class="trait-text"><strong>${t.label}</strong> — ${t.detail}</div>
          </div>`).join('')}
      </div>
      <div class="metrics-strip">
        <div class="metric">
          <div class="metric-val ${colorClass}">${p.metrics.winRate}</div>
          <div class="metric-label">Win Rate</div>
        </div>
        <div class="metric">
          <div class="metric-val ${colorClass}">${p.metrics.rr}</div>
          <div class="metric-label">Avg R:R</div>
        </div>
        <div class="metric">
          <div class="metric-val ${colorClass}">${p.metrics.speed}</div>
          <div class="metric-label">Decision Speed</div>
        </div>
      </div>
      <div class="psych-tags">
        ${p.psychTags.map(tag => `<div class="psych-tag">${tag}</div>`).join('')}
      </div>
      <button class="select-btn select-btn-${side}" id="btn-${side}">${p.btnLabel}</button>`;
  });
}

// ── Strategy selection ──
function selectStrategy(side) {
  if (!cardsReady) return; // don't allow clicks while loading
  if (chosen === side) return;
  chosen = side;
  const other = side === 'left' ? 'right' : 'left';

  document.getElementById('card-' + side).className = 'strategy-card selected-' + side;
  document.getElementById('card-' + other).className = 'strategy-card unselected';

  const btnSide = document.getElementById('btn-' + side);
  const btnOther = document.getElementById('btn-' + other);
  if (btnSide) { btnSide.textContent = '✓ Selected'; btnSide.classList.add('chosen'); }
  if (btnOther) {
    const otherProfile = profileData[other];
    btnOther.textContent = otherProfile ? otherProfile.btnLabel : (other === 'left' ? 'Choose Momentum →' : 'Choose Precision →');
    btnOther.classList.remove('chosen');
  }

  showResultPanel(side);
  addXP(25, 'Trading style chosen!');
}

// ── AI-generated result panel ──
async function showResultPanel(side) {
  const p = profileData[side];
  const panel = document.getElementById('resultPanel');

  // Show panel immediately with skeleton/loading state
  document.getElementById('resultIcon').textContent = p.icon;
  document.getElementById('resultTitle').textContent = p.title + ' selected';
  document.getElementById('resultDesc').textContent = 'Generating your personalised profile…';
  document.getElementById('insightGrid').innerHTML = `
    <div class="insight-card"><div class="skeleton skel-line" style="height:40px;border-radius:6px"></div></div>
    <div class="insight-card"><div class="skeleton skel-line" style="height:40px;border-radius:6px"></div></div>
    <div class="insight-card"><div class="skeleton skel-line" style="height:40px;border-radius:6px"></div></div>
    <div class="insight-card"><div class="skeleton skel-line" style="height:40px;border-radius:6px"></div></div>`;
  document.getElementById('aiResultText').innerHTML = `
    <div class="loading-indicator">
      <div class="loading-dots"><span></span><span></span><span></span></div>
      AI personalising your insight…
    </div>`;
  document.getElementById('aiResultText').className = 'ai-insight-text-result' + (side === 'right' ? ' teal' : '');
  document.getElementById('resultFooter').innerHTML = '';
  panel.classList.add('visible');
  setTimeout(() => panel.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);

  // Ask Claude for personalised result panel content
  const systemPrompt = `You are a trading psychology AI tutor for PocketPT. Generate a personalised result panel in valid JSON only — no markdown, no extra text.
JSON shape:
{
  "desc": "short subtitle, 1 line, lowercase",
  "insights": [
    { "label": "First Lesson", "val": "topic name" },
    { "label": "Watch out for", "val": "common pitfall" },
    { "label": "Key Indicator", "val": "indicator name" },
    { "label": "Best Instrument", "val": "market / pair" }
  ],
  "aiText": "2–3 sentences. Use <strong> for key warnings, <em> for emphasis. Address the user directly. Identify their #1 early challenge and what their first lessons will fix."
}`;

  try {
    const raw = await callClaude(
      systemPrompt,
      `The user chose the "${p.title}" style (${p.subtitle}). Their traits: ${p.traits.map(t => t.label).join(', ')}. Their psych profile: ${p.psychTags.join(', ')}. Generate a personalised result panel for them.`
    );
    const result = JSON.parse(raw);

    document.getElementById('resultDesc').textContent = result.desc;
    document.getElementById('insightGrid').innerHTML = result.insights.map(i => `
      <div class="insight-card">
        <div class="insight-label">${i.label}</div>
        <div class="insight-val">${i.val}</div>
      </div>`).join('');
    document.getElementById('aiResultText').innerHTML = result.aiText;
    document.getElementById('resultFooter').innerHTML = `
      <button class="btn-primary${side === 'right' ? ' teal' : ''}">Start My Curriculum →</button>
      <button class="btn-ghost">← Change my mind</button>`;

  } catch (err) {
    document.getElementById('aiResultText').innerHTML = `
      <div class="error-msg">
        <strong>Couldn't generate insight.</strong> ${err.message}<br>
        <button class="btn-ghost" style="margin-top:10px;font-size:12px" onclick="showResultPanel('${side}')">↻ Retry</button>
      </div>`;
    document.getElementById('resultFooter').innerHTML = `
      <button class="btn-primary${side === 'right' ? ' teal' : ''}">Start My Curriculum →</button>
      <button class="btn-ghost">← Change my mind</button>`;
  }
}

function resetChoice() {
  chosen = null;
  ['left', 'right'].forEach(side => {
    document.getElementById('card-' + side).className = 'strategy-card';
    const btn = document.getElementById('btn-' + side);
    if (btn) { btn.classList.remove('chosen'); btn.textContent = profileData[side] ? profileData[side].btnLabel : '—'; }
  });
  document.getElementById('resultPanel').classList.remove('visible');
}

// ── XP ──
function addXP(amount, reason) {
  document.getElementById('xpAmount').textContent = '+' + amount + ' XP';
  document.getElementById('xpReason').textContent = reason;
  const t = document.getElementById('xpToast');
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2800);
}

// ── Save trader type & generate curriculum ──
async function startCurriculum() {
  if (!chosen) return;

  const traderType = chosen === 'left' ? 'momentum' : 'precision';
  const session = getUserSession();

  if (!session || !session.id) {
    localStorage.setItem('tradept_trader_type', traderType);
    alert('No session found. Please log in first.');
    return;
  }

  // 1. Save trader type
  let updatedUser = session;

  try {
    const resp = fetch(`${BACKEND_URL}/users/${session.id}/trader-type`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      }

      ,
      body: JSON.stringify({
        trader_type: traderType
      })
    });

    if (resp.ok) {
      updatedUser = await resp.json();
      localStorage.setItem('user_session', JSON.stringify(updatedUser));
    }
  }

  catch (err) {
    console.error('Failed to save trader type:', err);
  }

  // 2. Show progress overlay
  const overlay = document.getElementById('progressOverlay');
  overlay.style.display = 'flex';
  const fill = document.getElementById('curriculumProgressFill');
  const pct = document.getElementById('progressPercent');
  const txt = document.getElementById('progressText');

  // Animate fake progress (0 → 80% over 4s while API runs)
  let progress = 0;

  const progressInterval = setInterval(() => {
    if (progress < 80) {
      progress += 2;
      fill.style.width = progress + '%';
      pct.textContent = progress + '%';
    }

    if (progress === 20) txt.textContent = 'Generating AI-powered questions...';
    if (progress === 50) txt.textContent = 'Building personalized modules...';
    if (progress === 70) txt.textContent = 'Almost ready...';
  }

    , 100);

  // 3. Generate curriculum
  try {
    const genResp = fetch(`${BACKEND_URL}/education/generate-curriculum`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }

      ,
      body: JSON.stringify({
        user_id: session.id
      })
    });

    clearInterval(progressInterval);

    if (genResp.ok) {
      const result = await genResp.json();
      fill.style.width = '100%';
      pct.textContent = '100%';

      txt.textContent = `Curriculum ready! ${result.generated + result.cached} modules loaded.`;

      // Redirect to dashboard after brief pause
      setTimeout(() => {
        const encoded = btoa(encodeURIComponent(JSON.stringify(updatedUser)));

        window.location.href = `/static/trading_edu.html?session=${encoded}`;
      }

        , 1200);
    }

    else {
      throw new Error('Generation failed');
    }
  }

  catch (err) {
    clearInterval(progressInterval);
    console.error('Curriculum generation failed:', err);
    txt.textContent = 'Generation failed. Redirecting...';
    fill.style.background = '#ff4444';

    // Still redirect to dashboard (quizzes can be generated on-demand)
    setTimeout(() => {
      const encoded = btoa(encodeURIComponent(JSON.stringify(updatedUser)));

      window.location.href = `/static/trading_edu.html?session=$ {
                encoded
            }

            `;
    }

      , 1500);
  }
}

// ── Init ──
generateStrategyCards();


// ══════════════════════════════════════════════════════════════
// Click Event Listeners Bindings
// ══════════════════════════════════════════════════════════════
document.getElementById('card-left').addEventListener('click', () => selectStrategy('left'));
document.getElementById('card-right').addEventListener('click', () => selectStrategy('right'));
document.querySelector('.btn-primary').addEventListener('click', () => {
  addXP(50, 'Curriculum started!');
});

document.querySelector('.btn-ghost').addEventListener('click', resetChoice);
document.querySelector('#btnGhostRetry').addEventListener('click', generateStrategyCards);