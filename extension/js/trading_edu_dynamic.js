/**
 * Dynamic module loading and progress tracking for trading_edu.html
 */

const API_BASE = "http://localhost:8000";
let currentUserId = 1; // TODO: Get from session

// Load user progress on page load
document.addEventListener("DOMContentLoaded", async () => {
    await loadUserProgress();
    await loadModules();
    checkURLForModule();
});

async function loadUserProgress() {
    try {
        const response = await fetch(`${API_BASE}/education/progress/${currentUserId}`);
        const data = await response.json();

        // Update UI with progress data
        document.getElementById("xpCount").textContent = data.total_exp;
        document.getElementById("streakCount").textContent = data.current_streak_days;

        // Update skill bars
        updateSkillBar("Technical_Analysis", data.skill_scores.Technical_Analysis);
        updateSkillBar("Risk_Management", data.skill_scores.Risk_Management);
        updateSkillBar("Psychology", data.skill_scores.Psychology);
        updateSkillBar("Market_Structure", data.skill_scores.Market_Structure);

        // Update learning path progress
        updateLearningPathProgress(data.category_progress);

    } catch (error) {
        console.error("Failed to load user progress:", error);
    }
}

async function loadModules() {
    try {
        const response = await fetch(`${API_BASE}/education/modules?user_id=${currentUserId}`);
        const modules = await response.json();

        renderConceptsToMaster(modules);

    } catch (error) {
        console.error("Failed to load modules:", error);
    }
}

function checkURLForModule() {
    const urlParams = new URLSearchParams(window.location.search);
    const moduleId = urlParams.get("module");

    if (moduleId) {
        openModule(parseInt(moduleId));
    }
}

async function openModule(moduleId) {
    try {
        const response = await fetch(`${API_BASE}/education/modules/${moduleId}?user_id=${currentUserId}`);
        const module = await response.json();

        // Switch to a module view
        displayModuleContent(module);

    } catch (error) {
        console.error("Failed to load module:", error);
    }
}

function displayModuleContent(module) {
    // Create module page HTML
    const modulePage = `
    <div class="module-page">
      <button onclick="window.location.reload()" class="back-btn">← Back to Dashboard</button>
      
      <div class="module-header">
        <h1>${module.title}</h1>
        <div class="module-meta">
          <span class="badge">${module.difficulty}</span>
          <span>🕐 ${module.estimated_minutes} min</span>
          <span>💎 ${module.exp_reward} XP</span>
        </div>
      </div>

      <div class="module-content">
        ${module.content.map(section => `
          <div class="section ${section.type}">
            ${section.title ? `<h3>${section.title}</h3>` : ''}
            ${Array.isArray(section.content) ?
            `<ul>${section.content.map(item => `<li>${item}</li>`).join('')}</ul>` :
            `<p>${section.content}</p>`}
          </div>
        `).join('')}
      </div>

      <div class="quiz-section">
        <h2>📝 Knowledge Check</h2>
        ${module.quiz.map((q, i) => `
          <div class="quiz-question">
            <p><strong>Question ${i + 1}:</strong> ${q.question}</p>
            ${q.options.map((opt) => `
              <label>
                <input type="radio" name="q${i}" value="${opt.charAt(0)}">
                ${opt}
              </label>
            `).join('')}
          </div>
        `).join('')}
        
        <button onclick="submitQuiz(${module.id})" class="btn-primary">Submit Quiz</button>
      </div>
    </div>
  `;

    // Replace main content
    document.querySelector(".app").innerHTML = modulePage;
}

async function submitQuiz(moduleId) {
    const answers = [];
    const quizQuestions = document.querySelectorAll(".quiz-question");

    quizQuestions.forEach((q, i) => {
        const selected = q.querySelector(`input[name="q${i}"]:checked`);
        if (selected) {
            answers.push(selected.value);
        }
    });

    if (answers.length < quizQuestions.length) {
        alert("Please answer all questions");
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/education/quiz/submit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: currentUserId,
                module_id: moduleId,
                answers: answers
            })
        });

        const result = await response.json();

        // Show results
        showQuizResults(result);

    } catch (error) {
        console.error("Failed to submit quiz:", error);
    }
}

function showQuizResults(result) {
    const resultHTML = `
    <div class="quiz-results">
      <h2>${result.passed ? '🎉 Congratulations!' : '📚 Keep Learning!'}</h2>
      <p>Score: ${result.score}%</p>
      <p>Correct: ${result.correct_count}/${result.total_questions}</p>
      ${result.passed ? `<p class="exp-earned">+${result.exp_earned} XP</p>` : ''}
      
      <div class="explanations">
        ${result.explanations.map(exp => `
          <div class="explanation ${exp.correct ? 'correct' : 'incorrect'}">
            <strong>Question ${exp.question_number}:</strong> 
            ${exp.correct ? '✅' : '❌'}
            <p>${exp.explanation}</p>
          </div>
        `).join('')}
      </div>

      <button onclick="location.reload()" class="btn-primary">
        ${result.passed ? 'Back to Dashboard' : 'Try Again'}
      </button>
    </div>
  `;

    document.querySelector(".quiz-section").innerHTML = resultHTML;

    // Show XP toast if passed
    if (result.passed) {
        showXPToast(result.exp_earned, "Module Completed!");
    }
}

function showXPToast(amount, reason) {
    const toast = document.getElementById("xpToast");
    if (toast) {
        document.getElementById("xpAmount").textContent = `+${amount} XP`;
        document.getElementById("xpReason").textContent = reason;
        toast.classList.add("show");

        setTimeout(() => {
            toast.classList.remove("show");
        }, 3000);
    }
}

function updateSkillBar(skillName, value) {
    // Update the skill profile bars in the dashboard
    const skillBars = document.querySelectorAll(".skill-bar");
    skillBars.forEach(bar => {
        if (bar.dataset.skill === skillName) {
            bar.querySelector(".fill").style.width = `${value}%`;
            const valueEl = bar.querySelector(".skill-value");
            if (valueEl) valueEl.textContent = value;
        }
    });
}

function updateLearningPathProgress(categoryProgress) {
    // Update the learning path cards with actual progress
    Object.keys(categoryProgress).forEach(category => {
        const progress = categoryProgress[category];
        const card = document.querySelector(`[data-category="${category}"]`);
        if (card) {
            const progressBar = card.querySelector(".progress-fill");
            const progressPct = card.querySelector(".progress-pct");

            if (progressBar) progressBar.style.width = `${progress.percentage}%`;
            if (progressPct) progressPct.textContent = `${progress.percentage}%`;

            const badge = card.querySelector(".path-badge");
            if (badge) badge.textContent = `${progress.completed} / ${progress.total}`;
        }
    });
}

function renderConceptsToMaster(modules) {
    const conceptsGrid = document.querySelector(".concepts-grid");
    if (!conceptsGrid) return;

    conceptsGrid.innerHTML = modules.slice(0, 6).map(module => {
        const status = module.progress?.status || "not_started";
        const statusText = status === "completed" ? "✓ Completed" :
            status === "in_progress" ? "→ Up next" :
                "→ Start here";

        return `
      <div class="concept-card ${status === 'completed' ? 'done' : ''}" onclick="openModule(${module.id})">
        <div class="concept-icon">📚</div>
        <div class="concept-title">${module.title}</div>
        <div class="concept-status ${status === 'completed' ? 'done' : 'todo'}">${statusText}</div>
      </div>
    `;
    }).join('');
}

// Make functions global for inline onclick handlers
window.openModule = openModule;
window.submitQuiz = submitQuiz;