"""
Calculations and Equations View.
Displays educational step-by-step physical derivations, live numerical substitutions,
interactive real-time Point Inspector across the screen, and direct export to Word (.docx) and PNG.
Fully styled with Vazirmatn and Space Grotesk typography.
"""

import math
from typing import Dict, Any, Optional, Callable
import customtkinter as ctk
import numpy as np

from utils.localization import LocalizationService, RLM
from utils.font_manager import FontManager
from physics.classical_engine import OpticalParameters
from physics.quantum_engine import QuantumEngine

class CalculationsView(ctk.CTkScrollableFrame):
    """
    Educational tab presenting live mathematical formulas, step-by-step substitutions,
    and a real-time point inspector allowing user to evaluate any screen coordinate.
    """

    def __init__(
        self,
        master,
        on_export_docx: Optional[Callable[[], None]] = None,
        on_export_png: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.on_export_docx = on_export_docx
        self.on_export_png = on_export_png

        # Inspector coordinate
        self.inspector_y_mm = 0.0

        # Cached physical state
        self.optical_params = OpticalParameters()
        self.quantum_engine: Optional[QuantumEngine] = None
        self.features: Dict[str, Any] = {}

        self.cards: Dict[str, ctk.CTkFrame] = {}
        self.card_labels: Dict[str, ctk.CTkLabel] = {}

        self._create_widgets()

    def _create_widgets(self):
        """Constructs mathematical equation cards, action buttons, and the point inspector."""
        self.grid_columnconfigure(0, weight=1)

        is_fa = LocalizationService.is_persian()

        # Top Action Bar with Section Title and Export Buttons
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=8, pady=(4, 10), sticky="ew")
        top_bar.grid_columnconfigure(0, weight=1)

        self.header_label = ctk.CTkLabel(
            top_bar,
            text=LocalizationService.get("calc_header"),
            font=FontManager.get_persian_font(13, "bold") if is_fa else FontManager.get_number_font(13, "bold"),
            anchor="e" if is_fa else "w"
        )
        self.header_label.pack(side="right" if is_fa else "left", padx=4)

        # Export Buttons Cluster
        btn_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_box.pack(side="left" if is_fa else "right", padx=4)

        self.btn_export_docx = ctk.CTkButton(
            btn_box,
            text=LocalizationService.get("export_docx"),
            command=self._handle_export_docx,
            font=FontManager.get_persian_font(10, "bold") if is_fa else FontManager.get_number_font(10, "bold"),
            fg_color="#1D4ED8",
            hover_color="#1E40AF",
            height=28
        )
        self.btn_export_docx.pack(side="left", padx=3)

        self.btn_export_png = ctk.CTkButton(
            btn_box,
            text=LocalizationService.get("export_calc_png"),
            command=self._handle_export_png,
            font=FontManager.get_persian_font(10, "bold") if is_fa else FontManager.get_number_font(10, "bold"),
            fg_color="#047857",
            hover_color="#065F46",
            height=28
        )
        self.btn_export_png.pack(side="left", padx=3)

        # ======================================================================
        # CARD 1: Optical Path Difference & Geometry
        # ======================================================================
        card1 = self._create_card(
            row=1,
            loc_key="calc_card1"
        )
        self.lbl_card1_formula = ctk.CTkLabel(
            card1,
            text="Δr = r₂ - r₁ = d · sin(θ) ≈ d · (y / L)",
            font=FontManager.get_number_font(12, "bold"),
            text_color="#00F0FF"
        )
        self.lbl_card1_formula.pack(anchor="w", padx=12, pady=(2, 2))

        self.lbl_card1_sub = ctk.CTkLabel(
            card1,
            text="Δr = (0.250 mm) × sin(θ) ≈ 0.250 × (y / 1.00 m)",
            font=FontManager.get_number_font(11),
            text_color="#E0E0E0"
        )
        self.lbl_card1_sub.pack(anchor="w", padx=12, pady=(0, 6))

        # ======================================================================
        # CARD 2: Constructive & Destructive Interference Conditions
        # ======================================================================
        card2 = self._create_card(
            row=2,
            loc_key="calc_card2"
        )
        self.lbl_card2_text = ctk.CTkLabel(
            card2,
            text="Constructive (Bright): d·sin(θ) = m·λ  =>  y_m = m·(λ·L / d)\nDestructive (Dark):   d·sin(θ) = (m + 0.5)·λ  =>  y'_m = (m + 0.5)·(λ·L / d)",
            font=FontManager.get_number_font(11, "bold"),
            text_color="#38BDF8",
            justify="left"
        )
        self.lbl_card2_text.pack(anchor="w", padx=12, pady=(2, 2))

        self.lbl_card2_sub = ctk.CTkLabel(
            card2,
            text="Central Max (m=0): y₀ = 0.00 mm | Order 1: y₁ = ±2.53 mm | Order 2: y₂ = ±5.06 mm",
            font=FontManager.get_number_font(11),
            text_color="#E0E0E0"
        )
        self.lbl_card2_sub.pack(anchor="w", padx=12, pady=(0, 6))

        # ======================================================================
        # CARD 3: Fringe Spacing Formula (Δy)
        # ======================================================================
        card3 = self._create_card(
            row=3,
            loc_key="calc_card3"
        )
        self.lbl_card3_formula = ctk.CTkLabel(
            card3,
            text="Δy = (λ · L) / (n · d)",
            font=FontManager.get_number_font(12, "bold"),
            text_color="#10B981"
        )
        self.lbl_card3_formula.pack(anchor="w", padx=12, pady=(2, 2))

        self.lbl_card3_sub = ctk.CTkLabel(
            card3,
            text="Δy = (632.8 nm × 1.00 m) / (1.000 × 0.250 mm) = 2.531 mm",
            font=FontManager.get_number_font(11),
            text_color="#E0E0E0"
        )
        self.lbl_card3_sub.pack(anchor="w", padx=12, pady=(0, 6))

        # ======================================================================
        # CARD 4: Fraunhofer Diffraction Envelope & Missing Orders
        # ======================================================================
        card4 = self._create_card(
            row=4,
            loc_key="calc_card4"
        )
        self.lbl_card4_formula = ctk.CTkLabel(
            card4,
            text="I(y) = I₀ · [sinc(π·a·sinθ / λ)]² · cos²(π·d·sinθ / λ)",
            font=FontManager.get_number_font(11, "bold"),
            text_color="#FBBF24"
        )
        self.lbl_card4_formula.pack(anchor="w", padx=12, pady=(2, 2))

        self.lbl_card4_sub = ctk.CTkLabel(
            card4,
            text="Central Envelope Width: W = 2·λ·L / a = 31.64 mm | Missing Orders: None",
            font=FontManager.get_number_font(11),
            text_color="#E0E0E0"
        )
        self.lbl_card4_sub.pack(anchor="w", padx=12, pady=(0, 6))

        # ======================================================================
        # CARD 5: Quantum Mechanics & De Broglie Matter Waves
        # ======================================================================
        card5 = self._create_card(
            row=5,
            loc_key="calc_card5"
        )
        self.lbl_card5_formula = ctk.CTkLabel(
            card5,
            text="λ_dB = h / p = h / √(2·m·E_k)  [De Broglie Relation]",
            font=FontManager.get_number_font(11, "bold"),
            text_color="#A78BFA"
        )
        self.lbl_card5_formula.pack(anchor="w", padx=12, pady=(2, 2))

        self.lbl_card5_sub = ctk.CTkLabel(
            card5,
            text="Electron: E = 100.0 eV => Momentum p = 5.40e-24 kg·m/s => λ_dB = 0.1226 nm",
            font=FontManager.get_number_font(11),
            text_color="#E0E0E0"
        )
        self.lbl_card5_sub.pack(anchor="w", padx=12, pady=(0, 6))

        # ======================================================================
        # CARD 6: Quantum Superposition vs Wavefunction Collapse
        # ======================================================================
        card6 = self._create_card(
            row=6,
            loc_key="calc_card6"
        )
        self.lbl_card6_text = ctk.CTkLabel(
            card6,
            text="Detector OFF: P(y) = |Ψ₁ + Ψ₂|² = P₁ + P₂ + 2√(P₁P₂)·cos(Δφ)  [Visibility V = 1.0]\nDetector ON:  P(y) = |Ψ₁|² + |Ψ₂|² = P₁ + P₂ (Interference Destroyed!) [Visibility V = 0.0]",
            font=FontManager.get_number_font(11, "bold"),
            text_color="#F472B6",
            justify="left"
        )
        self.lbl_card6_text.pack(anchor="w", padx=12, pady=(2, 2))

        # ======================================================================
        # CARD 7: Interactive Real-Time Point Inspector
        # ======================================================================
        inspector_card = ctk.CTkFrame(self, fg_color="#18181B", corner_radius=8, border_width=1, border_color="#3B82F6")
        inspector_card.grid(row=7, column=0, padx=8, pady=(8, 16), sticky="ew")
        inspector_card.grid_columnconfigure(0, weight=1)

        insp_header = ctk.CTkFrame(inspector_card, fg_color="transparent")
        insp_header.pack(fill="x", padx=10, pady=(6, 4))

        self.insp_title = ctk.CTkLabel(
            insp_header,
            text=LocalizationService.get("calc_card7"),
            font=FontManager.get_persian_font(12, "bold") if is_fa else FontManager.get_number_font(12, "bold"),
            text_color="#60A5FA"
        )
        self.insp_title.pack(side="right" if is_fa else "left")

        # Inspector Slider
        slider_row = ctk.CTkFrame(inspector_card, fg_color="transparent")
        slider_row.pack(fill="x", padx=10, pady=2)

        self.insp_slider_label = ctk.CTkLabel(
            slider_row,
            text=LocalizationService.get("inspector_slider"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )
        self.insp_slider_label.pack(side="right" if is_fa else "left", padx=4)

        self.insp_val_label = ctk.CTkLabel(
            slider_row,
            text="0.00 mm",
            font=FontManager.get_number_font(11, "bold"),
            text_color="#00F0FF"
        )
        self.insp_val_label.pack(side="left" if is_fa else "right", padx=6)

        self.insp_slider = ctk.CTkSlider(
            inspector_card,
            from_=-15.0,
            to=15.0,
            number_of_steps=300,
            command=self._on_inspector_slider_change
        )
        self.insp_slider.set(0.0)
        self.insp_slider.pack(fill="x", padx=10, pady=(4, 2))

        # Manual inspector position entry (local readout only)
        insp_entry_row = ctk.CTkFrame(inspector_card, fg_color="transparent")
        insp_entry_row.pack(fill="x", padx=10, pady=(0, 4))

        self._insp_syncing = False
        self.insp_entry = ctk.CTkEntry(
            insp_entry_row,
            width=100,
            height=26,
            justify="center",
            font=FontManager.get_number_font(11),
            border_color="#3F3F46",
            fg_color="#18181B"
        )
        self.insp_entry.insert(0, "0.00")
        self.insp_entry.pack(side="left", padx=(0, 6))
        self.insp_entry.bind("<KeyRelease>", lambda _e: self._on_inspector_entry_change(live=True))
        self.insp_entry.bind("<Return>", lambda _e: self._on_inspector_entry_change(live=False))
        self.insp_entry.bind("<FocusOut>", lambda _e: self._on_inspector_entry_change(live=False))

        insp_unit_lbl = ctk.CTkLabel(
            insp_entry_row,
            text="mm",
            font=FontManager.get_number_font(10),
            text_color="#9E9E9E"
        )
        insp_unit_lbl.pack(side="left")

        insp_range_lbl = ctk.CTkLabel(
            insp_entry_row,
            text="[-15.00 … +15.00]",
            font=FontManager.get_number_font(9),
            text_color="#71717A"
        )
        insp_range_lbl.pack(side="right")

        # Results Grid inside Inspector
        res_grid = ctk.CTkFrame(inspector_card, fg_color="#121214", corner_radius=6)
        res_grid.pack(fill="x", padx=10, pady=(4, 10))
        res_grid.grid_columnconfigure((0, 1), weight=1)

        self.lbl_insp_r = ctk.CTkLabel(
            res_grid,
            text="r₁ = 1.000008 m | r₂ = 1.000008 m",
            font=FontManager.get_number_font(11),
            text_color="#E2E8F0"
        )
        self.lbl_insp_r.grid(row=0, column=0, padx=8, pady=3, sticky="w")

        self.lbl_insp_deltar = ctk.CTkLabel(
            res_grid,
            text="Δr (Exact) = 0.0 nm | Δr (Paraxial) = 0.0 nm",
            font=FontManager.get_number_font(11, "bold"),
            text_color="#38BDF8"
        )
        self.lbl_insp_deltar.grid(row=0, column=1, padx=8, pady=3, sticky="w")

        self.lbl_insp_phase = ctk.CTkLabel(
            res_grid,
            text="Phase Diff Δφ = 0.00 rad (0.0°)",
            font=FontManager.get_number_font(11),
            text_color="#A78BFA"
        )
        self.lbl_insp_phase.grid(row=1, column=0, padx=8, pady=3, sticky="w")

        self.lbl_insp_intensity = ctk.CTkLabel(
            res_grid,
            text="Relative Intensity I/I₀ = 100.0%  [Bright Maximum]",
            font=FontManager.get_number_font(11, "bold"),
            text_color="#4ADE80"
        )
        self.lbl_insp_intensity.grid(row=1, column=1, padx=8, pady=3, sticky="w")

    def _create_card(self, row: int, loc_key: str) -> ctk.CTkFrame:
        """Helper to create an educational formula card."""
        is_fa = LocalizationService.is_persian()
        card = ctk.CTkFrame(self, fg_color="#18181B", corner_radius=6, border_width=1, border_color="#27272A")
        card.grid(row=row, column=0, padx=8, pady=4, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        t_lbl = ctk.CTkLabel(
            card,
            text=LocalizationService.get(loc_key),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            text_color="#CBD5E1",
            anchor="e" if is_fa else "w"
        )
        t_lbl.pack(anchor="e" if is_fa else "w", padx=10, pady=(6, 2), fill="x")
        self.card_labels[f"card_{row}"] = (t_lbl, loc_key)
        return card

    def _handle_export_docx(self):
        if self.on_export_docx:
            self.on_export_docx()

    def _handle_export_png(self):
        if self.on_export_png:
            self.on_export_png()

    def refresh_language(self):
        """Refreshes text and fonts on language change."""
        is_fa = LocalizationService.is_persian()
        self.header_label.configure(
            text=LocalizationService.get("calc_header"),
            font=FontManager.get_persian_font(13, "bold") if is_fa else FontManager.get_number_font(13, "bold"),
            anchor="e" if is_fa else "w"
        )
        self.header_label.pack(side="right" if is_fa else "left")

        self.btn_export_docx.configure(
            text=LocalizationService.get("export_docx"),
            font=FontManager.get_persian_font(10, "bold") if is_fa else FontManager.get_number_font(10, "bold")
        )
        self.btn_export_png.configure(
            text=LocalizationService.get("export_calc_png"),
            font=FontManager.get_persian_font(10, "bold") if is_fa else FontManager.get_number_font(10, "bold")
        )

        for key, (lbl, loc_key) in self.card_labels.items():
            lbl.configure(
                text=LocalizationService.get(loc_key),
                font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
                anchor="e" if is_fa else "w"
            )
            lbl.pack(anchor="e" if is_fa else "w")

        self.insp_title.configure(
            text=LocalizationService.get("calc_card7"),
            font=FontManager.get_persian_font(12, "bold") if is_fa else FontManager.get_number_font(12, "bold")
        )
        self.insp_title.pack(side="right" if is_fa else "left")

        self.insp_slider_label.configure(
            text=LocalizationService.get("inspector_slider"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )
        self.insp_slider_label.pack(side="right" if is_fa else "left")

        self._recalculate_inspector()

    def _on_inspector_slider_change(self, val: float):
        if getattr(self, "_insp_syncing", False):
            return
        self._insp_syncing = True
        try:
            self.inspector_y_mm = max(-15.0, min(15.0, float(val)))
            self.insp_val_label.configure(text=f"{self.inspector_y_mm:.2f} mm")
            if hasattr(self, "insp_entry"):
                self.insp_entry.delete(0, "end")
                self.insp_entry.insert(0, f"{self.inspector_y_mm:.2f}")
                self.insp_entry.configure(border_color="#3F3F46")
            self._recalculate_inspector()
        finally:
            self._insp_syncing = False

    def _on_inspector_entry_change(self, live: bool):
        """Commits a manually typed inspector position (local readout only)."""
        from utils.numeric_input import parse_number
        if getattr(self, "_insp_syncing", False):
            return
        parsed = parse_number(self.insp_entry.get())
        if parsed is None:
            self.insp_entry.configure(border_color="#F59E0B")
            return
        if live and not (-15.0 <= parsed <= 15.0):
            self.insp_entry.configure(border_color="#F59E0B")
            return
        self._insp_syncing = True
        try:
            clamped = max(-15.0, min(15.0, parsed))
            self.inspector_y_mm = clamped
            self.insp_slider.set(clamped)
            self.insp_entry.delete(0, "end")
            self.insp_entry.insert(0, f"{clamped:.2f}")
            self.insp_entry.configure(border_color="#3F3F46")
            self.insp_val_label.configure(text=f"{clamped:.2f} mm")
            self._recalculate_inspector()
        finally:
            self._insp_syncing = False

    def update_calculations(
        self,
        optical_params: OpticalParameters,
        quantum_engine: Optional[QuantumEngine],
        features: Dict[str, Any]
    ):
        """Updates live substitutions on all cards."""
        self.optical_params = optical_params
        self.quantum_engine = quantum_engine
        self.features = features

        wl_nm = optical_params.wavelength_m * 1e9
        d_mm = optical_params.slit_distance_d_m * 1000.0
        a_mm = optical_params.slit_width_a_m * 1000.0
        L_m = optical_params.screen_distance_L_m
        n = optical_params.refractive_index_n
        dy_mm = features.get("fringe_spacing_dy_mm", 0.0)
        env_mm = features.get("central_envelope_width_mm", 0.0)

        # Card 1 substitution
        self.lbl_card1_sub.configure(
            text=f"Δr = ({d_mm:.3f} mm) × sin(θ) ≈ {d_mm:.3f} × (y / {L_m:.2f} m)"
        )

        # Card 2 substitution
        self.lbl_card2_sub.configure(
            text=f"Central Max (m=0): y₀ = 0.00 mm | Order 1: y₁ = ±{dy_mm:.3f} mm | Order 2: y₂ = ±{2*dy_mm:.3f} mm"
        )

        # Card 3 substitution
        self.lbl_card3_sub.configure(
            text=f"Δy = ({wl_nm:.1f} nm × {L_m:.2f} m) / ({n:.3f} × {d_mm:.3f} mm) = {dy_mm:.3f} mm"
        )

        # Card 4 substitution
        ratio = d_mm / max(a_mm, 1e-4)
        miss = features.get("missing_orders", [])
        none_str = LocalizationService.get("missing_none")
        miss_txt = "m = ±" + ", ±".join([str(abs(m)) for m in miss if m > 0][:3]) if miss else none_str
        self.lbl_card4_sub.configure(
            text=f"Central Envelope Width: W = 2·λ·L / a = {env_mm:.2f} mm | Ratio d/a = {ratio:.2f} => Missing Orders: {miss_txt}"
        )

        # Card 5 substitution (Quantum)
        if quantum_engine:
            p_cat = quantum_engine.particle.name_en if not LocalizationService.is_persian() else quantum_engine.particle.name_fa
            ev = quantum_engine.energy_ev
            wl_m = quantum_engine.optical_params.wavelength_m
            wl_display = f"{wl_m*1e9:.4f} nm" if wl_m > 1e-10 else f"{wl_m*1e12:.2f} pm"
            self.lbl_card5_sub.configure(
                text=f"{p_cat} | Energy/Voltage = {ev:.1f} | Calculated De Broglie λ = {wl_display}"
            )

        self._recalculate_inspector()

    def _recalculate_inspector(self):
        """Evaluates physical optics equations at user chosen y coordinate."""
        L = max(self.optical_params.screen_distance_L_m, 1e-3)
        d = self.optical_params.slit_distance_d_m
        a = self.optical_params.slit_width_a_m
        wl = max(self.optical_params.medium_wavelength_m, 1e-12)

        y_m = self.inspector_y_mm * 1e-3

        # Ray path lengths
        r1 = math.sqrt(L ** 2 + (y_m - d / 2.0) ** 2)
        r2 = math.sqrt(L ** 2 + (y_m + d / 2.0) ** 2)
        self.lbl_insp_r.configure(text=f"r₁ = {r1:.6f} m | r₂ = {r2:.6f} m")

        # Path differences
        dr_exact_m = abs(r2 - r1)
        dr_exact_nm = dr_exact_m * 1e9

        sin_th = y_m / math.sqrt(y_m ** 2 + L ** 2)
        dr_parax_nm = abs(d * sin_th) * 1e9
        self.lbl_insp_deltar.configure(
            text=f"Δr (Exact) = {dr_exact_nm:.2f} nm | Δr (Paraxial) = {dr_parax_nm:.2f} nm"
        )

        # Phase difference
        phase_rad = (2.0 * math.pi * dr_exact_m) / wl
        phase_deg = math.degrees(phase_rad) % 360.0
        self.lbl_insp_phase.configure(
            text=f"Phase Diff Δφ = {phase_rad:.2f} rad ({phase_deg:.1f}°)"
        )

        # Intensity
        beta = (math.pi * a * sin_th) / wl
        sinc_sq = (math.sin(beta) / beta) ** 2 if abs(beta) > 1e-6 else 1.0
        alpha = (math.pi * d * sin_th) / wl
        cos_sq = (math.cos(alpha)) ** 2
        i_rel = sinc_sq * cos_sq * 100.0

        # State classification
        order_m = dr_exact_m / wl
        nearest_m = round(order_m)
        is_fa = LocalizationService.is_persian()
        if abs(order_m - nearest_m) < 0.05:
            cond = f"[{LocalizationService.get('status_bright')} (m={nearest_m})]"
            col = "#4ADE80"
        elif abs(order_m - (nearest_m + 0.5)) < 0.05:
            cond = f"[{LocalizationService.get('status_dark')}]"
            col = "#F87171"
        else:
            cond = f"[{LocalizationService.get('status_intermediate')}]"
            col = "#38BDF8"

        self.lbl_insp_intensity.configure(
            text=f"Relative Intensity I/I₀ = {i_rel:.1f}%  {cond}",
            text_color=col
        )
