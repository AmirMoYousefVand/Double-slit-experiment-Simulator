"""
2D Screen Detector View.
Renders physical detector screen in both Classical mode (continuous spectral fringes)
and Quantum mode (phosphor dot accumulation from individual particle impacts).
"""

import tkinter as tk
from typing import Tuple, List, Optional
import customtkinter as ctk
import numpy as np
from PIL import Image, ImageTk

from utils.color_utils import ColorUtils
from utils.localization import LocalizationService, RLM
from utils.font_manager import FontManager

class Screen2DView(ctk.CTkFrame):
    """
    Renders the 2D detector screen using Pillow and Tkinter Canvas.
    Supports real-time continuous laser diffraction bands and quantum hit accumulation.
    """

    def __init__(self, master, width: int = 700, height: int = 280, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas_width = width
        self.canvas_height = height

        # Internal image buffers
        self.quantum_buffer = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.float32)
        self.tk_image: Optional[ImageTk.PhotoImage] = None

        # Colormap tracking
        self.current_colormap = "physical"
        self._last_intensity_1d: Optional[np.ndarray] = None
        self._last_base_rgb: Tuple[int, int, int] = (255, 0, 0)

        # Mode tracking
        self.is_quantum_mode = False
        self.current_span_y_m = 0.04  # default +/- 20 mm span
        self.current_span_z_m = 0.02

        # Create Header / Controls inside frame
        self._create_widgets()

    def _create_widgets(self):
        """Builds canvas, legend, and ruler scale layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        is_fa = LocalizationService.current_language() == "fa"

        # Top title & status bar
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=10, pady=(6, 2), sticky="ew")

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=LocalizationService.get("tab_2d_screen"),
            font=FontManager.get_persian_font(13, "bold") if is_fa else FontManager.get_number_font(13, "bold")
        )
        self.title_label.pack(side="right" if is_fa else "left", padx=5)

        # Colormap segmented selector
        self.cmap_segmented = ctk.CTkSegmentedButton(
            self.header_frame,
            values=["Physical", "Turbo", "Inferno"],
            command=self._on_colormap_changed,
            height=24,
            font=FontManager.get_number_font(9, "bold")
        )
        self.cmap_segmented.set("Physical")
        self.cmap_segmented.pack(side="right" if not is_fa else "left", padx=10)

        self.info_label = ctk.CTkLabel(
            self.header_frame,
            text="Continuous Field",
            font=FontManager.get_number_font(11),
            text_color="#9E9E9E"
        )
        self.info_label.pack(side="left" if is_fa else "right", padx=10)

        # Main Canvas for screen display
        self.canvas = tk.Canvas(
            self,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#0A0A0A",
            highlightthickness=1,
            highlightbackground="#2A2A2A"
        )
        self.canvas.grid(row=1, column=0, padx=10, pady=(2, 6), sticky="nsew")
        self.canvas.bind("<Configure>", self._on_resize)

        # Initial blank screen
        self._render_blank()

    def _on_colormap_changed(self, choice: str):
        choice_lower = choice.lower()
        if "turbo" in choice_lower:
            self.current_colormap = "turbo"
        elif "inferno" in choice_lower:
            self.current_colormap = "inferno"
        else:
            self.current_colormap = "physical"

        if self._last_intensity_1d is not None and not self.is_quantum_mode:
            self.update_classical_screen(
                intensity_1d=self._last_intensity_1d,
                base_rgb=self._last_base_rgb,
                span_y_m=self.current_span_y_m
            )

    def _on_resize(self, event):
        """Handles responsive window resizing."""
        if event.width > 150 and event.height > 80:
            if abs(self.canvas_width - event.width) > 20 or abs(self.canvas_height - event.height) > 20:
                self.canvas_width = event.width
                self.canvas_height = event.height
                self.quantum_buffer = np.zeros((self.canvas_height, self.canvas_width, 3), dtype=np.float32)

    def _render_blank(self):
        """Clears canvas with dark phosphor glow background."""
        self.canvas.delete("all")
        self.canvas.create_rectangle(
            0, 0, self.canvas_width, self.canvas_height,
            fill="#080808", outline=""
        )
        self._draw_ruler(span_mm=self.current_span_y_m * 1000.0)

    def _draw_ruler(self, span_mm: float):
        """Draws physical millimeter ruler ticks and labels along the bottom of the screen."""
        y_ruler = self.canvas_height - 18
        # Center line
        mid_x = self.canvas_width // 2

        # Draw axis base line
        self.canvas.create_line(15, y_ruler, self.canvas_width - 15, y_ruler, fill="#444444", width=1)

        # Major ticks (-half, 0, +half)
        half_span = span_mm / 2.0
        ticks = [
            (mid_x, "0 mm", True),
            (25, f"-{half_span:.1f} mm", False),
            (self.canvas_width - 25, f"+{half_span:.1f} mm", False),
            (mid_x - self.canvas_width // 4, f"-{half_span/2:.1f} mm", False),
            (mid_x + self.canvas_width // 4, f"+{half_span/2:.1f} mm", False),
        ]

        for x_pos, label, is_center in ticks:
            tick_h = 8 if is_center else 5
            color = "#00F0FF" if is_center else "#777777"
            self.canvas.create_line(x_pos, y_ruler - tick_h, x_pos, y_ruler + tick_h, fill=color, width=1)
            self.canvas.create_text(
                x_pos, y_ruler + 10,
                text=label,
                fill=color,
                font=("Consolas", 8)
            )

    def update_classical_screen(
        self,
        intensity_1d: np.ndarray,
        base_rgb: Tuple[int, int, int],
        span_y_m: float
    ):
        """
        Renders continuous 2D interference fringes with realistic vertical slit dispersion
        and true spectral RGB laser color or false-color HDR colormaps.
        """
        self._last_intensity_1d = intensity_1d
        self._last_base_rgb = base_rgb
        self.is_quantum_mode = False
        self.current_span_y_m = span_y_m

        # Generate pixel array (H x W x 3) with active colormap
        img_array = ColorUtils.generate_screen_image_array(
            intensity_1d=intensity_1d,
            base_rgb=base_rgb,
            height=self.canvas_height,
            width=self.canvas_width,
            colormap_name=self.current_colormap
        )

        pil_image = Image.fromarray(img_array)
        self.tk_image = ImageTk.PhotoImage(pil_image)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self._draw_ruler(span_mm=span_y_m * 1000.0)

        self.info_label.configure(
            text=f"Classical Field | Span: ±{span_y_m * 500.0:.2f} mm"
        )

    def add_quantum_hits(
        self,
        batch_y: np.ndarray,
        batch_z: np.ndarray,
        base_rgb: Tuple[int, int, int],
        span_y_m: float,
        span_z_m: float,
        total_hits: int
    ):
        """
        Accumulates individual quantum particle impacts onto the phosphor screen.
        Adds glowing spots that gradually form the interference or collapse pattern.
        """
        self.is_quantum_mode = True
        self.current_span_y_m = span_y_m
        self.current_span_z_m = span_z_m

        if len(batch_y) == 0:
            return

        # Map spatial coordinates (y, z) in meters to pixel indices (px, py)
        # y: -half_y -> 0, +half_y -> width - 1
        half_y = span_y_m / 2.0
        half_z = span_z_m / 2.0

        px = ((batch_y + half_y) / (2.0 * half_y) * (self.canvas_width - 1)).astype(int)
        py = ((batch_z + half_z) / (2.0 * half_z) * (self.canvas_height - 1)).astype(int)

        # Filter out of bound hits
        valid = (px >= 1) & (px < self.canvas_width - 1) & (py >= 1) & (py < self.canvas_height - 1)
        px_valid = px[valid]
        py_valid = py[valid]

        if len(px_valid) == 0:
            return

        # Color channels normalized in [0, 1]
        r_glow = max(base_rgb[0] / 255.0, 0.2)
        g_glow = max(base_rgb[1] / 255.0, 0.2)
        b_glow = max(base_rgb[2] / 255.0, 0.2)

        # Add intensity to hit pixels and immediate neighbors (3x3 kernel for phosphor dot glow)
        spot_intensity = 42.0  # Brightness gain per particle impact
        for x, y in zip(px_valid, py_valid):
            # Center pixel
            self.quantum_buffer[y, x, 0] += spot_intensity * r_glow
            self.quantum_buffer[y, x, 1] += spot_intensity * g_glow
            self.quantum_buffer[y, x, 2] += spot_intensity * b_glow

            # 4-connected cross glow
            self.quantum_buffer[y - 1, x, :] += spot_intensity * 0.3 * np.array([r_glow, g_glow, b_glow])
            self.quantum_buffer[y + 1, x, :] += spot_intensity * 0.3 * np.array([r_glow, g_glow, b_glow])
            self.quantum_buffer[y, x - 1, :] += spot_intensity * 0.3 * np.array([r_glow, g_glow, b_glow])
            self.quantum_buffer[y, x + 1, :] += spot_intensity * 0.3 * np.array([r_glow, g_glow, b_glow])

        # Clip buffer to 255 and render
        clipped = np.clip(self.quantum_buffer, 0.0, 255.0).astype(np.uint8)
        pil_image = Image.fromarray(clipped)
        self.tk_image = ImageTk.PhotoImage(pil_image)

        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self._draw_ruler(span_mm=span_y_m * 1000.0)

        self.info_label.configure(
            text=f"Quantum Impacts: {total_hits:,} | Span: ±{span_y_m * 500.0:.2f} mm"
        )

    def clear_quantum_screen(self):
        """Resets the quantum phosphor accumulation buffer to complete black."""
        self.quantum_buffer.fill(0.0)
        self._render_blank()
        self.info_label.configure(text="Detector Screen Cleared")

    def refresh_language(self):
        """Updates labels and fonts on language switch."""
        is_fa = LocalizationService.current_language() == "fa"
        self.title_label.configure(
            text=LocalizationService.get("tab_2d_screen"),
            font=FontManager.get_persian_font(13, "bold") if is_fa else FontManager.get_number_font(13, "bold")
        )
        self.title_label.pack(side="right" if is_fa else "left", padx=5)
        self.info_label.pack(side="left" if is_fa else "right", padx=10)
