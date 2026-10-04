"""
Software Guide View — interactive classroom guide walking users through every feature of the simulator.

Dark cinematic laboratory theme with native CustomTkinter cards, Vazirmatn typography,
procedural vector visualizers for each tool, and full Presentation Mode support.
"""

import math
import tkinter as tk
from typing import Dict, Any, List, Optional

import customtkinter as ctk
import numpy as np

from ui.content.guide_content import GUIDE_MODULES
from utils.localization import LocalizationService
from utils.font_manager import FontManager

_BG = "#0B0F19"
_CARD = "#131B2E"
_CARD_BORDER = "#1E293B"
_CARD_ALT = "#162036"
_TIP_BG = "#0F231D"
_TIP_BORDER = "#10B981"
_INK = "#F3F4F6"
_MUTED = "#94A3B8"
_ACCENT = "#38BDF8"
_ACCENT2 = "#F59E0B"


class SoftwareGuideView(ctk.CTkScrollableFrame):
    """Educational walkthrough view explaining every module, view, and tool in the software."""

    def __init__(self, master, on_toggle_theater: Optional[Any] = None, **kwargs):
        super().__init__(master, fg_color=_BG, **kwargs)
        self.on_toggle_theater = on_toggle_theater
        self.module_index = 0
        self.is_presentation_mode = False

        self._point_labels: List[ctk.CTkLabel] = []
        self._canvas: Optional[tk.Canvas] = None
        self._built = False

        self._create_chrome()
        self.after_idle(self._first_show)

    def _first_show(self):
        self._built = True
        self.show_module(0)
        self._update_dropdown_values()

    def _update_dropdown_values(self):
        is_fa = LocalizationService.is_persian()
        names = [m["title_fa"] if is_fa else m["title_en"] for m in GUIDE_MODULES]
        try:
            self.module_menu.configure(values=names)
            self.module_menu.set(names[self.module_index])
        except Exception:
            pass

    # ======================================================================
    # Chrome Setup
    # ======================================================================
    def _create_chrome(self):
        self.grid_columnconfigure(0, weight=1)
        is_fa = LocalizationService.is_persian()

        # ---------------- Header Card ----------------
        self.header = ctk.CTkFrame(self, fg_color=_CARD, corner_radius=12, border_width=1, border_color=_CARD_BORDER)
        self.header.grid(row=0, column=0, padx=14, pady=(12, 6), sticky="ew")
        self.header.grid_columnconfigure(1, weight=1)

        self.category_badge = ctk.CTkLabel(
            self.header, text="",
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            fg_color="#065F46", text_color="#A7F3D0", corner_radius=8, padx=12, pady=4
        )
        self.category_badge.grid(row=0, column=0, padx=12, pady=8, sticky="w")

        self.btn_presentation = ctk.CTkButton(
            self.header,
            text=LocalizationService.get("presentation_mode"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            fg_color="#1E293B", hover_color="#334155", text_color="#E2E8F0",
            border_width=1, border_color="#10B981",
            height=28, width=100,
            command=self.toggle_presentation_mode
        )
        self.btn_presentation.grid(row=0, column=1, padx=4, pady=8, sticky="w")

        self.btn_web_presentation = ctk.CTkButton(
            self.header,
            text=LocalizationService.get("web_presentation_btn"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            fg_color="#065F46", hover_color="#059669", text_color="#FFFFFF",
            border_width=1, border_color="#10B981",
            height=28, width=150,
            command=self._open_web_presentation
        )
        self.btn_web_presentation.grid(row=0, column=2, padx=4, pady=8, sticky="w")

        self.counter_label = ctk.CTkLabel(
            self.header, text="",
            font=FontManager.get_number_font(11, "bold"),
            text_color=_MUTED
        )
        self.counter_label.grid(row=0, column=3, padx=12, pady=8, sticky="e")

        self.progress = ctk.CTkProgressBar(self.header, height=6, progress_color="#10B981", fg_color="#1E293B")
        self.progress.grid(row=1, column=0, columnspan=4, padx=12, pady=(0, 10), sticky="ew")
        self.progress.set(0.0)

        # ---------------- Main Instruction Card ----------------
        self.body_card = ctk.CTkFrame(self, fg_color=_CARD, corner_radius=12, border_width=1, border_color=_CARD_BORDER)
        self.body_card.grid(row=1, column=0, padx=14, pady=6, sticky="ew")
        self.body_card.grid_columnconfigure(0, weight=1)
        self.body_card.bind("<Configure>", lambda _e: self._on_body_resize())

        # Module Title
        self.title_label = ctk.CTkLabel(
            self.body_card, text="",
            font=FontManager.get_persian_font(16, "bold") if is_fa else FontManager.get_number_font(16, "bold"),
            text_color="#10B981", anchor="e" if is_fa else "w", justify="right" if is_fa else "left"
        )
        self.title_label.grid(row=0, column=0, padx=16, pady=(14, 8), sticky="ew")

        # Instruction points holder
        self.points_holder = ctk.CTkFrame(self.body_card, fg_color="transparent")
        self.points_holder.grid(row=1, column=0, padx=16, pady=(0, 10), sticky="ew")
        self.points_holder.grid_columnconfigure(0, weight=1)

        # Tip / Key Takeaway Card
        self.tip_frame = ctk.CTkFrame(self.body_card, fg_color=_TIP_BG, corner_radius=8, border_width=1, border_color=_TIP_BORDER)
        self.tip_frame.grid(row=2, column=0, padx=16, pady=(4, 14), sticky="ew")
        self.tip_frame.grid_columnconfigure(0, weight=1)

        self.tip_label = ctk.CTkLabel(
            self.tip_frame, text="",
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            text_color="#6EE7B7", wraplength=640,
            anchor="e" if is_fa else "w", justify="right" if is_fa else "left"
        )
        self.tip_label.grid(row=0, column=0, padx=14, pady=10, sticky="ew")

        # ---------------- Vector Diagram / Visualizer Card ----------------
        self.visual_card = ctk.CTkFrame(self, fg_color=_CARD, corner_radius=12, border_width=1, border_color=_CARD_BORDER)
        self.visual_card.grid(row=2, column=0, padx=14, pady=6, sticky="ew")
        self.visual_card.grid_columnconfigure(0, weight=1)

        self.visual_holder = ctk.CTkFrame(self.visual_card, fg_color="transparent")
        self.visual_holder.grid(row=0, column=0, padx=12, pady=12, sticky="ew")
        self.visual_holder.grid_columnconfigure(0, weight=1)

        # ---------------- Bottom Navigation Bar ----------------
        self.nav = ctk.CTkFrame(self, fg_color="transparent")
        self.nav.grid(row=3, column=0, padx=14, pady=(8, 16), sticky="ew")
        self.nav.grid_columnconfigure(1, weight=1)

        self.prev_btn = ctk.CTkButton(
            self.nav, text="", height=36, width=120,
            fg_color="#1E293B", hover_color="#334155",
            border_width=1, border_color="#10B981",
            command=self.prev_module,
            font=FontManager.get_persian_font(12, "bold") if is_fa else FontManager.get_number_font(12, "bold")
        )
        self.prev_btn.grid(row=0, column=0, padx=4, sticky="w")

        self.dots_label = ctk.CTkLabel(
            self.nav, text="", font=FontManager.get_number_font(11), text_color=_MUTED
        )
        self.dots_label.grid(row=0, column=1, sticky="ew")

        self.module_menu = ctk.CTkOptionMenu(
            self.nav, values=[], command=self._on_menu_jump, height=36, width=220,
            fg_color="#065F46", button_color="#047857",
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            dropdown_font=FontManager.get_persian_font(11) if is_fa else FontManager.get_number_font(11)
        )
        self.module_menu.grid(row=0, column=2, padx=4, sticky="e")

        self.next_btn = ctk.CTkButton(
            self.nav, text="", height=36, width=120,
            fg_color="#059669", hover_color="#047857",
            command=self.next_module,
            font=FontManager.get_persian_font(12, "bold") if is_fa else FontManager.get_number_font(12, "bold")
        )
        self.next_btn.grid(row=0, column=3, padx=4, sticky="e")

    # ======================================================================
    # Presentation Mode Toggle
    # ======================================================================
    def toggle_presentation_mode(self):
        self.is_presentation_mode = not self.is_presentation_mode
        if self.is_presentation_mode:
            self.btn_presentation.configure(
                text=LocalizationService.get("exit_presentation"),
                fg_color="#DC2626", hover_color="#B91C1C", border_color="#EF4444"
            )
            if callable(self.on_toggle_theater):
                self.on_toggle_theater(force_theater=True)
        else:
            self.btn_presentation.configure(
                text=LocalizationService.get("presentation_mode"),
                fg_color="#1E293B", hover_color="#334155", border_color="#10B981"
            )
            if callable(self.on_toggle_theater):
                self.on_toggle_theater(force_theater=False)
        self.show_module(self.module_index)

    def _open_web_presentation(self):
        """Launches the interactive web presentation deck at the Guide section."""
        from utils.web_presentation_service import WebPresentationService
        WebPresentationService.open_in_browser(section="guide")

    def _on_body_resize(self):
        w = self.body_card.winfo_width()
        if w < 100:
            return
        target_wrap = max(280, w - 52)
        self.title_label.configure(wraplength=target_wrap)
        self.tip_label.configure(wraplength=target_wrap)
        for lbl in self._point_labels:
            try:
                lbl.configure(wraplength=target_wrap)
            except Exception:
                pass

    # ======================================================================
    # Module Rendering
    # ======================================================================
    def show_module(self, index: int):
        total = len(GUIDE_MODULES)
        index = max(0, min(total - 1, index))
        self.module_index = index
        is_fa = LocalizationService.is_persian()
        mod = GUIDE_MODULES[index]

        cat = mod["category_fa"] if is_fa else mod["category_en"]
        title = mod["title_fa"] if is_fa else mod["title_en"]
        points = mod["points_fa"] if is_fa else mod["points_en"]
        tip = mod["tip_fa"] if is_fa else mod["tip_en"]

        self.category_badge.configure(text=f"{mod.get('icon', '📖')} {cat}")
        self.counter_label.configure(text=f"{index + 1} / {total}")
        self.progress.set((index + 1) / total)

        title_size = 20 if self.is_presentation_mode else 16
        body_size = 14 if self.is_presentation_mode else 12

        self.title_label.configure(
            text=f"{mod.get('icon', '')} {title}",
            font=FontManager.get_persian_font(title_size, "bold") if is_fa else FontManager.get_number_font(title_size, "bold"),
            anchor="e" if is_fa else "w",
            justify="right" if is_fa else "left"
        )

        # Clear existing point labels
        for child in self.points_holder.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass
        self._point_labels = []

        target_wrap = max(280, self.body_card.winfo_width() - 52)

        for p_text in points:
            row_frame = ctk.CTkFrame(self.points_holder, fg_color="transparent")
            row_frame.pack(fill="x", padx=2, pady=4)
            row_frame.grid_columnconfigure(0, weight=1)

            lbl = ctk.CTkLabel(
                row_frame,
                text=f"• {p_text}",
                font=FontManager.get_persian_font(body_size) if is_fa else FontManager.get_number_font(body_size),
                text_color=_INK,
                wraplength=target_wrap,
                anchor="e" if is_fa else "w",
                justify="right" if is_fa else "left"
            )
            lbl.grid(row=0, column=0, sticky="ew")
            self._point_labels.append(lbl)

        # Tip Card
        self.tip_label.configure(text=f"💡 {tip}")

        # Update Navigation Buttons
        self.prev_btn.configure(
            text=LocalizationService.get("guide_prev"),
            state="disabled" if index == 0 else "normal"
        )
        self.next_btn.configure(
            text=LocalizationService.get("guide_next"),
            state="disabled" if index == total - 1 else "normal"
        )

        dots = "".join("●" if i == index else "○" for i in range(total))
        self.dots_label.configure(text=dots)

        try:
            self.module_menu.set(title)
        except Exception:
            pass

        # Render Module Vector Graphic
        self._render_module_diagram(mod["id"], is_fa)

    def _render_module_diagram(self, mod_id: str, is_fa: bool):
        for child in self.visual_holder.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass

        h = 360 if self.is_presentation_mode else 240
        cv = tk.Canvas(
            self.visual_holder, bg=_BG, highlightthickness=1,
            highlightbackground=_CARD_BORDER, height=h
        )
        cv.grid(row=0, column=0, sticky="ew")
        self._canvas = cv
        cv.after_idle(lambda: self._draw_diagram(cv, mod_id, is_fa))

    def _draw_diagram(self, cv: tk.Canvas, mod_id: str, is_fa: bool):
        cv.delete("all")
        w = cv.winfo_width() or 640
        h = cv.winfo_height() or 240
        cy = h // 2

        if mod_id == "g1_overview":
            # Architecture Diagram: Top Bar, Left Controls, Views Workspace, Bottom Metrics
            cv.create_rectangle(30, 20, w - 30, 50, fill="#1E293B", outline="#3B82F6", width=2)
            LocalizationService.render_canvas_persian(cv, w // 2, 35, "نوار ناوبری بالایی (Top Bar: حالت‌ها، زبان، پوسته، تمام‌صفحه)" if is_fa else "Top Bar (Modes, Language, Theme, Fullscreen)", font=("Segoe UI", 9, "bold"), fill="#93C5FD")

            ctrl_w = int(w * 0.28)
            cv.create_rectangle(30, 60, 30 + ctrl_w, h - 55, fill="#1E293B", outline="#F59E0B", width=2)
            LocalizationService.render_canvas_persian(cv, 30 + ctrl_w // 2, cy - 10, "پنل کنترل\n(پارامترها و کوانتوم)" if is_fa else "Control Panel\n(Optics & Quantum)", font=("Segoe UI", 9, "bold"), fill="#FCD34D")

            cv.create_rectangle(40 + ctrl_w, 60, w - 30, h - 55, fill="#1E293B", outline="#10B981", width=2)
            LocalizationService.render_canvas_persian(cv, (40 + ctrl_w + w - 30) // 2, cy - 10, "فضای کاری ۷ نما (پرده، پروفایل، شماتیک، ۳D، محاسبات، تاریخچه، راهنما)" if is_fa else "7 Interactive Views (2D, 1D, Schematic, 3D, Calc, History, Guide)", font=("Segoe UI", 9, "bold"), fill="#6EE7B7")

            cv.create_rectangle(30, h - 45, w - 30, h - 15, fill="#1E293B", outline="#8B5CF6", width=2)
            LocalizationService.render_canvas_persian(cv, w // 2, h - 30, "پنل متریک‌ها و خروجی‌های آزمایشگاه (CSV، عکس ۳۰۰ DPI، مدل OBJ، بسته ZIP)" if is_fa else "Metrics & Scientific Exports (CSV, PNG, OBJ, ZIP)", font=("Segoe UI", 9, "bold"), fill="#C4B5FD")

        elif mod_id == "g2_screen_2d":
            # 2D Screen Ribbon with Millimeter Scale
            sx = w // 2
            cv.create_rectangle(sx - 160, 20, sx + 160, h - 20, fill="#0F172A", outline="#3B82F6", width=2)
            # Simulated interference fringes
            for y_idx in range(24, h - 24, 3):
                dy = (y_idx - cy) / 18.0
                inten = (math.cos(dy * 3.14) ** 2) * math.exp(-(dy ** 2) / 6.0)
                if inten > 0.05:
                    r_c = int(0x00 * inten)
                    g_c = int(0xE6 * inten)
                    b_c = int(0x76 * inten)
                    col = f"#{r_c:02x}{g_c:02x}{b_c:02x}"
                    cv.create_rectangle(sx - 150, y_idx - 1, sx + 150, y_idx + 1, fill=col, outline="")
            # Ruler ticks
            for r_y in range(30, h - 30, 20):
                cv.create_line(sx - 160, r_y, sx - 146, r_y, fill="#FFFFFF", width=1.5)
                cv.create_line(sx + 146, r_y, sx + 160, r_y, fill="#FFFFFF", width=1.5)
            LocalizationService.render_canvas_persian(cv, sx, h - 32, "پرده با پالت‌های رنگی و خط‌کش میلی‌متری" if is_fa else "Calibrated Screen & Millimeter Scale", font=("Segoe UI", 9, "bold"), fill="#FFFFFF")

        elif mod_id == "g3_profile_1d":
            # 1D Sinc Envelope & Maxima Markers
            cv.create_rectangle(40, 20, w - 40, h - 20, fill="#111827", outline="#374151")
            cv.create_line(40, cy + 50, w - 40, cy + 50, fill="#475569", width=1)
            x_arr = np.linspace(44, w - 44, 200)
            y_base = cy + 50
            # Sinc^2 Envelope
            y_env = y_base - 100 * np.exp(-((x_arr - w // 2) ** 2) / 10000.0)
            # Fringes
            y_fringes = y_base - 100 * (np.cos((x_arr - w // 2) * 0.12) ** 2) * np.exp(-((x_arr - w // 2) ** 2) / 10000.0)
            for i in range(len(x_arr) - 1):
                cv.create_line(x_arr[i], y_env[i], x_arr[i+1], y_env[i+1], fill="#F59E0B", width=1.5, dash=(4, 2))
                cv.create_line(x_arr[i], y_fringes[i], x_arr[i+1], y_fringes[i+1], fill="#38BDF8", width=2)
            # Maxima marker
            cv.create_text(w // 2, y_fringes[len(x_arr) // 2] - 12, text="▲ m=0", fill="#FFFFFF", font=("Segoe UI", 9, "bold"))
            LocalizationService.render_canvas_persian(cv, w // 2, 34, "پوش پراش تک‌شکاف sinc² (خط‌چین) و قله‌های بیشینه" if is_fa else "sinc² Diffraction Envelope (Dashed) & Maxima", font=("Segoe UI", 9, "bold"), fill="#F59E0B")

        elif mod_id == "g4_schematic":
            # Interactive point P, wavelets and right triangle
            cv.create_line(60, cy - 35, w - 120, cy - 15, fill="#00E676", width=2, dash=(6, 2))
            cv.create_line(60, cy + 35, w - 120, cy - 15, fill="#FFD600", width=2, dash=(6, 2))
            cv.create_oval(w - 126, cy - 21, w - 114, cy - 9, fill="#FFFFFF", outline="#00E676", width=2)
            LocalizationService.render_canvas_persian(cv, w - 90, cy - 15, "نقطه P (قابل کشیدن با ماوس)" if is_fa else "Point P (Draggable)", font=("Segoe UI", 9, "bold"), fill="#00E676")
            LocalizationService.render_canvas_persian(cv, w // 2, cy - 40, "مثلث اختلاف راه: Δr = |r2 - r1| = d · sinθ" if is_fa else "Path Difference: Δr = |r2 - r1| = d · sinθ", font=("Segoe UI", 10, "bold"), fill="#FCD34D")

        elif mod_id == "g5_setup_3d":
            # 3D Optical Bench Model Sketch
            cv.create_rectangle(60, cy - 40, w - 60, cy + 40, fill="#1E293B", outline="#475569", width=2)
            cv.create_line(120, cy, w - 140, cy, fill="#EF4444", width=3)
            LocalizationService.render_canvas_persian(cv, w // 2, cy - 15, "میز اپتیکی سه‌بعدی (چرخش ۳۶۰ درجه با درگ ماوس | زوم با اسکرول)" if is_fa else "3D Optical Table (Orbit via Mouse Drag | Zoom via Wheel)", font=("Segoe UI", 10, "bold"), fill="#38BDF8")
            LocalizationService.render_canvas_persian(cv, w // 2, cy + 18, "کلیدهای نماهای آماده: بالا (Top)، روبه‌رو (Front)، کنار (Side)" if is_fa else "Preset Views: Top, Front, Side, Reset", font=("Segoe UI", 9, "bold"), fill="#94A3B8")

        elif mod_id == "g6_calculations":
            # Equations Cards & Inspector Slider Preview
            cv.create_rectangle(50, 30, w - 50, h - 30, fill="#0F172A", outline="#2563EB", width=1.5)
            LocalizationService.render_canvas_persian(cv, w // 2, cy - 35, "Δr = d · (y / L) | Δy = (λ · L) / d | I = 4I₀ cos²(Δφ / 2)" if is_fa else "Δr = d·(y/L) | Δy = (λ·L)/d | I = 4I0 cos²(Δφ/2)", font=("Consolas", 12, "bold"), fill="#38BDF8")
            LocalizationService.render_canvas_persian(cv, w // 2, cy + 5, "کاوشگر نقطه‌ای: محاسبه لحظه‌ای زاویه، فاز و شدت در هر مختصات y" if is_fa else "Point Inspector: Live Angle, Phase & Intensity Evaluation", font=("Segoe UI", 9, "bold"), fill="#6EE7B7")
            LocalizationService.render_canvas_persian(cv, w // 2, cy + 35, "📄 خروجی گزارش Word با فرمول‌های ریاضی رسمی OMML" if is_fa else "📄 Export Word Lab Report with OMML Math Equations", font=("Segoe UI", 9, "bold"), fill="#F59E0B")

        elif mod_id == "g7_quantum":
            # Quantum Wave-Particle Duality
            cv.create_oval(w // 2 - 90, cy - 45, w // 2 - 30, cy + 15, fill="#1E3A8A", outline="#38BDF8", width=2)
            cv.create_text(w // 2 - 60, cy - 15, text="ψ(y)", fill="#38BDF8", font=("Consolas", 13, "bold"))
            cv.create_text(w // 2, cy - 15, text="➔", fill="#94A3B8", font=("Segoe UI", 16))
            cv.create_oval(w // 2 + 30, cy - 45, w // 2 + 90, cy + 15, fill="#065F46", outline="#10B981", width=2)
            cv.create_text(w // 2 + 60, cy - 15, text="|ψ|²", fill="#10B981", font=("Consolas", 13, "bold"))
            LocalizationService.render_canvas_persian(cv, w // 2, cy + 45, "دوگانگی موج-ذره: فوتون، الکترون، نوترون، آلفا، مولکول باکی‌بال C₆₀" if is_fa else "Wave-Particle Duality: Photons, Electrons, Neutrons, Alphas, C60 Buckyballs", font=("Segoe UI", 10, "bold"), fill="#A7F3D0")

        elif mod_id == "g8_which_way_exports":
            # Observer & 4 Export Formats
            formats = ["📊 CSV (22 ستون)", "🖼 عکس 300 DPI", "📐 مدل 3D OBJ", "📦 بسته ZIP"] if is_fa else \
                      ["📊 CSV (22 Cols)", "🖼 300 DPI Plot", "📐 3D OBJ Model", "📦 Lab ZIP Bundle"]
            box_w = (w - 100) // 4
            for i, fmt in enumerate(formats):
                bx = 50 + i * box_w
                cv.create_rectangle(bx + 4, cy - 25, bx + box_w - 4, cy + 25, fill="#1E293B", outline="#10B981", width=1.5)
                LocalizationService.render_canvas_persian(cv, bx + box_w // 2, cy, fmt, font=("Segoe UI", 9, "bold"), fill="#E2E8F0")
            LocalizationService.render_canvas_persian(cv, w // 2, cy - 50, "سوییچ ناظر Which-Way: شبیه‌سازی فروریزش تابع موج و ناهمدوسی" if is_fa else "Which-Way Switch: Simulates Decoherence & Wavefunction Collapse", font=("Segoe UI", 10, "bold"), fill="#EF4444")

    # ======================================================================
    # Navigation & Lifecycle
    # ======================================================================
    def next_module(self):
        self.show_module(self.module_index + 1)

    def prev_module(self):
        self.show_module(self.module_index - 1)

    def _on_menu_jump(self, chosen: str):
        is_fa = LocalizationService.is_persian()
        for i, m in enumerate(GUIDE_MODULES):
            if chosen in (m["title_fa"], m["title_en"]):
                self.show_module(i)
                return

    def refresh_language(self):
        self._update_dropdown_values()
        is_fa = LocalizationService.is_persian()
        self.btn_presentation.configure(
            text=LocalizationService.get("presentation_mode"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )
        if hasattr(self, "btn_web_presentation"):
            self.btn_web_presentation.configure(
                text=LocalizationService.get("web_presentation_btn"),
                font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
            )
        self.show_module(self.module_index)
