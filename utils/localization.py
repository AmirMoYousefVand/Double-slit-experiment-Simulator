"""
Localization Service providing bilingual (English & Persian) labels,
physical terminology, tooltips, presets, and educational descriptions.
Uses Unicode Right-to-Left Mark (RLM = U+200F) to ensure perfect RTL rendering.
"""

from typing import Dict, Any, List, Optional
import functools
import re
import arabic_reshaper
from bidi.algorithm import get_display

# Unicode Right-to-Left Mark to lock RTL direction for mixed Persian/Latin strings
RLM = "‏"

class LocalizationService:
    """Manages bilingual UI strings (English & Persian) with clean RTL formatting."""

    _CURRENT_LANG = "fa"  # Default to Persian

    STRINGS: Dict[str, Dict[str, str]] = {
        # App Title & Headers
        "app_title": {
            "en": "Thomas Young Double-Slit Experiment Simulator",
            "fa": f"{RLM}شبیه‌ساز جامع آزمایش دو شکاف یانگ{RLM}"
        },
        "app_subtitle": {
            "en": "Wave Optics & Quantum Wave-Particle Duality Lab",
            "fa": f"{RLM}آزمایشگاه اپتیک موجی و دوگانگی موج-ذره مکانیک کوانتومی{RLM}"
        },
        "copyright": {
            "en": "© 2026 — Created by Amir Mohammad Yousefvand",
            "fa": f"{RLM}ساخته شده توسط Amir Mohammad Yousefvand © ۲۰۲۶{RLM}"
        },
        "mode_classical": {
            "en": "Classical Wave Optics",
            "fa": f"{RLM}نورشناسی موجی کلاسیک{RLM}"
        },
        "mode_quantum": {
            "en": "Quantum Mechanics",
            "fa": f"{RLM}مکانیک کوانتومی{RLM}"
        },
        "lang_switch": {
            "en": f"{RLM}فارسی (FA){RLM}",
            "fa": "English (EN)"
        },
        "theme_toggle": {
            "en": "Theme",
            "fa": f"{RLM}پوسته{RLM}"
        },

        # Optics Parameters
        "optics_panel_title": {
            "en": "Optical & Apparatus Parameters",
            "fa": f"{RLM}پارامترهای اپتیکی و چیدمان آزمایش{RLM}"
        },
        "wavelength": {
            "en": "Wavelength (λ):",
            "fa": f"{RLM}طول موج (λ):{RLM}"
        },
        "slit_distance": {
            "en": "Slit Separation (d):",
            "fa": f"{RLM}فاصله دو شکاف (d):{RLM}"
        },
        "slit_width": {
            "en": "Slit Width (a):",
            "fa": f"{RLM}پهنای هر شکاف (a):{RLM}"
        },
        "screen_distance": {
            "en": "Screen Distance (L):",
            "fa": f"{RLM}فاصله تا پرده (L):{RLM}"
        },
        "refractive_index": {
            "en": "Refractive Index (n):",
            "fa": f"{RLM}ضریب شکست محیط (n):{RLM}"
        },
        "presets_label": {
            "en": "Presets & Laboratory Standards:",
            "fa": f"{RLM}پیش‌فرض‌ها و نمونه‌های آزمایشگاهی:{RLM}"
        },

        # Preset Names
        "preset_hene": {
            "en": "He-Ne Red Laser (632.8 nm)",
            "fa": f"{RLM}لیزر سرخ هلیوم-نئون (۶۳۲.۸ nm){RLM}"
        },
        "preset_argon": {
            "en": "Argon-Ion Green Laser (514.5 nm)",
            "fa": f"{RLM}لیزر سبز یون آرگون (۵۱۴.۵ nm){RLM}"
        },
        "preset_violet": {
            "en": "Violet Laser Diode (405.0 nm)",
            "fa": f"{RLM}دیود لیزر بنفش (۴۰۵.۰ nm){RLM}"
        },
        "preset_sodium": {
            "en": "Sodium D-Line (589.3 nm)",
            "fa": f"{RLM}خط زرد سدیم (۵۸۹.۳ nm){RLM}"
        },
        "preset_water": {
            "en": "Water Medium (n = 1.333)",
            "fa": f"{RLM}محیط آب (زیر آب n = ۱.۳۳۳){RLM}"
        },
        "preset_narrow": {
            "en": "High Diffraction (Narrow Slits)",
            "fa": f"{RLM}پراش شدید (شکاف‌های نزدیک){RLM}"
        },

        # Quantum Controls
        "quantum_panel_title": {
            "en": "Quantum Mechanics Controls",
            "fa": f"{RLM}کنترل‌های مکانیک کوانتومی{RLM}"
        },
        "particle_type": {
            "en": "Particle Type:",
            "fa": f"{RLM}نوع ذره تابشی:{RLM}"
        },
        "particle_photon": {
            "en": "Photon (Light Quantum)",
            "fa": f"{RLM}فوتون (کوانتوم نور){RLM}"
        },
        "particle_electron": {
            "en": "Electron (Matter Wave)",
            "fa": f"{RLM}الکترون (موج مادی){RLM}"
        },
        "particle_buckyball": {
            "en": "Buckyball C₆₀ (Macromolecule)",
            "fa": f"{RLM}باکی‌بال C₆₀ (درشت‌مولکول){RLM}"
        },
        "particle_energy": {
            "en": "Kinetic Energy (eV):",
            "fa": f"{RLM}انرژی جنبشی (eV):{RLM}"
        },
        "particle_voltage": {
            "en": "Accelerating Voltage (V₀):",
            "fa": f"{RLM}ولتاژ شتاب‌دهنده (V₀):{RLM}"
        },
        "particle_velocity": {
            "en": "Molecular Velocity (m/s):",
            "fa": f"{RLM}سرعت ذره (m/s):{RLM}"
        },
        "emission_rate": {
            "en": "Emission Rate (parts/s):",
            "fa": f"{RLM}آهنگ شلیک (ذره در ثانیه):{RLM}"
        },
        "which_way_title": {
            "en": "Which-Way Detector (Observer Effect):",
            "fa": f"{RLM}آشکارساز مسیر (اثر مشاهده‌گر):{RLM}"
        },
        "which_way_off": {
            "en": "OFF: Coherent Superposition |Ψ₁ + Ψ₂|²",
            "fa": f"{RLM}خاموش: برهم‌نهی همدوس |Ψ₁ + Ψ₂|²{RLM}"
        },
        "which_way_on": {
            "en": "ON: Wavefunction Collapse (Sum of Slits)",
            "fa": f"{RLM}روشن: فروپاشی تابع موج (مجموع دو شکاف){RLM}"
        },
        "which_way_warning": {
            "en": "OBSERVER ACTIVE: Phase coherence destroyed!",
            "fa": f"{RLM}ناظر فعال: همدوسی فاز و طرح تداخلی محو شد!{RLM}"
        },
        "play": {
            "en": "Start Firing",
            "fa": f"{RLM}شروع شلیک{RLM}"
        },
        "pause": {
            "en": "Pause",
            "fa": f"{RLM}توقف موقت{RLM}"
        },
        "step": {
            "en": "Single Burst",
            "fa": f"{RLM}شلیک تک‌دسته{RLM}"
        },
        "reset": {
            "en": "Clear Screen",
            "fa": f"{RLM}پاکسازی پرده{RLM}"
        },

        # View Tabs
        "tab_2d_screen": {
            "en": "2D Screen",
            "fa": f"{RLM}پرده آشکارساز (2D){RLM}"
        },
        "tab_1d_profile": {
            "en": "1D Profile",
            "fa": f"{RLM}نمودار شدت (1D){RLM}"
        },
        "tab_schematic": {
            "en": "2D Waves",
            "fa": f"{RLM}انتشار امواج (2D){RLM}"
        },
        "tab_3d_setup": {
            "en": "3D Apparatus",
            "fa": f"{RLM}چیدمان سه‌بعدی (3D){RLM}"
        },
        "tab_calculations": {
            "en": "Equations",
            "fa": f"{RLM}فرمول‌ها و محاسبات{RLM}"
        },

        # 3D View Specific Controls
        "cam_perspective": {
            "en": "Perspective",
            "fa": f"{RLM}دید پرسپکتیو{RLM}"
        },
        "cam_top": {
            "en": "Top View",
            "fa": f"{RLM}نمای بالا{RLM}"
        },
        "cam_side": {
            "en": "Side View",
            "fa": f"{RLM}نمای جانبی{RLM}"
        },
        "cam_front": {
            "en": "Screen View",
            "fa": f"{RLM}نمای روبرو پرده{RLM}"
        },
        "cam_reset": {
            "en": "Reset Camera",
            "fa": f"{RLM}بازنشانی دوربین{RLM}"
        },
        "zoom_in": {
            "en": "+ Zoom In",
            "fa": f"{RLM}+ بزرگ‌نمایی{RLM}"
        },
        "zoom_out": {
            "en": "- Zoom Out",
            "fa": f"{RLM}- کوچک‌نمایی{RLM}"
        },
        "rot_left": {
            "en": "◀ Left",
            "fa": f"{RLM}◀ چپ{RLM}"
        },
        "rot_right": {
            "en": "Right ▶",
            "fa": f"{RLM}راست ▶{RLM}"
        },
        "rot_up": {
            "en": "▲ Up",
            "fa": f"{RLM}▲ بالا{RLM}"
        },
        "rot_down": {
            "en": "▼ Down",
            "fa": f"{RLM}▼ پایین{RLM}"
        },

        # Metrics Panel
        "metrics_title": {
            "en": "Live Physical Metrics & Analytical Readouts",
            "fa": f"{RLM}پارامترهای فیزیکی و مقادیر تحلیلی زنده{RLM}"
        },
        "fringe_spacing": {
            "en": "Fringe Spacing (Δy):",
            "fa": f"{RLM}فاصله دو نوار روشن متوالی (Δy):{RLM}"
        },
        "angular_separation": {
            "en": "Angular Separation (θ):",
            "fa": f"{RLM}جدایی زاویه‌ای (θ):{RLM}"
        },
        "central_width": {
            "en": "Central Envelope Width:",
            "fa": f"{RLM}پهنای قله مرکزی پراش:{RLM}"
        },
        "visibility": {
            "en": "Fringe Visibility (V):",
            "fa": f"{RLM}دیداری فرانژها / کنتراست (V):{RLM}"
        },
        "detected_hits": {
            "en": "Detected Particles (N):",
            "fa": f"{RLM}کل ذرات ثبت‌شده (N):{RLM}"
        },
        "missing_orders": {
            "en": "Missing Orders:",
            "fa": f"{RLM}مراتب تداخلی غایب:{RLM}"
        },
        "missing_none": {
            "en": "None",
            "fa": f"{RLM}هیچ{RLM}"
        },
        "chi_square": {
            "en": "Quantum Convergence (χ²):",
            "fa": f"{RLM}همگرایی کوانتومی (χ²):{RLM}"
        },

        # Export & Actions
        "export_csv": {
            "en": "Export CSV (22 Columns)",
            "fa": f"{RLM}خروجی کامل CSV (۲۲ ستون){RLM}"
        },
        "export_plot": {
            "en": "Export Active View (PNG)",
            "fa": f"{RLM}ذخیره تصویر نمای جاری (PNG){RLM}"
        },
        "export_obj": {
            "en": "Export 3D Model (.OBJ)",
            "fa": f"{RLM}خروجی مدل ۳ بعدی (.OBJ){RLM}"
        },
        "export_docx": {
            "en": "Export Word Report (.docx)",
            "fa": f"{RLM}خروجی گزارش ورد (.docx){RLM}"
        },
        "export_calc_png": {
            "en": "Export Formats (PNG)",
            "fa": f"{RLM}ذخیره تصویر فرمول‌ها (PNG){RLM}"
        },
        "export_zip": {
            "en": "Export Lab Bundle (.ZIP)",
            "fa": f"{RLM}خروجی بسته جامع آزمایشگاهی (.ZIP){RLM}"
        },
        "colormap_label": {
            "en": "Colormap Mode:",
            "fa": f"{RLM}پالت رنگی پرده:{RLM}"
        },
        "colormap_physical": {
            "en": "Physical Monochromatic",
            "fa": f"{RLM}رنگ فیزیکی طول موج{RLM}"
        },
        "colormap_turbo": {
            "en": "Scientific Turbo (HDR)",
            "fa": f"{RLM}پالت علمی توربو (Turbo){RLM}"
        },
        "colormap_inferno": {
            "en": "Thermal Inferno",
            "fa": f"{RLM}پالت حرارتی (Inferno){RLM}"
        },
        "plot_1d_xlabel": {
            "en": "Screen Position y (mm)",
            "fa": "مکان روی پرده y (mm)"
        },
        "plot_1d_ylabel": {
            "en": "Normalized Intensity I / I₀",
            "fa": "شدت نسبی I / I₀"
        },
        "plot_1d_title": {
            "en": "Fraunhofer Diffraction & Interference Intensity Profile",
            "fa": "پروفایل شدت تداخل و پوش پراش فرانهوفر"
        },
        "plot_1d_theory": {
            "en": "Theory I(y)",
            "fa": "تئوری تداخل I(y)"
        },
        "plot_1d_envelope": {
            "en": "Diffraction Envelope sinc²",
            "fa": "پوش پراش sinc²"
        },
        "plot_1d_hits": {
            "en": "Quantum Hits",
            "fa": "ذرات کوانتومی"
        },
        "plot_1d_maxima": {
            "en": "Maxima",
            "fa": "بیشینه‌ها (ماکزیمم)"
        },
        "plot_1d_minima": {
            "en": "Minima",
            "fa": "کمینه‌ها (مینیمم)"
        },
        "sch_export_title": {
            "en": "Young's Double-Slit Optical Wave Propagation & Geometric Interference",
            "fa": "انتشار موج و چیدمان هندسی تداخل آزمایش دو شکاف یانگ"
        },
        "reset_defaults": {
            "en": "Reset All Parameters",
            "fa": f"{RLM}بازنشانی پارامترها{RLM}"
        },

        # Calculations & Point Inspector
        "calc_header": {
            "en": "Physical Formulations & Live Analytical Substitution",
            "fa": f"{RLM}روابط تحلیلی، فرمول‌های فیزیکی و جایگذاری لحظه‌ای مقادیر{RLM}"
        },
        "calc_card1": {
            "en": "1. Optical Path Difference & Geometry",
            "fa": f"{RLM}۱. اختلاف راه هندسی و هندسه آزمایش{RLM}"
        },
        "calc_card2": {
            "en": "2. Constructive & Destructive Interference Conditions",
            "fa": f"{RLM}۲. شرایط تداخل سازنده و ویرانگر (موقعیت نوارها){RLM}"
        },
        "calc_card3": {
            "en": "3. Fringe Width / Spacing Formulation (Δy)",
            "fa": f"{RLM}۳. فاصله بین دو نوار روشن متوالی (پهنای فرانژ Δy){RLM}"
        },
        "calc_card4": {
            "en": "4. Fraunhofer Diffraction Envelope & Missing Orders",
            "fa": f"{RLM}۴. پوش پراش فرانهوفر و مراتب تداخلی غایب{RLM}"
        },
        "calc_card5": {
            "en": "5. Quantum Mechanics & De Broglie Matter Waves",
            "fa": f"{RLM}۵. مکانیک کوانتومی و رابطه امواج مادی دوبروی{RLM}"
        },
        "calc_card6": {
            "en": "6. Quantum Superposition vs Wavefunction Collapse",
            "fa": f"{RLM}۶. برهم‌نهی کوانتومی در برابر فروپاشی تابع موج (اثر ناظر){RLM}"
        },
        "calc_card7": {
            "en": "7. Interactive Point Inspector (Screen Position y)",
            "fa": f"{RLM}۷. کاوشگر نقطه‌ای روی پرده (محاسبه دقیق در مختصات دلخواه y){RLM}"
        },
        "inspector_slider": {
            "en": "Screen Position y:",
            "fa": f"{RLM}موقعیت روی پرده y:{RLM}"
        },
        "status_bright": {
            "en": "Bright Maximum (Constructive)",
            "fa": f"{RLM}قله روشن بیشینه (سازنده){RLM}"
        },
        "status_dark": {
            "en": "Dark Minimum (Destructive)",
            "fa": f"{RLM}گره تاریک کمینه (ویرانگر){RLM}"
        },
        "status_intermediate": {
            "en": "Intermediate Region",
            "fa": f"{RLM}ناحیه روشنایی میانی{RLM}"
        },

        # Schematic Labels
        "sch_source": {
            "en": "SOURCE",
            "fa": f"{RLM}چشمه{RLM}"
        },
        "sch_barrier": {
            "en": "BARRIER",
            "fa": f"{RLM}مانع{RLM}"
        },
        "sch_screen": {
            "en": "SCREEN",
            "fa": f"{RLM}پرده{RLM}"
        },
        "sch_observer_active": {
            "en": "⚡ OBSERVER ACTIVE: PATH KNOWN - NO INTERFERENCE",
            "fa": f"{RLM}⚡ ناظر فعال: مسیر ذره معین شد - تداخل محو شد{RLM}"
        },

        # History / Classroom Tutorial Tab
        "tab_history": {
            "en": "History",
            "fa": f"{RLM}تاریخچه و آموزش{RLM}"
        },
        "hist_prev": {
            "en": "← Previous",
            "fa": f"{RLM}قبلی ←{RLM}"
        },
        "hist_next": {
            "en": "Next →",
            "fa": f"{RLM}بعدی →{RLM}"
        },
        "hist_contents": {
            "en": "Chapters:",
            "fa": f"{RLM}سرفصل‌ها:{RLM}"
        },
        "hist_sec_timeline": {
            "en": "Timeline of Light",
            "fa": f"{RLM}خط زمانی نور{RLM}"
        },
        "hist_sec_theory": {
            "en": "Classical Theory",
            "fa": f"{RLM}تئوری کلاسیک{RLM}"
        },
        "hist_sec_demo": {
            "en": "Live Demo",
            "fa": f"{RLM}نمایش زنده{RLM}"
        },
        "hist_sec_quantum": {
            "en": "Quantum Wonders",
            "fa": f"{RLM}شگفتی‌های کوانتومی{RLM}"
        },
        "hist_sec_quiz": {
            "en": "Class Quiz",
            "fa": f"{RLM}آزمون کلاسی{RLM}"
        },
        "hist_photo_na": {
            "en": "Photo unavailable offline",
            "fa": f"{RLM}عکس در حالت آفلاین در دسترس نیست{RLM}"
        },
        "hist_live_badge": {
            "en": "● LIVE — follows current lab settings",
            "fa": f"{RLM}● زنده — با تنظیمات فعلی آزمایشگاه{RLM}"
        },
        "hist_score": {
            "en": "Score",
            "fa": f"{RLM}امتیاز{RLM}"
        },
        "hist_correct": {
            "en": "✓ Correct! Well done.",
            "fa": f"{RLM}✓ آفرین! پاسخ درست است.{RLM}"
        },
        "hist_wrong": {
            "en": "✗ Not quite. Read the explanation below.",
            "fa": f"{RLM}✗ درست نیست. توضیح زیر را بخوان.{RLM}"
        },
        "hist_retry": {
            "en": "Restart Quiz",
            "fa": f"{RLM}شروع دوباره آزمون{RLM}"
        },
        "hist_explanation": {
            "en": "Why:",
            "fa": f"{RLM}چرا:{RLM}"
        },

        # Fullscreen & Theater Controls
        "fullscreen_toggle": {
            "en": "Fullscreen",
            "fa": f"{RLM}تمام‌صفحه{RLM}"
        },
        "windowed_toggle": {
            "en": "Windowed",
            "fa": f"{RLM}پنجره‌ای{RLM}"
        },
        "theater_toggle": {
            "en": "Theater",
            "fa": f"{RLM}حالت تئاتر{RLM}"
        },
        "restore_panels": {
            "en": "Restore Panels",
            "fa": f"{RLM}بازگردانی پنل‌ها{RLM}"
        },
        "presentation_mode": {
            "en": "Presentation",
            "fa": f"{RLM}حالت ارائه{RLM}"
        },
        "exit_presentation": {
            "en": "Exit",
            "fa": f"{RLM}خروج{RLM}"
        },
        "web_presentation_btn": {
            "en": "Open in Browser",
            "fa": f"{RLM}باز کردن ارائه در مرورگر{RLM}"
        },
        "web_presentation_short": {
            "en": "Web Presentation",
            "fa": f"{RLM}ارائه در مرورگر{RLM}"
        },

        # Software Guide Tab
        "tab_guide": {
            "en": "Software Guide",
            "fa": f"{RLM}راهنمای نرم‌افزار{RLM}"
        },
        "guide_prev": {
            "en": "Previous Step",
            "fa": f"{RLM}گام قبلی{RLM}"
        },
        "guide_next": {
            "en": "Next Step",
            "fa": f"{RLM}گام بعدی{RLM}"
        },
        "guide_contents": {
            "en": "Modules Guide",
            "fa": f"{RLM}فهرست بخش‌های راهنما{RLM}"
        },
        "guide_badge": {
            "en": "Interactive Software Walkthrough",
            "fa": f"{RLM}تور تعاملی و جامع بخش‌های نرم‌افزار{RLM}"
        },

        # Canvas & Diagram Localization
        "canvas_laser": {
            "en": "LASER",
            "fa": "لیزر"
        },
        "canvas_barrier": {
            "en": "BARRIER",
            "fa": "مانع"
        },
        "canvas_slits": {
            "en": "Slits (d)",
            "fa": "شکاف‌ها (d)"
        },
        "canvas_screen": {
            "en": "SCREEN",
            "fa": "پرده آشکارساز"
        },
        "canvas_maxima": {
            "en": "Bright Fringe",
            "fa": "نوار روشن (بیشینه)"
        },
        "canvas_minima": {
            "en": "Dark Fringe",
            "fa": "نوار تاریک (کمینه)"
        },
        "canvas_path_diff": {
            "en": "Path Diff Δr = d·sinθ",
            "fa": "اختلاف راه: Δr = d·sinθ"
        },
        "canvas_phase_diff": {
            "en": "Phase Diff Δφ",
            "fa": "اختلاف فاز: Δφ"
        },
        "canvas_coherence": {
            "en": "Coherent Interference",
            "fa": "تداخل همدوس"
        },
        "canvas_decoherence": {
            "en": "Decoherence (Observer)",
            "fa": "ناهمدوسی (ناظر فعال)"
        }
    }

    @classmethod
    def get(cls, key: str) -> str:
        """Returns localized string in current language."""
        return cls.STRINGS.get(key, {}).get(cls._CURRENT_LANG, key)

    @classmethod
    def set_language(cls, lang: str):
        """Sets active language ('fa' or 'en')."""
        if lang in ("fa", "en"):
            cls._CURRENT_LANG = lang

    @classmethod
    def toggle_language(cls) -> str:
        """Toggles between English and Persian."""
        cls._CURRENT_LANG = "en" if cls._CURRENT_LANG == "fa" else "fa"
        return cls._CURRENT_LANG

    @classmethod
    def current_language(cls) -> str:
        return cls._CURRENT_LANG

    @classmethod
    def is_persian(cls) -> bool:
        return cls._CURRENT_LANG == "fa"

    @classmethod
    @functools.lru_cache(maxsize=512)
    def reshape_text(cls, text: str) -> str:
        """
        Transforms Persian/Arabic bidirectional mixed text for graphical rendering engines
        (Matplotlib, PIL, Tkinter Canvas) lacking native complex text layout engines.
        Safely strips invisible directional control codes that trigger tofu boxes.
        """
        if not text:
            return ""
        # 1. Strip invisible directional control marks (RLM, LRM, embeddings, overrides)
        cleaned = re.sub(r"[‎‏‪-‮⁦-⁩]", "", str(text))

        # 2. Check if text contains Arabic/Persian script
        has_persian = any(
            '؀' <= ch <= 'ۿ' or
            'ݐ' <= ch <= 'ݿ' or
            'ﭐ' <= ch <= '﷿' or
            'ﹰ' <= ch <= '﻿'
            for ch in cleaned
        )
        if not has_persian:
            return cleaned

        # 3. Apply positional glyph connectivity
        reshaped = arabic_reshaper.reshape(cleaned)

        # 4. Apply Unicode Bidirectional Algorithm reordering
        return get_display(reshaped)

    @classmethod
    def get_reshaped(cls, key: str, **kwargs) -> str:
        """Returns localized string, and if language is Persian, reshapes it for graphic renderers."""
        raw = cls.get(key)
        if kwargs:
            raw = raw.format(**kwargs)
        return cls.reshape_text(raw) if cls.is_persian() else raw

    @classmethod
    def render_canvas_persian(
        cls,
        canvas: Any,
        x: float,
        y: float,
        text: str,
        font: Any = ("Segoe UI", 10),
        fill: str = "#FFFFFF",
        anchor: str = "center",
        **kwargs
    ) -> int:
        """
        Renders text on a Tkinter Canvas cleanly.
        Strips invisible directional control codes (RLM/LRM) to eliminate square tofu boxes.
        If in Persian mode and text contains Persian characters, reshapes connected glyphs
        and applies BiDi reordering for the single-line canvas text engine.
        """
        if not text:
            return -1
        # Strip invisible directional control codes
        cleaned = re.sub(r"[‎‏‪-‮⁦-⁩]", "", str(text))
        has_persian = any(
            '؀' <= ch <= 'ۿ' or
            'ݐ' <= ch <= 'ݿ' or
            'ﭐ' <= ch <= '﷿' or
            'ﹰ' <= ch <= '﻿'
            for ch in cleaned
        )
        if cls.is_persian() and has_persian:
            reshaped = arabic_reshaper.reshape(cleaned)
            final_text = get_display(reshaped)
        else:
            final_text = cleaned
        return canvas.create_text(x, y, text=final_text, font=font, fill=fill, anchor=anchor, **kwargs)

