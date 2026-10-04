"""
Interactive 3D Apparatus Setup View.
Renders the complete physical experiment in 3D:
- 3D Laser / Particle Gun (Electron gun, Laser cavity, or Molecular oven)
- 3D Double-slit barrier plate with apertures (d, a)
- 3D Detector screen at distance L with the 2D fringe pattern mapped onto its surface
- 3D Ray paths (r1, r2)
- Which-Way observer detector sensors with active laser probe beams
- Interactive mouse wheel zoom (mpl_connect scroll_event)
- Toolbar controls: Zoom (+/-), Manual Rotation (◀, ▲, ▼, ▶), Telemetry badge, and Camera Presets
"""

from typing import Tuple, Optional, Dict, Any, List
import customtkinter as ctk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from utils.localization import LocalizationService, RLM
from utils.font_manager import FontManager
from utils.color_utils import ColorUtils
from physics.particle_types import ParticleCategory

class Setup3DView(ctk.CTkFrame):
    """
    Embeds interactive 3D laboratory scene with rotatable & zoomable Matplotlib 3D projection.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Default physical parameters
        self.wavelength_nm = 632.8
        self.slit_distance_mm = 0.25
        self.slit_width_mm = 0.04
        self.screen_distance_m = 1.0
        self.which_way_active = False
        self.is_quantum = False
        self.particle_category = ParticleCategory.PHOTON

        # Zoom and camera tracking
        self.zoom_level = 1.0
        self.default_elev = 20.0
        self.default_azim = -60.0

        # Base 3D limits
        self.base_xlim = (-0.35, 1.1)
        self.base_ylim = (-20.0, 20.0)
        self.base_zlim = (-15.0, 15.0)

        self._create_widgets()

    def _create_widgets(self):
        """Constructs camera angle toolbar and 3D Matplotlib canvas."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        is_fa = LocalizationService.is_persian()

        # ----------------------------------------------------------------------
        # 1. Top Camera Angle & Navigation Control Toolbar
        # ----------------------------------------------------------------------
        self.toolbar = ctk.CTkFrame(self, fg_color="#18181B", corner_radius=6)
        self.toolbar.grid(row=0, column=0, padx=8, pady=(4, 2), sticky="ew")

        # Top row of toolbar: Presets
        row1 = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        row1.pack(fill="x", padx=6, pady=(4, 2))

        self.toolbar_title = ctk.CTkLabel(
            row1,
            text=LocalizationService.get("tab_3d_setup"),
            font=FontManager.get_persian_font(12, "bold") if is_fa else FontManager.get_number_font(12, "bold")
        )
        self.toolbar_title.pack(side="right" if is_fa else "left", padx=6)

        # Camera preset buttons
        btn_specs = [
            ("cam_perspective", self._set_cam_perspective),
            ("cam_top", self._set_cam_top),
            ("cam_side", self._set_cam_side),
            ("cam_front", self._set_cam_front),
            ("cam_reset", self._set_cam_reset),
        ]

        self.cam_buttons = []
        btn_pack_side = "left" if is_fa else "right"
        for key, cmd in btn_specs:
            btn = ctk.CTkButton(
                row1,
                text=LocalizationService.get(key),
                command=cmd,
                font=FontManager.get_persian_font(10, "bold") if is_fa else FontManager.get_number_font(10, "bold"),
                width=75,
                height=24,
                fg_color="#27272A",
                hover_color="#3F3F46"
            )
            btn.pack(side=btn_pack_side, padx=2)
            self.cam_buttons.append((key, btn))

        # Bottom row of toolbar: Zoom buttons, manual rotation buttons, and telemetry
        row2 = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        row2.pack(fill="x", padx=6, pady=(2, 4))

        # Zoom buttons
        self.btn_zoom_in = ctk.CTkButton(
            row2, text="+ Zoom", width=62, height=22,
            font=FontManager.get_number_font(10, "bold"),
            fg_color="#0284C7", hover_color="#0369A1",
            command=lambda: self._apply_zoom_factor(1.20)
        )
        self.btn_zoom_in.pack(side="left", padx=2)

        self.btn_zoom_out = ctk.CTkButton(
            row2, text="- Zoom", width=62, height=22,
            font=FontManager.get_number_font(10, "bold"),
            fg_color="#0284C7", hover_color="#0369A1",
            command=lambda: self._apply_zoom_factor(1.0 / 1.20)
        )
        self.btn_zoom_out.pack(side="left", padx=2)

        # Manual Rotation buttons: ◀, ▲, ▼, ▶
        rot_specs = [
            ("◀", lambda: self._rotate_camera(azim_delta=-10)),
            ("▲", lambda: self._rotate_camera(elev_delta=+5)),
            ("▼", lambda: self._rotate_camera(elev_delta=-5)),
            ("▶", lambda: self._rotate_camera(azim_delta=+10)),
        ]
        for symbol, cmd in rot_specs:
            btn = ctk.CTkButton(
                row2, text=symbol, width=28, height=22,
                font=FontManager.get_number_font(11, "bold"),
                fg_color="#374151", hover_color="#4B5563",
                command=cmd
            )
            btn.pack(side="left", padx=1)

        # Camera Telemetry Badge
        self.telemetry_label = ctk.CTkLabel(
            row2,
            text="Elev: 20° | Azim: -60° | Zoom: 1.0x",
            font=FontManager.get_number_font(10),
            text_color="#94A3B8"
        )
        self.telemetry_label.pack(side="right", padx=8)

        # ----------------------------------------------------------------------
        # 2. Matplotlib 3D Canvas
        # ----------------------------------------------------------------------
        self.fig = Figure(figsize=(7, 4.2), dpi=100, facecolor="#101012")
        self.ax = self.fig.add_subplot(111, projection="3d")
        self.ax.set_facecolor("#121214")

        # Styling
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        self.ax.xaxis.pane.set_edgecolor("#2A2A2E")
        self.ax.yaxis.pane.set_edgecolor("#2A2A2E")
        self.ax.zaxis.pane.set_edgecolor("#2A2A2E")
        self.ax.grid(True, linestyle=":", alpha=0.3, color="#404040")

        self.ax.tick_params(colors="#888888", labelsize=8)
        self.ax.set_xlabel("X (m) [Axis]", color="#AAAAAA", fontsize=8, labelpad=2)
        self.ax.set_ylabel("Y (mm) [Slits]", color="#AAAAAA", fontsize=8, labelpad=2)
        self.ax.set_zlabel("Z (mm) [Height]", color="#AAAAAA", fontsize=8, labelpad=2)

        self.ax.view_init(elev=self.default_elev, azim=self.default_azim)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=1, column=0, sticky="nsew", padx=8, pady=(2, 6))

        # Connect interactive mouse scroll wheel zoom
        self.canvas.mpl_connect("scroll_event", self._on_scroll_zoom)

    # ==========================================================================
    # Interactive Zoom & Camera Navigation
    # ==========================================================================
    def _on_scroll_zoom(self, event):
        """Mouse wheel scroll event handler for continuous zooming."""
        if event.inaxes != self.ax:
            return
        step = getattr(event, "step", 0)
        btn = getattr(event, "button", None)

        if btn == "up" or step > 0:
            self._apply_zoom_factor(1.15)
        elif btn == "down" or step < 0:
            self._apply_zoom_factor(1.0 / 1.15)

    def _apply_zoom_factor(self, factor: float):
        """Scales 3D axes bounding box relative to scene center."""
        new_zoom = self.zoom_level * factor
        if not (0.25 <= new_zoom <= 8.0):
            return

        self.zoom_level = new_zoom

        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        zlim = self.ax.get_zlim()

        cx = (xlim[0] + xlim[1]) / 2.0
        cy = (ylim[0] + ylim[1]) / 2.0
        cz = (zlim[0] + zlim[1]) / 2.0

        scale = 1.0 / factor
        self.ax.set_xlim([cx + (x - cx) * scale for x in xlim])
        self.ax.set_ylim([cy + (y - cy) * scale for y in ylim])
        self.ax.set_zlim([cz + (z - cz) * scale for z in zlim])

        self._update_telemetry()
        self.canvas.draw_idle()

    def _rotate_camera(self, azim_delta: float = 0, elev_delta: float = 0):
        """Rotates camera angles smoothly."""
        azim = (self.ax.azim + azim_delta) % 360
        elev = np.clip(self.ax.elev + elev_delta, -89.0, 89.0)
        self.ax.view_init(elev=elev, azim=azim)
        self._update_telemetry()
        self.canvas.draw_idle()

    def _update_telemetry(self):
        """Updates elevation, azimuth, and zoom readout badge."""
        elev = self.ax.elev
        azim = self.ax.azim
        self.telemetry_label.configure(
            text=f"Elev: {elev:.0f}° | Azim: {azim:.0f}° | Zoom: {self.zoom_level:.1f}x"
        )

    # Camera Presets
    def _set_cam_perspective(self):
        self.ax.view_init(elev=22, azim=-55)
        self._update_telemetry()
        self.canvas.draw_idle()

    def _set_cam_top(self):
        self.ax.view_init(elev=89, azim=-90)
        self._update_telemetry()
        self.canvas.draw_idle()

    def _set_cam_side(self):
        self.ax.view_init(elev=0, azim=-90)
        self._update_telemetry()
        self.canvas.draw_idle()

    def _set_cam_front(self):
        self.ax.view_init(elev=0, azim=0)
        self._update_telemetry()
        self.canvas.draw_idle()

    def _set_cam_reset(self):
        self.zoom_level = 1.0
        self.ax.view_init(elev=self.default_elev, azim=self.default_azim)
        self.ax.set_xlim(self.base_xlim)
        self.ax.set_ylim(self.base_ylim)
        self.ax.set_zlim(self.base_zlim)
        self._update_telemetry()
        self.canvas.draw_idle()

    def refresh_language(self):
        """Updates toolbar text and buttons when language toggles."""
        is_fa = LocalizationService.is_persian()
        self.toolbar_title.configure(
            text=LocalizationService.get("tab_3d_setup"),
            font=FontManager.get_persian_font(12, "bold") if is_fa else FontManager.get_number_font(12, "bold")
        )
        for key, btn in self.cam_buttons:
            btn.configure(
                text=LocalizationService.get(key),
                font=FontManager.get_persian_font(10, "bold") if is_fa else FontManager.get_number_font(10, "bold")
            )
        self.btn_zoom_in.configure(
            text="+ زوم" if is_fa else "+ Zoom",
            font=FontManager.get_persian_font(10, "bold") if is_fa else FontManager.get_number_font(10, "bold")
        )
        self.btn_zoom_out.configure(
            text="- زوم" if is_fa else "- Zoom",
            font=FontManager.get_persian_font(10, "bold") if is_fa else FontManager.get_number_font(10, "bold")
        )

    # ==========================================================================
    # 3D Scene Construction
    # ==========================================================================
    def update_3d_scene(
        self,
        wavelength_nm: float,
        slit_distance_mm: float,
        slit_width_mm: float,
        screen_distance_m: float,
        which_way_active: bool,
        intensity_1d: np.ndarray,
        y_grid_m: np.ndarray,
        base_rgb: Tuple[int, int, int],
        particle_category: ParticleCategory = ParticleCategory.PHOTON,
        is_quantum: bool = False,
        quantum_hits_y: Optional[List[float]] = None,
        quantum_hits_z: Optional[List[float]] = None
    ):
        """
        Reconstructs the 3D scene elements: source (laser/electron gun/oven),
        barrier plate with slits, detector screen with projected fringes or phosphor dots,
        rays, and which-way sensors. Preserves user zoom and rotation angles!
        """
        self.wavelength_nm = wavelength_nm
        self.slit_distance_mm = slit_distance_mm
        self.slit_width_mm = slit_width_mm
        self.screen_distance_m = screen_distance_m
        self.which_way_active = which_way_active
        self.particle_category = particle_category
        self.is_quantum = is_quantum

        # Preserve current user camera angle and zoom
        curr_elev = self.ax.elev if hasattr(self.ax, "elev") else self.default_elev
        curr_azim = self.ax.azim if hasattr(self.ax, "azim") else self.default_azim

        self.ax.cla()
        self.ax.set_facecolor("#121214")
        self.ax.grid(True, linestyle=":", alpha=0.3, color="#404040")
        self.ax.tick_params(colors="#888888", labelsize=8)

        is_fa = LocalizationService.is_persian()
        fprop_lbl = FontManager.get_mpl_persian_prop(8) if is_fa else FontManager.get_mpl_number_prop(8)
        lbl_x = LocalizationService.reshape_text("X (m) [محور اپتیکی]") if is_fa else "X (m) [Axis]"
        lbl_y = LocalizationService.reshape_text("Y (mm) [شکاف‌ها]") if is_fa else "Y (mm) [Slits]"
        lbl_z = LocalizationService.reshape_text("Z (mm) [ارتفاع]") if is_fa else "Z (mm) [Height]"
        self.ax.set_xlabel(lbl_x, color="#AAAAAA", fontsize=8, labelpad=2, fontproperties=fprop_lbl)
        self.ax.set_ylabel(lbl_y, color="#AAAAAA", fontsize=8, labelpad=2, fontproperties=fprop_lbl)
        self.ax.set_zlabel(lbl_z, color="#AAAAAA", fontsize=8, labelpad=2, fontproperties=fprop_lbl)

        L = max(screen_distance_m, 0.2)
        d_mm = slit_distance_mm
        a_mm = slit_width_mm

        x_source = -0.22 * L
        y_span_mm = max(d_mm * 6.0, 15.0)
        z_span_mm = 12.0

        # Save base limits for zoom scaling
        self.base_xlim = (x_source * 1.1, L * 1.05)
        self.base_ylim = (-y_span_mm, y_span_mm)
        self.base_zlim = (-z_span_mm, z_span_mm)

        # Apply current zoom level to limits
        scale = 1.0 / self.zoom_level
        cx = (self.base_xlim[0] + self.base_xlim[1]) / 2.0
        cy = 0.0
        cz = 0.0
        self.ax.set_xlim([cx + (x - cx) * scale for x in self.base_xlim])
        self.ax.set_ylim([cy + (y - cy) * scale for y in self.base_ylim])
        self.ax.set_zlim([cz + (z - cz) * scale for z in self.base_zlim])

        laser_hex = ColorUtils.get_particle_hex(particle_category, wavelength_nm) if is_quantum else ColorUtils.wavelength_to_hex(wavelength_nm)

        # ----------------------------------------------------------------------
        # 1. 3D Coherent Source (Adaptive for Photons, Electrons, Buckyballs)
        # ----------------------------------------------------------------------
        src_w_y = 4.5
        src_h_z = 4.5
        src_len_x = 0.08 * L

        x0, x1 = x_source - src_len_x, x_source
        y0, y1 = -src_w_y / 2, src_w_y / 2
        z0, z1 = -src_h_z / 2, src_h_z / 2

        src_faces = [
            [[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0]],
            [[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]],
            [[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1]],
            [[x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1]],
            [[x0, y0, z0], [x0, y1, z0], [x0, y1, z1], [x0, y0, z1]],
            [[x1, y0, z0], [x1, y1, z0], [x1, y1, z1], [x1, y0, z1]],
        ]

        if is_quantum and particle_category == ParticleCategory.ELECTRON:
            housing_col = "#0E7490"  # Electron gun cyan
            src_title = "e⁻ GUN" if not is_fa else LocalizationService.reshape_text("تفنگ الکترونی")
        elif is_quantum and particle_category == ParticleCategory.BUCKYBALL:
            housing_col = "#047857"  # Molecular oven emerald
            src_title = "C₆₀ OVEN" if not is_fa else LocalizationService.reshape_text("کوره باکی‌بال")
        else:
            housing_col = "#1E293B"  # Laser cavity
            src_title = "LASER" if not is_fa else LocalizationService.reshape_text("لیزر چشمه")

        self.ax.add_collection3d(Poly3DCollection(src_faces, facecolors=housing_col, edgecolors="#38BDF8", linewidths=1.2, alpha=0.9))
        self.ax.text(x_source - src_len_x/2, 0, z1 + 1.5, src_title, color="#38BDF8", fontsize=7, weight="bold", ha="center", fontproperties=FontManager.get_mpl_persian_prop(7) if is_fa else FontManager.get_mpl_number_prop(7))

        # Beam from source to slits
        self.ax.plot([x_source, 0], [0, -d_mm/2], [0, 0], color=laser_hex, lw=1.5, alpha=0.7)
        self.ax.plot([x_source, 0], [0, +d_mm/2], [0, 0], color=laser_hex, lw=1.5, alpha=0.7)

        # ----------------------------------------------------------------------
        # 2. 3D Double-Slit Barrier Plate (at X = 0)
        # ----------------------------------------------------------------------
        barrier_plate_y = y_span_mm * 0.95
        barrier_plate_z = z_span_mm * 0.95
        slit_h_mm = 8.0

        y_s1 = -d_mm / 2.0
        y_s2 = +d_mm / 2.0
        half_a = max(a_mm / 2.0, 0.05)

        barrier_panels = [
            # Left wing
            [[0, -barrier_plate_y, -barrier_plate_z], [0, y_s1 - half_a, -barrier_plate_z],
             [0, y_s1 - half_a, barrier_plate_z], [0, -barrier_plate_y, barrier_plate_z]],
            # Center septum
            [[0, y_s1 + half_a, -barrier_plate_z], [0, y_s2 - half_a, -barrier_plate_z],
             [0, y_s2 - half_a, barrier_plate_z], [0, y_s1 + half_a, barrier_plate_z]],
            # Right wing
            [[0, y_s2 + half_a, -barrier_plate_z], [0, barrier_plate_y, -barrier_plate_z],
             [0, barrier_plate_y, barrier_plate_z], [0, y_s2 + half_a, barrier_plate_z]],
            # Top block
            [[0, y_s1 - half_a, slit_h_mm/2], [0, y_s2 + half_a, slit_h_mm/2],
             [0, y_s2 + half_a, barrier_plate_z], [0, y_s1 - half_a, barrier_plate_z]],
            # Bottom block
            [[0, y_s1 - half_a, -barrier_plate_z], [0, y_s2 + half_a, -barrier_plate_z],
             [0, y_s2 + half_a, -slit_h_mm/2], [0, y_s1 - half_a, -slit_h_mm/2]],
        ]
        self.ax.add_collection3d(Poly3DCollection(barrier_panels, facecolors="#2D3748", edgecolors="#4A5568", linewidths=0.8, alpha=0.95))

        self.ax.text(0, y_s1, slit_h_mm/2 + 1.5, "S₁", color="#00E676", fontsize=8, weight="bold", ha="center")
        self.ax.text(0, y_s2, slit_h_mm/2 + 1.5, "S₂", color="#00E676", fontsize=8, weight="bold", ha="center")

        # ----------------------------------------------------------------------
        # 3. 3D Detector Screen with Surface Fringes (at X = L) - High Resolution Vectorized
        # ----------------------------------------------------------------------
        grid_res_y = 240
        grid_res_z = 36
        y_scr = np.linspace(-y_span_mm, y_span_mm, grid_res_y)
        z_scr = np.linspace(-z_span_mm, z_span_mm, grid_res_z)
        Y_mesh, Z_mesh = np.meshgrid(y_scr, z_scr)
        X_mesh = np.full_like(Y_mesh, L)

        y_grid_mm = y_grid_m * 1000.0
        i_interp = np.interp(y_scr, y_grid_mm, intensity_1d)
        max_i = np.max(i_interp)
        if max_i > 0:
            i_interp /= max_i

        r_f = base_rgb[0] / 255.0
        g_f = base_rgb[1] / 255.0
        b_f = base_rgb[2] / 255.0

        z_envelope = np.exp(-0.5 * (z_scr / (z_span_mm * 0.45)) ** 2)
        intensity_2d = np.outer(z_envelope, i_interp)

        fringe_colors = np.empty((grid_res_z, grid_res_y, 4), dtype=np.float32)
        fringe_colors[..., 0] = np.clip(intensity_2d * r_f, 0.0, 1.0)
        fringe_colors[..., 1] = np.clip(intensity_2d * g_f, 0.0, 1.0)
        fringe_colors[..., 2] = np.clip(intensity_2d * b_f, 0.0, 1.0)
        fringe_colors[..., 3] = np.clip(intensity_2d * 0.95 + 0.15, 0.15, 1.0)

        self.ax.plot_surface(X_mesh, Y_mesh, Z_mesh, facecolors=fringe_colors, shade=False, antialiased=False, rstride=1, cstride=1, zorder=3)

        # Screen frame outline
        scr_edge_x = [L, L, L, L, L]
        scr_edge_y = [-y_span_mm, y_span_mm, y_span_mm, -y_span_mm, -y_span_mm]
        scr_edge_z = [-z_span_mm, -z_span_mm, z_span_mm, z_span_mm, -z_span_mm]
        self.ax.plot(scr_edge_x, scr_edge_y, scr_edge_z, color="#64748B", lw=1.5)
        scr_title = f"SCREEN (L={L:.2f}m)" if not is_fa else LocalizationService.reshape_text(f"پرده (L={L:.2f}m)")
        self.ax.text(L, 0, z_span_mm + 1.5, scr_title, color="#94A3B8", fontsize=7, weight="bold", ha="center", fontproperties=FontManager.get_mpl_persian_prop(7) if is_fa else FontManager.get_mpl_number_prop(7))

        # In Quantum Mode: Render 3D phosphor impact points
        if is_quantum and quantum_hits_y is not None and len(quantum_hits_y) > 0:
            sample_n = min(len(quantum_hits_y), 400)
            sub_y = np.array(quantum_hits_y[-sample_n:]) * 1000.0
            sub_z = np.array(quantum_hits_z[-sample_n:]) * 1000.0
            sub_x = np.full(sample_n, L)
            self.ax.scatter(sub_x, sub_y, sub_z, color=laser_hex, s=4.0, alpha=0.8, zorder=5)

        # ----------------------------------------------------------------------
        # 4. 3D Ray Trajectories (r1, r2 to screen center)
        # ----------------------------------------------------------------------
        self.ax.plot([0, L], [y_s1, 0], [0, 0], color="#00E676", lw=1.8, ls="--", alpha=0.85)
        self.ax.plot([0, L], [y_s2, 0], [0, 0], color="#FFD600", lw=1.8, ls="--", alpha=0.85)
        self.ax.scatter([L], [0], [0], color="#FF1744", s=30, zorder=6)

        # ----------------------------------------------------------------------
        # 5. Which-Way Detector Sensors in 3D
        # ----------------------------------------------------------------------
        if which_way_active:
            det_col = "#EF4444"
            for y_slit, det_name in [(y_s1, "D₁"), (y_s2, "D₂")]:
                self.ax.scatter([0.02 * L], [y_slit], [0], color=det_col, s=60, edgecolors="#FFFFFF", lw=1.2, zorder=7)
                self.ax.plot([0, 0.04 * L], [y_slit, y_slit], [0, 0], color=det_col, lw=2.5)
                self.ax.text(0.04 * L, y_slit, 1.2, det_name, color=det_col, fontsize=8, weight="bold")

            alert_text = "⚡ OBSERVER ACTIVE: COLLAPSE" if not is_fa else LocalizationService.reshape_text("⚡ اثر ناظر فعال: فروریزش تابع موج")
            self.ax.text(L / 2.0, 0, z_span_mm + 3.0, alert_text,
                         color="#F87171", fontsize=8, weight="bold", ha="center",
                         fontproperties=FontManager.get_mpl_persian_prop(8) if is_fa else FontManager.get_mpl_number_prop(8),
                         bbox=dict(boxstyle="round,pad=0.3", fc="#450A0A", ec="#DC2626", lw=1))

        # Restore user camera angle
        self.ax.view_init(elev=curr_elev, azim=curr_azim)
        self._update_telemetry()
        self.canvas.draw_idle()
