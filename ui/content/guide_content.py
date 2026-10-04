"""
Software Guide Content — comprehensive tutorial modules for all views and tools in the simulator.

Pure data module for headless testing. Contains 8 structured instructional modules
covering the entire software architecture, views, controls, quantum mechanics, and exports.
"""

from typing import List, Dict, Any

GUIDE_MODULES: List[Dict[str, Any]] = [
    {
        "id": "g1_overview",
        "title_fa": "۱. ساختار کلی نرم‌افزار و ناوبری",
        "title_en": "1. Overall Architecture & Navigation",
        "category_fa": "معماری و ناوبری",
        "category_en": "Architecture & Navigation",
        "icon": "🏛",
        "points_fa": [
            "نوار بالایی (Top Bar): شامل عنوان نرم‌افزار، انتخابگر دو حالت اصلی «اپتیک موجی کلاسیک» و «مکانیک کوانتومی»، دکمه‌های تغییر زبان (FA/EN)، پوسته، و دکمه‌های تمام‌صفحه و حالت تئاتر.",
            "پنل کنترل سمت چپ: در حالت کلاسیک، تنظیم پارامترهای لیزر و شکاف‌ها، و در حالت کوانتومی، انتخاب ذرات مادی (فوتون، الکترون، باکی‌بال) و کلید ناظر (Which-Way).",
            "فضای کاری چندنمایی (وسط): دسترسی سریع به ۷ تب تخصصی (پرده ۲D، پروفایل ۱D، شماتیک ۲D، چیدمان ۳D، محاسبات، تاریخچه و راهنما).",
            "پنل پایینی متریک‌ها: نمایش زنده مشخصات تداخل (فاصله نوارها، کنتراست V، زاویه θ) و ۴ دکمه خروجی داده (CSV، عکس ۳۰۰ DPI، مدل سه‌بعدی OBJ، و بسته ZIP).",
        ],
        "points_en": [
            "Top Bar: hosts the app title, the main mode switcher (Classical Wave vs Quantum Mechanics), Language toggle (EN/FA), Theme, and Fullscreen/Theater buttons.",
            "Left Control Panel: adjusts laser wavelength, slit dimensions, screen distance, or quantum particle species and the Which-Way detector.",
            "Central Multi-View Workspace: provides 7 dedicated tabs (2D Screen, 1D Profile, 2D Schematic, 3D Lab, Calculations, History, and Guide).",
            "Bottom Metrics Panel: displays live telemetry (fringe spacing, contrast V, angle) and 4 scientific export buttons (CSV, PNG, 3D OBJ, ZIP bundle).",
        ],
        "tip_fa": "نکته کلیدی: با کلید F11 کل پنجره تمام‌صفحه می‌شود و با کلید F10 (حالت تئاتر) پنل‌های کناری جمع می‌شوند تا نمای فعال ۱۰۰٪ فضای تصویر را در بر بگیرد.",
        "tip_en": "Key Tip: Press F11 for full-window fullscreen, and press F10 (Theater Mode) to collapse sidebars and expand the active view to 100% display area."
    },
    {
        "id": "g2_screen_2d",
        "title_fa": "۲. پرده آشکارساز دو بعدی (2D Screen)",
        "title_en": "2. 2D Detector Screen View",
        "category_fa": "نماهای شبیه‌ساز",
        "category_en": "Simulation Views",
        "icon": "📺",
        "points_fa": [
            "نمایش بلادرنگ پرده فیزیکی: در حالت کلاسیک نوارهای تداخلی ممتد و در حالت کوانتومی اصابت دانه‌دانه ذرات به پرده فسفری را بازسازی می‌کند.",
            "خط‌کش میلی‌متری دقیق: با درجه‌بندی دقیق در کناره پرده جهت اندازه‌گیری مستقیم فاصله نوارها (Δy) و تطبیق آن با فرمول ریاضی.",
            "پالت رنگی فیزیکی (Physical Monochromatic): رنگ پرده دقیقاً بر اساس طول موج نور (فرمول Dan Bruton sRGB) تطبیق می‌یابد.",
            "پالت‌های علمی توربو و اینفرنو: پالت علمی توربو (Turbo HDR) نوارها و پراش‌های مرتبه بالا و کم‌نور را با وضوح فوق‌العاده آشکار می‌سازد.",
        ],
        "points_en": [
            "Real-time physical screen: renders continuous laser interference bands in Classical mode, and discrete phosphor hits in Quantum mode.",
            "Millimeter scale ruler: calibrated along the screen for direct spatial measurement of fringe spacing (Δy) against theoretical calculations.",
            "Physical Monochromatic Colormap: dynamically matches the exact spectral laser color via Dan Bruton sRGB wavelength formulation.",
            "Scientific Turbo & Inferno Colormaps: Turbo HDR highlights faint outer diffraction orders with extreme clarity and contrast.",
        ],
        "tip_fa": "امتحان کن: پالت رنگی را در پنل پایین به Turbo تغییر بده تا پوش پراش شکاف‌ها و نوارهای کم‌نور کناری به صورت رنگی و واضح آشکار شوند.",
        "tip_en": "Try it: Switch the colormap to Turbo in the bottom panel to clearly reveal faint higher-order diffraction fringes."
    },
    {
        "id": "g3_profile_1d",
        "title_fa": "۳. نمودار شدت یک‌بعدی (1D Profile)",
        "title_en": "3. 1D Intensity Profile View",
        "category_fa": "نماهای شبیه‌ساز",
        "category_en": "Simulation Views",
        "icon": "📈",
        "points_fa": [
            "پروفایل تحلیلی شدت تداخل: نمودار شدت نرمال‌شده I/I₀ بر حسب میلی‌متر روی پرده را رسم می‌کند.",
            "پوش پراش تک‌شکاف (sinc²): منحنی نقطه چین بالایی نشان‌دهنده اثر پهنای هر شکاف (a) است که روشنایی نوارها را مهار می‌کند.",
            "نشانگرهای بیشینه و کمینه: قله‌های سازنده با مثلث مشکی روبه‌بالا (▲) و گره‌های تاریک ویرانگر با مثلث روبه‌پایین (▼) علامت‌گذاری شده‌اند.",
            "هیستوگرام کوانتومی: در حالت کوانتومی، تجمع دانه‌دانه ذرات به صورت میله‌های هیستوگرام روی نمودار تئوری ظاهر شده و درستی آماری را اثبات می‌کند.",
        ],
        "points_en": [
            "Analytical Intensity Profile: plots normalized intensity I/I0 against screen coordinate y (mm).",
            "Single-Slit Envelope sinc²: dashed upper curve demonstrates single-slit diffraction limiting fringe brightness.",
            "Maxima & Minima Markers: constructive peaks are pinned with black up-triangles (▲) and destructive nodes with down-triangles (▼).",
            "Quantum Histogram Overlay: in quantum mode, accumulated discrete hits build up as histogram bars matching theory in real time.",
        ],
        "tip_fa": "امتحان کن: لغزونک پهنای شکاف (a) را در پنل چپ زیاد کن و ببین چطور پوش پراش تنگ‌تر شده و برخی نوارهای روشن غایب (Missing Orders) می‌شوند.",
        "tip_en": "Try it: Increase slit width (a) in the left panel to watch the sinc² envelope narrow and cause missing interference orders."
    },
    {
        "id": "g4_schematic",
        "title_fa": "۴. انتشار امواج و شماتیک ۲D (Schematic)",
        "title_en": "4. 2D Wave Propagation & Schematic",
        "category_fa": "نماهای شبیه‌ساز",
        "category_en": "Simulation Views",
        "icon": "🌊",
        "points_fa": [
            "تصویرسازی امواج هویگنس: انتشار جبهه موج تخت از چشمه لیزر و انتشار موجک‌های دایره‌ای از هر یک از دو شکاف را شبیه‌سازی می‌کند.",
            "کاوشگر تعاملی نقطه P: با کلیک و درگ ماوس روی روبان پرده، نقطه P را به هر کجا دلت خواست جابه‌جا کن.",
            "رهگیری پرتوهای هندسی: پرتوهای سبز (r₁) و زرد (r₂) و مثلث قائم‌الزاویه اختلاف راه به صورت آنلاین محاسبه و رسم می‌شوند.",
            "نقطه اصابت تپنده: در نقطه P، نقطه نورانی در تداخل سازنده منبسط و درخشان و در تداخل ویرانگر محو و خاکستری می‌شود.",
        ],
        "points_en": [
            "Huygens Wavelet Simulation: shows incident plane waves and expanding circular wavelets from both slits.",
            "Interactive Inspection Point P: click and drag along the screen ribbon to position observation point P anywhere.",
            "Geometric Ray Traces: green ray (r1), yellow ray (r2), and the path difference right triangle are tracked in real time.",
            "Pulsating Impact Spot: point P expands into a bright radiant halo at constructive fringes and dims at destructive nodes.",
        ],
        "tip_fa": "امتحان کن: نقطه P را روی نوار روشن مرکزی قرار بده؛ اختلاف راه Δr صفر می‌شود و شدت نوار به ۱۰۰٪ می‌رسد.",
        "tip_en": "Try it: Place point P on the central bright fringe; path difference Δr drops to zero and intensity peaks at 100%."
    },
    {
        "id": "g5_setup_3d",
        "title_fa": "۵. چیدمان آزمایشگاهی سه‌بعدی (3D Apparatus)",
        "title_en": "5. 3D Laboratory Apparatus View",
        "category_fa": "نماهای شبیه‌ساز",
        "category_en": "Simulation Views",
        "icon": "📐",
        "points_fa": [
            "میز اپتیکی سه‌بعدی: ماکت سه‌بعدی ابزار آزمایش شامل دیود لیزر، مانع شکاف‌ها، پرتوهای نوری و پرده آشکارساز.",
            "چرخش آزاد ۳۶۰ درجه: با نگه‌داشتن کلیک چپ ماوس و حرکت دادن آن، زاویه دید دوربین را به صورت دلخواه بچرخان.",
            "بزرگ‌نمایی و کوچک‌نمایی: با چرخاندن اسکرول ماوس (Mouse Wheel) یا دکمه‌های زوم، به اجزای چیدمان نزدیک یا دور شو.",
            "نماهای دوربین آماده: دکمه‌های نمای بالا (Top)، نمای جانبی (Side)، نمای روبه‌رو (Front) و بازنشانی برای بررسی از زوایای استاندارد.",
        ],
        "points_en": [
            "3D Optical Bench: interactive 3D model of the lab apparatus including laser diode, double-slit barrier, beams, and screen.",
            "Free 360° Rotation: left-click and drag with the mouse to orbit the camera at any azimuth and elevation.",
            "Smooth Zoom: use the mouse scroll wheel or zoom buttons to inspect apparatus components up close.",
            "Camera Preset Buttons: Top view, Side view, Front view, and Perspective reset for standard lab projections.",
        ],
        "tip_fa": "امتحان کن: دکمه نمای بالا (Top) را بزن تا تقارن پرتوهای نور را از دید عمودی و هندسه زاویه θ مشاهده کنی.",
        "tip_en": "Try it: Click Top view to examine ray symmetry and angular deviation θ from directly above the apparatus."
    },
    {
        "id": "g6_calculations",
        "title_fa": "۶. روابط فیزیکی و بازرس نقطه‌ای (Calculations)",
        "title_en": "6. Physics Formulations & Inspector",
        "category_fa": "روابط و محاسبات",
        "category_en": "Formulations & Inspector",
        "icon": "🧮",
        "points_fa": [
            "۷ کارت فرمول با جایگذاری لحظه‌ای: اختلاف راه، شرایط تداخل، فرمول پهنای نوار Δy، پوش پراش فرانهوفر و امواج دوبروی.",
            "کاوشگر دقیق نقطه‌ای (y): لغزونک مکان روی پرده را تکان بده تا زاویه θ، فاز Δφ، دامنه و وضعیت فیزیکی نقطه محاسبه شود.",
            "خروجی گزارش ورد (Word .docx): با دکمه گزارش Word، یک فایل رسمی مستند کلاسی با فرمول‌های ریاضی ادیت‌پذیر OMML بساز.",
            "خروجی تصویر کارت‌ها (PNG): ذخیره سریع کارت‌های فرمول در قالب یک فایل تصویری با کیفیت بالا.",
        ],
        "points_en": [
            "7 Formulation Cards with Live Substitution: path difference, fringe spacing Δy, sinc² diffraction, and de Broglie relations.",
            "Interactive Point Inspector (y): adjust the slider to compute angle θ, phase Δφ, amplitude, and physical status at that exact coordinate.",
            "Word Report Export (.docx): click Export Word to generate an official laboratory report with editable native OMML equations.",
            "Calculations PNG Export: quickly save all mathematical derivation cards into a high-resolution summary image.",
        ],
        "tip_fa": "امتحان کن: گزارش Word را صادر کن و در نرم‌افزار مایکروسافت ورد باز کن؛ تمام فرمول‌ها به صورت ریاضی نیتیو و قابل ادیت ذخیره شده‌اند.",
        "tip_en": "Try it: Export the Word report and open it in Microsoft Word; all equations are rendered as native editable OMML math blocks."
    },
    {
        "id": "g7_quantum",
        "title_fa": "۷. مکانیک کوانتومی و امواج دوبروی (Quantum)",
        "title_en": "7. Quantum Mechanics & Wave Duality",
        "category_fa": "مکانیک کوانتومی",
        "category_en": "Quantum Mechanics",
        "icon": "⚛",
        "points_fa": [
            "تابش ذرات کوانتومی: با کلید حالت کوانتوم در بالای برنامه، بین ۳ نوع ذره تابشی (فوتون، الکترون، باکی‌بال C₆₀) انتخاب کن.",
            "طول موج دوبروی (λ = h/p): با تغییر انرژی ذره بر حسب الکترون‌ولت (eV) یا سرعت (m/s)، تغییر طول موج ماده را مشاهده کن.",
            "شبیه‌ساز مونت‌کارلو ۶۰ فریم: دکمه پخش (Play) را بزن تا ذرات دانه‌دانه شلیک شده و نوارهای تداخلی را بسازند.",
            "آزمون همگرایی کای-دو (χ²): برنامه همگرایی آماری نقاط ثبت‌شده را با تابع احتمال تئوری مقایسه کرده و در پنل متریک نمایش می‌دهد.",
        ],
        "points_en": [
            "Quantum Particle Emission: switch to Quantum mode to shoot Photons, Electrons, or C60 Buckyballs.",
            "De Broglie Wavelength (λ = h/p): change particle energy (eV) or velocity (m/s) to observe matter wave dilation.",
            "High-Speed Monte Carlo Simulation: press Play to emit particles one by one and witness the emergence of interference fringes.",
            "Chi-Square Convergence Test (χ²): computes statistical convergence between discrete impacts and theoretical probability density.",
        ],
        "tip_fa": "امتحان کن: ذره را روی Buckyball (مولکول بزرگ کربن ۶۰) بگذار؛ متوجه می‌شوی حتی مولکول‌های سنگین هم خاصیت موجی دارند!",
        "tip_en": "Try it: Select Buckyball (C60 molecule); discover how even massive macromolecules exhibit quantum wave interference!"
    },
    {
        "id": "g8_which_way_exports",
        "title_fa": "۸. ناظر Which-Way و پایپ‌لاین خروجی‌ها (Exports)",
        "title_en": "8. Which-Way Detector & Export Pipeline",
        "category_fa": "ناظر و خروجی‌ها",
        "category_en": "Observer & Exports",
        "icon": "💾",
        "points_fa": [
            "ناظر مزاحم کوانتومی (Which-Way): سوییچ آشکارساز مسیر را روشن کن تا فروریزش تابع موج و ناپدید شدن نوارها (V → 0) را زنده ببینی.",
            "دیتاست ۲۲ ستونه CSV: ذخیره جدول کامل مختصات نقاط روی پرده، شدت تئوری، هیستوگرام کوانتومی و متادیتای کامل پارامترها.",
            "خروجی تصاویر ۳۰۰ DPI: ذخیره نمای فعال در قالب عکس باکیفیت استاندارد مقالات علمی (فرمت‌های PNG، PDF، و وکتور SVG).",
            "مدل سه‌بعدی CAD (.OBJ): خروجی گرفتن از کل چیدمان آزمایشگاهی و پرتوها برای باز کردن در نرم‌افزارهای Blender، Maya یا چاپ سه‌بعدی.",
            "بسته جامع آزمایشگاهی (.ZIP): یک آرشیو کامل شامل تمام داده‌ها، گزارش‌ها، مدل سه‌بعدی و تصاویر با یک کلیک.",
        ],
        "points_en": [
            "Which-Way Observer Detector: flip the Which-Way switch to witness decoherence, wave function collapse, and fringe erasure (V → 0).",
            "22-Column Scientific CSV: exports complete spatial grid, theoretical intensity, quantum histogram, and optical parameters.",
            "300 DPI Publication Figures: save the active view matching journal publication standards (PNG, PDF, SVG vector).",
            "3D CAD Model (.OBJ + .MTL): export the entire laboratory scene into Blender, Maya, or 3D printers.",
            "All-in-One Lab Bundle (.ZIP): comprehensive archive packing CSV, Word report, 3D model, and high-res figures in one click.",
        ],
        "tip_fa": "امتحان کن: دکمه بسته جامع آزمایشگاهی (.ZIP) را بزن تا یک پکیج آماده برای تحویل پروژه یا تکالیف دانشگاهی دریافت کنی.",
        "tip_en": "Try it: Click Export Lab Bundle (.ZIP) to generate a complete submission package for classroom assignments or research."
    },
]
