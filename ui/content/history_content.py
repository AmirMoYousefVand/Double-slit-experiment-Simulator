"""
Classroom slide-deck content for the History / Tutorial tab.

Pure data — no Tkinter imports — so it stays headless-testable.
Slide bodies are keyed into LocalizationService STRINGS in two parallel dicts
(SLIDE_FA / SLIDE_EN) to keep this module self-contained; HistoryView resolves
the active language at render time. Formulas are isolated onto discrete lines.
"""

from typing import List, Dict, Any

SECTIONS = ["timeline", "theory", "demo", "quantum", "quiz"]

SECTION_TITLES = {
    "timeline": ("hist_sec_timeline", "۱. خط زمانی نور", "1. Timeline of Light"),
    "theory": ("hist_sec_theory", "۲. تئوری کلاسیک", "2. Classical Theory"),
    "demo": ("hist_sec_demo", "۳. نمایش زنده", "3. Live Demo"),
    "quantum": ("hist_sec_quantum", "۴. شگفتی‌های کوانتومی", "4. Quantum Wonders"),
    "quiz": ("hist_sec_quiz", "۵. آزمون کلاسی", "5. Class Quiz"),
}

# Each slide: section, title (fa/en), body paragraphs (fa/en), optional figure.
# Pure formulas are placed on isolated lines for clean LaTeX / KaTeX rendering.
SLIDES: List[Dict[str, Any]] = [
    # ---------------- TIMELINE ----------------
    {
        "id": "t1_duel",
        "section": "timeline",
        "title_fa": "دوئل قرن‌ها: ذره یا موج؟",
        "title_en": "A Centuries-Long Duel: Particle or Wave?",
        "body_fa": [
            "از زمان باستان تا قرن هفدهم، فیزیک‌دانان بر سر ماهیت بنیادین نور اختلاف نظر عمیقی داشتند: آیا نور جریانی از ذرات مادی پرسرعت است یا موجی پیوسته که در فضا نوسان می‌کند؟",
            "در دهه ۱۶۶۰ فرانچسکو گریمالدی دید که مرز سایه اجسام کاملاً تیز نیست و مقداری نور به درون سایه هندسی خم می‌شود. او این پدیده را «پراش» (diffraction) نامید؛ نخستین نشانه جدی علیه نظریه حرکت خطی ذرات نور.",
            "در ۱۶۹۰ کریستیان هویگنس در «رساله نور» استدلال کرد که نور یک موج است و هر نقطه از یک جبهه موج، خود به عنوان منبع موجک‌های ثانویه کروی عمل می‌کند. او با این اصل، بازتاب و شکست نور را به دقت توضیح داد.",
            "اما در ۱۷۰۴ سر اسحاق نیوتن با کتاب مشهور «اپتیکس» از مدل ذره‌ای نور دفاع کرد. به دلیل اعتبار علمی عظیم نیوتن، دیدگاه ذره‌ای نزدیک به یک قرن بر محافل علمی حاکم شد و نظریه موجی به حاشیه رفت.",
        ],
        "body_en": [
            "For centuries, natural philosophers engaged in a fierce debate over the fundamental nature of light: is it a stream of microscopic ballistic bullets, or a continuous oscillating wave propagating through space?",
            "In the 1660s, Francesco Grimaldi discovered that the edges of shadows are not perfectly sharp: light bends slightly into geometric shadow boundaries. He coined this phenomenon diffraction — the first compelling clue against purely straight-line particle rays.",
            "In 1690, Christiaan Huygens argued in Treatise on Light that light is a wave, where every point on a advancing wavefront acts as a source of secondary spherical wavelets. With this principle, he successfully explained reflection and refraction.",
            "However, in 1704, Sir Isaac Newton championed the corpuscular particle model in Opticks. Due to Newton's monumental scientific authority, the particle theory dominated science for nearly a full century, sidelining wave theory.",
        ],
        "figure": {
            "kind": "photo",
            "files": [
                "Grimaldi_experiment_1.png",
                "Grimaldi_experiment_2.png",
                "christiaan huygens wave theory of light.jpg",
                "Opticks-newton.jpg",
            ],
            "caption_fa": "پراش گریمالدی، نظریه موج هویگنس و «اپتیکس» نیوتن: سه سند از دوئل ذره و موج",
            "caption_en": "Grimaldi's Diffraction, Huygens' Wave Theory and Newton's Opticks: Documents of the Particle-Wave Duel"
        },
    },
    {
        "id": "t2_young",
        "section": "timeline",
        "title_fa": "۱۸۰۱: توماس یانگ و آزمایش دو شکاف",
        "title_en": "1801: Thomas Young and the Two Slits",
        "body_fa": [
            "در سال ۱۸۰۱ توماس یانگ، دانشمند همه‌چیزدان و فیزیک‌دان انگلیسی، آزمایش تاریخی دو شکاف را برای اثبات قطعی ماهیت موجی نور طراحی و به انجمن سلطنتی بریتانیا ارائه کرد.",
            "یانگ می‌دانست اگر نور ذره باشد، عبور آن از دو شکاف نزدیک به هم تنها باید دو باریکه روشن روی پرده مقابل ایجاد کند. اما نتیجه آزمایش شگفت‌انگیز بود: پرده‌ای پر از نوارهای متناوب روشن و تاریک موازی پدیدار شد!",
            "او دریافت که درست مانند امواج آب که قله‌ها و دره‌هایشان با هم برهم‌نهی می‌کنند، نور نیز دچار پدیده «تداخل» (Interference) می‌شود؛ جایی که قله به قله می‌رسد روشن، و جایی که قله به دره می‌رسد تاریک می‌گردد.",
            "یانگ با اندازه‌گیری دقیق هندسه چیدمان و فاصله میان نوارها، توانست برای نخستین بار در تاریخ علم، طول‌موج نور قرمز را حدود ۰٫۷ میکرومتر تخمین بزند.",
        ],
        "body_en": [
            "In 1801, Thomas Young, an English polymath and physicist, devised the legendary double-slit experiment to conclusively resolve the wave-particle debate, presenting his findings to the Royal Society of London.",
            "Young realized that if light were composed of classical particles, passing through two adjacent slits would merely produce two bright stripes on the screen. Instead, he observed an alternating series of bright and dark interference fringes!",
            "He explained that just like ripples on a water surface, light waves undergo superposition: where two crests align, constructive interference produces light; where a crest meets a trough, destructive interference cancels the light into darkness.",
            "By measuring the geometry and fringe spacing, Young achieved the first quantitative measurement of light's wavelength in human history, calculating red light to be approximately 0.7 micrometers.",
        ],
        "figure": {
            "kind": "photo",
            "file": "young_portrait.jpg",
            "caption_fa": "توماس یانگ (۱۷۷۳–۱۸۲۹) — کاشف اصل تداخل نور",
            "caption_en": "Thomas Young (1773-1829) — Discoverer of the Principle of Light Interference"
        },
    },
    {
        "id": "t3_fresnel_maxwell",
        "section": "timeline",
        "title_fa": "فرنل و ماکسول: تثبیت نظریه موجی",
        "title_en": "Fresnel and Maxwell: The Wave Theory Triumphs",
        "body_fa": [
            "در سال ۱۸۱۸ آگوستن فرنل نظریه ریاضی دقیقی برای انتشار و پراش امواج نور فرمول‌بندی کرد. سیمون پواسون (از داوران حامی ذره) با تمسخر ادعا کرد این نظریه به نتیجه مضحکی می‌رسد: در مرکز سایه یک دیسک دایره‌ای مات باید یک نقطه کاملاً روشن وجود داشته باشد!",
            "اما در کمال شگفتی، فرانسوا آراگو این آزمایش را فوراً انجام داد و آن نقطه روشن را دقیقاً در مرکز سایه کشف کرد (لکه آراگو / لکه پواسون). این رخداد پیروزی درخشان و قاطعانه‌ای برای نظریه موجی نور بود.",
            "چند دهه بعد در سال ۱۸۶۵، جیمز کلارک ماکسول با پیوند زدن الکتریسیته و مغناطیس نشان داد که نور در حقیقت یک موج الکترومغناطیسی با میدان‌های الکتریکی و مغناطیسی نوسانی عمود بر هم است که با سرعت ۳۰۰ هزار کیلومتر بر ثانیه منتشر می‌شود.",
            "هاینریش هرتز در سال ۱۸۸۷ وجود امواج الکترومغناطیسی را در آزمایشگاه تولید و ثبت کرد تا مدل موجی کلاسیک به کمال برسد.",
        ],
        "body_en": [
            "In 1818, Augustin Fresnel developed a rigorous mathematical wave theory of diffraction. Siméon Poisson, a skeptic defending Newton's particles, attempted to disprove it by showing it led to an apparent absurdity: a bright spot must appear at the exact center of an opaque circular disk's shadow!",
            "To everyone's astonishment, François Arago immediately performed the test and discovered the bright spot right at the shadow's center (known as Arago's spot or Poisson's spot). This provided undeniable proof of the wave nature of light.",
            "Decades later in 1865, James Clerk Maxwell unified electricity and magnetism, revealing that light is an electromagnetic wave of perpendicular oscillating electric and magnetic fields traveling at 300,000 km/s.",
            "Heinrich Hertz experimentally generated and detected radio waves in 1887, completing the classical electromagnetic triumph.",
        ],
        "figure": {
            "kind": "photo",
            "files": [
                "Arago spot, Poisson spot.png",
                "fringes.jpg",
            ],
            "caption_fa": "لکه آراگو (پواسون) در مرکز سایه و نوارهای واقعی تداخل فرانهوفر روی پرده",
            "caption_en": "Arago's (Poisson's) Spot at the Shadow Center and Real Fraunhofer Fringes on a Detector"
        },
    },
    {
        "id": "t4_quantum_era",
        "section": "timeline",
        "title_fa": "عصر کوانتوم: بازگشت شگفت‌انگیز ذره!",
        "title_en": "The Quantum Era: The Return of the Particle!",
        "body_fa": [
            "درست در زمانی که فیزیک کلاسیک پیروزی موج را تثبیت‌شده می‌دید، در سال ۱۹۰۵ آلبرت اینشتین با تبیین اثر فوتوالکتریک نشان داد که نور علاوه بر رفتار موجی، از بسته‌های مجزای انرژی به نام «فوتون» تشکیل شده است.",
            "در سال ۱۹۲۴ لویی دوبروی فرضیه انقلابی خود را مطرح کرد: اگر نور موجی است که رفتار ذره‌ای دارد، پس ماده (مانند الکترون، پروتون و اتم‌ها) نیز ذراتی هستند که خصوصیات موجی با طول‌موج دوبروی از خود نشان می‌دهند.",
            "در سال ۱۹۶۱ کلائوس یونسون آزمایش دو شکاف یانگ را با باریکه‌ای از الکترون‌ها تکرار کرد و نوارهای تداخلی دقیقی مشاهده نمود؛ امواج مادی اثبات شدند!",
            "در سال ۱۹۸۹ آزمایشگاه هیتاچی این آزمایش را با شلیک تک‌تک الکترون‌ها انجام داد و نشان داد هر ذره به تنهایی از هر دو شکاف می‌گذرد و با خودش تداخل می‌کند. حتی در سال ۱۹۹۹ مولکول‌های درشت باکی‌بال C₆₀ نیز تداخل کردند.",
        ],
        "body_en": [
            "Just as classical physics declared wave victory, in 1905 Albert Einstein explained the photoelectric effect by demonstrating that light is delivered in discrete, quantized energy packets called photons.",
            "In 1924, Louis de Broglie introduced a revolutionary symmetry: if light waves exhibit particle behavior, then physical matter (such as electrons and atoms) must also possess matter waves with a de Broglie wavelength.",
            "In 1961, Claus Jönsson successfully replicated Young's double-slit experiment using electron beams, observing clear wave interference patterns and confirming de Broglie's prediction.",
            "In 1989, researchers at Hitachi fired electrons one by one: each electron registered as a discrete impact, yet thousands gradually accumulated into interference fringes. In 1999, even massive C60 fullerene molecules demonstrated quantum wave interference!",
        ],
        "figure": {
            "kind": "photo",
            "files": [
                "photo-electric.png",
                "hitachi_buildup.jpg",
            ],
            "caption_fa": "اثر فوتوالکتریک اینشتین (۱۹۰۵) و انباشت دانه‌دانه الکترون‌های تکی در آزمایشگاه هیتاچی (۱۹۸۹)",
            "caption_en": "Einstein's Photoelectric Effect (1905) and Dot-by-Dot Single-Electron Buildup at Hitachi (1989)"
        },
    },
    # ---------------- THEORY ----------------
    {
        "id": "c1_setup",
        "section": "theory",
        "title_fa": "اجزای هندسی چیدمان آزمایش یانگ",
        "title_en": "Geometric Architecture of Young's Experiment",
        "body_fa": [
            "برای مشاهده پدیده تداخل پایدار، چیدمان آزمایشگاهی یانگ از سه بخش اساسی و دقیق تشکیل شده است:",
            "۱. چشمه نور همدوس (Coherent Source): چشمه‌ای که نوری تک‌رنگ با طول‌موج مشخص تولید می‌کند تا امواج دارای اختلاف فاز ثابت و پایدار باشند (مانند پرتو لیزر).",
            "۲. صفحه مانع دو شکاف (Slits Barrier): مانعی مات با دو شکاف بسیار باریک به پهنای a که مرکز آن‌ها در فاصله کوچک d از یکدیگر قرار دارد. هر شکاف به عنوان یک منبع موجک مستقل عمل می‌کند.",
            "۳. پرده آشکارساز (Observation Screen): پرده‌ای مسطح در فاصله بسیار دورتر L از مانع که امواج رسیده از دو شکاف روی آن هم‌پوشانی کرده و نوارهای تداخلی را پدید می‌آورند.",
        ],
        "body_en": [
            "To observe a stable and visible interference pattern, Young's experimental setup relies on three core components:",
            "1. Coherent Monochromatic Source: Produces light of a single precise wavelength with a constant relative phase relationship (such as a laser diode).",
            "2. Double-Slit Barrier: An opaque plate pierced by two parallel apertures of width a, whose centers are separated by distance d. Each slit acts as a synchronized secondary wavelet emitter.",
            "3. Observation Screen: Placed at a significantly larger distance L from the barrier, where the diverging waves superpose to cast the fringe pattern.",
        ],
        "figure": {
            "kind": "apparatus",
            "caption_fa": "چیدمان اپتیکی: پرتو لیزر، دو شکاف با فاصله d، و پرده در فاصله L",
            "caption_en": "Optical Layout: Incident laser beam, double slits (d), and detector screen (L)"
        },
    },
    {
        "id": "c2_pathdiff",
        "section": "theory",
        "title_fa": "مفهوم کلیدی اختلاف راه هندسی",
        "title_en": "The Key Concept: Optical Path Difference",
        "body_fa": [
            "وقتی دو موج نوری هم‌زمان از شکاف اول و دوم به سمت یک نقطه مشخص مثل P روی پرده حرکت می‌کنند، مسافت یکسانی طی نمی‌کنند.",
            "به دلیل فاصله d بین دو شکاف، پرتوی خروجی از شکاف پایین‌تر باید مسافت اضافی‌تری نسبت به پرتوی بالایی طی کند تا به نقطه P برسد. این مسافت اضافی «اختلاف راه» (Path Difference) نامیده می‌شود.",
            "در تقریب فیزیکی زوایای کوچک (L بسیار بزرگ‌تر از d)، این اختلاف راه با رابطه هندسی زیر به دست می‌آید:",
            "Δr = d · sinθ",
            "اختلاف فاز حاصل از این اختلاف راه، مشخص‌کننده رابطه بین قله‌ها و دره‌های دو موج در نقطه P است:",
            "Δφ = 2πΔr / λ",
            "به این ترتیب، هر طول‌موج اختلاف مسافت (λ)، یک چرخش فاز کامل ۳۶۰ درجه‌ای می‌سازد.",
        ],
        "body_en": [
            "When two synchronized waves travel from the upper and lower slits toward a chosen observation point P on the screen, they traverse different distances.",
            "Because the slits are separated by distance d, the wave from the lower slit travels a slightly longer path than the wave from the upper slit. This geometric excess is called the Path Difference.",
            "Under the paraxial approximation where screen distance L is far greater than slit separation d, this path difference is determined by:",
            "Δr = d · sinθ",
            "The corresponding optical phase difference determines how crests and troughs align upon arrival at point P:",
            "Δφ = 2πΔr / λ",
            "Consequently, every wavelength of path difference corresponds to a complete 360° (2π radian) cycle of wave phase.",
        ],
        "figure": {
            "kind": "triangle",
            "caption_fa": "مثلث قائم‌الزاویه هندسی و محاسبه اختلاف راه: Δr = d · sinθ",
            "caption_en": "Geometric Right Triangle & Path Difference: Δr = d · sinθ"
        },
    },
    {
        "id": "c3_conditions",
        "section": "theory",
        "title_fa": "شرایط تشکیل نوارهای روشن و تاریک",
        "title_en": "Conditions for Bright and Dark Fringes",
        "body_fa": [
            "وضعیت روشنایی روی پرده تنها به هم‌فاز بودن یا ناهم‌فاز بودن امواج رسیده به هر نقطه بستگی دارد:",
            "۱. نوار روشن (تداخل سازنده): زمانی رخ می‌دهد که اختلاف راه مضرب صحیحی از طول‌موج کامل باشد. در این حالت قله به قله می‌رسد و یکدیگر را تقویت می‌کنند:",
            "d · sinθ = mλ",
            "۲. نوار تاریک (تداخل ویرانگر): زمانی رخ می‌دهد که اختلاف راه مضرب فردی از نصف طول‌موج باشد. در این حالت قله موج اول با دره موج دوم برخورد کرده و نور کاملاً خاموش می‌شود:",
            "d · sinθ = (m + ½)λ",
            "شدت نور کلی از رابطه جمع برداری دامنه‌ها به دست می‌آید. به دلیل برهم‌نهی همدوس، شدت در مرکز نوارهای روشن ۴ برابر شدت یک تک‌شکاف است:",
            "I = 4I₀ · cos²(Δφ/2)",
        ],
        "body_en": [
            "The optical pattern on the detector screen depends entirely on whether arriving waves are in-step or out-of-step:",
            "1. Bright Fringe (Constructive Interference): Occurs when the path difference is an integer multiple of full wavelengths. Crests meet crests, magnifying the light:",
            "d · sinθ = mλ",
            "2. Dark Fringe (Destructive Interference): Occurs when waves arrive out of phase by an odd half-wavelength. Crests cancel troughs, annihilating the light:",
            "d · sinθ = (m + ½)λ",
            "Total intensity results from coherent electric field amplitude superposition. At constructive peaks, intensity is four times greater than a single slit:",
            "I = 4I₀ · cos²(Δφ/2)",
        ],
        "figure": {
            "kind": "interference",
            "caption_fa": "برهم‌نهی امواج و جمع برداری فازورها در تداخل سازنده و ویرانگر",
            "caption_en": "Wave superposition and phasor vector addition in constructive & destructive interference"
        },
    },
    {
        "id": "c4_spacing",
        "section": "theory",
        "title_fa": "فاصله میان نوارها و قوانین تناسب",
        "title_en": "Fringe Spacing & Proportionality Laws",
        "body_fa": [
            "برای زوایای بسیار کوچک (شرایط استاندارد آزمایشگاه)، زاویه بر حسب رادیان برابر است با نسبت فاصله خطی روی پرده y به فاصله پرده L (یعنی sinθ ≈ y/L).",
            "با جایگذاری این تقریب، فاصله خطی میان دو نوار روشن متوالی (پهنای نوار Δy) با رابطه طلایی زیر داده می‌شود:",
            "Δy = λL / d",
            "قوانین طلایی تناسب نوارها:",
            "• نور قرمز (طول‌موج بلندتر) نوارهای پهن‌تر و بازتری نسبت به نور آبی یا بنفش می‌سازد.",
            "• دور کردن پرده (افزایش L) نوارها را بازتر و تفکیک‌پذیرتر می‌کند.",
            "• نزدیک‌تر کردن شکاف‌ها به یکدیگر (کاهش d) نوارها را پهن‌تر می‌کند؛ و برعکس، دور کردن شکاف‌ها نوارها را بسیار فشرده می‌سازد.",
        ],
        "body_en": [
            "Under small angle conditions typical of optical laboratories, angle theta in radians equals linear screen position y divided by screen distance L (sinθ ≈ y/L).",
            "Substituting this relation yields the master formula for the linear spacing between adjacent bright fringes (fringe width Δy):",
            "Δy = λL / d",
            "Golden Proportionality Rules:",
            "• Longer wavelength light (red) produces wider, more spread out fringes than shorter wavelength light (blue/violet).",
            "• Increasing screen distance L magnifies the pattern, spreading fringes farther apart.",
            "• Narrowing the slit separation d expands fringe spacing; widening d compresses fringes tightly together.",
        ],
        "figure": {
            "kind": "fringe",
            "caption_fa": "اندازه‌گیری فاصله دو نوار روشن متوالی (Δy) با خط‌کش کولیس",
            "caption_en": "Measuring fringe spacing (Δy) between adjacent bright bands"
        },
    },
    {
        "id": "c5_worked",
        "section": "theory",
        "title_fa": "مثال عددی حل‌شده در آزمایشگاه",
        "title_en": "Step-by-Step Worked Lab Example",
        "body_fa": [
            "فرض کنید در آزمایشگاه از یک لیزر استاندارد هلیوم-نئون با طول‌موج قرمز ۶۳۲٫۸ نانومتر، فاصله دو شکاف ۰٫۲۵ میلی‌متر و فاصله پرده ۱٫۰ متر استفاده می‌کنیم.",
            "قدم ۱: تبدیل مقادیر به واحدهای استاندارد SI (متر):",
            "λ = 632.8 × 10⁻⁹ m , d = 0.25 × 10⁻³ m , L = 1.0 m",
            "قدم ۲: جایگذاری مستقیم در رابطه پهنای نوار تداخلی:",
            "Δy = λL / d = 2.53 mm",
            "نتیجه فیزیکی: فاصله مرکز هر نوار روشن تا نوار روشن بعدی دقیقاً ۲٫۵۳ میلی‌متر روی پرده خواهد بود. همین مقادیر را در شبیه‌ساز ما امتحان کنید تا صحت این محاسبه را با چشم ببینید!",
        ],
        "body_en": [
            "Consider a real laboratory setup using a standard helium-neon red laser with wavelength 632.8 nm, slit separation 0.25 mm, and screen distance 1.0 m.",
            "Step 1: Convert all physical quantities into standard SI units (meters):",
            "λ = 632.8 × 10⁻⁹ m , d = 0.25 × 10⁻³ m , L = 1.0 m",
            "Step 2: Substitute directly into the fringe spacing formula:",
            "Δy = λL / d = 2.53 mm",
            "Physical Result: The center-to-center distance between adjacent bright bands is precisely 2.53 mm. Verify this directly with the sliders in the simulator!",
        ],
        "figure": {
            "kind": "worked_bench",
            "caption_fa": "محاسبه عددی لیزر هلیوم-نئون و بزرگ‌نمایی پرده (۲٫۵۳ میلی‌متر)",
            "caption_en": "Worked example with He-Ne laser and 2.53 mm screen magnification"
        },
    },
    {
        "id": "c6_envelope",
        "section": "theory",
        "title_fa": "پوش پراش تک‌شکاف و مراتب تداخلی غایب",
        "title_en": "Single-Slit Envelope & Missing Orders",
        "body_fa": [
            "در دنیای واقعی، شکاف‌ها خطوط ایده‌آل ریاضی با پهنای صفر نیستند، بلکه هر شکاف پهنای فیزیکی مشخصی به نام a دارد.",
            "طبق پدیده پراش فرانهوفر، هر تک‌شکاف خودش یک پوش روشنایی گسترده (تابع sinc²) روی پرده می‌اندازد که نوارها درون آن حبس می‌شوند. کمینه‌های این پوش پراش در زوایای زیر رخ می‌دهند:",
            "a · sinθ = mλ",
            "اگر زاویه‌ای که در آن یک نوار روشن دوشکاف باید تشکیل شود، دقیقاً با کمینه تاریک پوش تک‌شکاف یکی شود، آن نوار روشن هرگز ظاهر نخواهد شد! به این پدیده «مراتب غایب» (Missing Orders) می‌گویند.",
            "شرط ریاضی غایب شدن نوارها، صحیح بودن نسبت d به a است. برای مثال اگر d چهار برابر a باشد، نوارهای مرتبه ±۴ و ±۸ ناپدید می‌شوند.",
        ],
        "body_en": [
            "In physical experiments, slits are not zero-width mathematical lines; each aperture has a measurable finite width a.",
            "Each slit therefore produces its own Fraunhofer diffraction envelope (a sinc² profile) that modulates the double-slit fringes, with diffraction minima at:",
            "a · sinθ = mλ",
            "If an angle intended for an interference maximum coincides exactly with a diffraction minimum, that bright fringe is suppressed and cannot appear! These are called Missing Orders.",
            "The missing order condition requires the ratio d/a to be an exact integer. For example, if d is four times wider than a, orders m = ±4, ±8 vanish.",
        ],
        "figure": {
            "kind": "envelope",
            "caption_fa": "پوش پراش تک‌شکاف sinc² و مشخص شدن مراتب غایب (d/a)",
            "caption_en": "Single-slit sinc² envelope modulating interference fringes with missing orders"
        },
    },
    # ---------------- DEMO ----------------
    {
        "id": "d1_waves",
        "section": "demo",
        "title_fa": "انتشار دوبعدی امواج و ساختار تداخل",
        "title_en": "2D Wavefront Propagation & Fringe Emergence",
        "body_fa": [
            "در این شبیه‌ساز دوبعدی تعاملی، انتشار پیوسته جبهه امواج نوری را از لحظه خروج از لیزر تا پرده آشکارساز مشاهده می‌کنید:",
            "۱. جبهه امواج مسطح از سمت چپ با سرعت منظم به سمت مانع حرکت می‌کنند.",
            "۲. به محض برخورد امواج به دو شکاف، طبق اصل هویگنس دو خانواده از موجک‌های کروی متحدالمرکز از هر شکاف در فضای آزاد پخش می‌شوند.",
            "۳. هم‌پوشانی این دو خانواده موج در فضا، خطوط متقاطع هذلولی از تقویت (قله‌های نوری) و تضعیف (گره‌های تاریک) می‌سازد.",
            "۴. با ماوس روی پرده سمت راست کلیک کنید و نقطه P را حرکت دهید تا پرتوهای نوری و مثلث اختلاف راه را به صورت آنلاین تماشا کنید!",
        ],
        "body_en": [
            "In this interactive 2D simulation, follow the continuous propagation of light wavefronts from emission to screen detection:",
            "1. Planar wavefronts advance steadily from the laser source on the left toward the slit barrier.",
            "2. Upon reaching the apertures, the Huygens-Fresnel principle dictates the emission of two expanding families of circular wavelets.",
            "3. Superposition in space creates hyperbolic corridors of constructive reinforcement (antinodes) and destructive cancellation (nodes).",
            "4. Drag observation point P along the detector screen on the right to track optical rays and path difference geometry in real time!",
        ],
        "figure": {
            "kind": "huygens",
            "caption_fa": "انتشار دوبعدی امواج، رهگیری پرتوها به نقطه P و نوار تداخل پرده",
            "caption_en": "2D wave propagation, ray tracing to point P, and screen ribbon"
        },
    },
    {
        "id": "d2_live",
        "section": "demo",
        "title_fa": "آزمایشگاه زنده: بازی با پارامترهای تداخل",
        "title_en": "Interactive Lab: Exploring Optics Parameters",
        "body_fa": [
            "تئوری و فرمول‌ها زمانی ماندگار می‌شوند که خودتان اثر تغییر هر پارامتر را مستقیماً آزمایش و لمس کنید!",
            "در این نما یا با مراجعه به تب آزمایشگاه زنده (Live Lab)، طول‌موج را از بنفش (۴۰۰ نانومتر) تا قرمز (۷۰۰ نانومتر) تغییر دهید و باز شدن نوارها را ببینید.",
            "فاصله شکاف‌ها (d) را افزایش دهید تا فشرده شدن سریع نوارها را لمس کنید.",
            "تکلیف کلاسی: با لیزر قرمز ۶۳۲٫۸ نانومتر و پرده در فاصله ۱ متر، فاصله دو شکاف را طوری تنظیم کنید که فاصله نوارها دقیقاً ۵ میلی‌متر شود. (راهنمایی: d = λL / Δy).",
        ],
        "body_en": [
            "Physics formulas become intuitive when you directly manipulate apparatus parameters and observe the instantaneous response!",
            "Adjust the wavelength slider across the visible spectrum from violet (400 nm) to deep red (700 nm) and watch the fringe ribbon expand.",
            "Widen the slit separation d to watch the fringes squeeze tightly together.",
            "Classroom Challenge: With a 632.8 nm red laser and a 1-meter screen distance, what slit separation yields a fringe spacing of exactly 5.0 mm? (Hint: d = λL / Δy).",
        ],
        "figure": {
            "kind": "interactive_fringe",
            "caption_fa": "پرده تداخلی زنده با قابلیت تنظیم طول‌موج و ابعاد شکاف‌ها",
            "caption_en": "Live interference pattern following optical parameters"
        },
    },
    # ---------------- QUANTUM ----------------
    {
        "id": "q1_single",
        "section": "quantum",
        "title_fa": "معمای تک‌ذره: انباشت دانه‌دانه فوتون‌ها",
        "title_en": "The Single-Particle Enigma: Quantum Buildup",
        "body_fa": [
            "اگر شدت تابش چشمه نور را آن‌قدر کم کنیم که در هر ثانیه تنها یک فوتون (یا یک الکترون) از تفنگ شلیک شود، چه اتفاقی می‌افتد؟",
            "هر فوتون وقتی به پرده می‌رسد، فقط در یک نقطه منفرد و تصادفی یک جرقه نوری یا یک نقطه فسفری ایجاد می‌کند. با دیدن یک نقطه، هیچ اثری از تداخل به چشم نمی‌خورد.",
            "اما با ادامه شلیک ذرات و ثبت هزاران نقطه در طول زمان، نقاط تصادفی به شکلی حیرت‌آور در همان نوارهای تداخلی مرتب می‌شوند!",
            "نتیجه انقلابی مکانیک کوانتومی: ذرات با یکدیگر برخورد یا تداخل نمی‌کنند؛ بلکه تابع موج احتمال هر تک‌ذره هم‌زمان از هر دو شکاف عبور کرده و ذره با خودش تداخل می‌کند!",
        ],
        "body_en": [
            "What happens if we reduce source intensity so drastically that only one photon or electron travels through the apparatus at a time?",
            "Each quantum particle lands as a localized, discrete dot on the detector screen. Looking at an individual impact, no wave interference is discernible.",
            "Yet as thousands of individual particles arrive over time, their positions collectively map out the classic interference fringes with mathematical precision!",
            "The quantum revelation: Particles do not interfere with each other; rather, the probability wave amplitude of each single particle traverses both slits simultaneously, interfering with itself!",
        ],
        "figure": {
            "kind": "buildup",
            "caption_fa": "انباشت دانه‌دانه فوتون‌ها و الکترون‌ها روی پرده فسفری",
            "caption_en": "Single Photon & Electron Buildup on Phosphor Screen"
        },
    },
    {
        "id": "q2_whichway",
        "section": "quantum",
        "title_fa": "ناظر کوانتومی و محو شدن تداخل",
        "title_en": "The Quantum Observer: Which-Way Decoherence",
        "body_fa": [
            "اگر یک حسگر بسیار حساس در کنار شکاف‌ها نصب کنیم تا مشخص کند ذره واقعاً از شکاف اول عبور کرده یا از شکاف دوم، چه رخ می‌دهد؟",
            "به محض آنکه اطلاعات مسیر ذره (Which-Way Information) حتی به صورت غیرمستقیم در جهان ثبت شود، الگوی تداخلی فوراً از بین می‌رود و فقط دو لکه ساده ذره‌ای روی پرده باقی می‌ماند!",
            "علت این پدیده «ناهمدوسی کوانتومی» (Quantum Decoherence) است: هرگونه برهم‌کنش فیزیکی برای اندازه‌گیری مسیر، فاز نسبی امواج را بر هم زده و برهم‌نهی را نابود می‌کند.",
            "سوییچ ناظر تعاملی در بالای نگاره این اسلاید را کلیک کنید و فروریزش زنده نوارها به لکه‌های ذره‌ای را با چشمان خود ببینید!",
        ],
        "body_en": [
            "What happens if we place an ultra-sensitive detector at the slits to determine precisely which slit each particle actually took?",
            "The moment path information (Which-Way) is recorded anywhere in the physical universe, the interference fringes instantly vanish, collapsing into two classical clumps!",
            "The root physical cause is Quantum Decoherence: any physical interaction capable of measuring the path irrevocably scrambles the quantum phase relationship between the two paths.",
            "Click the interactive Which-Way toggle switch above the figure on this slide to watch the fringes collapse into particle clumps in real time!",
        ],
        "figure": {
            "kind": "buildup",
            "caption_fa": "ناظر کوانتومی مسیر: سوییچ ناظر را بزنید تا فروریزش تداخل را ببینید",
            "caption_en": "Quantum Which-Way detector: toggle observer to see wave collapse"
        },
    },
    {
        "id": "q3_eraser",
        "section": "quantum",
        "title_fa": "انتخاب تأخیری و پاک‌کن کوانتومی",
        "title_en": "Delayed Choice & The Quantum Eraser",
        "body_fa": [
            "جان ویلر در ۱۹۷۸ آزمایشی ذهنی طراحی کرد: اگر تصمیم به اندازه‌گیری یا عدم اندازه‌گیری مسیر را «بعد» از عبور ذره از صفحه شکاف‌ها بگیریم، چه رخ خواهد داد؟ آزمایش‌های عملی نشان دادند که ذره همواره متناسب با چیدمان نهایی آشکارسازها پاسخ می‌دهد.",
            "در ۱۹۸۲ اسکالی و درول «پاک‌کن کوانتومی» (Quantum Eraser) را معرفی کردند: اگر اطلاعات ثبت‌شده مسیر به نحوی پاک شود که دیگر نتوان فهمید ذره از کجا گذشته، نوارهای تداخلی دوباره پدیدار می‌شوند!",
            "چهار سوءتفاهم رایج در فیزیک کوانتوم:",
            "۱. ذره هرگز در آزمایش دو شکاف نصف نمی‌شود؛ همواره یک ذره کامل ثبت می‌گردد.",
            "۲. ذرات با یکدیگر برخورد نمی‌کنند؛ تداخل کاملاً نتیجه خودتداخلی تک‌ذره است.",
            "۳. ناظر کوانتومی نیازی به «هوشیاری انسان» ندارد؛ هر برهم‌کنش ترمودینامیکی با محیط یک ناظر است.",
            "۴. آزمایش انتخاب تأخیری گذشته را بازنویسی نمی‌کند؛ بلکه برهم‌نهی تا لحظه اندازه‌گیری نهایی حفظ می‌شود.",
        ],
        "body_en": [
            "In 1978, John Wheeler proposed the delayed-choice thought experiment: what if the choice to observe or not observe the path is made AFTER the particle has already traversed the slits? Experimental implementations confirm that quantum behavior depends strictly on the final measurement configuration.",
            "In 1982, Scully and Drühl conceived the Quantum Eraser: if path information is recorded but subsequently erased such that it is fundamentally impossible to know the route, wave interference miraculously reappears!",
            "Four Crucial Quantum Truths:",
            "1. The particle never splits in half; each detection event registers a single, indivisible entity.",
            "2. Particles do not collide to create fringes; interference is purely single-particle self-superposition.",
            "3. The quantum observer does NOT require human consciousness; any irreversible physical recording in the environment causes decoherence.",
            "4. Delayed choice does not alter past history; rather, quantum states remain indefinite until a terminal measurement occurs.",
        ],
        "figure": {
            "kind": "photo",
            "file": "c60.jpg",
            "caption_fa": "تداخل مولکول‌های غول‌پیکر باکی‌بال C₆₀ در آزمایشگاه زایلینگر (۱۹۹۹)",
            "caption_en": "Quantum wave interference of macroscopic C60 buckyball molecules (Zeilinger 1999)"
        },
    },
]

# Quiz bank: 6 questions, 4 options each, zero-based correct index.
# Fully conceptual, testing physical principles without tedious manual calculations.
QUIZ: List[Dict[str, Any]] = [
    {
        "q_fa": "توماس یانگ با اندازه‌گیری فاصله نوارها، طول‌موج نور قرمز را برای نخستین بار در تاریخ حدود چقدر تخمین زد؟",
        "q_en": "From his fringe spacing measurements, what was Young's historical estimate for the wavelength of red light?",
        "opts_fa": ["۷ نانومتر", "۰٫۷ میکرومتر", "۷ میکرومتر", "۷ میلی‌متر"],
        "opts_en": ["7 nanometers", "0.7 micrometers", "7 micrometers", "7 millimeters"],
        "correct": 1,
        "explain_fa": "طول‌موج نور مرئی در محدوده ۴۰۰ تا ۷۰۰ نانومتر (۰٫۴ تا ۰٫۷ میکرومتر) است و یانگ برای نور قرمز حدود ۰٫۷ میکرومتر به دست آورد.",
        "explain_en": "Visible light wavelengths span 400 to 700 nanometers (0.4 to 0.7 micrometers); Young reported approximately 0.7 micrometers for red light.",
    },
    {
        "q_fa": "شرط تشکیل نوار روشن (تداخل سازنده) مرتبه m بر حسب اختلاف راه Δr کدام است؟",
        "q_en": "Which condition guarantees a bright fringe (constructive interference) of order m in terms of path difference Δr?",
        "opts_fa": ["d · sinθ = mλ", "a · sinθ = mλ", "d · sinθ = (m + ½)λ", "Δy = λd / L"],
        "opts_en": ["d · sinθ = mλ", "a · sinθ = mλ", "d · sinθ = (m + ½)λ", "Δy = λd / L"],
        "correct": 0,
        "explain_fa": "برای تداخل سازنده، اختلاف راه دو پرتو باید مضرب صحیحی از طول‌موج کامل (mλ) باشد تا قله‌ها هم‌جهت با یکدیگر جمع شوند.",
        "explain_en": "For constructive interference, the path difference must equal an integer number of full wavelengths (mλ) so crests align with crests.",
    },
    {
        "q_fa": "اگر کل چیدمان آزمایش دو شکاف را درون آب (با ضریب شکست n = ۱٫۳۳) قرار دهیم، فاصله نوارها چه تغییری می‌کند؟",
        "q_en": "If the entire double-slit setup is placed in water (refractive index n = 1.33), how does fringe spacing change?",
        "opts_fa": [
            "فاصله نوارها بیشتر می‌شود",
            "فاصله نوارها کمتر و فشرده‌تر می‌شود",
            "فاصله نوارها تغییری نمی‌کند",
            "نوارها کاملاً ناپدید می‌شوند"
        ],
        "opts_en": [
            "Fringe spacing increases",
            "Fringe spacing decreases and compresses",
            "Fringe spacing remains unchanged",
            "Fringes disappear completely"
        ],
        "correct": 1,
        "explain_fa": "درون آب به دلیل کاهش سرعت نور، طول‌موج به λ/n کاهش می‌یابد و طبق رابطه Δy = λL/d، فاصله نوارها به همان نسبت فشرده‌تر می‌شود.",
        "explain_en": "In water, slower light velocity shortens wavelength to λ/n. By Δy = λL/d, fringe spacing decreases by 1/n, compressing the pattern.",
    },
    {
        "q_fa": "پدیده «مراتب غایب» در تداخل دوشکاف ناشی از چیست؟",
        "q_en": "What causes the phenomenon of 'Missing Orders' in double-slit interference?",
        "opts_fa": [
            "نقص در منبع لیزر",
            "انطباق یک بیشینه دوشکاف با کمینه تاریک پوش پراش تک‌شکاف",
            "تاریک شدن محیط آزمایشگاه",
            "فروپاشی تابع موج ناشی از ناظر"
        ],
        "opts_en": [
            "A defect in the laser source",
            "Coincidence of an interference peak with a single-slit diffraction minimum",
            "Darkness of the laboratory room",
            "Wavefunction collapse from observation"
        ],
        "correct": 1,
        "explain_fa": "وقتی یک زاویه بیشینه تداخلی دوشکاف روی زاویه کمینه صفر پوش تک‌شکاف (a·sinθ = mλ) بیفتد، آن نوار به کل ناپدید می‌شود.",
        "explain_en": "When a double-slit interference maximum lands precisely on a single-slit diffraction zero (a·sinθ = mλ), that fringe is suppressed.",
    },
    {
        "q_fa": "در آزمایش تک‌الکترونی هیتاچی (۱۹۸۹)، نتیجه ارسال تک‌تک ذرات به سوی دو شکاف چه بود؟",
        "q_en": "In the 1989 Hitachi single-electron experiment, what occurred when particles were fired one at a time?",
        "opts_fa": [
            "الکترون‌ها به دو نیم تقسیم شدند",
            "نقاط مجزای ثبت‌شده به‌تدریج الگوی تداخلی موجی را ساختند",
            "هیچ نواری تشکیل نشد و فقط دو لکه ذره‌ای ظاهر شد",
            "الکترون‌ها در فضا با یکدیگر برخورد کردند"
        ],
        "opts_en": [
            "Each electron split in half",
            "Discrete single hits gradually accumulated into an interference pattern",
            "No fringes formed, leaving only two particle blobs",
            "Electrons collided with each other mid-flight"
        ],
        "correct": 1,
        "explain_fa": "هر ذره به صورت مجزا ثبت شد اما تجمع هزاران نقطه توزیع تداخلی را شکل داد؛ این نشان داد هر ذره با خودش تداخل می‌کند.",
        "explain_en": "Each particle registered as a point, but their collective distribution produced fringes, proving single-particle self-interference.",
    },
    {
        "q_fa": "اثر روشن کردن آشکارساز مسیر (Which-Way Detector) در آزمایش دو شکاف چیست؟",
        "q_en": "What is the physical consequence of activating a Which-Way detector at the double slits?",
        "opts_fa": [
            "نوارها درخشان‌تر و تفکیک‌پذیرتر می‌شوند",
            "نوارهای تداخلی محو شده و دو لکه ذره‌ای کلاسیک باقی می‌ماند (V → 0)",
            "طول‌موج ذرات تغییر می‌کند",
            "فاصله میان دو شکاف افزایش می‌یابد"
        ],
        "opts_en": [
            "Fringes become brighter and sharper",
            "Interference fringes wash out, leaving two classical particle clumps (V → 0)",
            "The particle wavelength changes",
            "The slit separation increases"
        ],
        "correct": 1,
        "explain_fa": "ثبت اطلاعات مسیر باعث ناهمدوسی کوانتومی شده، برهم‌نهی دو راه را نابود می‌کند و کنتراست تداخل به صفر می‌رسد.",
        "explain_en": "Recording path information induces quantum decoherence, destroying superposition and reducing fringe visibility to zero.",
    },
]


def grade(question: Dict[str, Any], choice: int) -> bool:
    """Pure quiz grading function (headless-testable)."""
    return int(choice) == int(question.get("correct", -1))


def get_slides_by_section() -> Dict[str, List[int]]:
    """Returns slide indices grouped by section id."""
    grouped: Dict[str, List[int]] = {s: [] for s in SECTIONS}
    for i, slide in enumerate(SLIDES):
        grouped[slide["section"]].append(i)
    return grouped
