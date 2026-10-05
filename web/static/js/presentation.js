/**
 * Thomas Young Simulator — Web Presentation Controller
 * Orchestrates slide deck navigation, KaTeX mathematical typesetting,
 * dynamic language switching, and interactive optics laboratory.
 */

let appData = {
    slides: [],
    quiz: [],
    sections: [],
    section_titles: {},
    guide_modules: [],
    defaults: {}
};

let currentSection = 'history'; // 'history' | 'guide' | 'lab'
let currentSlideIndex = 0;
let currentGuideIndex = 0;
let currentLanguage = 'fa';

document.addEventListener('DOMContentLoaded', () => {
    // 1. Load initial data from embedded JSON script
    const payloadEl = document.getElementById('initial-payload');
    if (payloadEl && payloadEl.textContent) {
        try {
            appData = JSON.parse(payloadEl.textContent);
        } catch (e) {
            console.error('Failed to parse initial presentation payload:', e);
        }
    }

    // 2. Initialize Quiz
    ClassroomQuiz.init(appData.quiz, currentLanguage);

    // 3. Handle URL hash routing (#history, #guide, #lab)
    const hash = window.location.hash.replace('#', '');
    if (hash === 'guide') {
        switchSection('guide');
    } else if (hash === 'lab') {
        switchSection('lab');
    } else {
        switchSection('history');
    }

    // Keep browser Back/Forward in sync with the visible section.
    // switchSection rewrites the same hash, which does not re-fire this event.
    window.addEventListener('hashchange', () => {
        const section = window.location.hash.replace('#', '');
        if ((section === 'history' || section === 'guide' || section === 'lab')
            && section !== currentSection) {
            switchSection(section);
        }
    });

    // 4. Keyboard Shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);

    // 5. Initial Math rendering
    triggerMathRendering();
});

/**
 * Switch top-level modes: History / Guide / Live Lab
 */
function switchSection(section) {
    currentSection = section;
    PhysicsAnimations.stopAllAnimations();

    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    const activeBtn = document.getElementById(`btn-mode-${section}`);
    if (activeBtn) activeBtn.classList.add('active');

    const slideCard = document.getElementById('slide-card-container');
    const labCard = document.getElementById('live-lab-card');
    const footer = document.querySelector('.presentation-footer');

    if (section === 'lab') {
        slideCard.style.display = 'none';
        labCard.style.display = 'flex';
        footer.style.display = 'none';
        updateLabSimulation();
    } else {
        slideCard.style.display = 'flex';
        labCard.style.display = 'none';
        footer.style.display = 'flex';

        if (section === 'guide') {
            renderGuideModule(currentGuideIndex);
        } else {
            renderHistorySlide(currentSlideIndex);
        }
    }

    window.location.hash = section;
}

/**
 * Checks if a string represents an isolated, pure mathematical equation
 * without descriptive Persian sentences.
 */
function isPureFormula(text) {
    if (!text) return false;
    const clean = text.trim();
    // If it contains Persian/Arabic characters, it is NOT an isolated formula card
    if (/[؀-ۿ]/.test(clean)) return false;
    if (clean.length > 85) return false;

    return clean.startsWith('Δy =') || clean.startsWith('Δr =') || clean.startsWith('Δφ =') ||
           clean.startsWith('d · sinθ =') || clean.startsWith('d · sin') || clean.startsWith('a · sinθ =') ||
           clean.startsWith('I = 4I₀') || clean.startsWith('λ =');
}

/**
 * Converts pure math formula string to clean LaTeX for KaTeX display
 */
function convertFormulaToLatex(str) {
    const s = str.trim();
    if (s.includes('Δy = λL / d = 2.53 mm') || s.includes('Δy = λL/d = 2.53 mm')) {
        return '\\Delta y = \\frac{\\lambda L}{d} = 2.53\\text{ mm}';
    }
    if (s === 'Δy = λL / d' || s === 'Δy = λL/d') {
        return '\\Delta y = \\frac{\\lambda L}{d}';
    }
    if (s === 'Δr = d · sinθ') {
        return '\\Delta r = d \\cdot \\sin\\theta';
    }
    if (s === 'Δφ = 2πΔr / λ') {
        return '\\Delta\\phi = \\frac{2\\pi \\Delta r}{\\lambda}';
    }
    if (s.includes('d · sinθ = mλ')) {
        return 'd \\cdot \\sin\\theta = m\\lambda \\quad (m = 0, \\pm 1, \\pm 2, \\dots)';
    }
    if (s.includes('d · sinθ = (m + ½)λ')) {
        return 'd \\cdot \\sin\\theta = \\left(m + \\frac{1}{2}\\right)\\lambda';
    }
    if (s.includes('I = 4I₀') && s.includes('cos²')) {
        return 'I = 4I_0 \\cos^2\\left(\\frac{\\Delta\\phi}{2}\\right)';
    }
    if (s.includes('a · sinθ = mλ')) {
        return 'a \\cdot \\sin\\theta = m\\lambda \\quad (m = \\pm 1, \\pm 2, \\dots)';
    }

    return s.replace(/·/g, ' \\cdot ')
            .replace(/Δy/g, '\\Delta y')
            .replace(/Δr/g, '\\Delta r')
            .replace(/Δφ/g, '\\Delta\\phi')
            .replace(/sinθ/g, '\\sin\\theta')
            .replace(/sin/g, '\\sin ')
            .replace(/cos²/g, '\\cos^2')
            .replace(/θ/g, '\\theta')
            .replace(/λL/g, '\\lambda L')
            .replace(/λ/g, '\\lambda ')
            .replace(/I₀/g, 'I_0')
            .replace(/½/g, '\\frac{1}{2}')
            .replace(/×10⁻⁹/g, '\\times 10^{-9}')
            .replace(/×10⁻³/g, '\\times 10^{-3}');
}

/**
 * Trigger smooth CSS entrance animation on slide card
 */
function triggerSlideCardAnimation() {
    const card = document.getElementById('slide-card-container');
    if (card) {
        card.classList.remove('transitioning');
        void card.offsetWidth; // Force CSS DOM reflow
        card.classList.add('transitioning');
    }
}

/**
 * Render standard History / Theory slide
 */
function renderHistorySlide(index) {
    PhysicsAnimations.stopAllAnimations();
    const totalSlides = (appData.slides.length || 0) + (appData.quiz.length || 0);
    currentSlideIndex = Math.max(0, Math.min(totalSlides - 1, index));
    const isFa = currentLanguage === 'fa';

    // Trigger smooth slide transition
    triggerSlideCardAnimation();

    // Update progress banner
    const pill = document.getElementById('current-chapter-badge');
    const counter = document.getElementById('current-slide-counter');
    const progressFill = document.getElementById('slide-progress-fill');
    const pct = ((currentSlideIndex + 1) / totalSlides) * 100;
    progressFill.style.width = `${pct}%`;

    const titleEl = document.getElementById('slide-title-text');
    const paragraphsBox = document.getElementById('slide-paragraphs-box');
    const diagramBox = document.getElementById('diagram-container-box');
    const mediaWrapper = document.getElementById('diagram-media-wrapper');
    const captionEl = document.getElementById('diagram-caption-text');
    const quizBox = document.getElementById('quiz-container-box');

    paragraphsBox.innerHTML = '';
    mediaWrapper.innerHTML = '';

    if (currentSlideIndex < appData.slides.length) {
        // Content Slide
        quizBox.style.display = 'none';
        diagramBox.style.display = 'flex';

        const slide = appData.slides[currentSlideIndex];
        const secInfo = appData.section_titles[slide.section] || ['', '', ''];
        pill.textContent = isFa ? secInfo[1] : secInfo[2];
        counter.textContent = isFa
            ? `اسلاید ${currentSlideIndex + 1} از ${totalSlides}`
            : `Slide ${currentSlideIndex + 1} of ${totalSlides}`;

        titleEl.textContent = isFa ? slide.title_fa : slide.title_en;

        const paras = isFa ? slide.body_fa : slide.body_en;
        paras.forEach(p => {
            if (isPureFormula(p)) {
                // Isolated pure mathematical equation rendered with KaTeX
                const fCard = document.createElement('div');
                fCard.className = 'math-formula-card';
                const latex = convertFormulaToLatex(p);
                fCard.textContent = `$$${latex}$$`;
                paragraphsBox.appendChild(fCard);
            } else {
                // Natural descriptive paragraph in Vazirmatn font
                const pEl = document.createElement('p');
                pEl.className = 'slide-paragraph';
                pEl.textContent = p;
                paragraphsBox.appendChild(pEl);
            }
        });

        // Handle Figures: Every slide has a distinct, rich visualizer!
        const fig = slide.figure || { kind: 'none' };
        captionEl.textContent = isFa ? (fig.caption_fa || '') : (fig.caption_en || '');

        try {
            if (fig.kind === 'photo' && (fig.files?.length || fig.file)) {
                const files = (fig.files && fig.files.length) ? fig.files : [fig.file];
                const grid = document.createElement('div');
                grid.className = files.length > 1 ? 'photo-grid' : 'photo-single';
                for (const fname of files) {
                    if (!fname) continue;
                    const img = document.createElement('img');
                    img.src = `/assets/images/history/${encodeURIComponent(fname)}`;
                    img.alt = fname;
                    img.className = 'photo-preview';
                    img.title = isFa ? 'برای بزرگ‌نمایی کلیک کنید ⛶' : 'Click to enlarge ⛶';
                    img.onclick = () => openDiagramLightbox();
                    grid.appendChild(img);
                }
                mediaWrapper.appendChild(grid);
            } else if (fig.kind === 'duel') {
                const cv = createVisualCanvas();
                mediaWrapper.appendChild(cv);
                PhysicsAnimations.startDuelAnimation(cv);
            } else if (fig.kind === 'apparatus') {
                const cv = createVisualCanvas();
                mediaWrapper.appendChild(cv);
                PhysicsAnimations.startHuygensAnimation(cv, { wavelength_nm: 632.8, slit_distance_mm: 0.25 });
            } else if (fig.kind === 'triangle') {
                const cv = createVisualCanvas();
                mediaWrapper.appendChild(cv);
                PhysicsAnimations.startTriangleAnimation(cv);
            } else if (fig.kind === 'interference') {
                const cv = createVisualCanvas();
                mediaWrapper.appendChild(cv);
                PhysicsAnimations.startInterferenceAnimation(cv);
            } else if (fig.kind === 'fringe') {
                const cv = createVisualCanvas();
                mediaWrapper.appendChild(cv);
                PhysicsAnimations.startAnalyticalFringe(cv);
            } else if (fig.kind === 'worked_bench') {
                const cv = createVisualCanvas();
                mediaWrapper.appendChild(cv);
                PhysicsAnimations.startWorkedBenchVisualizer(cv);
            } else if (fig.kind === 'envelope') {
                const cv = createVisualCanvas();
                mediaWrapper.appendChild(cv);
                PhysicsAnimations.startEnvelopeAnimation(cv);
            } else if (fig.kind === 'huygens') {
                const cv = createVisualCanvas();
                mediaWrapper.appendChild(cv);
                PhysicsAnimations.startHuygensAnimation(cv, { wavelength_nm: 632.8, slit_distance_mm: 0.25 });
            } else if (fig.kind === 'interactive_fringe') {
                const cv = createVisualCanvas();
                mediaWrapper.appendChild(cv);
                PhysicsAnimations.startAnalyticalFringe(cv);
            } else if (fig.kind === 'buildup') {
                const isObserverInitiallyActive = slide.id === 'q2_whichway';
                renderWhichWayBuildupView(mediaWrapper, isObserverInitiallyActive, isFa);
            } else {
                const cv = createVisualCanvas();
                mediaWrapper.appendChild(cv);
                PhysicsAnimations.startHuygensAnimation(cv, { wavelength_nm: 632.8, slit_distance_mm: 0.25 });
            }
        } catch (figErr) {
            console.error('Figure rendering error:', figErr);
        }
    } else {
        // Quiz Slide
        const qIndex = currentSlideIndex - appData.slides.length;
        pill.textContent = isFa ? '۵. آزمون کلاسی' : '5. Class Quiz';
        counter.textContent = isFa
            ? `سوال ${qIndex + 1} از ${appData.quiz.length}`
            : `Question ${qIndex + 1} of ${appData.quiz.length}`;

        titleEl.textContent = isFa
            ? `پرسش کلاسی ${qIndex + 1} از ${appData.quiz.length}`
            : `Class Quiz Question ${qIndex + 1} of ${appData.quiz.length}`;

        diagramBox.style.display = 'none';
        quizBox.style.display = 'flex';
        ClassroomQuiz.renderQuestion(qIndex, true);
    }

    renderDots(totalSlides, currentSlideIndex, (i) => renderHistorySlide(i));
    triggerMathRendering();
    setTimeout(triggerMathRendering, 80);
}

/**
 * Creates and configures a canvas element for physics animations
 */
function createVisualCanvas() {
    const cv = document.createElement('canvas');
    cv.className = 'canvas-visual';
    cv.height = 360;
    cv.title = currentLanguage === 'fa' ? 'برای بزرگ‌نمایی کلیک کنید ⛶' : 'Click to enlarge ⛶';
    cv.onclick = () => openDiagramLightbox();
    return cv;
}

/**
 * Renders the Quantum Buildup canvas alongside an interactive Which-Way toggle button
 */
function renderWhichWayBuildupView(container, isObserverActive, isFa) {
    container.innerHTML = '';

    // Interactive Control Toolbar for Which-Way Detector
    const toolbar = document.createElement('div');
    toolbar.style.display = 'flex';
    toolbar.style.justifyContent = 'space-between';
    toolbar.style.alignItems = 'center';
    toolbar.style.width = '100%';
    toolbar.style.padding = '0.5rem 1rem';
    toolbar.style.background = 'rgba(15, 23, 42, 0.9)';
    toolbar.style.borderBottom = '1px solid var(--border)';

    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'btn-action';
    toggleBtn.id = 'btn-whichway-toggle';
    toggleBtn.style.padding = '0.55rem 1.25rem';
    toggleBtn.style.fontSize = '0.95rem';

    let observerState = Boolean(isObserverActive);

    function updateBtnVisuals() {
        if (observerState) {
            toggleBtn.style.background = 'rgba(239, 68, 68, 0.25)';
            toggleBtn.style.borderColor = '#EF4444';
            toggleBtn.style.color = '#FCA5A5';
            toggleBtn.innerHTML = isFa
                ? '👁️ ناظر مسیر فعال است (فروپاشی موج → دو لکه ذره‌ای)'
                : '👁️ Which-Way Detector ON (Wavefunction Collapse)';
        } else {
            toggleBtn.style.background = 'rgba(16, 185, 129, 0.25)';
            toggleBtn.style.borderColor = '#10B981';
            toggleBtn.style.color = '#6EE7B7';
            toggleBtn.innerHTML = isFa
                ? '🌊 ناظر خاموش است (برهم‌نهی کوانتومی و تشکیل نوارها)'
                : '🌊 Which-Way Detector OFF (Quantum Interference)';
        }
    }

    updateBtnVisuals();

    const cv = createVisualCanvas();
    container.appendChild(toolbar);
    toolbar.appendChild(toggleBtn);
    container.appendChild(cv);

    PhysicsAnimations.startQuantumBuildup(cv, observerState);

    toggleBtn.onclick = () => {
        observerState = PhysicsAnimations.toggleQuantumObserver();
        updateBtnVisuals();
    };
}

/**
 * Render Software Guide Module
 */
function renderGuideModule(index) {
    PhysicsAnimations.stopAllAnimations();
    const modules = appData.guide_modules || [];
    currentGuideIndex = Math.max(0, Math.min(modules.length - 1, index));
    const isFa = currentLanguage === 'fa';
    const mod = modules[currentGuideIndex];

    triggerSlideCardAnimation();

    const pill = document.getElementById('current-chapter-badge');
    const counter = document.getElementById('current-slide-counter');
    const progressFill = document.getElementById('slide-progress-fill');
    const pct = ((currentGuideIndex + 1) / modules.length) * 100;
    progressFill.style.width = `${pct}%`;

    pill.textContent = `${mod.icon || '📖'} ${isFa ? mod.category_fa : mod.category_en}`;
    counter.textContent = isFa
        ? `ماژول ${currentGuideIndex + 1} از ${modules.length}`
        : `Module ${currentGuideIndex + 1} of ${modules.length}`;

    const titleEl = document.getElementById('slide-title-text');
    titleEl.textContent = `${mod.icon || ''} ${isFa ? mod.title_fa : mod.title_en}`;

    const paragraphsBox = document.getElementById('slide-paragraphs-box');
    paragraphsBox.innerHTML = '';

    // Points list
    const listContainer = document.createElement('div');
    listContainer.className = 'guide-points-list';

    const points = isFa ? mod.points_fa : mod.points_en;
    points.forEach(pt => {
        const item = document.createElement('div');
        item.className = 'guide-point-item';
        item.innerHTML = `<span class="guide-point-bullet">✦</span><span>${pt}</span>`;
        listContainer.appendChild(item);
    });
    paragraphsBox.appendChild(listContainer);

    // Tip Banner
    const tipText = isFa ? mod.tip_fa : mod.tip_en;
    if (tipText) {
        const tipEl = document.createElement('div');
        tipEl.className = 'tip-banner';
        tipEl.style.marginTop = '1rem';
        tipEl.innerHTML = `<span>💡</span><span>${tipText}</span>`;
        paragraphsBox.appendChild(tipEl);
    }

    // Hide Quiz, configure Diagram
    document.getElementById('quiz-container-box').style.display = 'none';
    const diagramBox = document.getElementById('diagram-container-box');
    const mediaWrapper = document.getElementById('diagram-media-wrapper');
    diagramBox.style.display = 'flex';
    mediaWrapper.innerHTML = PhysicsAnimations.renderRayTracingSVG(45 + currentGuideIndex * 5);
    const guideCaptionEl = document.getElementById('diagram-caption-text');
    if (guideCaptionEl) {
        guideCaptionEl.textContent = isFa ? (mod.title_fa || '') : (mod.title_en || '');
    }
    const guideSvg = mediaWrapper.querySelector('svg');
    if (guideSvg) {
        guideSvg.style.cursor = 'zoom-in';
        guideSvg.title = isFa ? 'برای بزرگ‌نمایی کلیک کنید ⛶' : 'Click to enlarge ⛶';
        guideSvg.onclick = () => openDiagramLightbox();
    }

    renderDots(modules.length, currentGuideIndex, (i) => renderGuideModule(i));
    triggerMathRendering();
}

/**
 * Render Pagination Dots in Footer
 */
function renderDots(total, current, onSelect) {
    const container = document.getElementById('dots-indicator-container');
    if (!container) return;
    container.innerHTML = '';
    for (let i = 0; i < total; i++) {
        const dot = document.createElement('div');
        dot.className = `dot-item ${i === current ? 'active' : ''}`;
        dot.onclick = () => onSelect(i);
        container.appendChild(dot);
    }

    const prevBtn = document.getElementById('btn-prev-slide');
    const nextBtn = document.getElementById('btn-next-slide');
    if (prevBtn) prevBtn.disabled = current === 0;
    if (nextBtn) nextBtn.disabled = current === total - 1;
}

function nextSlide() {
    if (currentSection === 'lab') return;
    const lightbox = document.getElementById('diagram-lightbox');
    if (lightbox && lightbox.style.display === 'flex') return;
    if (currentSection === 'guide') {
        renderGuideModule(currentGuideIndex + 1);
    } else {
        renderHistorySlide(currentSlideIndex + 1);
    }
}

function prevSlide() {
    if (currentSection === 'lab') return;
    const lightbox = document.getElementById('diagram-lightbox');
    if (lightbox && lightbox.style.display === 'flex') return;
    if (currentSection === 'guide') {
        renderGuideModule(currentGuideIndex - 1);
    } else {
        renderHistorySlide(currentSlideIndex - 1);
    }
}

/**
 * Fringe spacing moved → derive wavelength λ = Δy·d/L (nm), clamp to the
 * 380–780 nm band, then re-run the shared lab update.
 */
function updateLabSimulationFromDy() {
    const dy = parseFloat(document.getElementById('slider-dy').value);
    const d = parseFloat(document.getElementById('slider-d').value);
    const L = parseFloat(document.getElementById('slider-l').value);
    if (!(L > 0) || !(d > 0) || Number.isNaN(dy)) return;
    let wl = (dy * d / L) * 1000.0;
    wl = Math.min(780, Math.max(380, wl));
    document.getElementById('slider-wl').value = wl;
    updateLabSimulation();
}

/**
 * Live Laboratory Simulation Updates
 */
function updateLabSimulation() {
    const wl = parseFloat(document.getElementById('slider-wl').value);
    const d = parseFloat(document.getElementById('slider-d').value);
    const a = parseFloat(document.getElementById('slider-a').value);
    const L = parseFloat(document.getElementById('slider-l').value);

    document.getElementById('lab-val-wl').textContent = `${wl.toFixed(1)} nm`;
    document.getElementById('lab-val-d').textContent = `${d.toFixed(2)} mm`;
    document.getElementById('lab-val-a').textContent = `${a.toFixed(3)} mm`;
    document.getElementById('lab-val-l').textContent = `${L.toFixed(2)} m`;

    const dy = (wl * 1e-9 * L) / (d * 1e-3) * 1000.0;

    // Keep the fringe-spacing slider bidirectionally in sync: its range maps
    // the fixed 380–780 nm band onto the current d/L (step = 1 nm equivalent).
    const sliderDy = document.getElementById('slider-dy');
    if (sliderDy) {
        const dyMin = ((380 * 1e-9 * L) / (d * 1e-3) * 1000.0);
        const dyMax = ((780 * 1e-9 * L) / (d * 1e-3) * 1000.0);
        sliderDy.min = dyMin.toFixed(6);
        sliderDy.max = dyMax.toFixed(6);
        sliderDy.step = Math.max((dyMax - dyMin) / 4000, 1e-9);
        sliderDy.value = dy;
        const valDy = document.getElementById('lab-val-dy');
        if (valDy) valDy.textContent = `${dy.toFixed(4)} mm`;
    }

    const theta1 = (wl * 1e-9 / (d * 1e-3)) * 1000.0;
    const missingRatio = d / a;
    let missingText = currentLanguage === 'fa' ? 'ندارد' : 'None';
    if (Math.abs(missingRatio - Math.round(missingRatio)) < 0.05) {
        const m = Math.round(missingRatio);
        missingText = `±${m}, ±${2*m}`;
    }

    document.getElementById('lab-calc-dy').textContent = `$$\\Delta y = \\frac{\\lambda L}{d} = ${dy.toFixed(2)}\\text{ mm}$$`;
    document.getElementById('lab-calc-theta').textContent = `$$\\theta_1 = ${theta1.toFixed(2)}\\text{ mrad}$$`;
    document.getElementById('lab-calc-missing').textContent = currentLanguage === 'fa' ? `مراتب غایب: ${missingText}` : `Missing Orders: ${missingText}`;

    // Draw on live canvas
    const canvas = document.getElementById('lab-simulation-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width = canvas.clientWidth || 800;
    const h = canvas.height = canvas.clientHeight || 340;
    const cy = h / 2;

    ctx.fillStyle = '#060911';
    ctx.fillRect(0, 0, w, h);

    const laserHex = PhysicsAnimations.wavelengthToHex(wl).hex;
    const dM = d * 1e-3;
    const aM = a * 1e-3;
    const wlM = wl * 1e-9;
    const spanY = 0.03; // +/- 15 mm

    ctx.strokeStyle = '#334155';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(20, cy);
    ctx.lineTo(w - 20, cy);
    ctx.stroke();

    // Plot theoretical intensity curve
    ctx.strokeStyle = laserHex;
    ctx.lineWidth = 2.5;
    ctx.beginPath();

    for (let x = 20; x < w - 20; x++) {
        const yCoord = ((x - w / 2) / (w / 2)) * (spanY / 2);
        const sinTheta = yCoord / Math.sqrt(yCoord * yCoord + L * L);
        const beta = (Math.PI * aM * sinTheta) / wlM;
        const sinc = Math.abs(beta) > 1e-6 ? Math.sin(beta) / beta : 1.0;
        const alpha = (Math.PI * dM * sinTheta) / wlM;
        const intensity = (sinc * sinc) * Math.pow(Math.cos(alpha), 2);

        const yPlot = cy - intensity * 120;
        if (x === 20) {
            ctx.moveTo(x, yPlot);
        } else {
            ctx.lineTo(x, yPlot);
        }
    }
    ctx.stroke();

    triggerMathRendering();
}

/**
 * Language Switching (Persian <-> English)
 */
function toggleLanguage() {
    currentLanguage = currentLanguage === 'fa' ? 'en' : 'fa';
    const isFa = currentLanguage === 'fa';
    document.documentElement.lang = currentLanguage;
    document.documentElement.dir = isFa ? 'rtl' : 'ltr';

    document.getElementById('brand-title').textContent = isFa
        ? 'شبیه‌ساز جامع آزمایش دو شکاف یانگ'
        : 'Thomas Young Double-Slit Experiment Simulator';
    document.getElementById('brand-subtitle').textContent = isFa
        ? 'ارائه آموزشی تعاملی و راهنمای کامل نرم‌افزار'
        : 'Interactive Classroom Presentation & Simulator Guide';

    document.getElementById('label-history-tab').textContent = isFa ? 'تاریخچه و آموزش' : 'History & Physics';
    document.getElementById('label-guide-tab').textContent = isFa ? 'راهنمای نرم‌افزار' : 'Software Guide';
    document.getElementById('label-lab-tab').textContent = isFa ? 'آزمایشگاه زنده' : 'Live Lab';

    document.getElementById('lang-label').textContent = isFa ? 'English (EN)' : 'فارسی (FA)';
    document.getElementById('label-prev').textContent = isFa ? 'قبلی' : 'Previous';
    document.getElementById('label-next').textContent = isFa ? 'بعدی' : 'Next';

    const fsLabel = document.getElementById('fs-label');
    if (fsLabel) {
        fsLabel.textContent = document.fullscreenElement
            ? (isFa ? 'خروج' : 'Exit')
            : (isFa ? 'تمام‌صفحه' : 'Fullscreen');
    }

    ClassroomQuiz.setLanguage(currentLanguage);

    if (currentSection === 'guide') {
        renderGuideModule(currentGuideIndex);
    } else if (currentSection === 'lab') {
        updateLabSimulation();
    } else {
        renderHistorySlide(currentSlideIndex);
    }
}

/**
 * Fullscreen Toggle API
 */
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => {
            console.warn(`Fullscreen error: ${err.message}`);
        });
        document.getElementById('fs-label').textContent = currentLanguage === 'fa' ? 'خروج' : 'Exit';
    } else {
        document.exitFullscreen();
        document.getElementById('fs-label').textContent = currentLanguage === 'fa' ? 'تمام‌صفحه' : 'Fullscreen';
    }
}

function handleKeyboardShortcuts(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === 'PageDown' || e.key === ' ') {
        e.preventDefault();
        nextSlide();
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'PageUp') {
        e.preventDefault();
        prevSlide();
    } else if (e.key === 'f' || e.key === 'F') {
        e.preventDefault();
        toggleFullscreen();
    } else if (e.key === 'Escape') {
        const lightbox = document.getElementById('diagram-lightbox');
        if (lightbox && lightbox.style.display !== 'none') {
            closeDiagramLightbox();
            return;
        }
        if (document.fullscreenElement) document.exitFullscreen();
    }
}

function openDiagramLightbox() {
    const lightbox = document.getElementById('diagram-lightbox');
    const mediaWrapper = document.getElementById('diagram-media-wrapper');
    const titleEl = document.getElementById('lightbox-title');
    const bodyEl = document.getElementById('lightbox-body');
    const capEl = document.getElementById('lightbox-caption');
    const slideTitle = document.getElementById('slide-title-text');
    const slideCaption = document.getElementById('diagram-caption-text');

    if (!lightbox || !mediaWrapper) return;

    titleEl.textContent = slideTitle ? slideTitle.textContent : '';
    capEl.textContent = slideCaption ? slideCaption.textContent : '';
    bodyEl.innerHTML = '';

    const photos = mediaWrapper.querySelectorAll('img');
    if (photos.length > 0) {
        photos.forEach(img => {
            const clone = document.createElement('img');
            clone.src = img.src;
            clone.alt = img.alt;
            bodyEl.appendChild(clone);
        });
    } else {
        const svgs = mediaWrapper.querySelectorAll('svg');
        if (svgs.length > 0) {
            svgs.forEach(svg => bodyEl.appendChild(svg.cloneNode(true)));
        } else {
            const canvases = mediaWrapper.querySelectorAll('canvas');
            if (canvases.length > 0) {
                const src = canvases[0];
                const clone = document.createElement('canvas');
                clone.width = src.width || src.clientWidth || 800;
                clone.height = src.height || src.clientHeight || 450;
                const ctx = clone.getContext('2d');
                ctx.drawImage(src, 0, 0);
                bodyEl.appendChild(clone);
            }
        }
    }

    lightbox.style.display = 'flex';
}

function closeDiagramLightbox(e) {
    if (e && e.target && e.target.closest('.lightbox-content') && !e.target.closest('button')) {
        return;
    }
    const lightbox = document.getElementById('diagram-lightbox');
    if (lightbox) {
        lightbox.style.display = 'none';
        const bodyEl = document.getElementById('lightbox-body');
        if (bodyEl) bodyEl.innerHTML = '';
    }
}

function triggerMathRendering() {
    if (window.renderMathInElement) {
        window.renderMathInElement(document.body, {
            delimiters: [
                { left: '$$', right: '$$', display: true },
                { left: '$', right: '$', display: false }
            ],
            throwOnError: false
        });
    }
}

function resetQuiz() {
    ClassroomQuiz.reset();
}
