"""
2D Apparatus Setup & Wave Propagation Schematic View.
Draws interactive optical laboratory apparatus:
- Dynamic spectral laser / particle colors matching current wavelength
- Animated Huygens expanding wavelets with realistic opacity falloff
- Pulsating luminous impact spot at Point P scaling with local intensity I(y)
- Live illuminated interference fringe ribbon along the detector screen
- Geometric path difference right-triangle construction (Δr = d · sin θ)
- Full bilingual labels and Which-Way detector indicators
"""

import tkinter as tk
import math
from typing import Optional, Tuple
import customtkinter as ctk

from utils.localization import LocalizationService, RLM
from utils.font_manager import FontManager
from utils.color_utils import ColorUtils
from physics.particle_types import ParticleCategory

class SetupSchematicView(ctk.CTkFrame):
    """
    Renders 2D physical apparatus diagram and Huygens wavelet interference animation.
    Allows user to drag an inspection point on the screen to observe path difference Δr in real time.
    """

    def __init__(self, master, width: int = 700, height: int = 340, **kwargs):
        super().__init__(master, **kwargs)
        self.width = width
        self.height = height

        # Physical parameters
        self.wavelength_nm = 632.8
        self.slit_distance_mm = 0.25
        self.slit_width_mm = 0.04
        self.screen_distance_m = 1.0
        self.which_way_active = False
        self.particle_category = ParticleCategory.PHOTON
        self.is_quantum = False

        # Animation state for Huygens wavelets
        self.wave_phase = 0.0
        self.anim_running = True

        # Interactive inspection point Y offset on screen (in canvas pixels from center)
        self.target_y_offset = 0.0

        self._create_widgets()
        self._start_wave_animation()

    def _create_widgets(self):
        """Creates the Tkinter canvas and info overlay."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        is_fa = LocalizationService.is_persian()

        # Header status
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=10, pady=(6, 2), sticky="ew")

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=LocalizationService.get("tab_schematic"),
            font=FontManager.get_persian_font(13, "bold") if is_fa else FontManager.get_number_font(13, "bold")
        )
        self.title_label.pack(side="right" if is_fa else "left", padx=5)

        self.path_diff_label = ctk.CTkLabel(
            self.header_frame,
            text="Δr = 0.00 nm (Phase: 0.0°)",
            font=FontManager.get_number_font(11, "bold"),
            text_color="#00F0FF"
        )
        self.path_diff_label.pack(side="left" if is_fa else "right", padx=10)

        # Canvas
        self.canvas = tk.Canvas(
            self,
            width=self.width,
            height=self.height,
            bg="#0B0B0F",
            highlightthickness=1,
            highlightbackground="#2A2A2A"
        )
        self.canvas.grid(row=1, column=0, padx=10, pady=(2, 6), sticky="nsew")

        # Interactive dragging of inspection point
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<Button-1>", self._on_canvas_drag)
        self.canvas.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        if event.width > 200 and event.height > 150:
            self.width = event.width
            self.height = event.height

    def _on_canvas_drag(self, event):
        """Move inspection point on screen when user clicks or drags."""
        screen_x = self.width - 50
        if event.x > screen_x - 120:
            mid_y = self.height / 2.0
            self.target_y_offset = float(event.y - mid_y)
            self._redraw_schematic()

    def update_optical_params(
        self,
        wavelength_nm: float,
        slit_distance_mm: float,
        slit_width_mm: float,
        screen_distance_m: float,
        which_way_active: bool,
        particle_category: ParticleCategory = ParticleCategory.PHOTON,
        is_quantum: bool = False
    ):
        """Updates parameters and redraws."""
        self.wavelength_nm = wavelength_nm
        self.slit_distance_mm = slit_distance_mm
        self.slit_width_mm = slit_width_mm
        self.screen_distance_m = screen_distance_m
        self.which_way_active = which_way_active
        self.particle_category = particle_category
        self.is_quantum = is_quantum
        self._redraw_schematic()

    def refresh_language(self):
        """Updates title and fonts on language switch."""
        is_fa = LocalizationService.is_persian()
        self.title_label.configure(
            text=LocalizationService.get("tab_schematic"),
            font=FontManager.get_persian_font(13, "bold") if is_fa else FontManager.get_number_font(13, "bold")
        )
        self.title_label.pack(side="right" if is_fa else "left", padx=5)
        self.path_diff_label.pack(side="left" if is_fa else "right", padx=10)
        self._redraw_schematic()

    def _start_wave_animation(self):
        """Advances wave phase for expanding wavefronts."""
        if self.anim_running:
            self.wave_phase = (self.wave_phase + 1.2) % 32.0
            self._redraw_schematic()
            self.after(50, self._start_wave_animation)

    def _redraw_schematic(self):
        """Draws the complete laboratory setup with geometric annotations."""
        self.canvas.delete("all")

        mid_y = self.height / 2.0
        is_fa = LocalizationService.is_persian()

        # Dynamic Spectral Colors
        if self.is_quantum:
            wave_hex = ColorUtils.get_particle_hex(self.particle_category, self.wavelength_nm)
            base_rgb = ColorUtils.get_particle_color(self.particle_category, self.wavelength_nm)
        else:
            wave_hex = ColorUtils.wavelength_to_hex(self.wavelength_nm)
            base_rgb = ColorUtils.wavelength_to_rgb(self.wavelength_nm)

        # Apparatus geometric X coordinates
        x_source = 50
        x_barrier = self.width * 0.38
        x_screen = self.width - 50

        # Slit positions in canvas coords
        slit_spacing_pixels = max(min(self.slit_distance_mm * 160.0, self.height * 0.4), 18.0)
        y_slit1 = mid_y - slit_spacing_pixels / 2.0
        y_slit2 = mid_y + slit_spacing_pixels / 2.0
        slit_w_pixels = max(self.slit_width_mm * 120.0, 4.0)

        # ----------------------------------------------------------------------
        # 1. Coherent Source (Laser / Particle Gun)
        # ----------------------------------------------------------------------
        self.canvas.create_rectangle(
            x_source - 35, mid_y - 25, x_source, mid_y + 25,
            fill="#1E293B", outline=wave_hex, width=2
        )
        LocalizationService.render_canvas_persian(
            self.canvas,
            x_source - 18, mid_y,
            text=LocalizationService.get("sch_source"),
            fill="#E0E0E0",
            font=(FontManager.PERSIAN_FAMILY if is_fa else "Arial", 8, "bold")
        )

        # Plane waves from source to barrier in spectral color
        num_plane_waves = 5
        plane_step = (x_barrier - x_source) / num_plane_waves
        for i in range(num_plane_waves):
            px = x_source + ((i * plane_step + self.wave_phase) % (x_barrier - x_source))
            self.canvas.create_line(
                px, mid_y - 55, px, mid_y + 55,
                fill=wave_hex, width=1.5, dash=(3, 3)
            )

        # ----------------------------------------------------------------------
        # 2. Slit Barrier (Opaque with two apertures)
        # ----------------------------------------------------------------------
        barrier_thick = 8
        barrier_color = "#334155"

        # Top section
        self.canvas.create_rectangle(
            x_barrier - barrier_thick / 2, 20,
            x_barrier + barrier_thick / 2, y_slit1 - slit_w_pixels / 2,
            fill=barrier_color, outline="#475569"
        )
        # Middle section between slits
        self.canvas.create_rectangle(
            x_barrier - barrier_thick / 2, y_slit1 + slit_w_pixels / 2,
            x_barrier + barrier_thick / 2, y_slit2 - slit_w_pixels / 2,
            fill=barrier_color, outline="#475569"
        )
        # Bottom section
        self.canvas.create_rectangle(
            x_barrier - barrier_thick / 2, y_slit2 + slit_w_pixels / 2,
            x_barrier + barrier_thick / 2, self.height - 20,
            fill=barrier_color, outline="#475569"
        )

        # Slit Labels (S1, S2)
        self.canvas.create_text(x_barrier - 16, y_slit1, text="S₁", fill="#00E676", font=("Consolas", 10, "bold"))
        self.canvas.create_text(x_barrier - 16, y_slit2, text="S₂", fill="#00E676", font=("Consolas", 10, "bold"))

        # Dimension d bracket
        self.canvas.create_line(
            x_barrier - 8, y_slit1, x_barrier - 8, y_slit2,
            fill="#FFB300", width=1, arrow=tk.BOTH
        )
        self.canvas.create_text(
            x_barrier - 26, mid_y,
            text=f"d={self.slit_distance_mm:.2f}mm",
            fill="#FFB300", font=("Consolas", 8)
        )

        # ----------------------------------------------------------------------
        # 3. Expanding Wavelets in Spectral Color (or Collapsed if Which-Way is ON)
        # ----------------------------------------------------------------------
        num_rings = 7
        ring_spacing = 26.0

        if not self.which_way_active:
            # Coherent expanding circular wavelets from BOTH slits
            for r_idx in range(1, num_rings + 1):
                radius = (r_idx * ring_spacing + self.wave_phase) % (ring_spacing * num_rings)
                alpha_frac = max(0.15, 1.0 - (radius / (ring_spacing * num_rings)))
                # Fade color towards background
                r_c = int(base_rgb[0] * alpha_frac)
                g_c = int(base_rgb[1] * alpha_frac)
                b_c = int(base_rgb[2] * alpha_frac)
                arc_col = f"#{r_c:02x}{g_c:02x}{b_c:02x}"

                # Upper slit wavelets
                self.canvas.create_arc(
                    x_barrier - radius, y_slit1 - radius,
                    x_barrier + radius, y_slit1 + radius,
                    start=-80, extent=160,
                    style=tk.ARC, outline=arc_col, width=1.5
                )
                # Lower slit wavelets
                self.canvas.create_arc(
                    x_barrier - radius, y_slit2 - radius,
                    x_barrier + radius, y_slit2 + radius,
                    start=-80, extent=160,
                    style=tk.ARC, outline=arc_col, width=1.5
                )
        else:
            # Observer Active: Single slit incoherent wavelets
            for r_idx in range(1, num_rings + 1):
                radius = (r_idx * ring_spacing + self.wave_phase) % (ring_spacing * num_rings)
                alpha_frac = max(0.15, 1.0 - (radius / (ring_spacing * num_rings)))
                r_c = int(base_rgb[0] * alpha_frac * 0.7)
                g_c = int(base_rgb[1] * alpha_frac * 0.7)
                b_c = int(base_rgb[2] * alpha_frac * 0.7)
                arc_col = f"#{r_c:02x}{g_c:02x}{b_c:02x}"

                self.canvas.create_arc(
                    x_barrier - radius, y_slit1 - radius,
                    x_barrier + radius, y_slit1 + radius,
                    start=-80, extent=160,
                    style=tk.ARC, outline=arc_col, width=1, dash=(4, 4)
                )

        # ----------------------------------------------------------------------
        # 4. Detector Screen with Live Interference Fringe Ribbon
        # ----------------------------------------------------------------------
        screen_top = 22
        screen_bottom = self.height - 22

        # Draw physical screen background
        self.canvas.create_rectangle(
            x_screen - 6, screen_top, x_screen + 6, screen_bottom,
            fill="#0F172A", outline="#475569", width=2
        )
        LocalizationService.render_canvas_persian(
            self.canvas,
            x_screen + 24, mid_y,
            text=LocalizationService.get("sch_screen"),
            fill="#94A3B8",
            font=(FontManager.PERSIAN_FAMILY if is_fa else "Arial", 8, "bold")
        )

        # Scale factor: convert canvas pixel offset to physical screen coordinate in meters
        scale_y_m_per_pixel = (self.wavelength_nm * 1e-9 * self.screen_distance_m) / (self.slit_distance_mm * 1e-3 * 18.0)

        # Draw live illuminated interference fringe ribbon directly along the screen
        ribbon_steps = int(screen_bottom - screen_top)
        d_m = self.slit_distance_mm * 1e-3
        a_m = max(self.slit_width_mm * 1e-3, 1e-6)
        wl_m = self.wavelength_nm * 1e-9
        L_m = self.screen_distance_m

        for py_idx in range(screen_top, screen_bottom, 3):
            phys_y = (py_idx - mid_y) * scale_y_m_per_pixel
            sin_t = phys_y / math.sqrt(phys_y**2 + L_m**2)

            if not self.which_way_active:
                beta = (math.pi * a_m * sin_t) / wl_m
                sinc_sq = (math.sin(beta) / beta)**2 if abs(beta) > 1e-6 else 1.0
                alpha = (math.pi * d_m * sin_t) / wl_m
                int_local = sinc_sq * (math.cos(alpha)**2)
            else:
                # Sum of two single slits
                sin_t1 = (phys_y - d_m/2.0) / math.sqrt((phys_y - d_m/2.0)**2 + L_m**2)
                sin_t2 = (phys_y + d_m/2.0) / math.sqrt((phys_y + d_m/2.0)**2 + L_m**2)
                b1 = (math.pi * a_m * sin_t1) / wl_m
                b2 = (math.pi * a_m * sin_t2) / wl_m
                s1 = (math.sin(b1)/b1)**2 if abs(b1) > 1e-6 else 1.0
                s2 = (math.sin(b2)/b2)**2 if abs(b2) > 1e-6 else 1.0
                int_local = 0.5 * s1 + 0.5 * s2

            int_local = min(max(int_local, 0.0), 1.0)
            r_pix = int(base_rgb[0] * int_local)
            g_pix = int(base_rgb[1] * int_local)
            b_pix = int(base_rgb[2] * int_local)
            fringe_col = f"#{r_pix:02x}{g_pix:02x}{b_pix:02x}"

            self.canvas.create_line(
                x_screen - 4, py_idx, x_screen + 4, py_idx,
                fill=fringe_col, width=3
            )

        # Dimension L bracket
        y_dim_L = self.height - 14
        self.canvas.create_line(
            x_barrier, y_dim_L, x_screen, y_dim_L,
            fill="#94A3B8", width=1, arrow=tk.BOTH
        )
        self.canvas.create_text(
            (x_barrier + x_screen) / 2.0, y_dim_L - 8,
            text=f"L = {self.screen_distance_m:.2f} m",
            fill="#94A3B8", font=("Consolas", 8)
        )

        # ----------------------------------------------------------------------
        # 5. Inspection Point P on Screen & Pulsating Luminous Impact Spot
        # ----------------------------------------------------------------------
        p_x = x_screen
        p_y = mid_y + self.target_y_offset
        p_y = max(min(p_y, screen_bottom - 2), screen_top + 2)

        physical_y_m = (p_y - mid_y) * scale_y_m_per_pixel
        sin_p = physical_y_m / math.sqrt(physical_y_m**2 + L_m**2)

        # Compute Point P intensity
        beta_p = (math.pi * a_m * sin_p) / wl_m
        sinc_p = (math.sin(beta_p) / beta_p)**2 if abs(beta_p) > 1e-6 else 1.0
        alpha_p = (math.pi * d_m * sin_p) / wl_m
        if not self.which_way_active:
            i_p = sinc_p * (math.cos(alpha_p)**2)
        else:
            i_p = 0.5 * sinc_p
        i_p = min(max(i_p, 0.0), 1.0)

        # Ray r1 (from Slit 1 to P)
        self.canvas.create_line(
            x_barrier, y_slit1, p_x, p_y,
            fill="#00E676", width=2, dash=(6, 2)
        )
        # Ray r2 (from Slit 2 to P)
        self.canvas.create_line(
            x_barrier, y_slit2, p_x, p_y,
            fill="#FFD600", width=2, dash=(6, 2)
        )

        # Path Lengths
        r1 = math.sqrt(L_m ** 2 + (physical_y_m - d_m / 2.0) ** 2)
        r2 = math.sqrt(L_m ** 2 + (physical_y_m + d_m / 2.0) ** 2)
        delta_r_m = abs(r2 - r1)
        delta_r_nm = delta_r_m * 1e9

        phase_rad = (2.0 * math.pi * delta_r_m) / wl_m
        phase_deg = math.degrees(phase_rad) % 360.0

        # --- Dynamic Pulsating Luminous Impact Spot ---
        pulse_osc = 0.75 + 0.25 * math.sin(self.wave_phase * 0.4)
        base_spot_radius = max(3.0, 10.0 * i_p * pulse_osc)

        if i_p > 0.3:
            # Outer radiant halo in laser color
            self.canvas.create_oval(
                p_x - base_spot_radius * 1.6, p_y - base_spot_radius * 1.6,
                p_x + base_spot_radius * 1.6, p_y + base_spot_radius * 1.6,
                outline=wave_hex, width=1
            )
            # Radiant core
            self.canvas.create_oval(
                p_x - base_spot_radius, p_y - base_spot_radius,
                p_x + base_spot_radius, p_y + base_spot_radius,
                fill=wave_hex, outline="#FFFFFF", width=1.5
            )
            # White hot center dot
            self.canvas.create_oval(
                p_x - 2, p_y - 2, p_x + 2, p_y + 2,
                fill="#FFFFFF", outline=""
            )
        else:
            # Dim destructive cancellation spot
            self.canvas.create_oval(
                p_x - 3, p_y - 3, p_x + 3, p_y + 3,
                fill="#374151", outline="#6B7280", width=1
            )

        # Intensity percentage readout at Point P
        self.canvas.create_text(
            p_x - 28, p_y - 12,
            text=f"P: {i_p*100.0:.0f}%",
            fill="#FFFFFF" if i_p > 0.5 else "#94A3B8",
            font=("Consolas", 8, "bold")
        )

        # ----------------------------------------------------------------------
        # 6. Geometric Path Difference Δr Right-Triangle Projection
        # ----------------------------------------------------------------------
        if abs(y_slit2 - y_slit1) > 10 and abs(p_y - y_slit2) > 5:
            # Direction vector of Ray 2: S2 -> P
            vx = p_x - x_barrier
            vy = p_y - y_slit2
            v_len = math.sqrt(vx**2 + vy**2)
            if v_len > 1e-4:
                ux = vx / v_len
                uy = vy / v_len

                # Vector from S2 to S1: (0, y_slit1 - y_slit2)
                wx = 0.0
                wy = y_slit1 - y_slit2

                # Projection of w onto u
                proj = wx * ux + wy * uy
                hx = x_barrier + proj * ux
                hy = y_slit2 + proj * uy

                # Drop perpendicular from S1 to Ray 2 at H
                self.canvas.create_line(
                    x_barrier, y_slit1, hx, hy,
                    fill="#38BDF8", width=1, dash=(2, 2)
                )

                # Segment S2-H is the physical Delta r!
                self.canvas.create_line(
                    x_barrier, y_slit2, hx, hy,
                    fill="#00F0FF", width=3
                )
                self.canvas.create_text(
                    (x_barrier + hx)/2.0 - 10, (y_slit2 + hy)/2.0,
                    text="Δr", fill="#00F0FF", font=("Consolas", 8, "bold")
                )

        # Update Path Difference Telemetry Header
        order_m = delta_r_m / wl_m
        nearest_m = round(order_m)
        is_constructive = abs(order_m - nearest_m) < 0.08
        is_destructive = abs(order_m - (nearest_m + 0.5)) < 0.08

        condition_text = ""
        if is_constructive:
            condition_text = f" [Max: m={nearest_m}]" if not is_fa else f" [بیشینه مرتبه m={nearest_m}]"
        elif is_destructive:
            condition_text = " [Min: Dark]" if not is_fa else " [کمینه تاریک]"

        self.path_diff_label.configure(
            text=f"Δr = {delta_r_nm:.1f} nm | Phase: {phase_deg:.1f}°{condition_text}"
        )

        # ----------------------------------------------------------------------
        # 7. Which-Way Detector Graphic (Observer Effect)
        # ----------------------------------------------------------------------
        if self.which_way_active:
            det_color = "#FF1744"
            for y_s, name in [(y_slit1, "D₁"), (y_slit2, "D₂")]:
                self.canvas.create_rectangle(
                    x_barrier + 6, y_s - 8, x_barrier + 24, y_s + 8,
                    fill="#311B92", outline=det_color, width=2
                )
                self.canvas.create_text(
                    x_barrier + 15, y_s,
                    text=name, fill="#FFFFFF", font=("Consolas", 8, "bold")
                )
                self.canvas.create_line(
                    x_barrier + 24, y_s, x_barrier + 48, y_s,
                    fill=det_color, width=2, arrow=tk.LAST
                )

            obs_txt = LocalizationService.get("sch_observer_active")
            self.canvas.create_rectangle(
                self.width * 0.35, 10, self.width * 0.90, 34,
                fill="#450A0A", outline="#DC2626", width=2
            )
            LocalizationService.render_canvas_persian(
                self.canvas,
                self.width * 0.625, 22,
                text=obs_txt,
                fill="#FCA5A5",
                font=(FontManager.PERSIAN_FAMILY if is_fa else "Arial", 8, "bold")
            )
