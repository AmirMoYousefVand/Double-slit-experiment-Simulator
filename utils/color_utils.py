"""
Color utilities for visible spectrum wavelength to RGB mapping,
false-color matter wave rendering, and 2D canvas pixel buffer synthesis.
"""

from typing import Tuple
import numpy as np
from physics.particle_types import ParticleCategory

class ColorUtils:
    """
    Implements physical wavelength-to-sRGB mapping based on the Dan Bruton
    CIE colorimetric approximation with gamma correction and eye sensitivity curve.
    """

    @staticmethod
    def wavelength_to_rgb(wavelength_nm: float, gamma: float = 0.8) -> Tuple[int, int, int]:
        """
        Converts visible wavelength (380 to 780 nm) into sRGB integer values (0 to 255).
        Clamps or produces graceful fallbacks for UV / IR bounds.
        """
        wl = float(wavelength_nm)

        # 1. Base RGB Spectral Interpolation
        if 380.0 <= wl < 440.0:
            r = -(wl - 440.0) / (440.0 - 380.0)
            g = 0.0
            b = 1.0
        elif 440.0 <= wl < 490.0:
            r = 0.0
            g = (wl - 440.0) / (490.0 - 440.0)
            b = 1.0
        elif 490.0 <= wl < 510.0:
            r = 0.0
            g = 1.0
            b = -(wl - 510.0) / (510.0 - 490.0)
        elif 510.0 <= wl < 580.0:
            r = (wl - 510.0) / (580.0 - 510.0)
            g = 1.0
            b = 0.0
        elif 580.0 <= wl < 645.0:
            r = 1.0
            g = -(wl - 645.0) / (645.0 - 580.0)
            b = 0.0
        elif 645.0 <= wl <= 780.0:
            r = 1.0
            g = 0.0
            b = 0.0
        elif wl < 380.0:
            # Ultraviolet fallback (Fluorescent violet)
            return (138, 43, 226)
        else:
            # Infrared fallback (Deep ruby crimson)
            return (178, 34, 34)

        # 2. Human Photopic Eye Sensitivity Falloff at vision boundaries
        if 380.0 <= wl < 420.0:
            factor = 0.3 + 0.7 * (wl - 380.0) / (420.0 - 380.0)
        elif 420.0 <= wl <= 700.0:
            factor = 1.0
        elif 700.0 < wl <= 780.0:
            factor = 0.3 + 0.7 * (780.0 - wl) / (780.0 - 700.0)
        else:
            factor = 0.0

        # 3. Gamma Correction and Scaling
        r_corr = int(np.clip((r * factor) ** gamma * 255.0, 0, 255))
        g_corr = int(np.clip((g * factor) ** gamma * 255.0, 0, 255))
        b_corr = int(np.clip((b * factor) ** gamma * 255.0, 0, 255))

        return (r_corr, g_corr, b_corr)

    @classmethod
    def wavelength_to_hex(cls, wavelength_nm: float) -> str:
        """Converts wavelength in nanometers to HTML hex color string (#RRGGBB)."""
        r, g, b = cls.wavelength_to_rgb(wavelength_nm)
        return f"#{r:02x}{g:02x}{b:02x}"

    @classmethod
    def get_particle_color(
        cls,
        category: ParticleCategory,
        wavelength_nm: float
    ) -> Tuple[int, int, int]:
        """
        Returns physical spectral color for photons, or distinct false-color phosphor
        glows for matter waves (electrons, macromolecules).
        """
        if category == ParticleCategory.PHOTON:
            return cls.wavelength_to_rgb(wavelength_nm)
        elif category == ParticleCategory.ELECTRON:
            return (0, 240, 255)  # Phosphor cyan
        elif category == ParticleCategory.BUCKYBALL:
            return (0, 230, 118)  # Jade emerald
        return (255, 255, 255)

    @classmethod
    def get_particle_hex(cls, category: ParticleCategory, wavelength_nm: float) -> str:
        """Returns hex string for particle trajectory and markers."""
        r, g, b = cls.get_particle_color(category, wavelength_nm)
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
        """Converts '#RRGGBB' to (r, g, b) integer tuple."""
        h = hex_str.lstrip('#')
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    @staticmethod
    def generate_screen_image_array(
        intensity_1d: np.ndarray,
        base_rgb: Tuple[int, int, int],
        height: int,
        width: int,
        colormap_name: str = "physical"
    ) -> np.ndarray:
        """
        Synthesizes a realistic 2D detector screen pixel matrix (height x width x 3, uint8).
        Supports physical monochromatic color or scientific false-color colormaps (Turbo, Inferno).
        """
        # Resample intensity_1d to match screen pixel width
        if len(intensity_1d) != width:
            x_in = np.linspace(0, 1, len(intensity_1d))
            x_out = np.linspace(0, 1, width)
            horiz_intensity = np.interp(x_out, x_in, intensity_1d)
        else:
            horiz_intensity = intensity_1d

        # Normalize in [0, 1]
        max_val = np.max(horiz_intensity)
        if max_val > 0:
            horiz_intensity = horiz_intensity / max_val

        # Vertical Gaussian falloff along slit height
        y_coords = np.linspace(-1.0, 1.0, height)
        vert_falloff = np.exp(-0.5 * (y_coords / 0.55) ** 2)

        # 2D outer product: (height, width)
        intensity_2d = np.outer(vert_falloff, horiz_intensity)

        if colormap_name == "turbo":
            import matplotlib
            rgba = matplotlib.colormaps["turbo"](intensity_2d)
            return (rgba[:, :, :3] * 255).astype(np.uint8)
        elif colormap_name == "inferno":
            import matplotlib
            rgba = matplotlib.colormaps["inferno"](intensity_2d)
            return (rgba[:, :, :3] * 255).astype(np.uint8)
        else:
            # Scale by base RGB
            img_array = np.zeros((height, width, 3), dtype=np.uint8)
            img_array[:, :, 0] = np.clip(intensity_2d * base_rgb[0], 0, 255).astype(np.uint8)
            img_array[:, :, 1] = np.clip(intensity_2d * base_rgb[1], 0, 255).astype(np.uint8)
            img_array[:, :, 2] = np.clip(intensity_2d * base_rgb[2], 0, 255).astype(np.uint8)
            return img_array

        return img_array
