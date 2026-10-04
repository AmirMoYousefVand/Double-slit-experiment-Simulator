"""
Quantum Mechanics Control Panel.
Includes particle selector (Photon, Electron, Buckyball), kinetic energy/velocity sliders,
emission rate, simulation speed, Play/Pause/Burst/Reset buttons, and the Which-Way Observer switch.
Fully adapted for dynamic Persian RTL and English LTR layouts with Vazirmatn and Space Grotesk typography.
"""

from typing import Callable, Optional, List
import customtkinter as ctk

from physics.particle_types import ParticleCategory, PARTICLE_PRESETS
from utils.localization import LocalizationService, RLM
from utils.font_manager import FontManager
from utils.numeric_input import parse_number, clamp_range

class QuantumPanel(ctk.CTkFrame):
    """
    Control panel for quantum particle emission and observer effect interaction.
    """

    PARTICLE_KEYS = [
        ("particle_photon", ParticleCategory.PHOTON),
        ("particle_electron", ParticleCategory.ELECTRON),
        ("particle_buckyball", ParticleCategory.BUCKYBALL),
    ]

    def __init__(
        self,
        master,
        on_particle_change: Callable[[ParticleCategory], None],
        on_energy_change: Callable[[float], None],
        on_rate_change: Callable[[int], None],
        on_which_way_toggle: Callable[[bool], None],
        on_play: Callable[[], None],
        on_pause: Callable[[], None],
        on_step: Callable[[], None],
        on_reset: Callable[[], None],
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.on_particle_change = on_particle_change
        self.on_energy_change = on_energy_change
        self.on_rate_change = on_rate_change
        self.on_which_way_toggle = on_which_way_toggle
        self.on_play = on_play
        self.on_pause = on_pause
        self.on_step = on_step
        self.on_reset = on_reset

        self.current_category = ParticleCategory.ELECTRON
        self.is_running = False
        self._syncing = False

        # Active energy entry range (min, max, decimals) — reconfigured per particle
        self.energy_range = (10.0, 500.0, 1)

        self._create_widgets()

    def _get_particle_options(self) -> List[str]:
        return [LocalizationService.get(k) for k, _ in self.PARTICLE_KEYS]

    def _create_widgets(self):
        """Constructs particle controls, observer switch, and playback buttons."""
        self.grid_columnconfigure(0, weight=1)

        is_fa = LocalizationService.is_persian()

        # 1. Title
        self.title_label = ctk.CTkLabel(
            self,
            text=LocalizationService.get("quantum_panel_title"),
            font=FontManager.get_persian_font(13, "bold") if is_fa else FontManager.get_number_font(13, "bold"),
            anchor="e" if is_fa else "w"
        )
        self.title_label.grid(row=0, column=0, pady=(6, 8), sticky="e" if is_fa else "w")

        # 2. Particle Type Selector
        type_frame = ctk.CTkFrame(self, fg_color="transparent")
        type_frame.grid(row=1, column=0, pady=2, sticky="ew")

        self.particle_title_label = ctk.CTkLabel(
            type_frame,
            text=LocalizationService.get("particle_type"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            anchor="e" if is_fa else "w"
        )
        self.particle_title_label.pack(anchor="e" if is_fa else "w", pady=(0, 2))

        particle_options = self._get_particle_options()
        self.particle_menu = ctk.CTkOptionMenu(
            type_frame,
            values=particle_options,
            command=self._handle_particle_select,
            font=FontManager.get_persian_font(11) if is_fa else FontManager.get_number_font(11),
            dropdown_font=FontManager.get_persian_font(11) if is_fa else FontManager.get_number_font(11),
            height=28
        )
        self.particle_menu.set(particle_options[1])  # Default to electron
        self.particle_menu.pack(fill="x", pady=2)

        # 3. Particle Energy / Accelerating Voltage / Velocity
        self.energy_frame = ctk.CTkFrame(self, corner_radius=6)
        self.energy_frame.grid(row=2, column=0, pady=6, sticky="ew")
        self.energy_frame.grid_columnconfigure(0, weight=1)

        self.e_header = ctk.CTkFrame(self.energy_frame, fg_color="transparent")
        self.e_header.grid(row=0, column=0, padx=8, pady=(4, 2), sticky="ew")

        self.energy_title_label = ctk.CTkLabel(
            self.e_header,
            text=LocalizationService.get("particle_voltage"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )
        self.energy_title_label.pack(side="right" if is_fa else "left", anchor="e" if is_fa else "w")

        self.energy_val_label = ctk.CTkLabel(
            self.e_header,
            text="100.0 V",
            font=FontManager.get_number_font(11, "bold"),
            text_color="#00F0FF"
        )
        self.energy_val_label.pack(side="left" if is_fa else "right", anchor="w" if is_fa else "e")

        self.energy_slider = ctk.CTkSlider(
            self.energy_frame,
            from_=10.0,
            to=500.0,
            number_of_steps=98,
            command=self._handle_energy_slider
        )
        self.energy_slider.set(100.0)
        self.energy_slider.grid(row=1, column=0, padx=8, pady=(2, 2), sticky="ew")

        # Manual energy entry row
        energy_entry_row = ctk.CTkFrame(self.energy_frame, fg_color="transparent")
        energy_entry_row.grid(row=2, column=0, padx=8, pady=(0, 2), sticky="ew")

        self.energy_entry = ctk.CTkEntry(
            energy_entry_row,
            width=100,
            height=26,
            justify="center",
            font=FontManager.get_number_font(11),
            border_color="#3F3F46",
            fg_color="#18181B"
        )
        self.energy_entry.insert(0, "100.0")
        self.energy_entry.pack(side="left", padx=(0, 6))
        self.energy_entry.bind("<KeyRelease>", lambda _e: self._handle_energy_entry(live=True))
        self.energy_entry.bind("<Return>", lambda _e: self._handle_energy_entry(live=False))
        self.energy_entry.bind("<FocusOut>", lambda _e: self._handle_energy_entry(live=False))

        self.energy_unit_label = ctk.CTkLabel(
            energy_entry_row,
            text="V",
            font=FontManager.get_number_font(10),
            text_color="#9E9E9E"
        )
        self.energy_unit_label.pack(side="left")

        # De Broglie wavelength readout
        self.de_broglie_label = ctk.CTkLabel(
            self.energy_frame,
            text="λ_dB = 0.1226 nm (Matter Wave)",
            font=FontManager.get_number_font(11),
            text_color="#00E676"
        )
        self.de_broglie_label.grid(row=3, column=0, padx=8, pady=(0, 4), sticky="w")

        # 4. Emission Rate Slider
        rate_frame = ctk.CTkFrame(self, corner_radius=6)
        rate_frame.grid(row=3, column=0, pady=4, sticky="ew")
        rate_frame.grid_columnconfigure(0, weight=1)

        self.r_header = ctk.CTkFrame(rate_frame, fg_color="transparent")
        self.r_header.grid(row=0, column=0, padx=8, pady=(4, 2), sticky="ew")

        self.rate_title_label = ctk.CTkLabel(
            self.r_header,
            text=LocalizationService.get("emission_rate"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )
        self.rate_title_label.pack(side="right" if is_fa else "left", anchor="e" if is_fa else "w")

        self.rate_val_label = ctk.CTkLabel(
            self.r_header,
            text="200 parts/s",
            font=FontManager.get_number_font(11, "bold"),
            text_color="#00F0FF"
        )
        self.rate_val_label.pack(side="left" if is_fa else "right", anchor="w" if is_fa else "e")

        self.rate_slider = ctk.CTkSlider(
            rate_frame,
            from_=1,
            to=2000,
            number_of_steps=199,
            command=self._handle_rate_slider
        )
        self.rate_slider.set(200)
        self.rate_slider.grid(row=1, column=0, padx=8, pady=(2, 2), sticky="ew")

        # Manual rate entry row
        rate_entry_row = ctk.CTkFrame(rate_frame, fg_color="transparent")
        rate_entry_row.grid(row=2, column=0, padx=8, pady=(0, 6), sticky="ew")

        self.rate_entry = ctk.CTkEntry(
            rate_entry_row,
            width=100,
            height=26,
            justify="center",
            font=FontManager.get_number_font(11),
            border_color="#3F3F46",
            fg_color="#18181B"
        )
        self.rate_entry.insert(0, "200")
        self.rate_entry.pack(side="left", padx=(0, 6))
        self.rate_entry.bind("<KeyRelease>", lambda _e: self._handle_rate_entry(live=True))
        self.rate_entry.bind("<Return>", lambda _e: self._handle_rate_entry(live=False))
        self.rate_entry.bind("<FocusOut>", lambda _e: self._handle_rate_entry(live=False))

        rate_unit_label = ctk.CTkLabel(
            rate_entry_row,
            text="parts/s",
            font=FontManager.get_number_font(10),
            text_color="#9E9E9E"
        )
        rate_unit_label.pack(side="left")

        rate_range_label = ctk.CTkLabel(
            rate_entry_row,
            text="[1 … 2000]",
            font=FontManager.get_number_font(9),
            text_color="#71717A"
        )
        rate_range_label.pack(side="right")

        # 5. WHICH-WAY DETECTOR TOGGLE (Observer Effect)
        self.detector_frame = ctk.CTkFrame(self, corner_radius=8, fg_color="#1F1B24", border_width=1, border_color="#374151")
        self.detector_frame.grid(row=4, column=0, pady=8, sticky="ew")
        self.detector_frame.grid_columnconfigure(0, weight=1)

        det_header = ctk.CTkFrame(self.detector_frame, fg_color="transparent")
        det_header.grid(row=0, column=0, padx=8, pady=4, sticky="ew")

        self.det_title_label = ctk.CTkLabel(
            det_header,
            text=LocalizationService.get("which_way_title"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            text_color="#FBBF24"
        )
        self.det_title_label.pack(side="right" if is_fa else "left", anchor="e" if is_fa else "w")

        self.detector_switch = ctk.CTkSwitch(
            self.detector_frame,
            text=LocalizationService.get("which_way_off"),
            font=FontManager.get_persian_font(10) if is_fa else FontManager.get_number_font(10),
            command=self._handle_detector_toggle,
            onvalue=1,
            offvalue=0,
            progress_color="#DC2626"
        )
        self.detector_switch.grid(row=1, column=0, padx=8, pady=(2, 6), sticky="w")

        # Collapsed notice badge (hidden initially)
        self.collapse_alert = ctk.CTkLabel(
            self.detector_frame,
            text=LocalizationService.get("which_way_warning"),
            font=FontManager.get_persian_font(10, "bold") if is_fa else FontManager.get_number_font(10, "bold"),
            text_color="#F87171"
        )

        # 6. Playback Control Buttons (Grid of 4 buttons)
        btn_grid = ctk.CTkFrame(self, fg_color="transparent")
        btn_grid.grid(row=5, column=0, pady=8, sticky="ew")
        btn_grid.grid_columnconfigure((0, 1), weight=1)

        self.play_btn = ctk.CTkButton(
            btn_grid,
            text=LocalizationService.get("play"),
            command=self._toggle_play_pause,
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=30
        )
        self.play_btn.grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        self.step_btn = ctk.CTkButton(
            btn_grid,
            text=LocalizationService.get("step"),
            command=self.on_step,
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            height=30
        )
        self.step_btn.grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        self.clear_btn = ctk.CTkButton(
            btn_grid,
            text=LocalizationService.get("reset"),
            command=self.on_reset,
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            fg_color="#6B7280",
            hover_color="#4B5563",
            height=30
        )
        self.clear_btn.grid(row=1, column=0, columnspan=2, padx=2, pady=(4, 2), sticky="ew")

    def refresh_language(self):
        """Refreshes text, particle dropdown options, and fonts on language switch."""
        is_fa = LocalizationService.is_persian()

        self.title_label.configure(
            text=LocalizationService.get("quantum_panel_title"),
            font=FontManager.get_persian_font(13, "bold") if is_fa else FontManager.get_number_font(13, "bold"),
            anchor="e" if is_fa else "w"
        )
        self.title_label.grid(sticky="e" if is_fa else "w")

        self.particle_title_label.configure(
            text=LocalizationService.get("particle_type"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold"),
            anchor="e" if is_fa else "w"
        )
        self.particle_title_label.pack(anchor="e" if is_fa else "w")

        # Update particle dropdown options
        opts = self._get_particle_options()
        self.particle_menu.configure(
            values=opts,
            font=FontManager.get_persian_font(11) if is_fa else FontManager.get_number_font(11),
            dropdown_font=FontManager.get_persian_font(11) if is_fa else FontManager.get_number_font(11)
        )
        # Select current
        idx = 1
        if self.current_category == ParticleCategory.PHOTON:
            idx = 0
        elif self.current_category == ParticleCategory.BUCKYBALL:
            idx = 2
        self.particle_menu.set(opts[idx])

        # Repack Energy Title & Value
        self.energy_title_label.pack_forget()
        self.energy_val_label.pack_forget()
        self._update_energy_title()
        self.energy_title_label.pack(side="right" if is_fa else "left", anchor="e" if is_fa else "w")
        self.energy_val_label.pack(side="left" if is_fa else "right", anchor="w" if is_fa else "e")

        # Repack Rate Title & Value
        self.rate_title_label.pack_forget()
        self.rate_val_label.pack_forget()
        self.rate_title_label.configure(
            text=LocalizationService.get("emission_rate"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )
        self.rate_title_label.pack(side="right" if is_fa else "left", anchor="e" if is_fa else "w")
        self.rate_val_label.pack(side="left" if is_fa else "right", anchor="w" if is_fa else "e")

        self.det_title_label.configure(
            text=LocalizationService.get("which_way_title"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )

        active = bool(self.detector_switch.get())
        switch_txt = LocalizationService.get("which_way_on") if active else LocalizationService.get("which_way_off")
        self.detector_switch.configure(
            text=switch_txt,
            font=FontManager.get_persian_font(10) if is_fa else FontManager.get_number_font(10)
        )
        self.collapse_alert.configure(
            text=LocalizationService.get("which_way_warning"),
            font=FontManager.get_persian_font(10, "bold") if is_fa else FontManager.get_number_font(10, "bold")
        )

        self.play_btn.configure(
            text=LocalizationService.get("pause") if self.is_running else LocalizationService.get("play"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )
        self.step_btn.configure(
            text=LocalizationService.get("step"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )
        self.clear_btn.configure(
            text=LocalizationService.get("reset"),
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )

    def _update_energy_title(self):
        is_fa = LocalizationService.is_persian()
        if self.current_category == ParticleCategory.PHOTON:
            t = LocalizationService.get("particle_energy")
        elif self.current_category == ParticleCategory.ELECTRON:
            t = LocalizationService.get("particle_voltage")
        else:
            t = LocalizationService.get("particle_velocity")

        self.energy_title_label.configure(
            text=t,
            font=FontManager.get_persian_font(11, "bold") if is_fa else FontManager.get_number_font(11, "bold")
        )

    def _toggle_play_pause(self):
        """Toggles between Play and Pause states."""
        self.is_running = not self.is_running
        if self.is_running:
            self.play_btn.configure(
                text=LocalizationService.get("pause"),
                fg_color="#F59E0B",
                hover_color="#D97706"
            )
            self.on_play()
        else:
            self.play_btn.configure(
                text=LocalizationService.get("play"),
                fg_color="#10B981",
                hover_color="#059669"
            )
            self.on_pause()

    def set_paused_state(self):
        """Externally reset play button to paused."""
        self.is_running = False
        self.play_btn.configure(
            text=LocalizationService.get("play"),
            fg_color="#10B981",
            hover_color="#059669"
        )

    def _handle_particle_select(self, chosen_label: str):
        """Adapts slider ranges for selected particle."""
        cat = ParticleCategory.ELECTRON
        for loc_k, p_cat in self.PARTICLE_KEYS:
            if LocalizationService.get(loc_k) == chosen_label:
                cat = p_cat
                break

        self.current_category = cat
        self._update_energy_title()

        if cat == ParticleCategory.PHOTON:
            self.energy_range = (1.5, 3.5, 2)
            self.energy_unit_label.configure(text="eV")
            self.energy_slider.configure(from_=1.5, to=3.5, number_of_steps=40)
            self.energy_slider.set(1.96)
            self._handle_energy_slider(1.96)
        elif cat == ParticleCategory.ELECTRON:
            self.energy_range = (10.0, 500.0, 1)
            self.energy_unit_label.configure(text="V")
            self.energy_slider.configure(from_=10.0, to=500.0, number_of_steps=98)
            self.energy_slider.set(100.0)
            self._handle_energy_slider(100.0)
        else:
            self.energy_range = (50.0, 500.0, 1)
            self.energy_unit_label.configure(text="m/s")
            self.energy_slider.configure(from_=50.0, to=500.0, number_of_steps=90)
            self.energy_slider.set(200.0)
            self._handle_energy_slider(200.0)

        self.on_particle_change(self.current_category)

    def _handle_energy_slider(self, val: float):
        """Updates readout, mirrors into entry field, and triggers callback."""
        if self._syncing:
            return
        self._syncing = True
        try:
            lo, hi, _dec = self.energy_range
            val = clamp_range(float(val), lo, hi)
            if self.current_category == ParticleCategory.PHOTON:
                self.energy_val_label.configure(text=f"{val:.2f} eV")
                wl_nm = 1239.84 / val
                self.de_broglie_label.configure(text=f"λ = {wl_nm:.1f} nm (Light Quantum)")
            elif self.current_category == ParticleCategory.ELECTRON:
                self.energy_val_label.configure(text=f"{val:.1f} V")
                wl_nm = 1.22639 / (val ** 0.5)
                self.de_broglie_label.configure(text=f"λ_dB = {wl_nm:.4f} nm (Matter Wave)")
            else:
                self.energy_val_label.configure(text=f"{val:.1f} m/s")
                from config import PLANCK_CONSTANT, BUCKYBALL_MASS
                wl_pm = (PLANCK_CONSTANT / (BUCKYBALL_MASS * val)) * 1e12
                self.de_broglie_label.configure(text=f"λ_dB = {wl_pm:.2f} pm (C₆₀ Molecule)")

            self._set_entry_text(self.energy_entry, val, _dec)
            self.energy_entry.configure(border_color="#3F3F46")
            self.on_energy_change(val)
        finally:
            self._syncing = False

    @staticmethod
    def _set_entry_text(entry: ctk.CTkEntry, value: float, decimals: int):
        entry.delete(0, "end")
        entry.insert(0, f"{value:.{decimals}f}")

    def _handle_energy_entry(self, live: bool):
        """Commits a manually typed energy/velocity value."""
        if self._syncing:
            return
        parsed = parse_number(self.energy_entry.get())
        if parsed is None:
            self.energy_entry.configure(border_color="#F59E0B")
            return
        lo, hi, dec = self.energy_range
        in_range = lo <= parsed <= hi
        if live and not in_range:
            self.energy_entry.configure(border_color="#F59E0B")
            return
        self._syncing = True
        try:
            clamped = clamp_range(parsed, lo, hi)
            self.energy_slider.set(clamped)
            self._set_entry_text(self.energy_entry, clamped, dec)
            self.energy_entry.configure(border_color="#3F3F46")
            if self.current_category == ParticleCategory.PHOTON:
                self.energy_val_label.configure(text=f"{clamped:.2f} eV")
                wl_nm = 1239.84 / clamped
                self.de_broglie_label.configure(text=f"λ = {wl_nm:.1f} nm (Light Quantum)")
            elif self.current_category == ParticleCategory.ELECTRON:
                self.energy_val_label.configure(text=f"{clamped:.1f} V")
                wl_nm = 1.22639 / (clamped ** 0.5)
                self.de_broglie_label.configure(text=f"λ_dB = {wl_nm:.4f} nm (Matter Wave)")
            else:
                self.energy_val_label.configure(text=f"{clamped:.1f} m/s")
                from config import PLANCK_CONSTANT, BUCKYBALL_MASS
                wl_pm = (PLANCK_CONSTANT / (BUCKYBALL_MASS * clamped)) * 1e12
                self.de_broglie_label.configure(text=f"λ_dB = {wl_pm:.2f} pm (C₆₀ Molecule)")
            self.on_energy_change(clamped)
        finally:
            self._syncing = False

    def _handle_rate_slider(self, val: float):
        if self._syncing:
            return
        self._syncing = True
        try:
            int_rate = int(clamp_range(float(val), 1, 2000))
            self.rate_val_label.configure(text=f"{int_rate} parts/s")
            self.rate_entry.delete(0, "end")
            self.rate_entry.insert(0, str(int_rate))
            self.rate_entry.configure(border_color="#3F3F46")
            self.on_rate_change(int_rate)
        finally:
            self._syncing = False

    def _handle_rate_entry(self, live: bool):
        """Commits a manually typed emission rate."""
        if self._syncing:
            return
        parsed = parse_number(self.rate_entry.get())
        if parsed is None:
            self.rate_entry.configure(border_color="#F59E0B")
            return
        if live and not (1 <= parsed <= 2000):
            self.rate_entry.configure(border_color="#F59E0B")
            return
        self._syncing = True
        try:
            int_rate = int(clamp_range(parsed, 1, 2000))
            self.rate_slider.set(int_rate)
            self.rate_entry.delete(0, "end")
            self.rate_entry.insert(0, str(int_rate))
            self.rate_entry.configure(border_color="#3F3F46")
            self.rate_val_label.configure(text=f"{int_rate} parts/s")
            self.on_rate_change(int_rate)
        finally:
            self._syncing = False

    def _handle_detector_toggle(self):
        active = bool(self.detector_switch.get())
        if active:
            self.detector_switch.configure(text=LocalizationService.get("which_way_on"))
            self.detector_frame.configure(border_color="#DC2626", fg_color="#361014")
            self.collapse_alert.grid(row=2, column=0, padx=8, pady=(0, 6), sticky="w")
        else:
            self.detector_switch.configure(text=LocalizationService.get("which_way_off"))
            self.detector_frame.configure(border_color="#374151", fg_color="#1F1B24")
            self.collapse_alert.grid_forget()

        self.on_which_way_toggle(active)
