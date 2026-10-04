"""
1D Intensity Profile View.
Embeds high-performance Matplotlib figure inside CustomTkinter, displaying theoretical
interference curve, diffraction envelope, analytical peak markers, and quantum accumulation histogram.
"""

from typing import Tuple, List, Optional
import customtkinter as ctk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.lines import Line2D

from utils.localization import LocalizationService
from utils.font_manager import FontManager
from utils.units import choose_length_scale

class Profile1DView(ctk.CTkFrame):
    """
    Renders 1D cross-sectional intensity profile and quantum probability histogram.
    Optimized for real-time slider updates and 60 FPS animation via persistent Line2D data updating.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.bins_count = 150
        self.is_quantum_active = False
        self.fill_poly = None
        # Display scale for the x-axis: meters -> current unit (mm by default,
        # recomputed from the span on every profile update)
        self._y_scale, self._y_unit = 1000.0, "mm"

        self._create_figure()
        self.refresh_language()

    def _create_figure(self):
        """Constructs styled Matplotlib canvas and persistent plot artists."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create Dark Themed Figure
        self.fig = Figure(figsize=(7, 3.2), dpi=100, facecolor="#141414")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#1A1A1A")

        # Visual styling with major and minor grid lines
        self.ax.minorticks_on()
        self.ax.grid(True, which="major", linestyle="--", alpha=0.35, color="#404040")
        self.ax.grid(True, which="minor", linestyle=":", alpha=0.15, color="#555555")
        self.ax.tick_params(colors="#CCCCCC", labelsize=9)
        for spine in self.ax.spines.values():
            spine.set_color("#333333")

        # Bounds with 22% headroom above peak so legend never obstructs central fringe
        self.ax.set_ylim(-0.05, 1.22)

        # Persistent Line Artists
        # 1. Theoretical Interference Curve (solid, enhanced linewidth)
        self.line_theory, = self.ax.plot([], [], color="#00F0FF", lw=2.4, label="Theory I(y)", zorder=4)

        # 2. Single-slit Diffraction Envelope (dashed)
        self.line_envelope, = self.ax.plot([], [], color="#FFA000", lw=1.5, ls="--", alpha=0.85, label="Envelope sinc²", zorder=3)

        # 3. Quantum Hits Histogram (stepped line for fast updating)
        self.line_hist, = self.ax.step([], [], where="mid", color="#39FF14", lw=1.6, alpha=0.9, label="Quantum Hits", zorder=5)

        # 4. Analytical Maxima Markers (green triangles)
        self.markers_max, = self.ax.plot([], [], marker="^", color="#00E676", ls="", ms=7, markeredgewidth=1.0, markeredgecolor="#FFFFFF", label="Maxima", zorder=6)

        # 5. Analytical Minima Markers (red triangles)
        self.markers_min, = self.ax.plot([], [], marker="v", color="#FF5252", ls="", ms=6, markeredgewidth=0.8, markeredgecolor="#FFFFFF", label="Minima", zorder=6)

        self.legend = self.ax.legend(
            loc="upper right",
            facecolor="#18181B",
            edgecolor="#3F3F46",
            labelcolor="#E0E0E0",
            fontsize=8,
            framealpha=0.85
        )

        # Embed in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

    def refresh_language(self):
        """Updates axis labels, titles, and legend items based on active language."""
        is_fa = LocalizationService.is_persian()
        fprop_lbl = FontManager.get_mpl_persian_prop(10) if is_fa else FontManager.get_mpl_number_prop(10)
        fprop_leg = FontManager.get_mpl_persian_prop(8) if is_fa else FontManager.get_mpl_number_prop(8)

        xlabel = f"{LocalizationService.get_reshaped('plot_1d_xlabel_base')} ({self._y_unit})"
        ylabel = LocalizationService.get_reshaped("plot_1d_ylabel")
        self.ax.set_xlabel(xlabel, color="#E0E0E0", fontsize=10, fontproperties=fprop_lbl)
        self.ax.set_ylabel(ylabel, color="#E0E0E0", fontsize=10, fontproperties=fprop_lbl)

        # Update legend labels
        self.line_theory.set_label(LocalizationService.get_reshaped("plot_1d_theory"))
        self.line_envelope.set_label(LocalizationService.get_reshaped("plot_1d_envelope"))
        self.line_hist.set_label(LocalizationService.get_reshaped("plot_1d_hits"))
        self.markers_max.set_label(LocalizationService.get_reshaped("plot_1d_maxima"))
        self.markers_min.set_label(LocalizationService.get_reshaped("plot_1d_minima"))

        self.legend = self.ax.legend(
            loc="upper right",
            facecolor="#18181B",
            edgecolor="#3F3F46",
            labelcolor="#E0E0E0",
            prop=fprop_leg,
            framealpha=0.85
        )
        self.canvas.draw_idle()

    def update_theoretical_profile(
        self,
        y_grid_m: np.ndarray,
        intensity: np.ndarray,
        envelope: np.ndarray,
        curve_hex_color: str,
        analytical_features: Optional[dict] = None
    ):
        """
        Updates the theoretical curves, under-curve luminous fill, and analytical markers.
        Executes in under 1 ms using set_data without clearing the axes.
        """
        # Choose display unit from the span (mm / µm / nm / pm)
        half_m = abs(y_grid_m[-1]) if len(y_grid_m) else 0.02
        self._y_scale, self._y_unit = choose_length_scale(half_m)
        y_disp = y_grid_m * self._y_scale
        # Keep the axis unit in sync when the span changes (font props persist)
        self.ax.set_xlabel(
            f"{LocalizationService.get_reshaped('plot_1d_xlabel_base')} ({self._y_unit})"
        )

        # Update curve color to match laser wavelength
        self.line_theory.set_color(curve_hex_color)
        self.line_theory.set_data(y_disp, intensity)
        self.line_envelope.set_data(y_disp, envelope)

        # Translucent luminous glow under interference curve
        if self.fill_poly is not None:
            self.fill_poly.remove()
            self.fill_poly = None
        if len(y_disp) > 0 and len(intensity) > 0:
            self.fill_poly = self.ax.fill_between(y_disp, 0, intensity, color=curve_hex_color, alpha=0.18, zorder=2)

        # Update axis bounds smoothly
        span_disp = (y_disp[-1] - y_disp[0]) / 2.0
        self.ax.set_xlim(-span_disp, span_disp)

        # Update analytical peak markers if provided
        if analytical_features:
            max_y = analytical_features.get("maxima_y_m", np.array([])) * self._y_scale
            # Filter within current display window
            valid_max = max_y[np.abs(max_y) <= span_disp]
            if len(valid_max) > 0:
                # Interpolate intensity at peak positions
                peak_int = np.interp(valid_max, y_disp, intensity)
                self.markers_max.set_data(valid_max, peak_int)
            else:
                self.markers_max.set_data([], [])

        if not self.is_quantum_active:
            self.line_hist.set_data([], [])

        self.canvas.draw_idle()

    def update_quantum_histogram(
        self,
        hits_y: List[float],
        span_y_m: float,
        particle_hex: str = "#39FF14"
    ):
        """
        Computes and updates the histogram of accumulated quantum particles.
        """
        self.is_quantum_active = True
        total = len(hits_y)
        if total == 0:
            self.line_hist.set_data([], [])
            self.canvas.draw_idle()
            return

        half_span_m = span_y_m / 2.0
        bins = np.linspace(-half_span_m, half_span_m, self.bins_count + 1)
        counts, _ = np.histogram(hits_y, bins=bins)

        # Normalize histogram so peak scales nicely with theoretical I/I0
        max_c = np.max(counts)
        norm_counts = (counts / max_c) if max_c > 0 else counts

        # Bin centers in the current display unit (set by update_theoretical_profile)
        bin_centers = 0.5 * (bins[:-1] + bins[1:]) * self._y_scale

        self.line_hist.set_color(particle_hex)
        self.line_hist.set_data(bin_centers, norm_counts)
        self.canvas.draw_idle()

    def clear_quantum_data(self):
        """Removes quantum histogram data from plot."""
        self.is_quantum_active = False
        self.line_hist.set_data([], [])
        self.canvas.draw_idle()
