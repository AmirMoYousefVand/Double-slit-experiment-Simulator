"""
Control Panel for Optical and Apparatus Parameters.
Provides real-time sliders, numeric entries, preset selector, and color preview swatch.
Fully adapted for dynamic Persian RTL and English LTR layouts with Vazirmatn and Space Grotesk typography.
"""

from typing import Callable, Dict, Any, Optional, List
import customtkinter as ctk

from config import PARAM_LIMITS, PARAM_DECIMALS, PRESETS
from utils.color_utils import ColorUtils
from utils.localization import LocalizationService, RLM
from utils.font_manager import FontManager
from utils.numeric_input import parse_number, clamp, clamp_range
from physics.classical_engine import fringe_spacing_mm, wavelength_nm_from_fringe_spacing

class ControlPanel(ctk.CTkScrollableFrame):
    """
    Scrollable control panel hosting sliders for wavelength, slit distance,
    slit width, screen distance, refractive index, and laboratory presets.
    """

    PRESET_KEYS = [
        ("preset_hene", "He-Ne Red Laser"),
        ("preset_argon", "Argon-Ion Green"),
        ("preset_violet", "Violet Laser Diode"),
        ("preset_sodium", "Sodium D-Line"),
        ("preset_water", "Water Medium (Underwater)"),
        ("preset_narrow", "High Diffraction (Close Slits)")
    ]

    def __init__(
        self,
        master,
        on_param_change: Callable[[str, float], None],
        on_preset_selected: Callable[[str], None],
        on_reset_defaults: Callable[[], None],
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.on_param_change = on_param_change
        self.on_preset_selected = on_preset_selected
        self.on_reset_defaults = on_reset_defaults

        self.sliders: Dict[str, ctk.CTkSlider] = {}
        self.value_labels: Dict[str, ctk.CTkLabel] = {}
        self.param_title_labels: Dict[str, ctk.CTkLabel] = {}
        self.range_labels: Dict[str, ctk.CTkLabel] = {}
        self.entries: Dict[str, ctk.CTkEntry] = {}
        self._syncing = False
        # Exact (unquantized) parameter values: CTkSlider.set() snaps to the
        # step grid (632.8 nm -> 633), so slider.get() must not be used as a
        # source of truth for the Δy <-> λ conversion.
        self._exact_values: Dict[str, float] = {
            k: cfg["default"] for k, cfg in PARAM_LIMITS.items()
        }
        self.units = {
            "wavelength_nm": "nm",
            "fringe_spacing_mm": "mm",
            "slit_distance_mm": "mm",
            "slit_width_mm": "mm",
            "screen_distance_m": "m",
            "refractive_index": ""
        }

        self.slider_configs = [
            ("wavelength_nm", "wavelength"),
            ("fringe_spacing_mm", "fringe_spacing_param"),
            ("slit_distance_mm", "slit_distance"),
            ("slit_width_mm", "slit_width"),
            ("screen_distance_m", "screen_distance"),
            ("refractive_index", "refractive_index")
        ]

        self._create_widgets()

    def _get_preset_display_names(self) -> List[str]:
        return [LocalizationService.get(k) for k, _ in self.PRESET_KEYS]

    def _create_widgets(self):
        """Builds all controls and presets."""
        self.grid_columnconfigure(0, weight=1)

        is_fa = LocalizationService.is_persian()

        # 1. Section Title
        self.title_label = ctk.CTkLabel(
            self,
            text=LocalizationService.get("optics_panel_title"),
            font=FontManager.get_persian_font(13, "bold") if is_fa else FontManager.get_number_font(13, "bold"),
            anchor="e" if is_fa else "w"
        )
        self.title_label.grid(row=0, column=0, pady=(4, 8), sticky="e" if is_fa else "w")

        # 2. Presets Selector
        preset_frame = ctk.CTkFrame(self, fg_color="transparent")
        preset_frame.grid(row=1, column=0, pady=(0, 8), sticky="ew")

        self.preset_label = ctk.CTkLabel(
            preset_frame,
            text=LocalizationService.get("presets_label"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            anchor="e" if is_fa else "w"
        )
        self.preset_label.pack(anchor="e" if is_fa else "w", pady=(0, 2))

        preset_names = self._get_preset_display_names()
        self.preset_menu = ctk.CTkOptionMenu(
            preset_frame,
            values=preset_names,
            command=self._handle_preset_select,
            font=FontManager.get_persian_font(11) if is_fa else FontManager.get_number_font(11),
            dropdown_font=FontManager.get_persian_font(11) if is_fa else FontManager.get_number_font(11),
            dynamic_resizing=False,
            height=28
        )
        self.preset_menu.set(preset_names[0])
        self.preset_menu.pack(fill="x", pady=2)

        # 3. Parameters Sliders
        row_idx = 2

        for param_key, loc_key in self.slider_configs:
            cfg = PARAM_LIMITS[param_key]

            frame = ctk.CTkFrame(self, corner_radius=6)
            frame.grid(row=row_idx, column=0, pady=4, sticky="ew")
            frame.grid_columnconfigure(0, weight=1)

            # Header row
            header_row = ctk.CTkFrame(frame, fg_color="transparent")
            header_row.grid(row=0, column=0, padx=8, pady=(4, 2), sticky="ew")

            param_title = ctk.CTkLabel(
                header_row,
                text=LocalizationService.get(loc_key),
                font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
            )
            param_title.pack(side="right" if is_fa else "left", anchor="e" if is_fa else "w")
            self.param_title_labels[param_key] = (param_title, loc_key, header_row)

            # Value indicator
            unit = self.units[param_key]
            val_text = self._format_value(param_key, cfg['default'])
            val_label = ctk.CTkLabel(
                header_row,
                text=val_text,
                font=FontManager.get_number_font(11, "bold"),
                text_color="#00F0FF"
            )
            val_label.pack(side="left" if is_fa else "right", anchor="w" if is_fa else "e")
            self.value_labels[param_key] = val_label

            # Color preview swatch (only for wavelength)
            if param_key == "wavelength_nm":
                self.color_swatch = ctk.CTkButton(
                    header_row,
                    text="",
                    width=22,
                    height=16,
                    corner_radius=4,
                    fg_color=ColorUtils.wavelength_to_hex(cfg["default"]),
                    hover=False
                )
                self.color_swatch.pack(side="left" if is_fa else "right", padx=(4, 4))

            # The Slider itself
            slider = ctk.CTkSlider(
                frame,
                from_=cfg["min"],
                to=cfg["max"],
                number_of_steps=int((cfg["max"] - cfg["min"]) / cfg["step"]),
                command=lambda val, k=param_key: self._handle_slider_change(k, val)
            )
            slider.set(cfg["default"])
            slider.grid(row=1, column=0, padx=8, pady=(2, 2), sticky="ew")
            self.sliders[param_key] = slider

            # Manual numeric entry row (Latin digits, LTR in both languages)
            entry_row = ctk.CTkFrame(frame, fg_color="transparent")
            entry_row.grid(row=2, column=0, padx=8, pady=(0, 6), sticky="ew")

            entry = ctk.CTkEntry(
                entry_row,
                width=100,
                height=26,
                justify="center",
                font=FontManager.get_number_font(11),
                border_color="#3F3F46",
                fg_color="#18181B"
            )
            entry.insert(0, self._format_entry(param_key, cfg["default"]))
            entry.pack(side="left", padx=(0, 6))
            entry.bind("<KeyRelease>", lambda _e, k=param_key: self._handle_entry_change(k, live=True))
            entry.bind("<Return>", lambda _e, k=param_key: self._handle_entry_change(k, live=False))
            entry.bind("<FocusOut>", lambda _e, k=param_key: self._handle_entry_change(k, live=False))
            self.entries[param_key] = entry

            unit_lbl = ctk.CTkLabel(
                entry_row,
                text=unit if unit else "—",
                font=FontManager.get_number_font(10),
                text_color="#9E9E9E"
            )
            unit_lbl.pack(side="left")

            # Range hint label
            range_lbl = ctk.CTkLabel(
                entry_row,
                text=f"[{self._format_entry(param_key, cfg['min'])} … {self._format_entry(param_key, cfg['max'])}]",
                font=FontManager.get_number_font(9),
                text_color="#71717A"
            )
            range_lbl.pack(side="right")
            self.range_labels[param_key] = range_lbl

            row_idx += 1

        # 4. Reset Button
        self.reset_btn = ctk.CTkButton(
            self,
            text=LocalizationService.get("reset_defaults"),
            command=self.on_reset_defaults,
            font=FontManager.get_persian_font(12, "bold") if is_fa else FontManager.get_number_font(12, "bold"),
            fg_color="#374151",
            hover_color="#4B5563",
            height=30
        )
        self.reset_btn.grid(row=row_idx, column=0, pady=(12, 5), sticky="ew")

        # Derived Δy slider range must follow the current d / L / n values
        self._refresh_fringe_spacing_slider()

    def refresh_language(self):
        """Refreshes text, fonts, presets, and packing alignment on language toggle."""
        is_fa = LocalizationService.is_persian()

        self.title_label.configure(
            text=LocalizationService.get("optics_panel_title"),
            font=FontManager.get_persian_font(13, "bold") if is_fa else FontManager.get_number_font(13, "bold"),
            anchor="e" if is_fa else "w"
        )
        self.title_label.grid(sticky="e" if is_fa else "w")

        self.preset_label.configure(
            text=LocalizationService.get("presets_label"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            anchor="e" if is_fa else "w"
        )
        self.preset_label.pack(anchor="e" if is_fa else "w")

        # Update presets in dropdown
        preset_names = self._get_preset_display_names()
        self.preset_menu.configure(
            values=preset_names,
            font=FontManager.get_persian_font(11) if is_fa else FontManager.get_number_font(11),
            dropdown_font=FontManager.get_persian_font(11) if is_fa else FontManager.get_number_font(11)
        )
        self.preset_menu.set(preset_names[0])

        # Repack slider headers for proper RTL / LTR direction
        for param_key, (lbl, loc_key, h_row) in self.param_title_labels.items():
            lbl.configure(
                text=LocalizationService.get(loc_key),
                font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
            )
            # Re-pack in correct order
            lbl.pack_forget()
            v_lbl = self.value_labels[param_key]
            v_lbl.pack_forget()
            if param_key == "wavelength_nm" and hasattr(self, "color_swatch"):
                self.color_swatch.pack_forget()

            lbl.pack(side="right" if is_fa else "left", anchor="e" if is_fa else "w")
            v_lbl.pack(side="left" if is_fa else "right", anchor="w" if is_fa else "e")
            if param_key == "wavelength_nm" and hasattr(self, "color_swatch"):
                self.color_swatch.pack(side="left" if is_fa else "right", padx=(4, 4))

        self.reset_btn.configure(
            text=LocalizationService.get("reset_defaults"),
            font=FontManager.get_persian_font(12, "bold") if is_fa else FontManager.get_number_font(12, "bold")
        )

    @staticmethod
    def _format_value(key: str, value: float) -> str:
        """Formats a parameter readout with unit (header value label)."""
        unit = {"wavelength_nm": "nm", "fringe_spacing_mm": "mm",
                "slit_distance_mm": "mm", "slit_width_mm": "mm",
                "screen_distance_m": "m", "refractive_index": ""}.get(key, "")
        decimals = PARAM_DECIMALS.get(key, 2)
        return f"{value:.{decimals}f} {unit}".strip()

    @staticmethod
    def _format_entry(key: str, value: float) -> str:
        """Formats a bare number for the entry field (no unit)."""
        decimals = PARAM_DECIMALS.get(key, 2)
        return f"{value:.{decimals}f}"

    def _handle_slider_change(self, key: str, value: float):
        """Formats readout, mirrors into entry field, and triggers listener callback."""
        if self._syncing:
            return
        if key == "fringe_spacing_mm":
            self._handle_fringe_spacing_change(float(value))
            return
        self._syncing = True
        try:
            value = clamp(key, float(value))
            self._exact_values[key] = value
            self.value_labels[key].configure(text=self._format_value(key, value))

            if key in self.entries:
                entry = self.entries[key]
                entry.delete(0, "end")
                entry.insert(0, self._format_entry(key, value))
                entry.configure(border_color="#3F3F46")

            if key == "wavelength_nm" and hasattr(self, "color_swatch"):
                hex_col = ColorUtils.wavelength_to_hex(value)
                self.color_swatch.configure(fg_color=hex_col)

            if key in ("wavelength_nm", "slit_distance_mm", "screen_distance_m", "refractive_index"):
                self._refresh_fringe_spacing_slider(current_wavelength=value if key == "wavelength_nm" else None)

            self.on_param_change(key, value)
        finally:
            self._syncing = False

    def _handle_entry_change(self, key: str, live: bool):
        """
        Commits a manually typed number.

        Live keystrokes apply immediately when the text parses and is in range
        (out-of-range text waits for Enter/focus-out, when it gets clamped).
        Invalid/partial text is soft-ignored with an amber border, no error popup.
        """
        if self._syncing:
            return
        entry = self.entries.get(key)
        if entry is None:
            return
        parsed = parse_number(entry.get())
        if parsed is None:
            entry.configure(border_color="#F59E0B")
            return
        if key == "fringe_spacing_mm":
            slider = self.sliders[key]
            dyn_min = float(slider.cget("from_"))
            dyn_max = float(slider.cget("to"))
            in_range = dyn_min <= parsed <= dyn_max
        else:
            cfg = PARAM_LIMITS.get(key, {})
            in_range = (cfg.get("min", parsed) <= parsed <= cfg.get("max", parsed))
        if live and not in_range:
            entry.configure(border_color="#F59E0B")
            return
        self._syncing = True
        try:
            if key == "fringe_spacing_mm":
                clamped = clamp_range(parsed, dyn_min, dyn_max)
                d = self._exact_values["slit_distance_mm"]
                L = self._exact_values["screen_distance_m"]
                n = self._exact_values["refractive_index"]
                lam = round(clamp("wavelength_nm", wavelength_nm_from_fringe_spacing(clamped, d, L, n)), 1)
                actual_dy = fringe_spacing_mm(lam, d, L, n)
                self._exact_values["fringe_spacing_mm"] = actual_dy
                self._exact_values["wavelength_nm"] = lam

                # Sync both widgets locally: the Δy entry must keep the user's
                # in-progress text (no full refresh while typing).
                self.sliders["fringe_spacing_mm"].set(actual_dy)
                self.value_labels["fringe_spacing_mm"].configure(
                    text=self._format_value("fringe_spacing_mm", actual_dy))
                self.sliders["wavelength_nm"].set(lam)
                self.value_labels["wavelength_nm"].configure(
                    text=self._format_value("wavelength_nm", lam))
                if hasattr(self, "color_swatch"):
                    self.color_swatch.configure(fg_color=ColorUtils.wavelength_to_hex(lam))
                if not live or abs(actual_dy - parsed) > 1e-9:
                    entry.delete(0, "end")
                    entry.insert(0, self._format_entry("fringe_spacing_mm", actual_dy))
                entry.configure(border_color="#3F3F46")
                self.on_param_change("wavelength_nm", lam)
                return

            clamped = clamp(key, parsed)
            self._exact_values[key] = clamped
            self.sliders[key].set(clamped)
            self.value_labels[key].configure(text=self._format_value(key, clamped))
            if key == "wavelength_nm" and hasattr(self, "color_swatch"):
                self.color_swatch.configure(fg_color=ColorUtils.wavelength_to_hex(clamped))
            if key in ("wavelength_nm", "slit_distance_mm", "screen_distance_m", "refractive_index"):
                self._refresh_fringe_spacing_slider(current_wavelength=clamped if key == "wavelength_nm" else None)
            if not live or clamped != parsed:
                entry.delete(0, "end")
                entry.insert(0, self._format_entry(key, clamped))
            entry.configure(border_color="#3F3F46")
            self.on_param_change(key, clamped)
        finally:
            self._syncing = False

    def _handle_fringe_spacing_change(self, value: float):
        """Δy moved: derive λ = Δy·n·d/L, sync widgets, propagate as a wavelength change."""
        if self._syncing:
            return
        slider = self.sliders["fringe_spacing_mm"]
        dyn_min = float(slider.cget("from_"))
        dyn_max = float(slider.cget("to"))
        value = clamp_range(value, dyn_min, dyn_max)
        d = self._exact_values["slit_distance_mm"]
        L = self._exact_values["screen_distance_m"]
        n = self._exact_values["refractive_index"]
        lam = round(clamp("wavelength_nm", wavelength_nm_from_fringe_spacing(value, d, L, n)), 1)
        actual_dy = fringe_spacing_mm(lam, d, L, n)
        self._exact_values["fringe_spacing_mm"] = actual_dy

        self._syncing = True
        try:
            slider.set(actual_dy)
            self.value_labels["fringe_spacing_mm"].configure(
                text=self._format_value("fringe_spacing_mm", actual_dy))
            if "fringe_spacing_mm" in self.entries:
                entry = self.entries["fringe_spacing_mm"]
                entry.delete(0, "end")
                entry.insert(0, self._format_entry("fringe_spacing_mm", actual_dy))
                entry.configure(border_color="#3F3F46")
        finally:
            self._syncing = False

        # Delegate to the wavelength path: mirrors λ entry/swatch, fires
        # on_param_change("wavelength_nm", …) and re-syncs the Δy range/value.
        self._handle_slider_change("wavelength_nm", lam)

    def _refresh_fringe_spacing_slider(self, current_wavelength: Optional[float] = None):
        """Re-derives the Δy slider's range from d/L/n and its value from λ."""
        key = "fringe_spacing_mm"
        required = (key, "wavelength_nm", "slit_distance_mm", "screen_distance_m", "refractive_index")
        if not all(k in self.sliders for k in required):
            return
        d = self._exact_values["slit_distance_mm"]
        L = self._exact_values["screen_distance_m"]
        n = self._exact_values["refractive_index"]
        lam = self._exact_values["wavelength_nm"] if current_wavelength is None else current_wavelength
        dyn_min = fringe_spacing_mm(PARAM_LIMITS["wavelength_nm"]["min"], d, L, n)
        dyn_max = fringe_spacing_mm(PARAM_LIMITS["wavelength_nm"]["max"], d, L, n)
        dy = fringe_spacing_mm(lam, d, L, n)
        self._exact_values[key] = dy

        prev = self._syncing
        self._syncing = True
        try:
            slider = self.sliders[key]
            steps = max(int(round((dyn_max - dyn_min) / PARAM_LIMITS[key]["step"])), 1)
            slider.configure(from_=dyn_min, to=dyn_max, number_of_steps=steps)
            slider.set(dy)
            self.value_labels[key].configure(text=self._format_value(key, dy))
            if key in self.range_labels:
                self.range_labels[key].configure(
                    text=f"[{self._format_entry(key, dyn_min)} … {self._format_entry(key, dyn_max)}]")
            if key in self.entries:
                entry = self.entries[key]
                entry.delete(0, "end")
                entry.insert(0, self._format_entry(key, dy))
                entry.configure(border_color="#3F3F46")
        finally:
            self._syncing = prev

    def _handle_preset_select(self, chosen_label: str):
        """Applies chosen laboratory preset."""
        # Find which preset was selected
        preset_key_name = None
        for loc_k, config_k in self.PRESET_KEYS:
            if LocalizationService.get(loc_k) == chosen_label:
                preset_key_name = config_k
                break

        if not preset_key_name:
            preset_key_name = chosen_label

        preset = PRESETS.get(preset_key_name)
        if not preset:
            return

        for k in ["wavelength_nm", "slit_distance_mm", "slit_width_mm", "screen_distance_m", "refractive_index"]:
            if k in preset and k in self.sliders:
                val = preset[k]
                self.sliders[k].set(val)
                self._handle_slider_change(k, val)

        self.on_preset_selected(preset_key_name)

    def set_parameter_value(self, key: str, value: float):
        """Externally updates slider value."""
        if key in self.sliders:
            self.sliders[key].set(value)
            self._handle_slider_change(key, value)

    def get_parameter_value(self, key: str) -> float:
        """Returns the current slider value for a parameter (source of truth
        for classical settings while the control panel is hidden)."""
        if key in self.sliders:
            return float(self.sliders[key].get())
        raise KeyError(f"Unknown parameter: {key}")
