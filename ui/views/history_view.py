"""
History & Classroom Tutorial View — animated slide deck about Young's experiment.

Dark cinematic laboratory theme (deep space background, luminous cards, glowing lasers)
with high readability in both Persian and English.
Uses native CustomTkinter card components (CTkLabel, CTkFrame) with Vazirmatn typography
to provide natural, flawless right-to-left Persian text flow without line inversion.

Figures:
  - Real historical photos (Thomas Young, Hitachi buildup, C60)
  - Procedural Vector Apparatus Diagram (Laser, Collimator, Slits, Screen, Ray Tracing)
  - 60 FPS Huygens Wave Propagation with constructive & destructive interference bands
  - Path-Difference Right Triangle Geometry with localized annotations
  - Wave Superposition & Rotating Phasor Diagram
  - Quantum Particle Buildup with phosphor decay trail and Which-Way detector toggle
  - Live Matplotlib Analytical Fringe Plot wired to simulator engine parameters
  - Interactive Classroom Quiz with Persian numbering, right-aligned options, and feedback
  - Full Presentation / Theater Mode with scaled typography and wide-screen projection.
"""

import math
import os
import re
import tkinter as tk
from typing import Dict, Any, List, Optional

import customtkinter as ctk
import numpy as np
from PIL import Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ui.content.history_content import SLIDES, QUIZ, SECTIONS, SECTION_TITLES, grade
from utils.localization import LocalizationService
from utils.font_manager import FontManager
from utils.color_utils import ColorUtils
from physics.classical_engine import OpticalParameters

# Cinematic Dark Palette
_BG = "#0B0F19"
_CARD = "#131B2E"
_CARD_BORDER = "#1E293B"
_CARD_ALT = "#162036"
_FORMULA_BG = "#0D1527"
_FORMULA_BORDER = "#2563EB"
_INK = "#F3F4F6"
_MUTED = "#94A3B8"
_ACCENT = "#38BDF8"
_ACCENT_HOVER = "#0284C7"
_ACCENT2 = "#F59E0B"
_GOOD = "#10B981"
_BAD = "#EF4444"

_IMG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "assets", "images", "history",
)


class HistoryView(ctk.CTkScrollableFrame):
    """Slide-deck classroom view with native card typography, procedural vector diagrams, and quiz."""

    def __init__(self, master, on_toggle_theater: Optional[Any] = None, **kwargs):
        super().__init__(master, fg_color=_BG, **kwargs)
        self.on_toggle_theater = on_toggle_theater
        self.slide_index = 0
        self.quiz_index = 0
        self.quiz_score = 0
        self.quiz_answered = 0
        self.quiz_locked = False
        self.is_presentation_mode = False

        self._anim_job: Optional[str] = None
        self._anim_phase = 0.0
        self._photo_refs: List[Any] = []
        self._optical = OpticalParameters()
        self._buildup_dots: List[Dict[str, Any]] = []
        self._buildup_job_active = False
        self._buildup_observer_active = False
        self._quiz_buttons: List[ctk.CTkButton] = []
        self._canvas: Optional[tk.Canvas] = None
        self._mpl_fig: Optional[Figure] = None
        self._mpl_canvas: Optional[FigureCanvasTkAgg] = None
        self._mpl_line = None
        self._body_labels: List[ctk.CTkLabel] = []
        self._modal_window: Optional[ctk.CTkToplevel] = None
        self._modal_canvas: Optional[tk.Canvas] = None
        self._built = False

        self._create_chrome()
        self.after_idle(self._first_show)

    def _first_show(self):
        self._built = True
        self.show_slide(0)
        try:
            is_fa = LocalizationService.is_persian()
            names = [SECTION_TITLES[s][1] if is_fa else SECTION_TITLES[s][2] for s in SECTIONS]
            self.section_menu.configure(values=names)
            self.section_menu.set(names[0])
        except Exception:
            pass

    # ======================================================================
    # UI Layout & Chrome
    # ======================================================================
    def _create_chrome(self):
        self.grid_columnconfigure(0, weight=1)
        is_fa = LocalizationService.is_persian()

        # ---------------- Top Navigation & Progress Bar ----------------
        self.header = ctk.CTkFrame(self, fg_color=_CARD, corner_radius=12, border_width=1, border_color=_CARD_BORDER)
        self.header.grid(row=0, column=0, padx=14, pady=(12, 6), sticky="ew")
        self.header.grid_columnconfigure(1, weight=1)

        # Section badge (Timeline / Theory / Demo / Quantum / Quiz)
        self.section_badge = ctk.CTkLabel(
            self.header, text="",
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            fg_color="#1E3A8A", text_color="#93C5FD", corner_radius=8, padx=12, pady=4
        )
        self.section_badge.grid(row=0, column=0, padx=12, pady=8, sticky="w")

        # Presentation Mode Button
        self.btn_presentation = ctk.CTkButton(
            self.header,
            text=LocalizationService.get("presentation_mode"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            fg_color="#1E293B", hover_color="#334155", text_color="#E2E8F0",
            border_width=1, border_color="#3B82F6",
            height=28, width=100,
            command=self.toggle_presentation_mode
        )
        self.btn_presentation.grid(row=0, column=1, padx=4, pady=8, sticky="w")

        # Open in Web Browser Button
        self.btn_web_presentation = ctk.CTkButton(
            self.header,
            text=LocalizationService.get("web_presentation_btn"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            fg_color="#1E3A8A", hover_color="#2563EB", text_color="#FFFFFF",
            border_width=1, border_color="#38BDF8",
            height=28, width=150,
            command=self._open_web_presentation
        )
        self.btn_web_presentation.grid(row=0, column=2, padx=4, pady=8, sticky="w")

        # Slide counter
        self.counter_label = ctk.CTkLabel(
            self.header, text="",
            font=FontManager.get_number_font(11, "bold"),
            text_color=_MUTED
        )
        self.counter_label.grid(row=0, column=3, padx=12, pady=8, sticky="e")

        # Progress bar
        self.progress = ctk.CTkProgressBar(self.header, height=6, progress_color=_ACCENT, fg_color="#1E293B")
        self.progress.grid(row=1, column=0, columnspan=4, padx=12, pady=(0, 10), sticky="ew")
        self.progress.set(0.0)

        # ---------------- Native Card Body Container ----------------
        self.body_card = ctk.CTkFrame(self, fg_color=_CARD, corner_radius=12, border_width=1, border_color=_CARD_BORDER)
        self.body_card.grid(row=1, column=0, padx=14, pady=6, sticky="ew")
        self.body_card.grid_columnconfigure(0, weight=1)
        self.body_card.bind("<Configure>", lambda _e: self._on_body_resize())

        # Slide Title
        self.title_label = ctk.CTkLabel(
            self.body_card, text="",
            font=FontManager.get_persian_font(16, "bold") if is_fa else FontManager.get_number_font(16, "bold"),
            text_color="#38BDF8", anchor="e" if is_fa else "w", justify="right" if is_fa else "left"
        )
        self.title_label.grid(row=0, column=0, padx=16, pady=(14, 8), sticky="ew")

        # Container for paragraph and formula cards
        self.paragraphs_holder = ctk.CTkFrame(self.body_card, fg_color="transparent")
        self.paragraphs_holder.grid(row=1, column=0, padx=16, pady=(0, 14), sticky="ew")
        self.paragraphs_holder.grid_columnconfigure(0, weight=1)

        # ---------------- Figure Container ----------------
        self.fig_card = ctk.CTkFrame(self, fg_color=_CARD, corner_radius=12, border_width=1, border_color=_CARD_BORDER)
        self.fig_card.grid(row=2, column=0, padx=14, pady=6, sticky="ew")
        self.fig_card.grid_columnconfigure(0, weight=1)

        fig_top_bar = ctk.CTkFrame(self.fig_card, fg_color="transparent")
        fig_top_bar.grid(row=0, column=0, padx=12, pady=(8, 0), sticky="ew")
        fig_top_bar.grid_columnconfigure(0, weight=1)

        self.live_badge = ctk.CTkLabel(
            fig_top_bar, text="",
            font=FontManager.get_persian_font(10, "bold") if is_fa else FontManager.get_number_font(10, "bold"),
            text_color=_ACCENT2, anchor="w"
        )
        self.live_badge.grid(row=0, column=0, sticky="w")

        # Interactive controls for figures (e.g., Which-Way observer toggle in buildup)
        self.fig_ctrl_btn = ctk.CTkButton(
            fig_top_bar, text="", height=24, width=130,
            font=FontManager.get_persian_font(9, "bold") if is_fa else FontManager.get_number_font(9, "bold"),
            fg_color="#1E293B", hover_color="#334155",
            command=self._toggle_buildup_observer
        )

        # Fullscreen / Enlarged modal expansion button
        self.expand_btn = ctk.CTkButton(
            fig_top_bar, text=LocalizationService.get("fig_expand"),
            height=24, width=95,
            font=FontManager.get_persian_font(9, "bold") if is_fa else FontManager.get_number_font(9, "bold"),
            fg_color="#1E293B", hover_color="#2563EB",
            border_width=1, border_color="#3B82F6",
            command=self._open_enlarged_figure
        )
        self.expand_btn.grid(row=0, column=2, sticky="e", padx=(4, 0))

        self.fig_holder = ctk.CTkFrame(self.fig_card, fg_color="transparent")
        self.fig_holder.grid(row=1, column=0, padx=12, pady=6, sticky="ew")
        self.fig_holder.grid_columnconfigure(0, weight=1)

        self.caption_label = ctk.CTkLabel(
            self.fig_card, text="",
            font=FontManager.get_persian_font(10) if is_fa else FontManager.get_number_font(10),
            text_color=_MUTED, wraplength=640, anchor="center"
        )
        self.caption_label.grid(row=2, column=0, padx=12, pady=(0, 10), sticky="ew")

        # ---------------- Quiz Card (Visible on Quiz Slides) ----------------
        self.quiz_card = ctk.CTkFrame(self, fg_color=_CARD, corner_radius=12, border_width=1, border_color=_CARD_BORDER)
        self.quiz_card.grid(row=3, column=0, padx=14, pady=6, sticky="ew")
        self.quiz_card.grid_columnconfigure(0, weight=1)

        self.quiz_q_label = ctk.CTkLabel(
            self.quiz_card, text="", wraplength=640,
            justify="right" if is_fa else "left",
            anchor="e" if is_fa else "w",
            font=FontManager.get_persian_font(13, "bold") if is_fa else FontManager.get_number_font(13, "bold"),
            text_color=_INK
        )
        self.quiz_q_label.grid(row=0, column=0, padx=16, pady=(14, 8), sticky="ew")

        self.quiz_btns_frame = ctk.CTkFrame(self.quiz_card, fg_color="transparent")
        self.quiz_btns_frame.grid(row=1, column=0, padx=16, pady=4, sticky="ew")
        self.quiz_btns_frame.grid_columnconfigure(0, weight=1)

        # Feedback box container
        self.quiz_feedback_frame = ctk.CTkFrame(self.quiz_card, fg_color=_CARD_ALT, corner_radius=8, border_width=1, border_color=_CARD_BORDER)
        self.quiz_feedback_frame.grid(row=2, column=0, padx=16, pady=6, sticky="ew")
        self.quiz_feedback_frame.grid_columnconfigure(0, weight=1)

        self.quiz_feedback = ctk.CTkLabel(
            self.quiz_feedback_frame, text="", wraplength=640,
            justify="right" if is_fa else "left",
            anchor="e" if is_fa else "w",
            font=FontManager.get_persian_font(11) if is_fa else FontManager.get_number_font(11),
            text_color=_INK
        )
        self.quiz_feedback.grid(row=0, column=0, padx=12, pady=10, sticky="ew")
        self.quiz_feedback_frame.grid_remove()

        quiz_bottom = ctk.CTkFrame(self.quiz_card, fg_color="transparent")
        quiz_bottom.grid(row=3, column=0, padx=16, pady=(4, 14), sticky="ew")

        self.quiz_score_label = ctk.CTkLabel(
            quiz_bottom, text="",
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            text_color=_ACCENT
        )
        self.quiz_score_label.pack(side="left" if not is_fa else "right", padx=6)

        self.quiz_retry_btn = ctk.CTkButton(
            quiz_bottom, text="", height=28,
            fg_color="#1E293B", hover_color="#334155",
            border_width=1, border_color="#475569",
            command=self._reset_quiz,
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )
        self.quiz_retry_btn.pack(side="right" if not is_fa else "left", padx=6)

        # ---------------- Bottom Navigation Bar ----------------
        self.nav = ctk.CTkFrame(self, fg_color="transparent")
        self.nav.grid(row=4, column=0, padx=14, pady=(8, 16), sticky="ew")
        self.nav.grid_columnconfigure(1, weight=1)

        self.prev_btn = ctk.CTkButton(
            self.nav, text="", height=36, width=120,
            fg_color="#1E293B", hover_color="#334155",
            border_width=1, border_color="#3B82F6",
            command=self.prev_slide,
            font=FontManager.get_persian_font(12, "bold") if is_fa else FontManager.get_number_font(12, "bold")
        )
        self.prev_btn.grid(row=0, column=0, padx=4, sticky="w")

        self.dots_label = ctk.CTkLabel(
            self.nav, text="", font=FontManager.get_number_font(11), text_color=_MUTED
        )
        self.dots_label.grid(row=0, column=1, sticky="ew")

        self.section_menu = ctk.CTkOptionMenu(
            self.nav, values=[], command=self._on_section_jump, height=36, width=180,
            fg_color="#1E3A8A", button_color="#1E40AF",
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            dropdown_font=FontManager.get_persian_font(11) if is_fa else FontManager.get_number_font(11)
        )
        self.section_menu.grid(row=0, column=2, padx=4, sticky="e")

        self.next_btn = ctk.CTkButton(
            self.nav, text="", height=36, width=120,
            fg_color="#2563EB", hover_color="#1D4ED8",
            command=self.next_slide,
            font=FontManager.get_persian_font(12, "bold") if is_fa else FontManager.get_number_font(12, "bold")
        )
        self.next_btn.grid(row=0, column=3, padx=4, sticky="e")

    # ======================================================================
    # Responsive Resizing & Typography
    # ======================================================================
    def _on_body_resize(self):
        w = self.body_card.winfo_width()
        if w < 100:
            return
        target_wrap = max(280, w - 48)
        self.title_label.configure(wraplength=target_wrap)
        for lbl in self._body_labels:
            try:
                lbl.configure(wraplength=target_wrap)
            except Exception:
                pass
        self.quiz_q_label.configure(wraplength=target_wrap)
        self.quiz_feedback.configure(wraplength=target_wrap)
        self.caption_label.configure(wraplength=target_wrap)

    # ======================================================================
    # Presentation Mode Toggle
    # ======================================================================
    def toggle_presentation_mode(self):
        self.is_presentation_mode = not self.is_presentation_mode
        is_fa = LocalizationService.is_persian()
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
                fg_color="#1E293B", hover_color="#334155", border_color="#3B82F6"
            )
            if callable(self.on_toggle_theater):
                self.on_toggle_theater(force_theater=False)
        self.show_slide(self.slide_index)

    def _open_web_presentation(self):
        """Launches the interactive web presentation deck in the default browser."""
        from utils.web_presentation_service import WebPresentationService
        WebPresentationService.open_in_browser(section="history")

    # ======================================================================
    # Slide Rendering Engine
    # ======================================================================
    def _stop_animation(self):
        if self._anim_job is not None:
            try:
                self.after_cancel(self._anim_job)
            except Exception:
                pass
            self._anim_job = None
        self._buildup_job_active = False

    def show_slide(self, index: int):
        total_slides = len(SLIDES) + len(QUIZ)
        index = max(0, min(total_slides - 1, index))
        self.slide_index = index
        is_fa = LocalizationService.is_persian()

        if index < len(SLIDES):
            self._show_content_slide(index, total_slides, is_fa)
        else:
            self._show_quiz_slide(index - len(SLIDES), total_slides, is_fa)

        # Reset scroll position to top of new slide
        try:
            self._parent_canvas.yview_moveto(0.0)
        except Exception:
            pass

        self.counter_label.configure(text=f"{index + 1} / {total_slides}")
        self.progress.set((index + 1) / total_slides)
        dots = "".join("●" if i == index else "○" for i in range(total_slides))
        self.dots_label.configure(text=dots)

        self.prev_btn.configure(
            text=LocalizationService.get("hist_prev"),
            state="disabled" if index == 0 else "normal"
        )
        self.next_btn.configure(
            text=LocalizationService.get("hist_next"),
            state="disabled" if index == total_slides - 1 else "normal"
        )

        # Update active section in dropdown
        cur_sec = SLIDES[index]["section"] if index < len(SLIDES) else "quiz"
        cur_name = SECTION_TITLES[cur_sec][1] if is_fa else SECTION_TITLES[cur_sec][2]
        try:
            self.section_menu.set(cur_name)
        except Exception:
            pass

    def _show_content_slide(self, index: int, total: int, is_fa: bool):
        slide = SLIDES[index]
        title = slide["title_fa"] if is_fa else slide["title_en"]
        paras = slide["body_fa"] if is_fa else slide["body_en"]
        _badge, sec_fa, sec_en = SECTION_TITLES[slide["section"]]
        self.section_badge.configure(text=sec_fa if is_fa else sec_en)

        # Scale fonts for presentation mode
        title_size = 20 if self.is_presentation_mode else 15
        body_size = 14 if self.is_presentation_mode else 12
        formula_size = 15 if self.is_presentation_mode else 13

        self.title_label.configure(
            text=title,
            font=FontManager.get_persian_font(title_size, "bold") if is_fa else FontManager.get_number_font(title_size, "bold"),
            anchor="e" if is_fa else "w",
            justify="right" if is_fa else "left"
        )

        # Clear existing paragraph widgets
        for child in self.paragraphs_holder.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass
        self._body_labels = []

        target_wrap = max(280, self.body_card.winfo_width() - 48)

        # Render each paragraph or formula card
        for p in paras:
            is_pure_formula = (
                ("Δy =" in p or "Δr =" in p or "Δφ =" in p or "I =" in p or "d · sinθ =" in p or "a · sinθ =" in p)
                and len(p) < 80
            )
            if is_pure_formula:
                # Dedicated Formula Callout Card with neon glow
                f_card = ctk.CTkFrame(
                    self.paragraphs_holder,
                    fg_color=_FORMULA_BG,
                    corner_radius=8,
                    border_width=1,
                    border_color=_FORMULA_BORDER
                )
                f_card.pack(fill="x", padx=4, pady=5)

                f_lbl = ctk.CTkLabel(
                    f_card,
                    text=p,
                    font=FontManager.get_number_font(formula_size, "bold"),
                    text_color="#38BDF8",
                    anchor="center",
                    justify="center"
                )
                f_lbl.pack(padx=16, pady=8)
            else:
                p_lbl = ctk.CTkLabel(
                    self.paragraphs_holder,
                    text=p,
                    font=FontManager.get_persian_font(body_size) if is_fa else FontManager.get_number_font(body_size),
                    text_color=_INK,
                    wraplength=target_wrap,
                    anchor="e" if is_fa else "w",
                    justify="right" if is_fa else "left"
                )
                p_lbl.pack(fill="x", padx=4, pady=3)
                self._body_labels.append(p_lbl)

        # Hide Quiz Card on regular content slides
        self.quiz_card.grid_remove()
        self.fig_ctrl_btn.grid_remove()

        # Render associated figure
        self._clear_figure()
        fig = slide.get("figure", {"kind": "none"})
        kind = fig.get("kind", "none")
        cap = fig.get("caption_fa", "") if is_fa else fig.get("caption_en", "")

        if kind != "none":
            self.expand_btn.grid(row=0, column=2, sticky="e", padx=(4, 0))
        else:
            self.expand_btn.grid_remove()

        if kind == "photo":
            self.live_badge.configure(text="")
            self._build_photo(fig, is_fa)
        elif kind in ("apparatus", "duel"):
            self.live_badge.configure(text="")
            self._build_apparatus_canvas(is_fa)
            self.caption_label.configure(text=cap)
        elif kind == "huygens":
            self.live_badge.configure(text="")
            self._build_huygens_canvas(animated=True, is_fa=is_fa)
            self.caption_label.configure(text=cap)
        elif kind == "triangle":
            self.live_badge.configure(text="")
            self._build_triangle_canvas(is_fa)
            self.caption_label.configure(text=cap)
        elif kind == "interference":
            self.live_badge.configure(text="")
            self._build_interference_canvas(is_fa)
            self.caption_label.configure(text=cap)
        elif kind in ("fringe", "worked_bench", "envelope", "interactive_fringe"):
            self.live_badge.configure(text=LocalizationService.get("hist_live_badge"))
            self._build_fringe_plot(is_fa)
            self.caption_label.configure(text=cap)
        elif kind == "buildup":
            self.live_badge.configure(text="")
            self.fig_ctrl_btn.grid(row=0, column=1, sticky="e")
            self._update_buildup_btn_text()
            self._build_buildup_canvas(is_fa)
            self.caption_label.configure(text=cap)
        else:
            self.live_badge.configure(text="")
            self.caption_label.configure(text="")

    def _show_quiz_slide(self, q_index: int, total: int, is_fa: bool):
        q_index = max(0, min(len(QUIZ) - 1, q_index))
        self.quiz_index = q_index
        self.quiz_locked = False
        q = QUIZ[q_index]
        _badge, sec_fa, sec_en = SECTION_TITLES["quiz"]
        self.section_badge.configure(text=sec_fa if is_fa else sec_en)

        # Title
        q_title = f"پرسش کلاسی {q_index + 1} از {len(QUIZ)}" if is_fa else f"Class Quiz: Question {q_index + 1} of {len(QUIZ)}"
        self.title_label.configure(
            text=q_title,
            anchor="e" if is_fa else "w",
            justify="right" if is_fa else "left"
        )

        for child in self.paragraphs_holder.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass
        self._body_labels = []

        self._clear_figure()
        self.live_badge.configure(text="")
        self.caption_label.configure(text="")
        self.fig_ctrl_btn.grid_remove()
        self.expand_btn.grid_remove()

        self.quiz_card.grid()
        self._render_quiz_question(is_fa)
        self._update_quiz_score_label()

    def _clear_figure(self):
        self._stop_animation()
        for child in self.fig_holder.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass
        # Reset grid weights so multi-image columns do not squash procedural canvases
        self.fig_holder.grid_columnconfigure(0, weight=1)
        self.fig_holder.grid_columnconfigure(1, weight=0)
        self._canvas = None
        self._mpl_fig = None
        self._mpl_canvas = None
        self._mpl_line = None
        self._photo_refs = []

    def _get_canvas_width(self, cv: tk.Canvas) -> int:
        """Safely returns the canvas pixel width, falling back to parent container
        if the canvas is not yet mapped on screen."""
        try:
            w = cv.winfo_width()
            if w > 50:
                return w
            pw = self.fig_holder.winfo_width()
            if pw > 50:
                return pw
        except Exception:
            pass
        return 800 if self.is_presentation_mode else 640

    # ======================================================================
    # Procedural Vector Figures & Canvases
    # ======================================================================
    def _new_canvas(self, height: int = 300) -> tk.Canvas:
        h = 440 if self.is_presentation_mode else height
        cv = tk.Canvas(
            self.fig_holder, bg=_BG, highlightthickness=1,
            highlightbackground=_CARD_BORDER, height=h, cursor="hand2"
        )
        cv.grid(row=0, column=0, columnspan=2, sticky="ew", pady=6)
        cv.bind("<Configure>", lambda _e: self._redraw_canvas())
        cv.bind("<Button-1>", lambda _e: self._open_enlarged_figure())
        self._canvas = cv
        return cv

    def _redraw_canvas(self):
        slide = SLIDES[self.slide_index] if self.slide_index < len(SLIDES) else None
        if slide is None or self._canvas is None:
            return
        kind = slide.get("figure", {}).get("kind", "none")
        try:
            w = self._get_canvas_width(self._canvas)
            is_fa = LocalizationService.is_persian()
            if kind in ("apparatus", "duel"):
                self._draw_apparatus(self._canvas, w, is_fa)
            elif kind == "huygens":
                self._draw_huygens(self._canvas, w, animated=False, is_fa=is_fa)
            elif kind == "triangle":
                self._draw_triangle(self._canvas, w, is_fa)
            elif kind == "interference":
                self._draw_interference(self._canvas, w, is_fa)
            elif kind == "buildup":
                self._draw_buildup(self._canvas, w, is_fa)
        except Exception:
            pass

    # ---- 1. Optical Apparatus Vector Diagram ----
    def _build_apparatus_canvas(self, is_fa: bool):
        cv = self._new_canvas(300)
        cv.after_idle(lambda: self._draw_apparatus(cv, self._get_canvas_width(cv), is_fa))

    def _draw_apparatus(self, cv: tk.Canvas, w: int, is_fa: bool):
        cv.delete("all")
        h = cv.winfo_height() or 300
        cy = h // 2

        # 1. Laser Source
        lx1, lx2 = 30, 95
        cv.create_rectangle(lx1, cy - 26, lx2, cy + 26, fill="#1E293B", outline="#3B82F6", width=2)
        cv.create_rectangle(lx2, cy - 14, lx2 + 10, cy + 14, fill="#DC2626", outline="")
        LocalizationService.render_canvas_persian(
            cv, (lx1 + lx2) // 2, cy, LocalizationService.get("canvas_laser"),
            font=("Segoe UI", 10, "bold"), fill="#60A5FA"
        )

        # Incident collimated laser beam
        bx = int(w * 0.40)
        slit_gap = 50
        cv.create_line(lx2 + 10, cy, bx - 8, cy, fill="#EF4444", width=4)
        for off in (-10, 10):
            cv.create_line(lx2 + 10, cy + off, bx - 8, cy + off, fill="#EF4444", width=1.5, dash=(4, 2))

        # 2. Double Slit Barrier Plate
        cv.create_rectangle(bx - 6, 16, bx + 6, cy - slit_gap // 2, fill="#475569", outline="#94A3B8")
        cv.create_rectangle(bx - 6, cy + slit_gap // 2, bx + 6, h - 16, fill="#475569", outline="#94A3B8")
        s1 = (bx, cy - slit_gap // 2)
        s2 = (bx, cy + slit_gap // 2)

        # Slit dimension arrows
        cv.create_line(bx - 18, s1[1], bx - 18, s2[1], fill="#F59E0B", width=2, arrow="both", arrowshape=(6, 8, 3))
        LocalizationService.render_canvas_persian(
            cv, bx - 32, cy, "d", font=("Segoe UI", 11, "bold"), fill="#F59E0B"
        )
        LocalizationService.render_canvas_persian(
            cv, bx, h - 18, LocalizationService.get("canvas_barrier"),
            font=("Segoe UI", 9, "bold"), fill="#94A3B8"
        )

        # 3. Detector Screen
        sx = int(w * 0.90)
        cv.create_rectangle(sx - 6, 16, sx + 6, h - 16, fill="#0F172A", outline="#3B82F6", width=2)
        LocalizationService.render_canvas_persian(
            cv, sx, 18, LocalizationService.get("canvas_screen"),
            font=("Segoe UI", 9, "bold"), fill="#38BDF8"
        )

        # Distance L dimension line
        cv.create_line(bx + 10, h - 26, sx - 10, h - 26, fill="#38BDF8", width=1.5, arrow="both", arrowshape=(6, 8, 3))
        LocalizationService.render_canvas_persian(
            cv, (bx + sx) // 2, h - 38, "L", font=("Segoe UI", 11, "bold"), fill="#38BDF8"
        )

        # Ray Traces to Screen Point P
        py = cy - 44
        cv.create_line(s1[0], s1[1], sx, py, fill="#00E676", width=2, dash=(6, 2))
        cv.create_line(s2[0], s2[1], sx, py, fill="#FFD600", width=2, dash=(6, 2))

        # Spot at point P
        cv.create_oval(sx - 4, py - 4, sx + 4, py + 4, fill="#FFFFFF", outline="#00E676", width=2)
        LocalizationService.render_canvas_persian(
            cv, sx + 18, py, "P", font=("Segoe UI", 10, "bold"), fill="#FFFFFF"
        )

    # ---- 2. 60 FPS Huygens Wave Propagation ----
    def _build_huygens_canvas(self, animated: bool, is_fa: bool):
        cv = self._new_canvas(300)
        if animated:
            self._anim_phase = 0.0
            self._tick_huygens()
        else:
            cv.after_idle(lambda: self._draw_huygens(cv, self._get_canvas_width(cv), animated=False, is_fa=is_fa))

    def _tick_huygens(self):
        if self._canvas is None or not self._canvas.winfo_exists():
            self._anim_job = None
            return
        try:
            w = self._get_canvas_width(self._canvas)
            is_fa = LocalizationService.is_persian()
            self._draw_huygens(self._canvas, w, animated=True, is_fa=is_fa)
        except Exception:
            pass
        self._anim_phase = (self._anim_phase + 0.32) % (2 * math.pi)
        self._anim_job = self.after(30, self._tick_huygens)

    def _draw_huygens(self, cv: tk.Canvas, w: int, animated: bool, is_fa: bool):
        cv.delete("all")
        h = cv.winfo_height() or 300
        barrier_x = int(w * 0.38)
        slit_gap = 60
        cy = h // 2
        phase = self._anim_phase if animated else 1.2
        sx = int(w * 0.90)

        # 1. Incoming Plane Wavefronts
        for k in range(8):
            x = barrier_x - 18 - k * 26 + int(8 * math.sin(phase + k * 0.6))
            if x < 12:
                continue
            alpha = max(0.2, 1.0 - (k / 9.0))
            col = "#38BDF8" if k % 2 == 0 else "#60A5FA"
            cv.create_line(x, 24, x, h - 24, fill=col, width=2)

        # 2. Barrier with Two Slits
        cv.create_rectangle(barrier_x - 6, 12, barrier_x + 6, cy - slit_gap // 2, fill="#334155", outline="#64748B")
        cv.create_rectangle(barrier_x - 6, cy + slit_gap // 2, barrier_x + 6, h - 12, fill="#334155", outline="#64748B")
        s1 = (barrier_x, cy - slit_gap // 2)
        s2 = (barrier_x, cy + slit_gap // 2)

        # 3. Huygens Wavelets expanding from each slit (bounded so they don't overshoot screen or canvas)
        max_r = min(int(w * 0.48), sx - barrier_x - 12)
        for r in range(16, max_r, 22):
            rr = r + (6 * math.sin(phase) if animated else 0)
            if rr <= 6:
                continue
            cv.create_arc(s1[0] - rr, s1[1] - rr, s1[0] + rr, s1[1] + rr,
                          start=-68, extent=136, outline="#00F0FF", width=1.5, style=tk.ARC)
            cv.create_arc(s2[0] - rr, s2[1] - rr, s2[0] + rr, s2[1] + rr,
                          start=-68, extent=136, outline="#F59E0B", width=1.5, style=tk.ARC)

        # 4. Detector Screen & Luminous Interference Ribbon
        cv.create_rectangle(sx - 4, 16, sx + 4, h - 16, fill="#0F172A", outline="#475569")
        for y_idx in range(20, h - 20, 4):
            dy = (y_idx - cy) / 28.0
            inten = (math.cos(dy * 2.8) ** 2) * math.exp(-(dy ** 2) / 6.0)
            if inten > 0.05:
                r_c = int(0x38 * inten)
                g_c = int(0xBD * inten)
                b_c = int(0xF8 * inten)
                col = f"#{r_c:02x}{g_c:02x}{b_c:02x}"
                cv.create_rectangle(sx - 3, y_idx - 2, sx + 3, y_idx + 2, fill=col, outline="")

        # Labels
        LocalizationService.render_canvas_persian(
            cv, 50, 16, LocalizationService.get("canvas_laser"),
            font=("Segoe UI", 9, "bold"), fill="#38BDF8"
        )
        LocalizationService.render_canvas_persian(
            cv, barrier_x, cy, "d", font=("Segoe UI", 10, "bold"), fill="#F59E0B"
        )
        LocalizationService.render_canvas_persian(
            cv, barrier_x, h - 18, LocalizationService.get("canvas_barrier"),
            font=("Segoe UI", 9, "bold"), fill="#94A3B8"
        )
        LocalizationService.render_canvas_persian(
            cv, sx, 18, LocalizationService.get("canvas_screen"),
            font=("Segoe UI", 9, "bold"), fill="#38BDF8"
        )

    # ---- 3. Path Difference Right Triangle ----
    def _build_triangle_canvas(self, is_fa: bool):
        cv = self._new_canvas(300)
        cv.after_idle(lambda: self._draw_triangle(cv, self._get_canvas_width(cv), is_fa))

    def _draw_triangle(self, cv: tk.Canvas, w: int, is_fa: bool):
        cv.delete("all")
        h = cv.winfo_height() or 300
        cy = h // 2
        slit_spacing = min(150, int(h * 0.45))
        s1 = (100, cy - slit_spacing // 2)
        s2 = (100, cy + slit_spacing // 2)
        p = (w - 110, cy - int(slit_spacing * 0.35))

        # Ray lines
        cv.create_line(s1[0], s1[1], p[0], p[1], fill="#38BDF8", width=2.5)
        cv.create_line(s2[0], s2[1], p[0], p[1], fill="#F59E0B", width=2.5)

        # Geometrically accurate projection of S1 onto ray S2 -> P (normal H)
        vx = p[0] - s2[0]
        vy = p[1] - s2[1]
        v_len = max(math.hypot(vx, vy), 1e-6)
        ux, uy = vx / v_len, vy / v_len
        wx = s1[0] - s2[0]
        wy = s1[1] - s2[1]
        proj = wx * ux + wy * uy
        hx = int(s2[0] + proj * ux)
        hy = int(s2[1] + proj * uy)

        # Normal perpendicular line from S1 to H
        cv.create_line(s1[0], s1[1], hx, hy, fill="#EF4444", width=2, dash=(5, 3))
        # Perpendicular right-angle mark at H
        norm_x, norm_y = -uy, ux
        box_sz = 9
        cv.create_line(hx + norm_x * box_sz, hy + norm_y * box_sz,
                       hx + (norm_x + ux) * box_sz, hy + (norm_y + uy) * box_sz,
                       fill="#EF4444", width=1.5)
        cv.create_line(hx + (norm_x + ux) * box_sz, hy + (norm_y + uy) * box_sz,
                       hx + ux * box_sz, hy + uy * box_sz,
                       fill="#EF4444", width=1.5)

        # Highlight extra path segment S2 -> H as Delta r
        cv.create_line(s2[0], s2[1], hx, hy, fill="#EF4444", width=4)

        # Points S1, S2, P, and H
        for cx, cy_pt, t, col in (
            (s1[0], s1[1], "S1", "#38BDF8"),
            (s2[0], s2[1], "S2", "#F59E0B"),
            (p[0], p[1], "P", "#10B981"),
            (hx, hy, "H", "#EF4444")
        ):
            cv.create_oval(cx - 5, cy_pt - 5, cx + 5, cy_pt + 5, fill=col, outline="#FFFFFF", width=1.5)
            cv.create_text(cx - 18 if cx < w // 2 else cx + 18, cy_pt, text=t, fill="#FFFFFF", font=("Segoe UI", 10, "bold"))

        cv.create_text((s1[0] + p[0]) // 2 - 20, (s1[1] + p[1]) // 2 - 16,
                       text="r1", fill="#38BDF8", font=("Segoe UI", 12, "bold"))
        cv.create_text((hx + p[0]) // 2 - 20, (hy + p[1]) // 2 + 18,
                       text="r2", fill="#F59E0B", font=("Segoe UI", 12, "bold"))

        # Slit separation d
        cv.create_line(s1[0] - 16, s1[1], s1[0] - 16, s2[1], fill="#F59E0B", width=2, arrow="both", arrowshape=(6, 8, 3))
        cv.create_text(s1[0] - 32, (s1[1] + s2[1]) // 2, text="d", fill="#F59E0B", font=("Segoe UI", 12, "bold"))

        # Delta r callout badge
        mid_dh_x = (s2[0] + hx) // 2
        mid_dh_y = (s2[1] + hy) // 2 + 28
        cv.create_rectangle(mid_dh_x - 70, mid_dh_y - 14, mid_dh_x + 70, mid_dh_y + 14, fill="#1E293B", outline="#EF4444", width=1.5)
        cv.create_text(mid_dh_x, mid_dh_y, text="Δr = d · sinθ", fill="#EF4444", font=("Segoe UI", 11, "bold"))

    # ---- 4. Superposition & Phasor Circle Visualizer ----
    def _build_interference_canvas(self, is_fa: bool):
        cv = self._new_canvas(300)
        cv.after_idle(lambda: self._draw_interference(cv, self._get_canvas_width(cv), is_fa))

    def _draw_interference(self, cv: tk.Canvas, w: int, is_fa: bool):
        cv.delete("all")
        h = cv.winfo_height() or 300
        cy = h // 2

        # 1. Left side: Superposed Waves plot
        plot_w = int(w * 0.58)
        cv.create_rectangle(20, 20, plot_w, h - 20, fill="#111827", outline="#374151")
        cv.create_line(20, cy, plot_w, cy, fill="#475569", width=1, dash=(3, 3))

        x_pts = np.linspace(24, plot_w - 4, 180)
        # In-phase constructive addition: Wave 1, Wave 2, and Resultant E_net
        y_wave1 = cy - 28 * np.sin((x_pts - 24) * 0.08)
        y_wave2 = cy - 28 * np.sin((x_pts - 24) * 0.08)
        y_net = cy - 56 * np.sin((x_pts - 24) * 0.08)

        # Draw component waves
        for i in range(len(x_pts) - 1):
            cv.create_line(x_pts[i], y_wave1[i], x_pts[i+1], y_wave1[i+1], fill="#38BDF8", width=1.5, dash=(4, 2))
            cv.create_line(x_pts[i], y_net[i], x_pts[i+1], y_net[i+1], fill="#10B981", width=2.5)

        interf_title = "E_net = E1 + E2 (تداخل سازنده I = 4I₀)" if is_fa else "E_net = E1 + E2 (Constructive I = 4I0)"
        LocalizationService.render_canvas_persian(
            cv, plot_w // 2, 34, interf_title,
            font=("Segoe UI", 9 if plot_w > 380 else 8, "bold"), fill="#10B981"
        )

        # 2. Right side: Phasor Circle Diagram
        cx_phasor = int(w * 0.79)
        r_circ = 60
        cv.create_oval(cx_phasor - r_circ, cy - r_circ, cx_phasor + r_circ, cy + r_circ, outline="#475569", width=1.5)
        cv.create_line(cx_phasor - r_circ - 10, cy, cx_phasor + r_circ + 10, cy, fill="#374151", width=1)
        cv.create_line(cx_phasor, cy - r_circ - 10, cx_phasor, cy + r_circ + 10, fill="#374151", width=1)

        # Phasor arrows
        cv.create_line(cx_phasor, cy, cx_phasor + r_circ, cy, fill="#38BDF8", width=3, arrow="last", arrowshape=(6, 8, 3))
        cv.create_text(cx_phasor + r_circ // 2, cy - 12, text="E1", fill="#38BDF8", font=("Segoe UI", 10, "bold"))

        LocalizationService.render_canvas_persian(
            cv, cx_phasor, cy + r_circ + 20, "نمودار فازورها (هم‌فاز Δφ = 0)" if is_fa else "Phasor Diagram (Δφ = 0)",
            font=("Segoe UI", 9, "bold"), fill="#94A3B8"
        )

    # ---- 5. Live Matplotlib Fringe Plot ----
    def _build_fringe_plot(self, is_fa: bool):
        fig_h = 3.6 if self.is_presentation_mode else 2.8
        self._mpl_fig = Figure(figsize=(6.8, fig_h), dpi=100, facecolor=_CARD)
        self._mpl_fig.subplots_adjust(bottom=0.24, top=0.92, left=0.10, right=0.96)
        ax = self._mpl_fig.add_subplot(111, facecolor=_BG)
        ax.set_ylim(-0.06, 1.24)
        ax.grid(True, linestyle="--", alpha=0.3, color="#475569")
        ax.tick_params(colors="#94A3B8", labelsize=8)
        for spine in ax.spines.values():
            spine.set_color("#334155")

        y = np.linspace(-8, 8, 400)
        self._mpl_line, = ax.plot(y, np.zeros_like(y), color=_ACCENT, lw=2.4)
        ax.set_xlabel(LocalizationService.get("plot_1d_xlabel"), color="#94A3B8", fontsize=9)
        ax.set_ylabel(LocalizationService.get("plot_1d_ylabel"), color="#94A3B8", fontsize=9)

        self._refresh_fringe_data()
        self._mpl_canvas = FigureCanvasTkAgg(self._mpl_fig, master=self.fig_holder)
        tk_w = self._mpl_canvas.get_tk_widget()
        tk_w.configure(cursor="hand2")
        tk_w.bind("<Button-1>", lambda _e: self._open_enlarged_figure())
        tk_w.grid(row=0, column=0, columnspan=2, sticky="ew", pady=6)

    def _refresh_fringe_data(self):
        if self._mpl_line is None or self._mpl_fig is None:
            return
        try:
            from physics.classical_engine import ClassicalEngine
            eng = ClassicalEngine()
            eng.update_params(
                wavelength_m=self._optical.wavelength_m,
                slit_distance_d_m=self._optical.slit_distance_d_m,
                slit_width_a_m=self._optical.slit_width_a_m,
                screen_distance_L_m=self._optical.screen_distance_L_m,
                refractive_index_n=self._optical.refractive_index_n,
            )
            feats = eng.get_analytical_features()
            dy = feats.get("fringe_spacing_dy_m", 1e-3)
            span = max(dy * 8.0, 1e-9)  # no mm floor: keep ~8 fringes even for extreme classical configs
            y = np.linspace(-span / 2, span / 2, 400)
            inten = eng.compute_intensity_profile(y)
            self._mpl_line.set_data(y * 1000.0, inten)
            wl = self._optical.wavelength_m * 1e9
            self._mpl_line.set_color(ColorUtils.wavelength_to_hex(wl))
            ax = self._mpl_fig.axes[0]
            ax.set_xlim(-span * 500.0, span * 500.0)
            self._mpl_fig.canvas.draw_idle()
        except Exception:
            pass

    # ---- 6. Quantum Particle Buildup with Trail Glow ----
    def _build_buildup_canvas(self, is_fa: bool):
        cv = self._new_canvas(300)
        self._buildup_dots = []
        self._buildup_job_active = True
        self._tick_buildup()

    def _toggle_buildup_observer(self):
        self._buildup_observer_active = not self._buildup_observer_active
        self._update_buildup_btn_text()
        self._buildup_dots = []

    def _update_buildup_btn_text(self):
        is_fa = LocalizationService.is_persian()
        if self._buildup_observer_active:
            txt = "ناظر روشن (ذره‌ای)" if is_fa else "Observer ON (Clumps)"
            col = "#EF4444"
        else:
            txt = "ناظر خاموش (تداخلی)" if is_fa else "Observer OFF (Fringes)"
            col = "#10B981"
        self.fig_ctrl_btn.configure(text=txt, fg_color=col, hover_color=col)

    def _tick_buildup(self):
        target_cv = self._modal_canvas if (self._modal_canvas and self._modal_canvas.winfo_exists()) else self._canvas
        if not self._buildup_job_active or target_cv is None or not target_cv.winfo_exists():
            return
        rng = np.random.default_rng()
        w = target_cv.winfo_width() or self._get_canvas_width(target_cv)
        h = target_cv.winfo_height() or 300

        # Sample particles
        for _ in range(12):
            x_frac = rng.random()
            if not self._buildup_observer_active:
                # Coherent interference cos^2 pattern
                prob = (math.cos((x_frac - 0.5) * math.pi * 7.5) ** 2) * math.exp(-((x_frac - 0.5) ** 2) / 0.07)
            else:
                # Classical incoherent two-slit clumps
                prob = 0.5 * (math.exp(-((x_frac - 0.42) ** 2) / 0.015) + math.exp(-((x_frac - 0.58) ** 2) / 0.015))

            if rng.random() < prob:
                py_offset = float(rng.normal(0, 45))
                self._buildup_dots.append({"xf": x_frac, "dy": py_offset, "age": 0})
                if len(self._buildup_dots) > 1000:
                    self._buildup_dots.pop(0)

        # Increment age for glow decay
        for d in self._buildup_dots:
            if d["age"] < 10:
                d["age"] += 1

        try:
            self._draw_buildup(target_cv, w, LocalizationService.is_persian())
        except Exception:
            pass

        if self._buildup_job_active:
            self._anim_job = self.after(70, self._tick_buildup)

    def _draw_buildup(self, cv: tk.Canvas, w: int, is_fa: bool):
        cv.delete("all")
        h = cv.winfo_height() or 300
        cy = h // 2
        cv.create_rectangle(0, 0, w, h, fill="#0F172A", outline="")

        for d in self._buildup_dots:
            x = int(d.get("xf", 0.5) * (w - 80) + 40)
            y = max(20, min(h - 20, int(cy + d.get("dy", 0.0))))
            age = d["age"]
            if age < 3:
                # Hot white core with neon cyan aura
                cv.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#22D3EE", outline="")
                cv.create_oval(x - 1, y - 1, x + 1, y + 1, fill="#FFFFFF", outline="")
            else:
                cv.create_oval(x - 1, y - 1, x + 1, y + 1, fill="#00E676" if not self._buildup_observer_active else "#F59E0B", outline="")

        vis = "0.00" if self._buildup_observer_active else "0.98"
        status = "ناظر فعال (فروپاشی تابع موج)" if self._buildup_observer_active else "برهم‌نهی کوانتومی همدوس" if is_fa else \
                 "Which-Way Observer (Decoherence)" if self._buildup_observer_active else "Coherent Quantum Superposition"

        cv.create_text(w - 110, 16, text=f"N = {len(self._buildup_dots)} | V = {vis}",
                       fill="#94A3B8", font=("Consolas", 10, "bold"))
        LocalizationService.render_canvas_persian(
            cv, 24, 16, status,
            font=("Segoe UI", 9, "bold"),
            fill="#EF4444" if self._buildup_observer_active else "#10B981",
            anchor="w"
        )

    # ---- Fullscreen / Enlarged Figure Modal ----
    def _open_enlarged_figure(self):
        """Opens the active slide's visualizer or photo in a large modal window."""
        if getattr(self, "_modal_window", None) is not None:
            try:
                self._modal_window.focus()
                return
            except Exception:
                self._modal_window = None

        slide = SLIDES[self.slide_index] if self.slide_index < len(SLIDES) else None
        if slide is None:
            return
        fig = slide.get("figure", {})
        kind = fig.get("kind", "none")
        if kind == "none":
            return

        is_fa = LocalizationService.is_persian()
        title = slide.get("title_fa" if is_fa else "title_en", "")
        cap = fig.get("caption_fa" if is_fa else "caption_en", "")

        modal = ctk.CTkToplevel(self)
        modal.title(f"{LocalizationService.get('fig_enlarged_title')} — {title}")
        modal.configure(fg_color="#0A0E1A")

        sw = modal.winfo_screenwidth()
        sh = modal.winfo_screenheight()
        mw = max(800, min(1400, int(sw * 0.88)))
        mh = max(560, min(900, int(sh * 0.86)))
        mx = (sw - mw) // 2
        my = max(20, (sh - mh) // 2 - 20)
        modal.geometry(f"{mw}x{mh}+{mx}+{my}")
        modal.minsize(720, 500)

        header = ctk.CTkFrame(modal, fg_color="#111827", height=44, corner_radius=0)
        header.pack(fill="x", side="top")

        close_btn = ctk.CTkButton(
            header, text=LocalizationService.get("fig_close"),
            width=96, height=28,
            fg_color="#EF4444", hover_color="#DC2626",
            font=FontManager.get_persian_font(10, "bold") if is_fa else FontManager.get_number_font(10, "bold"),
            command=self._close_enlarged_figure
        )
        close_btn.pack(side="right" if not is_fa else "left", padx=12, pady=8)

        if kind == "buildup":
            def _modal_toggle_observer():
                self._toggle_buildup_observer()
                self._update_buildup_btn_text()
                status_txt = LocalizationService.get("hist_obs_active") if self._buildup_observer_active else LocalizationService.get("hist_obs_off")
                obs_btn.configure(text=f"👁 {status_txt}")

            status_txt = LocalizationService.get("hist_obs_active") if self._buildup_observer_active else LocalizationService.get("hist_obs_off")
            obs_btn = ctk.CTkButton(
                header, text=f"👁 {status_txt}",
                width=160, height=28,
                fg_color="#1E3A8A", hover_color="#2563EB",
                font=FontManager.get_persian_font(9, "bold") if is_fa else FontManager.get_number_font(9, "bold"),
                command=_modal_toggle_observer
            )
            obs_btn.pack(side="right" if not is_fa else "left", padx=6, pady=8)

        title_lbl = ctk.CTkLabel(
            header, text=title,
            font=FontManager.get_persian_font(12, "bold") if is_fa else FontManager.get_number_font(12, "bold"),
            text_color="#38BDF8"
        )
        title_lbl.pack(side="left" if not is_fa else "right", padx=16, pady=8)

        content_frame = ctk.CTkFrame(modal, fg_color="#060911")
        content_frame.pack(fill="both", expand=True, padx=12, pady=(8, 4))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        if cap:
            cap_lbl = ctk.CTkLabel(
                modal, text=cap,
                font=FontManager.get_persian_font(10) if is_fa else FontManager.get_number_font(10),
                text_color=_MUTED, wraplength=mw - 40, justify="center"
            )
            cap_lbl.pack(side="bottom", pady=(2, 8))

        self._modal_window = modal
        self._modal_canvas = None

        if kind == "photo":
            files = fig.get("files") or ([fig.get("file")] if fig.get("file") else [])
            resolved = [(fn, p) for fn in files if (p := self._photo_path(fn)) is not None]
            if resolved:
                cols = 1 if len(resolved) == 1 else 2
                max_w_per = (mw - 60) // cols
                max_h_per = mh - 130
                photo_holder = ctk.CTkScrollableFrame(content_frame, fg_color="transparent")
                photo_holder.pack(fill="both", expand=True)
                for c in range(cols):
                    photo_holder.grid_columnconfigure(c, weight=1)
                for i, (_fn, p) in enumerate(resolved):
                    with Image.open(p) as im:
                        im = im.convert("RGB")
                        scale = min(max_w_per / im.width, max_h_per / im.height)
                        pw = max(1, int(im.width * scale))
                        ph = max(1, int(im.height * scale))
                        im = im.resize((pw, ph), Image.LANCZOS)
                        p_photo = ctk.CTkImage(light_image=im.copy(), dark_image=im.copy(), size=(pw, ph))
                        self._photo_refs.append(p_photo)
                    lbl = ctk.CTkLabel(photo_holder, text="", image=p_photo)
                    lbl.grid(row=i // cols, column=i % cols, padx=8, pady=8)
        elif kind in ("fringe", "worked_bench", "envelope", "interactive_fringe"):
            modal_fig = Figure(figsize=(9.2, 5.0), dpi=115, facecolor=_CARD)
            modal_ax = modal_fig.add_subplot(111, facecolor=_BG)
            modal_ax.set_ylim(-0.06, 1.24)
            modal_ax.grid(True, linestyle="--", alpha=0.3, color="#475569")
            modal_ax.tick_params(colors="#94A3B8", labelsize=9)
            for spine in modal_ax.spines.values():
                spine.set_color("#334155")
            modal_ax.set_xlabel(LocalizationService.get("plot_1d_xlabel"), color="#94A3B8", fontsize=10)
            modal_ax.set_ylabel(LocalizationService.get("plot_1d_ylabel"), color="#94A3B8", fontsize=10)
            modal_fig.subplots_adjust(bottom=0.18, top=0.92, left=0.10, right=0.96)
            if self._mpl_line is not None:
                x_d, y_d = self._mpl_line.get_data()
                modal_ax.plot(x_d, y_d, color=self._mpl_line.get_color(), lw=2.8)
                if self._mpl_fig and self._mpl_fig.axes:
                    modal_ax.set_xlim(self._mpl_fig.axes[0].get_xlim())
            m_canvas = FigureCanvasTkAgg(modal_fig, master=content_frame)
            m_canvas.get_tk_widget().pack(fill="both", expand=True)
            m_canvas.draw()
        else:
            m_cv = tk.Canvas(content_frame, bg=_BG, highlightthickness=0)
            m_cv.pack(fill="both", expand=True)
            self._modal_canvas = m_cv

            def _draw_m():
                if not m_cv.winfo_exists():
                    return
                cw = m_cv.winfo_width()
                if cw < 50:
                    cw = mw - 40
                if kind in ("apparatus", "duel"):
                    self._draw_apparatus(m_cv, cw, is_fa)
                elif kind == "huygens":
                    self._draw_huygens(m_cv, cw, animated=True, is_fa=is_fa)
                elif kind == "triangle":
                    self._draw_triangle(m_cv, cw, is_fa)
                elif kind == "interference":
                    self._draw_interference(m_cv, cw, is_fa)
                elif kind == "buildup":
                    self._draw_buildup(m_cv, cw, is_fa)

            m_cv.after_idle(_draw_m)
            m_cv.bind("<Configure>", lambda _e: _draw_m())

        modal.bind("<Escape>", lambda _e: self._close_enlarged_figure())
        modal.protocol("WM_DELETE_WINDOW", self._close_enlarged_figure)

    def _close_enlarged_figure(self):
        """Closes the enlarged modal window and restores primary canvas drawing."""
        self._modal_canvas = None
        if getattr(self, "_modal_window", None) is not None:
            try:
                self._modal_window.destroy()
            except Exception:
                pass
            self._modal_window = None
        if self._canvas is not None and self._canvas.winfo_exists():
            self._redraw_canvas()

    # ---- 7. Historical Photo Loader ----
    def _photo_path(self, fname: str) -> Optional[str]:
        path = os.path.join(_IMG_DIR, fname)
        return path if os.path.exists(path) else None

    def _build_photo(self, fig: Dict[str, Any], is_fa: bool):
        from customtkinter import CTkImage
        files = fig.get("files") or ([fig.get("file")] if fig.get("file") else [])
        resolved = [(fname, p) for fname in files if (p := self._photo_path(fname)) is not None]
        if not resolved:
            ph = ctk.CTkLabel(
                self.fig_holder, text=LocalizationService.get("hist_photo_na"),
                font=FontManager.get_persian_font(12, "bold") if is_fa else FontManager.get_number_font(12, "bold"),
                text_color=_MUTED, fg_color="#1E293B", corner_radius=8,
                width=560, height=220,
            )
            ph.grid(row=0, column=0, pady=8)
            self.caption_label.configure(text="")
            return
        try:
            n = len(resolved)
            cols = 1 if n == 1 else 2
            base_max_w = 720 if self.is_presentation_mode else 560
            max_h = (440 if self.is_presentation_mode else 320) if n == 1 else (
                260 if self.is_presentation_mode else 200)
            per_img_max_w = base_max_w if n == 1 else int(base_max_w / cols)
            for c in range(cols):
                self.fig_holder.grid_columnconfigure(c, weight=1)
            for i, (_fname, path) in enumerate(resolved):
                with Image.open(path) as im:
                    im = im.convert("RGB")
                    # Proportional aspect-ratio scaling (never squashes portrait photos)
                    scale = min(per_img_max_w / im.width, max_h / im.height)
                    w = max(1, int(im.width * scale))
                    h = max(1, int(im.height * scale))
                    im = im.resize((w, h), Image.LANCZOS)
                    photo = CTkImage(light_image=im.copy(), dark_image=im.copy(), size=(w, h))
                    self._photo_refs.append(photo)
                lbl = ctk.CTkLabel(self.fig_holder, text="", image=photo, cursor="hand2")
                lbl.bind("<Button-1>", lambda _e: self._open_enlarged_figure())
                lbl.grid(row=i // cols, column=i % cols, padx=4, pady=6, sticky="n")
            cap = fig.get("caption_fa", "") if is_fa else fig.get("caption_en", "")
            self.caption_label.configure(text=cap)
        except Exception:
            self.caption_label.configure(text=LocalizationService.get("hist_photo_na"))

    # ======================================================================
    # Quiz Engine (RTL-Aligned & Styled)
    # ======================================================================
    def _render_quiz_question(self, is_fa: bool):
        for child in self.quiz_btns_frame.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass
        self._quiz_buttons = []
        q = QUIZ[self.quiz_index]
        opts = q["opts_fa"] if is_fa else q["opts_en"]

        fa_digits = ["۱", "۲", "۳", "۴"]
        self.quiz_q_label.configure(text=(q["q_fa"] if is_fa else q["q_en"]))

        for i, opt in enumerate(opts):
            num_prefix = f"{fa_digits[i]}. " if is_fa else f"{i + 1}. "
            btn_text = f"{num_prefix}{opt}" if is_fa else f"{num_prefix}{opt}"
            btn = ctk.CTkButton(
                self.quiz_btns_frame,
                text=btn_text,
                height=38,
                anchor="e" if is_fa else "w",
                fg_color="#1E293B", hover_color="#334155",
                text_color=_INK,
                border_width=1, border_color="#334155",
                font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
                command=lambda c=i: self._answer_quiz(c)
            )
            btn.grid(row=i, column=0, pady=4, sticky="ew")
            self._quiz_buttons.append(btn)

        self.quiz_feedback.configure(text="")
        self.quiz_feedback_frame.grid_remove()
        self.quiz_retry_btn.configure(
            text=LocalizationService.get("hist_retry"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )

    def _answer_quiz(self, choice: int):
        if self.quiz_locked:
            return
        self.quiz_locked = True
        is_fa = LocalizationService.is_persian()
        q = QUIZ[self.quiz_index]
        ok = grade(q, choice)
        self.quiz_answered += 1
        if ok:
            self.quiz_score += 1

        for i, btn in enumerate(self._quiz_buttons):
            btn.configure(state="disabled")
            if i == q["correct"]:
                btn.configure(fg_color="#059669", text_color="#FFFFFF", border_color="#10B981")
            elif i == choice:
                btn.configure(fg_color="#DC2626", text_color="#FFFFFF", border_color="#EF4444")
            else:
                btn.configure(fg_color="#0F172A", text_color=_MUTED, border_color="#1E293B")

        explain = q["explain_fa"] if is_fa else q["explain_en"]
        head = LocalizationService.get("hist_correct" if ok else "hist_wrong")
        why = LocalizationService.get("hist_explanation")

        self.quiz_feedback_frame.configure(border_color="#10B981" if ok else "#EF4444")
        self.quiz_feedback_frame.grid()
        self.quiz_feedback.configure(
            text=f"{head}\n{why} {explain}",
            text_color="#10B981" if ok else "#F87171"
        )
        self._update_quiz_score_label()

    def _update_quiz_score_label(self):
        is_fa = LocalizationService.is_persian()
        label = LocalizationService.get("hist_score")
        self.quiz_score_label.configure(text=f"{label}: {self.quiz_score} / {self.quiz_answered}")

    def _reset_quiz(self):
        self.quiz_score = 0
        self.quiz_answered = 0
        self.show_slide(len(SLIDES))

    # ======================================================================
    # Navigation / Lifecycle / Language
    # ======================================================================
    def next_slide(self):
        self.show_slide(self.slide_index + 1)

    def prev_slide(self):
        self.show_slide(self.slide_index - 1)

    def _on_section_jump(self, chosen: str):
        for sec in SECTIONS:
            _key, fa_t, en_t = SECTION_TITLES[sec]
            if chosen in (fa_t, en_t):
                if sec == "quiz":
                    self.show_slide(len(SLIDES))
                else:
                    for i, s in enumerate(SLIDES):
                        if s["section"] == sec:
                            self.show_slide(i)
                            return
                return

    def on_show(self):
        self.show_slide(self.slide_index)

    def on_hide(self):
        self._stop_animation()

    def update_optical_params(self, optical_params: OpticalParameters, **_kwargs):
        self._optical = optical_params
        slide = SLIDES[self.slide_index] if self.slide_index < len(SLIDES) else None
        if slide is not None and slide.get("figure", {}).get("kind") == "fringe":
            self._refresh_fringe_data()

    def refresh_language(self):
        is_fa = LocalizationService.is_persian()
        names = [SECTION_TITLES[s][1] if is_fa else SECTION_TITLES[s][2] for s in SECTIONS]
        self.section_menu.configure(
            values=names,
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            dropdown_font=FontManager.get_persian_font(11) if is_fa else FontManager.get_number_font(11),
        )
        cur = SLIDES[self.slide_index]["section"] if self.slide_index < len(SLIDES) else "quiz"
        cur_name = SECTION_TITLES[cur][1] if is_fa else SECTION_TITLES[cur][2]
        try:
            self.section_menu.set(cur_name)
        except Exception:
            pass

        self.btn_presentation.configure(
            text=LocalizationService.get("presentation_mode"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )
        if hasattr(self, "btn_web_presentation"):
            self.btn_web_presentation.configure(
                text=LocalizationService.get("web_presentation_btn"),
                font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
            )
        self.live_badge.configure(
            font=FontManager.get_persian_font(10, "bold") if is_fa else FontManager.get_number_font(10, "bold")
        )
        self.caption_label.configure(
            font=FontManager.get_persian_font(10) if is_fa else FontManager.get_number_font(10)
        )
        if hasattr(self, "expand_btn"):
            self.expand_btn.configure(
                text=LocalizationService.get("fig_expand"),
                font=FontManager.get_persian_font(9, "bold") if is_fa else FontManager.get_number_font(9, "bold")
            )
        self.show_slide(self.slide_index)
