"""
Main Application Window and Simulation Coordinator.
Orchestrates CustomTkinter interface, physics engines, views, and real-time animation loop.
Supports 5 dedicated views: 2D Screen, 1D Profile, 2D Wave Propagation, 3D Laboratory Apparatus, and Calculations & Equations.
Full multi-format export pipeline: Context-Aware PNG/PDF, 22-column CSV, 3D OBJ model, and Word (.docx) with OMML equations.
Fully styled with Vazirmatn and Space Grotesk typography.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Dict, Any, Optional
import customtkinter as ctk
import numpy as np

from config import (
    APP_TITLE,
    APP_SUBTITLE,
    APPEARANCE_MODE,
    COLOR_THEME,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
    WINDOW_DEFAULT_GEOMETRY,
    ANIMATION_INTERVAL_MS,
    DEFAULT_WAVELENGTH_NM,
    DEFAULT_SLIT_DISTANCE_MM,
    DEFAULT_SLIT_WIDTH_MM,
    DEFAULT_SCREEN_DISTANCE_M,
    DEFAULT_REFRACTIVE_INDEX
)
from physics.classical_engine import OpticalParameters, ClassicalEngine
from physics.quantum_engine import QuantumEngine
from physics.particle_types import ParticleCategory
from utils.color_utils import ColorUtils
from utils.stats_calculator import StatsCalculator
from utils.export_service import ExportService
from utils.localization import LocalizationService, RLM
from utils.font_manager import FontManager

from ui.components.control_panel import ControlPanel
from ui.components.quantum_panel import QuantumPanel
from ui.components.metrics_panel import MetricsPanel

from ui.views.screen_2d_view import Screen2DView
from ui.views.profile_1d_view import Profile1DView
from ui.views.setup_schematic_view import SetupSchematicView
from ui.views.setup_3d_view import Setup3DView
from ui.views.calculations_view import CalculationsView
from ui.views.history_view import HistoryView
from ui.views.guide_view import SoftwareGuideView

import webbrowser

GITHUB_REPO_URL = "https://github.com/AmirMoYousefVand/Double-slit-experiment-Simulator"


class MainWindow(ctk.CTk):
    """
    Main application root window hosting classical and quantum double-slit simulations.
    """

    def _set_window_icon(self):
        """Applies the application logo to the title bar, taskbar and Alt-Tab list."""
        logo_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "Logo"
        )
        ico_path = os.path.join(logo_dir, "favicon.ico")
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception as e:
                print(f"Warning: window icon (.ico) load failed: {e}")

        png_path = os.path.join(logo_dir, "icon.png")
        if os.path.exists(png_path):
            try:
                self.iconphoto(True, tk.PhotoImage(file=png_path))
            except Exception as e:
                print(f"Warning: window icon (.png) load failed: {e}")

    def __init__(self):
        super().__init__()

        # Initialize Typography & System Fonts
        FontManager.initialize()

        # Appearance configuration
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)

        self.title(LocalizationService.get("app_title"))
        self.geometry(WINDOW_DEFAULT_GEOMETRY)
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self._set_window_icon()

        # Simulation Mode: "classical" or "quantum"
        self.mode = "classical"
        self.is_quantum_running = False
        self.emission_rate = 200

        # Fullscreen & Theater mode states
        self._is_window_fullscreen: bool = False
        self._is_theater_mode: bool = False

        # Physical Engines Initialization
        self.optical_params = OpticalParameters(
            wavelength_m=DEFAULT_WAVELENGTH_NM * 1e-9,
            slit_distance_d_m=DEFAULT_SLIT_DISTANCE_MM * 1e-3,
            slit_width_a_m=DEFAULT_SLIT_WIDTH_MM * 1e-3,
            screen_distance_L_m=DEFAULT_SCREEN_DISTANCE_M,
            refractive_index_n=DEFAULT_REFRACTIVE_INDEX
        )
        self.classical_engine = ClassicalEngine(self.optical_params)
        self.quantum_engine = QuantumEngine(
            particle_category=ParticleCategory.ELECTRON,
            optical_params=self.optical_params
        )
        # QuantumEngine.__init__ overwrote the shared wavelength with the
        # matter-wave value; restore the classical default before first render.
        self.optical_params.wavelength_m = DEFAULT_WAVELENGTH_NM * 1e-9

        # Screen spatial coordinates grid
        self.y_grid_points = 1200
        self.screen_span_y_m = 0.04  # +/- 20 mm default
        self.screen_span_z_m = 0.02
        self.y_grid_m = np.linspace(-self.screen_span_y_m / 2.0, self.screen_span_y_m / 2.0, self.y_grid_points)

        # Build UI layout
        self._build_layout()

        # Initial calculation & rendering across all views
        self._recalculate_classical_field()

        # Start animation ticker
        self._schedule_animation_tick()

        # Keyboard shortcuts for Fullscreen, Theater, Presentation, and Web
        self.bind("<F11>", lambda _e: self._toggle_window_fullscreen())
        self.bind("<F10>", lambda _e: self._toggle_theater_mode())
        self.bind("<Escape>", lambda _e: self._handle_escape_key())
        self.bind("<F5>", lambda _e: self._handle_presentation_shortcut())
        self.bind("<F9>", lambda _e: self._open_web_presentation())

    def _build_layout(self):
        """Builds top bar, left sidebar controls, right views tabview, and metrics panel."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        is_fa = LocalizationService.is_persian()

        # ======================================================================
        # 1. Top Navigation & Header Bar
        # ======================================================================
        self.top_bar = ctk.CTkFrame(self, height=52, corner_radius=0, fg_color="#18181B")
        self.top_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.top_bar.grid_columnconfigure(1, weight=1)

        # App Title & Subtitle
        title_box = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        title_box.grid(row=0, column=0, padx=16, pady=6, sticky="w")

        self.main_title_label = ctk.CTkLabel(
            title_box,
            text=LocalizationService.get("app_title"),
            font=FontManager.get_persian_font(15, "bold") if is_fa else FontManager.get_number_font(15, "bold")
        )
        self.main_title_label.pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            title_box,
            text=LocalizationService.get("app_subtitle"),
            font=FontManager.get_persian_font(10) if is_fa else FontManager.get_number_font(10),
            text_color="#9CA3AF"
        )
        self.subtitle_label.pack(anchor="w")

        # Mode Selector (Classical vs Quantum)
        mode_box = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        mode_box.grid(row=0, column=1, padx=20, pady=8)

        self.mode_selector = ctk.CTkSegmentedButton(
            mode_box,
            values=[
                LocalizationService.get("mode_classical"),
                LocalizationService.get("mode_quantum")
            ],
            command=self._handle_mode_change,
            height=32,
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )
        self.mode_selector.set(LocalizationService.get("mode_classical"))
        self.mode_selector.pack()

        # Actions (Language switch, Theme, Fullscreen, Theater, Web Deck)
        actions_box = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        actions_box.grid(row=0, column=2, padx=16, pady=8, sticky="e")

        self.btn_web = ctk.CTkButton(
            actions_box,
            text=LocalizationService.get("web_presentation_short"),
            command=self._open_web_presentation,
            width=100,
            height=28,
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            fg_color="#1E3A8A",
            hover_color="#2563EB",
            border_width=1,
            border_color="#38BDF8"
        )
        self.btn_web.pack(side="right", padx=3)

        self.btn_fullscreen = ctk.CTkButton(
            actions_box,
            text=LocalizationService.get("fullscreen_toggle"),
            command=self._toggle_window_fullscreen,
            width=90,
            height=28,
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            border_width=1,
            border_color="#3B82F6"
        )
        self.btn_fullscreen.pack(side="right", padx=3)

        self.btn_theater = ctk.CTkButton(
            actions_box,
            text=LocalizationService.get("theater_toggle"),
            command=self._toggle_theater_mode,
            width=85,
            height=28,
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            border_width=1,
            border_color="#10B981"
        )
        self.btn_theater.pack(side="right", padx=3)

        self.btn_lang = ctk.CTkButton(
            actions_box,
            text=LocalizationService.get("lang_switch"),
            command=self._toggle_language,
            width=90,
            height=28,
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            fg_color="#374151",
            hover_color="#4B5563"
        )
        self.btn_lang.pack(side="right", padx=3)

        self.btn_theme = ctk.CTkButton(
            actions_box,
            text=LocalizationService.get("theme_toggle"),
            command=self._toggle_theme,
            width=70,
            height=28,
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            fg_color="#374151",
            hover_color="#4B5563"
        )
        self.btn_theme.pack(side="right", padx=2)

        # ======================================================================
        # 2. Left Control Panels
        # ======================================================================
        self.left_frame = ctk.CTkFrame(self, width=350, corner_radius=0, fg_color="#121214")
        self.left_frame.grid(row=1, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        # Control Panel for Optics Parameters
        self.control_panel = ControlPanel(
            self.left_frame,
            on_param_change=self._on_optical_param_change,
            on_preset_selected=self._on_preset_selected,
            on_reset_defaults=self._on_reset_defaults,
            width=335
        )
        self.control_panel.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        # Quantum Panel (Created and placed in quantum mode)
        self.quantum_panel = QuantumPanel(
            self.left_frame,
            on_particle_change=self._on_particle_change,
            on_energy_change=self._on_energy_change,
            on_rate_change=self._on_rate_change,
            on_which_way_toggle=self._on_which_way_toggle,
            on_play=self._on_quantum_play,
            on_pause=self._on_quantum_pause,
            on_step=self._on_quantum_step,
            on_reset=self._on_quantum_reset,
            width=335
        )

        # ======================================================================
        # 3. Right Views (5-Tab Tabview) & Bottom Metrics Panel
        # ======================================================================
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=1, column=1, sticky="nsew", padx=8, pady=(4, 6))
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=1)

        # Tabview for Multi-Views (command runs AFTER the internal tab-switch,
        # so button clicks keep working — never override _segmented_button command)
        self.tabview = ctk.CTkTabview(self.right_frame, command=self._on_tab_changed)
        self.tabview.grid(row=0, column=0, sticky="nsew")

        self.tab_2d = self.tabview.add("tab_2d")
        self.tab_1d = self.tabview.add("tab_1d")
        self.tab_sch = self.tabview.add("tab_sch")
        self.tab_3d = self.tabview.add("tab_3d")
        self.tab_calc = self.tabview.add("tab_calc")
        self.tab_hist = self.tabview.add("tab_hist")
        self.tab_guide = self.tabview.add("tab_guide")
        self._update_tabview_titles()

        # Populate Tab 1: 2D Screen View
        self.tab_2d.grid_columnconfigure(0, weight=1)
        self.tab_2d.grid_rowconfigure(0, weight=1)
        self.screen_2d_view = Screen2DView(self.tab_2d)
        self.screen_2d_view.grid(row=0, column=0, sticky="nsew")

        # Populate Tab 2: 1D Profile View
        self.tab_1d.grid_columnconfigure(0, weight=1)
        self.tab_1d.grid_rowconfigure(0, weight=1)
        self.profile_1d_view = Profile1DView(self.tab_1d)
        self.profile_1d_view.grid(row=0, column=0, sticky="nsew")

        # Populate Tab 3: Setup Schematic View (2D Wave Propagation)
        self.tab_sch.grid_columnconfigure(0, weight=1)
        self.tab_sch.grid_rowconfigure(0, weight=1)
        self.setup_schematic_view = SetupSchematicView(self.tab_sch)
        self.setup_schematic_view.grid(row=0, column=0, sticky="nsew")

        # Populate Tab 4: 3D Laboratory Apparatus View
        self.tab_3d.grid_columnconfigure(0, weight=1)
        self.tab_3d.grid_rowconfigure(0, weight=1)
        self.setup_3d_view = Setup3DView(self.tab_3d)
        self.setup_3d_view.grid(row=0, column=0, sticky="nsew")

        # Populate Tab 5: Calculations & Equations View (with Word & PNG export callbacks)
        self.tab_calc.grid_columnconfigure(0, weight=1)
        self.tab_calc.grid_rowconfigure(0, weight=1)
        self.calculations_view = CalculationsView(
            self.tab_calc,
            on_export_docx=self._on_export_calculations_docx,
            on_export_png=self._on_export_calculations_png
        )
        self.calculations_view.grid(row=0, column=0, sticky="nsew")

        # Populate Tab 6: History & Classroom Tutorial View
        self.tab_hist.grid_columnconfigure(0, weight=1)
        self.tab_hist.grid_rowconfigure(0, weight=1)
        self.history_view = HistoryView(self.tab_hist, on_toggle_theater=self._toggle_theater_mode)
        self.history_view.grid(row=0, column=0, sticky="nsew")

        # Populate Tab 7: Software Guide Walkthrough View
        self.tab_guide.grid_columnconfigure(0, weight=1)
        self.tab_guide.grid_rowconfigure(0, weight=1)
        self.guide_view = SoftwareGuideView(self.tab_guide, on_toggle_theater=self._toggle_theater_mode)
        self.guide_view.grid(row=0, column=0, sticky="nsew")

        # Bottom Metrics Panel with CSV, Plot, 3D OBJ, and ZIP export buttons
        self.metrics_panel = MetricsPanel(
            self.right_frame,
            on_export_csv=self._on_export_csv,
            on_export_plot=self._on_export_plot,
            on_export_obj=self._on_export_3d_model,
            on_export_zip=self._on_export_all_in_one_zip
        )
        self.metrics_panel.grid(row=1, column=0, sticky="ew", pady=(6, 0))

        # ======================================================================
        # Footer Bar — Copyright Credit + GitHub Repo Link
        # ======================================================================
        self.footer_bar = ctk.CTkFrame(self, height=22, corner_radius=0, fg_color="#18181B")
        self.footer_bar.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.footer_inner = ctk.CTkFrame(self.footer_bar, fg_color="transparent")
        self.footer_inner.pack(pady=3)

        # Clickable GitHub mark (text fallback if the asset is missing)
        self._github_image = None
        gh_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "Logo", "github-mark.png"
        )
        if os.path.exists(gh_path):
            try:
                from PIL import Image
                with Image.open(gh_path) as im:
                    im = im.convert("RGBA").resize((16, 16), Image.LANCZOS)
                    self._github_image = ctk.CTkImage(
                        light_image=im.copy(), dark_image=im.copy(), size=(16, 16)
                    )
            except Exception as e:
                print(f"Warning: GitHub icon load failed: {e}")

        self.btn_github = ctk.CTkButton(
            self.footer_inner,
            text="" if self._github_image is not None else LocalizationService.get("github_link"),
            image=self._github_image,
            width=26 if self._github_image is not None else 70,
            height=16,
            corner_radius=4,
            fg_color="transparent",
            hover_color="#334155",
            font=FontManager.get_number_font(9, "bold"),
            text_color="#9CA3AF",
            command=self._open_github_repo
        )

        self.copyright_label = ctk.CTkLabel(
            self.footer_inner,
            text=LocalizationService.get("copyright"),
            font=FontManager.get_persian_font(10) if is_fa else FontManager.get_number_font(10),
            text_color="#6B7280"
        )
        self._pack_footer_children(is_fa)

    def _pack_footer_children(self, is_fa: bool):
        """Lays out [icon][text] in English and flips to [text][icon] for RTL."""
        for widget in (self.btn_github, self.copyright_label):
            widget.pack_forget()
        if is_fa:
            self.copyright_label.pack(side="left")
            self.btn_github.pack(side="left", padx=(8, 0))
        else:
            self.btn_github.pack(side="left", padx=(0, 8))
            self.copyright_label.pack(side="left")

    def _open_github_repo(self):
        """Opens the project repository in the default web browser."""
        try:
            webbrowser.open_new_tab(GITHUB_REPO_URL)
        except Exception as e:
            print(f"Failed to open GitHub repository: {e}")

    # ==========================================================================
    # Optical & Physical Calculations Coordination
    # ==========================================================================
    def _adapt_screen_span(self):
        """Dynamically scales screen spatial span to ensure ~10-15 fringes are visible.

        No millimeter floor: matter-wave fringes (electron ~0.5 µm, C60 ~11 pm)
        would otherwise be clamped to a 5 mm span and alias into noise. With the
        span always 16×Δy, grid points per fringe stay constant (1200/16 = 75).
        """
        features = self.classical_engine.get_analytical_features()
        dy = features["fringe_spacing_dy_m"]
        if dy > 0:
            target_span = max(dy * 16.0, 1e-12)
            target_span = min(target_span, 0.20)
            self.screen_span_y_m = target_span
            self.y_grid_m = np.linspace(-self.screen_span_y_m / 2.0, self.screen_span_y_m / 2.0, self.y_grid_points)

    def _display_colors(self):
        """(rgb, hex) for the current mode — particle false-colour in quantum
        mode, since the shared matter-wave wavelength maps to UV/violet."""
        wl_nm = self.optical_params.wavelength_m * 1e9
        if self.mode == "quantum":
            cat = self.quantum_engine.particle.category
            return ColorUtils.get_particle_color(cat, wl_nm), ColorUtils.get_particle_hex(cat, wl_nm)
        return ColorUtils.wavelength_to_rgb(wl_nm), ColorUtils.wavelength_to_hex(wl_nm)

    def _recalculate_classical_field(self):
        """Computes analytical values and updates all 5 views."""
        self._adapt_screen_span()

        # Compute theoretical profiles
        intensity = self.classical_engine.compute_intensity_profile(self.y_grid_m)
        envelope = self.classical_engine.compute_diffraction_envelope(self.y_grid_m)
        features = self.classical_engine.get_analytical_features()

        base_rgb, curve_hex = self._display_colors()
        wl_nm = self.optical_params.wavelength_m * 1e9

        # 1. Update 1D Profile View
        self.profile_1d_view.update_theoretical_profile(
            y_grid_m=self.y_grid_m,
            intensity=intensity,
            envelope=envelope,
            curve_hex_color=curve_hex,
            analytical_features=features
        )

        # 2. Update 2D Screen View (if in classical mode)
        if self.mode == "classical":
            self.screen_2d_view.update_classical_screen(
                intensity_1d=intensity,
                base_rgb=base_rgb,
                span_y_m=self.screen_span_y_m
            )

        # 3. Update 2D Schematic View
        self.setup_schematic_view.update_optical_params(
            wavelength_nm=wl_nm,
            slit_distance_mm=self.optical_params.slit_distance_d_m * 1000.0,
            slit_width_mm=self.optical_params.slit_width_a_m * 1000.0,
            screen_distance_m=self.optical_params.screen_distance_L_m,
            which_way_active=self.quantum_engine.which_way_active if self.mode == "quantum" else False,
            particle_category=self.quantum_engine.particle.category if self.mode == "quantum" else ParticleCategory.PHOTON,
            is_quantum=(self.mode == "quantum")
        )

        # 4. Update 3D Apparatus View
        self.setup_3d_view.update_3d_scene(
            wavelength_nm=wl_nm,
            slit_distance_mm=self.optical_params.slit_distance_d_m * 1000.0,
            slit_width_mm=self.optical_params.slit_width_a_m * 1000.0,
            screen_distance_m=self.optical_params.screen_distance_L_m,
            which_way_active=self.quantum_engine.which_way_active if self.mode == "quantum" else False,
            intensity_1d=intensity,
            y_grid_m=self.y_grid_m,
            base_rgb=base_rgb,
            particle_category=self.quantum_engine.particle.category if self.mode == "quantum" else ParticleCategory.PHOTON,
            is_quantum=(self.mode == "quantum"),
            quantum_hits_y=self.quantum_engine.hits_y if self.mode == "quantum" else None,
            quantum_hits_z=self.quantum_engine.hits_z if self.mode == "quantum" else None
        )

        # 5. Update Calculations & Equations View
        self.calculations_view.update_calculations(
            optical_params=self.optical_params,
            quantum_engine=self.quantum_engine if self.mode == "quantum" else None,
            features=features,
            screen_span_y_m=self.screen_span_y_m
        )

        # 6. Feed live params into History tab demo slides (classical only —
        # quantum mode carries a matter-wave wavelength that would alias them)
        if self.mode == "classical" and hasattr(self, "history_view"):
            try:
                self.history_view.update_optical_params(optical_params=self.optical_params)
            except Exception:
                pass

        # Update Metrics Panel
        total_hits = self.quantum_engine.total_hits if self.mode == "quantum" else 0
        self.metrics_panel.update_metrics(features, total_hits=total_hits)

    def _on_tab_changed(self, _selected: str = ""):
        """Starts/stops history-tab animations and updates views when switching tabs."""
        try:
            active = self.tabview.get()
        except Exception:
            return
        tab_hist_title = LocalizationService.get("tab_history")
        tab_guide_title = LocalizationService.get("tab_guide")
        if hasattr(self, "history_view"):
            if active in ("tab_hist", tab_hist_title):
                self.history_view.on_show()
            else:
                self.history_view.on_hide()
        if hasattr(self, "guide_view"):
            if active in ("tab_guide", tab_guide_title):
                self.guide_view.show_module(self.guide_view.module_index)

    # ==========================================================================
    # Event Handlers & Control Callbacks
    # ==========================================================================
    def _handle_mode_change(self, selected_mode: str):
        """Switches between Classical Wave and Quantum Mechanics simulations."""
        from utils.numeric_input import clamp
        if selected_mode == LocalizationService.get("mode_classical"):
            self.mode = "classical"
            self.is_quantum_running = False
            # Restore the classical wavelength the panel slider still holds
            # (quantum mode overwrote the shared optical_params with matter λ)
            wl_nm = clamp("wavelength_nm", float(self.control_panel.get_parameter_value("wavelength_nm")))
            self.optical_params.wavelength_m = wl_nm * 1e-9
            if getattr(self, "_saved_refractive_index_n", None) is not None:
                self.optical_params.refractive_index_n = self._saved_refractive_index_n
                self.control_panel.set_parameter_value("refractive_index", self._saved_refractive_index_n)
                self._saved_refractive_index_n = None
            self.classical_engine.update_params(wavelength_m=self.optical_params.wavelength_m)
            self.quantum_engine.invalidate_cache()
            self.quantum_panel.set_paused_state()
            self.quantum_panel.grid_forget()
            self.control_panel.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
            self._recalculate_classical_field()
        else:
            self.mode = "quantum"
            # Matter waves: refractive index of a classical medium does not
            # apply; save the user's setting and restore it on exit.
            self._saved_refractive_index_n = self.optical_params.refractive_index_n
            self.optical_params.refractive_index_n = 1.0
            self.quantum_engine.update_wavelength()
            self.quantum_engine.reset_hits()
            self.classical_engine.update_params(
                wavelength_m=self.optical_params.wavelength_m,
                refractive_index_n=1.0
            )
            self.control_panel.grid_forget()
            self.quantum_panel.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
            self.screen_2d_view.clear_quantum_screen()
            self.profile_1d_view.clear_quantum_data()
            self._recalculate_classical_field()

    def _on_optical_param_change(self, key: str, value: float):
        """Handles slider/entry changes in the control panel (defensively clamped)."""
        from utils.numeric_input import clamp
        value = clamp(key, float(value))
        if key == "wavelength_nm":
            self.optical_params.wavelength_m = value * 1e-9
        elif key == "slit_distance_mm":
            self.optical_params.slit_distance_d_m = value * 1e-3
        elif key == "slit_width_mm":
            self.optical_params.slit_width_a_m = value * 1e-3
        elif key == "screen_distance_m":
            self.optical_params.screen_distance_L_m = value
        elif key == "refractive_index":
            self.optical_params.refractive_index_n = value

        self.classical_engine.update_params(
            wavelength_m=self.optical_params.wavelength_m,
            slit_distance_d_m=self.optical_params.slit_distance_d_m,
            slit_width_a_m=self.optical_params.slit_width_a_m,
            screen_distance_L_m=self.optical_params.screen_distance_L_m,
            refractive_index_n=self.optical_params.refractive_index_n
        )
        self.quantum_engine.invalidate_cache()
        self._recalculate_classical_field()

    def _on_preset_selected(self, preset_name: str):
        """Handles selecting a laboratory preset."""
        self._recalculate_classical_field()

    def _on_reset_defaults(self):
        """Resets all parameters to He-Ne red laser standard."""
        self.control_panel.set_parameter_value("wavelength_nm", DEFAULT_WAVELENGTH_NM)
        self.control_panel.set_parameter_value("slit_distance_mm", DEFAULT_SLIT_DISTANCE_MM)
        self.control_panel.set_parameter_value("slit_width_mm", DEFAULT_SLIT_WIDTH_MM)
        self.control_panel.set_parameter_value("screen_distance_m", DEFAULT_SCREEN_DISTANCE_M)
        self.control_panel.set_parameter_value("refractive_index", DEFAULT_REFRACTIVE_INDEX)

    # ==========================================================================
    # Quantum Callbacks
    # ==========================================================================
    def _on_particle_change(self, category: ParticleCategory):
        self.quantum_engine.set_particle(category)
        self._recalculate_classical_field()

    def _on_energy_change(self, energy_ev: float):
        if self.quantum_engine.particle.category == ParticleCategory.BUCKYBALL:
            self.quantum_engine.set_velocity(energy_ev)
        else:
            self.quantum_engine.set_energy(energy_ev)
        self._recalculate_classical_field()

    def _on_rate_change(self, rate: int):
        self.emission_rate = rate

    def _on_which_way_toggle(self, active: bool):
        self.quantum_engine.set_which_way_detector(active)
        self._recalculate_classical_field()

    def _on_quantum_play(self):
        self.is_quantum_running = True

    def _on_quantum_pause(self):
        self.is_quantum_running = False

    def _on_quantum_step(self):
        """Emits a single discrete burst of particles."""
        self._emit_particle_burst(burst_count=100)

    def _on_quantum_reset(self):
        self.quantum_engine.reset_hits()
        self.screen_2d_view.clear_quantum_screen()
        self.profile_1d_view.clear_quantum_data()
        self.metrics_panel.update_metrics(
            self.classical_engine.get_analytical_features(),
            total_hits=0
        )

    # ==========================================================================
    # Real-Time Monte Carlo Animation Loop
    # ==========================================================================
    def _schedule_animation_tick(self):
        """Maintains smooth ~60 FPS event loop without blocking Tkinter."""
        self._animation_tick()
        self.after(ANIMATION_INTERVAL_MS, self._schedule_animation_tick)

    def _animation_tick(self):
        if self.mode == "quantum" and self.is_quantum_running:
            particles_per_tick = max(1, int(self.emission_rate * (ANIMATION_INTERVAL_MS / 1000.0)))
            self._emit_particle_burst(burst_count=particles_per_tick)

    def _emit_particle_burst(self, burst_count: int):
        """Samples and renders a batch of quantum particle hits."""
        batch_y, batch_z = self.quantum_engine.sample_particles(
            count=burst_count,
            screen_span_y_m=self.screen_span_y_m,
            screen_span_z_m=self.screen_span_z_m
        )
        self.quantum_engine.accumulate_hits(batch_y, batch_z)

        # Render onto 2D screen
        cat = self.quantum_engine.particle.category
        wl_nm = self.optical_params.wavelength_m * 1e9
        base_rgb = ColorUtils.get_particle_color(cat, wl_nm)
        total_hits = self.quantum_engine.total_hits

        self.screen_2d_view.add_quantum_hits(
            batch_y=batch_y,
            batch_z=batch_z,
            base_rgb=base_rgb,
            span_y_m=self.screen_span_y_m,
            span_z_m=self.screen_span_z_m,
            total_hits=total_hits
        )

        # Update 1D Histogram
        particle_hex = ColorUtils.get_particle_hex(cat, wl_nm)
        self.profile_1d_view.update_quantum_histogram(
            hits_y=self.quantum_engine.hits_y,
            span_y_m=self.screen_span_y_m,
            particle_hex=particle_hex
        )

        # Periodically compute Chi-Square statistical convergence test
        chi2_res = None
        if total_hits > 100:
            hist_bins = self.profile_1d_view.bins_count
            half_span = self.screen_span_y_m / 2.0
            bins = np.linspace(-half_span, half_span, hist_bins + 1)
            obs_counts, _ = np.histogram(self.quantum_engine.hits_y, bins=bins)
            bin_centers = 0.5 * (bins[:-1] + bins[1:])
            theo_prob = self.quantum_engine.compute_probability_density(bin_centers) * (bins[1] - bins[0])
            chi2_res = StatsCalculator.compute_chi_square(obs_counts, theo_prob, total_hits)

        features = self.classical_engine.get_analytical_features()
        if self.quantum_engine.which_way_active:
            features["visibility"] = 0.0

        self.metrics_panel.update_metrics(features, total_hits=total_hits, chi2_dict=chi2_res)

    # ==========================================================================
    # Language & Appearance Toggles
    # ==========================================================================
    def _toggle_language(self):
        new_lang = LocalizationService.toggle_language()
        is_fa = new_lang == "fa"

        self.title(LocalizationService.get("app_title"))
        self.main_title_label.configure(
            text=LocalizationService.get("app_title"),
            font=FontManager.get_persian_font(15, "bold") if is_fa else FontManager.get_number_font(15, "bold")
        )
        self.subtitle_label.configure(
            text=LocalizationService.get("app_subtitle"),
            font=FontManager.get_persian_font(10) if is_fa else FontManager.get_number_font(10)
        )
        self.copyright_label.configure(
            text=LocalizationService.get("copyright"),
            font=FontManager.get_persian_font(10) if is_fa else FontManager.get_number_font(10)
        )
        if hasattr(self, "btn_github"):
            if self._github_image is None:
                self.btn_github.configure(
                    text=LocalizationService.get("github_link"),
                    font=FontManager.get_persian_font(9, "bold") if is_fa else FontManager.get_number_font(9, "bold")
                )
            self._pack_footer_children(is_fa)

        self.btn_lang.configure(
            text=LocalizationService.get("lang_switch"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )
        self.btn_theme.configure(
            text=LocalizationService.get("theme_toggle"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )

        # Update fullscreen, theater & web button texts
        if hasattr(self, "btn_web"):
            self.btn_web.configure(
                text=LocalizationService.get("web_presentation_short"),
                font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
            )
        fs_key = "windowed_toggle" if self._is_window_fullscreen else "fullscreen_toggle"
        self.btn_fullscreen.configure(
            text=LocalizationService.get(fs_key),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )
        th_key = "restore_panels" if self._is_theater_mode else "theater_toggle"
        self.btn_theater.configure(
            text=LocalizationService.get(th_key),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )

        # Re-set mode selector labels
        self.mode_selector.configure(
            values=[
                LocalizationService.get("mode_classical"),
                LocalizationService.get("mode_quantum")
            ],
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )
        current_mode_text = LocalizationService.get("mode_classical") if self.mode == "classical" else LocalizationService.get("mode_quantum")
        self.mode_selector.set(current_mode_text)

        # Update tabview tab titles and fonts
        self._update_tabview_titles()

        # Notify all sub-panels
        self.control_panel.refresh_language()
        self.quantum_panel.refresh_language()
        self.metrics_panel.refresh_language()
        self.profile_1d_view.refresh_language()
        self.screen_2d_view.refresh_language()
        self.setup_schematic_view.refresh_language()
        self.setup_3d_view.refresh_language()
        self.calculations_view.refresh_language()
        if hasattr(self, "history_view"):
            self.history_view.refresh_language()
        if hasattr(self, "guide_view"):
            self.guide_view.refresh_language()

    def _update_tabview_titles(self):
        """Updates tabview segmented button labels for the active language."""
        is_fa = LocalizationService.is_persian()
        self.tabview._segmented_button.configure(
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )
        tab_map = [
            ("tab_2d", "tab_2d_screen"),
            ("tab_1d", "tab_1d_profile"),
            ("tab_sch", "tab_schematic"),
            ("tab_3d", "tab_3d_setup"),
            ("tab_calc", "tab_calculations"),
            ("tab_hist", "tab_history"),
            ("tab_guide", "tab_guide"),
        ]
        for tab_id, loc_key in tab_map:
            btn_text = LocalizationService.get(loc_key)
            btn = self.tabview._segmented_button._buttons_dict.get(tab_id)
            if btn is not None:
                btn.configure(
                    text=btn_text,
                    font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
                )

    def _toggle_theme(self):
        curr = ctk.get_appearance_mode()
        new_theme = "Light" if curr == "Dark" else "Dark"
        ctk.set_appearance_mode(new_theme)

    # ==========================================================================
    # Fullscreen, Theater, & Presentation Mode Controls
    # ==========================================================================
    def _toggle_window_fullscreen(self):
        """Toggles borderless full-window fullscreen mode (F11)."""
        self._is_window_fullscreen = not self._is_window_fullscreen
        self.attributes("-fullscreen", self._is_window_fullscreen)
        fs_key = "windowed_toggle" if self._is_window_fullscreen else "fullscreen_toggle"
        self.btn_fullscreen.configure(text=LocalizationService.get(fs_key))

    def _toggle_theater_mode(self, force_theater: Optional[bool] = None):
        """
        Toggles View-Level Theater Mode (F10).
        Collapses left controls and bottom metrics panel so active view occupies 100% space.
        """
        if force_theater is not None:
            self._is_theater_mode = force_theater
        else:
            self._is_theater_mode = not self._is_theater_mode

        if self._is_theater_mode:
            self.left_frame.grid_remove()
            self.metrics_panel.grid_remove()
            self.grid_columnconfigure(0, weight=0, minsize=0)
            self.right_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=8, pady=(4, 6))
            self.btn_theater.configure(
                text=LocalizationService.get("restore_panels"),
                fg_color="#2563EB", hover_color="#1D4ED8"
            )
        else:
            self.right_frame.grid(row=1, column=1, columnspan=1, sticky="nsew", padx=8, pady=(4, 6))
            self.grid_columnconfigure(0, weight=0, minsize=350)
            self.left_frame.grid()
            self.metrics_panel.grid()
            self.btn_theater.configure(
                text=LocalizationService.get("theater_toggle"),
                fg_color="#1E293B", hover_color="#334155"
            )

    def _handle_escape_key(self):
        """Context-aware Escape key handler: exits presentation, theater, or fullscreen."""
        try:
            active_tab = self.tabview.get()
        except Exception:
            active_tab = ""

        tab_hist_title = LocalizationService.get("tab_history")
        tab_guide_title = LocalizationService.get("tab_guide")

        if active_tab in ("tab_hist", tab_hist_title) and getattr(self.history_view, "is_presentation_mode", False):
            self.history_view.toggle_presentation_mode()
            return
        if active_tab in ("tab_guide", tab_guide_title) and getattr(self.guide_view, "is_presentation_mode", False):
            self.guide_view.toggle_presentation_mode()
            return

        if self._is_theater_mode:
            self._toggle_theater_mode(force_theater=False)
            return

        if self._is_window_fullscreen:
            self._toggle_window_fullscreen()

    def _handle_presentation_shortcut(self):
        """F5 hotkey: toggles presentation mode for History or Guide tab, or toggles theater mode."""
        try:
            active_tab = self.tabview.get()
        except Exception:
            active_tab = ""

        tab_hist_title = LocalizationService.get("tab_history")
        tab_guide_title = LocalizationService.get("tab_guide")

        if active_tab in ("tab_hist", tab_hist_title):
            self.history_view.toggle_presentation_mode()
        elif active_tab in ("tab_guide", tab_guide_title):
            self.guide_view.toggle_presentation_mode()
        else:
            self._toggle_theater_mode()

    def _open_web_presentation(self):
        """Launches the interactive web presentation deck in the default browser (F9)."""
        from utils.web_presentation_service import WebPresentationService
        try:
            active = self.tabview.get()
        except Exception:
            active = ""
        tab_guide_title = LocalizationService.get("tab_guide")
        sec = "guide" if active in ("tab_guide", tab_guide_title) else "history"
        WebPresentationService.open_in_browser(section=sec)

    # ==========================================================================
    # Multi-Format Export Pipelines
    # ==========================================================================
    def _on_export_csv(self):
        """Exports 22-column scientific dataset with metadata."""
        filepath = filedialog.asksaveasfilename(
            title="Export 22-Column Simulation Data (CSV)",
            defaultextension=".csv",
            filetypes=[("CSV Spreadsheet", "*.csv"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        intensity = self.classical_engine.compute_intensity_profile(self.y_grid_m)
        features = self.classical_engine.get_analytical_features()

        params_dict = {
            "wavelength_m": self.optical_params.wavelength_m,
            "slit_distance_d_m": self.optical_params.slit_distance_d_m,
            "slit_width_a_m": self.optical_params.slit_width_a_m,
            "screen_distance_L_m": self.optical_params.screen_distance_L_m,
            "refractive_index_n": self.optical_params.refractive_index_n,
            "simulation_mode": self.mode,
            "which_way_observer_active": self.quantum_engine.which_way_active if self.mode == "quantum" else False
        }

        quantum_hist = None
        total_hits = self.quantum_engine.total_hits if self.mode == "quantum" else 0
        if self.mode == "quantum" and total_hits > 0:
            half_span = self.screen_span_y_m / 2.0
            bins = np.linspace(-half_span, half_span, len(self.y_grid_m) + 1)
            counts, _ = np.histogram(self.quantum_engine.hits_y, bins=bins)
            quantum_hist = counts

        result = ExportService.export_csv(
            filepath=filepath,
            y_grid_m=self.y_grid_m,
            intensity_theory=intensity,
            quantum_histogram=quantum_hist,
            params_dict=params_dict,
            stats_dict=features,
            total_hits=total_hits
        )
        if result["success"]:
            messagebox.showinfo("Export Successful", result["message"])
        else:
            messagebox.showerror("Export Failed", result["message"])

    def _on_export_plot(self):
        """Context-Aware Image Export: Exports image matching the active tab."""
        active_tab = self.tabview.get()

        filepath = filedialog.asksaveasfilename(
            title=f"Export Active View Image ({active_tab})",
            defaultextension=".png",
            filetypes=[
                ("PNG Image (300 DPI)", "*.png"),
                ("PDF Document", "*.pdf"),
                ("SVG Vector", "*.svg"),
                ("All Files", "*.*")
            ]
        )
        if not filepath:
            return

        # Route export based on active tab
        tab_3d_title = LocalizationService.get("tab_3d_setup")
        tab_2d_title = LocalizationService.get("tab_2d_screen")
        tab_sch_title = LocalizationService.get("tab_schematic")
        tab_calc_title = LocalizationService.get("tab_calculations")
        tab_hist_title = LocalizationService.get("tab_history")

        if active_tab in ("tab_3d", tab_3d_title):
            # Export 3D Figure
            result = ExportService.export_figure(filepath=filepath, figure=self.setup_3d_view.fig, dpi=300)
        elif active_tab in ("tab_2d", tab_2d_title):
            # Export 2D Screen with millimeter ruler
            intensity = self.classical_engine.compute_intensity_profile(self.y_grid_m)
            rgb, _hex = self._display_colors()
            result = ExportService.export_screen_image(
                filepath=filepath,
                intensity_1d=intensity,
                base_rgb=rgb,
                span_y_m=self.screen_span_y_m,
                quantum_buffer=self.screen_2d_view.quantum_buffer,
                is_quantum=(self.mode == "quantum")
            )
        elif active_tab in ("tab_sch", tab_sch_title):
            # Export 2D Wave Propagation & Interference Schematic
            wl_nm = self.optical_params.wavelength_m * 1e9
            result = ExportService.export_schematic_image(
                filepath=filepath,
                wavelength_nm=wl_nm,
                slit_distance_mm=self.optical_params.slit_distance_d_m * 1000.0,
                slit_width_mm=self.optical_params.slit_width_a_m * 1000.0,
                screen_distance_m=self.optical_params.screen_distance_L_m,
                which_way_active=(self.quantum_engine.which_way_active if self.mode == "quantum" else False),
                particle_category=(self.quantum_engine.particle.category if self.mode == "quantum" else ParticleCategory.PHOTON),
                is_quantum=(self.mode == "quantum"),
                target_y_offset=self.setup_schematic_view.target_y_offset,
                is_persian=LocalizationService.is_persian()
            )
        elif active_tab in ("tab_calc", tab_calc_title):
            # Export Calculations card graphic
            features = self.classical_engine.get_analytical_features()
            result = ExportService.export_calculations_image(
                filepath=filepath,
                optical_params=self.optical_params,
                features=features,
                inspector_y_mm=self.calculations_view.inspector_y_mm,
                is_persian=LocalizationService.is_persian(),
                quantum_engine=self.quantum_engine if self.mode == "quantum" else None
            )
        elif active_tab in ("tab_hist", tab_hist_title):
            # Export the history tab's live fringe figure when present
            fig = getattr(self.history_view, "_mpl_fig", None)
            if fig is not None:
                result = ExportService.export_figure(filepath=filepath, figure=fig, dpi=300)
            else:
                result = {"success": False, "message": "This history slide has no figure to export."}
        else:
            # Default to 1D Profile Plot
            result = ExportService.export_figure(filepath=filepath, figure=self.profile_1d_view.fig, dpi=300)

        if result["success"]:
            messagebox.showinfo("Plot Saved", result["message"])
        else:
            messagebox.showerror("Save Failed", result["message"])

    def _on_export_3d_model(self):
        """Exports CAD-compatible 3D Wavefront OBJ + MTL + PNG Texture."""
        filepath = filedialog.asksaveasfilename(
            title="Export 3D Laboratory Model (.OBJ)",
            defaultextension=".obj",
            filetypes=[("Wavefront 3D Model (*.obj)", "*.obj"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        intensity = self.classical_engine.compute_intensity_profile(self.y_grid_m)
        wl_nm = self.optical_params.wavelength_m * 1e9
        base_rgb, _hex = self._display_colors()

        result = ExportService.export_3d_model(
            filepath=filepath,
            wavelength_nm=wl_nm,
            slit_distance_mm=self.optical_params.slit_distance_d_m * 1000.0,
            slit_width_mm=self.optical_params.slit_width_a_m * 1000.0,
            screen_distance_m=self.optical_params.screen_distance_L_m,
            which_way_active=self.quantum_engine.which_way_active if self.mode == "quantum" else False,
            intensity_1d=intensity,
            base_rgb=base_rgb
        )
        if result["success"]:
            messagebox.showinfo("3D Model Exported", result["message"])
        else:
            messagebox.showerror("Export Failed", result["message"])

    def _on_export_all_in_one_zip(self):
        """Exports complete Laboratory Archive (.zip) containing CSV, Word report, 3D model, and 300 DPI figures."""
        filepath = filedialog.asksaveasfilename(
            title="Export Laboratory Complete Bundle (.ZIP)",
            defaultextension=".zip",
            filetypes=[("ZIP Archive (*.zip)", "*.zip"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        intensity = self.classical_engine.compute_intensity_profile(self.y_grid_m)
        features = self.classical_engine.get_analytical_features()
        params_dict = {
            "wavelength_m": self.optical_params.wavelength_m,
            "slit_distance_d_m": self.optical_params.slit_distance_d_m,
            "slit_width_a_m": self.optical_params.slit_width_a_m,
            "screen_distance_L_m": self.optical_params.screen_distance_L_m,
            "refractive_index_n": self.optical_params.refractive_index_n,
            "simulation_mode": self.mode,
            "which_way_observer_active": self.quantum_engine.which_way_active if self.mode == "quantum" else False,
            "screen_span_y_m": self.screen_span_y_m
        }

        quantum_hist = None
        total_hits = self.quantum_engine.total_hits if self.mode == "quantum" else 0
        if self.mode == "quantum" and total_hits > 0:
            half_span = self.screen_span_y_m / 2.0
            bins = np.linspace(-half_span, half_span, len(self.y_grid_m) + 1)
            counts, _ = np.histogram(self.quantum_engine.hits_y, bins=bins)
            quantum_hist = counts

        which_way = self.quantum_engine.which_way_active if self.mode == "quantum" else False

        result = ExportService.export_all_in_one_zip(
            filepath=filepath,
            y_grid_m=self.y_grid_m,
            intensity_theory=intensity,
            quantum_histogram=quantum_hist,
            params_dict=params_dict,
            stats_dict=features,
            total_hits=total_hits,
            optical_params=self.optical_params,
            quantum_engine=self.quantum_engine if self.mode == "quantum" else None,
            features=features,
            setup_3d_fig=self.setup_3d_view.fig,
            profile_1d_fig=self.profile_1d_view.fig,
            screen_2d_quantum_buffer=self.screen_2d_view.quantum_buffer,
            which_way_active=which_way,
            target_y_offset=self.setup_schematic_view.target_y_offset,
            inspector_y_mm=self.calculations_view.inspector_y_mm,
            is_persian=LocalizationService.is_persian(),
            is_quantum=(self.mode == "quantum")
        )
        if result["success"]:
            messagebox.showinfo("Lab Bundle Exported", result["message"])
        else:
            messagebox.showerror("Export Failed", result["message"])

    def _on_export_calculations_docx(self):
        """Exports educational Word (.docx) report with native OMML equations."""
        filepath = filedialog.asksaveasfilename(
            title="Export Calculations Report (Word .docx)",
            defaultextension=".docx",
            filetypes=[("Microsoft Word Document (*.docx)", "*.docx"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        features = self.classical_engine.get_analytical_features()
        result = ExportService.export_word_report(
            filepath=filepath,
            optical_params=self.optical_params,
            quantum_engine=self.quantum_engine if self.mode == "quantum" else None,
            features=features,
            inspector_y_mm=self.calculations_view.inspector_y_mm,
            is_persian=LocalizationService.is_persian()
        )
        if result["success"]:
            messagebox.showinfo("Word Report Exported", result["message"])
        else:
            messagebox.showerror("Export Failed", result["message"])

    def _on_export_calculations_png(self):
        """Exports Calculations summary to high-resolution PNG image."""
        filepath = filedialog.asksaveasfilename(
            title="Export Calculations Summary (PNG)",
            defaultextension=".png",
            filetypes=[("PNG Image (*.png)", "*.png"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        features = self.classical_engine.get_analytical_features()
        result = ExportService.export_calculations_image(
            filepath=filepath,
            optical_params=self.optical_params,
            features=features,
            inspector_y_mm=self.calculations_view.inspector_y_mm,
            is_persian=LocalizationService.is_persian(),
            quantum_engine=self.quantum_engine if self.mode == "quantum" else None
        )
        if result["success"]:
            messagebox.showinfo("Calculations Image Saved", result["message"])
        else:
            messagebox.showerror("Save Failed", result["message"])
