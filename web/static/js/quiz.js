/**
 * Thomas Young Simulator — Interactive Classroom Quiz Module
 * Real-time grading, feedback, score tracking, and KaTeX rendering.
 */

const ClassroomQuiz = (function () {
    let quizQuestions = [];
    let currentQIndex = 0;
    let score = 0;
    let answered = 0;
    let isLocked = false;
    let lastChosen = null;
    let currentLang = 'fa';

    function init(quizData, lang) {
        quizQuestions = quizData || [];
        currentQIndex = 0;
        score = 0;
        answered = 0;
        isLocked = false;
        lastChosen = null;
        currentLang = lang || 'fa';
    }

    function setLanguage(lang) {
        currentLang = lang;
        // keepLock=true: re-rendering in the other language must not unlock an
        // already-answered question (that allowed the score to be double-counted).
        renderQuestion(currentQIndex, true);
    }

    function renderQuestion(qIndex, keepLock) {
        if (!quizQuestions || quizQuestions.length === 0) return;
        const targetIndex = Math.max(0, Math.min(quizQuestions.length - 1, qIndex));
        const preserve = Boolean(keepLock) && targetIndex === currentQIndex && isLocked;
        currentQIndex = targetIndex;
        if (!preserve) {
            isLocked = false;
            lastChosen = null;
        }

        const q = quizQuestions[currentQIndex];
        const isFa = currentLang === 'fa';
        const qTextEl = document.getElementById('quiz-q-text');
        const optionsWrapper = document.getElementById('quiz-options-wrapper');
        const feedbackCard = document.getElementById('quiz-feedback-card');

        if (!qTextEl || !optionsWrapper) return;

        // Hide feedback card
        if (feedbackCard) feedbackCard.style.display = 'none';

        // Question title
        qTextEl.textContent = isFa ? q.q_fa : q.q_en;

        // Options
        const opts = isFa ? q.opts_fa : q.opts_en;
        const faNums = ['۱', '۲', '۳', '۴'];

        optionsWrapper.innerHTML = '';
        opts.forEach((optText, idx) => {
            const btn = document.createElement('button');
            btn.className = 'quiz-opt-btn';
            const numPrefix = isFa ? `${faNums[idx]}. ` : `${idx + 1}. `;
            btn.innerHTML = `<span style="color:var(--accent-cyan); font-weight:700;">${numPrefix}</span><span>${optText}</span>`;
            btn.onclick = () => answerQuestion(idx);
            optionsWrapper.appendChild(btn);
        });

        updateScoreBadge();

        // Re-apply answered/locked visuals after a keepLock re-render
        if (preserve) applyAnsweredVisuals();

        // Render KaTeX for any mathematical notations
        if (window.renderMathInElement) {
            window.renderMathInElement(document.getElementById('quiz-container-box'), {
                delimiters: [
                    { left: '$$', right: '$$', display: true },
                    { left: '$', right: '$', display: false }
                ],
                throwOnError: false
            });
        }
    }

    function applyAnsweredVisuals() {
        const q = quizQuestions[currentQIndex];
        const isFa = currentLang === 'fa';
        const chosenIndex = lastChosen;
        const isCorrect = chosenIndex === q.correct;

        const optionButtons = document.querySelectorAll('.quiz-opt-btn');
        optionButtons.forEach((btn, idx) => {
            btn.disabled = true;
            btn.classList.add('disabled');
            if (idx === q.correct) {
                btn.classList.add('correct');
            } else if (idx === chosenIndex) {
                btn.classList.add('wrong');
            }
        });

        // Show feedback card
        const feedbackCard = document.getElementById('quiz-feedback-card');
        const feedbackTitle = document.getElementById('quiz-feedback-title');
        const feedbackExpl = document.getElementById('quiz-feedback-explanation');

        if (feedbackCard && feedbackTitle && feedbackExpl) {
            feedbackCard.className = `feedback-card ${isCorrect ? 'correct' : 'wrong'}`;
            feedbackTitle.textContent = isCorrect
                ? (isFa ? '✓ آفرین! پاسخ درست است.' : '✓ Correct! Well done.')
                : (isFa ? '✗ درست نیست. توضیح زیر را بخوانید:' : '✗ Not quite. See explanation below:');
            feedbackExpl.textContent = isFa ? q.explain_fa : q.explain_en;
            feedbackCard.style.display = 'flex';
        }

        updateScoreBadge();
    }

    function answerQuestion(chosenIndex) {
        if (isLocked) return;
        isLocked = true;
        lastChosen = chosenIndex;
        answered++;

        const q = quizQuestions[currentQIndex];
        if (chosenIndex === q.correct) score++;

        applyAnsweredVisuals();
    }

    function updateScoreBadge() {
        const badge = document.getElementById('quiz-score-badge');
        if (!badge) return;
        const isFa = currentLang === 'fa';
        badge.textContent = isFa
            ? `امتیاز: ${score} از ${answered} سوال`
            : `Score: ${score} of ${answered} questions`;
    }

    function reset() {
        score = 0;
        answered = 0;
        currentQIndex = 0;
        renderQuestion(0);
    }

    return {
        init,
        setLanguage,
        renderQuestion,
        answerQuestion,
        reset
    };
})();
