"""
Configuration and Physical Constants for Young's Double-Slit Simulator.
"""

from dataclasses import dataclass
from typing import Dict, Any

# ==============================================================================
# Fundamental Physical Constants (CODATA 2018 / SI Standard)
# ==============================================================================
PLANCK_CONSTANT = 6.62607015e-34       # J*s (h)
H_BAR = PLANCK_CONSTANT / (2.0 * 3.141592653589793)  # J*s (hbar)
SPEED_OF_LIGHT = 299792458.0           # m/s (c)
ELEMENTARY_CHARGE = 1.602176634e-19    # C (e)
ELECTRON_MASS = 9.1093837015e-31       # kg (m_e)
ATOMIC_MASS_UNIT = 1.66053906660e-27   # kg (u / Dalton)

# Buckyball C60 Mass (Carbon-12 x 60)
BUCKYBALL_MASS = 60.0 * 12.0 * ATOMIC_MASS_UNIT # ~ 1.1956e-24 kg

# ==============================================================================
# Default Optical Simulation Parameters
# ==============================================================================
DEFAULT_WAVELENGTH_NM = 632.8       # Helium-Neon Laser (Red)
DEFAULT_SLIT_DISTANCE_MM = 0.25     # Distance between slit centers (d)
DEFAULT_SLIT_WIDTH_MM = 0.04        # Width of each slit aperture (a)
DEFAULT_SCREEN_DISTANCE_M = 1.0     # Distance from slit barrier to screen (L)
DEFAULT_REFRACTIVE_INDEX = 1.000    # Air / Vacuum (n)
DEFAULT_INTENSITY_I0 = 1.0          # Normalized peak intensity

# Slider Ranges & Parameter Limits
PARAM_LIMITS = {
    "wavelength_nm": {"min": 380.0, "max": 780.0, "step": 1.0, "default": 632.8},
    # Derived parameter (Δy = λ·L/(n·d)); runtime range is recomputed by the
    # control panel whenever d, L or n change — values below are at defaults.
    "fringe_spacing_mm": {"min": 0.38, "max": 3.12, "step": 0.005, "default": 2.5312},
    "slit_distance_mm": {"min": 0.05, "max": 2.00, "step": 0.01, "default": 0.25},
    "slit_width_mm": {"min": 0.005, "max": 0.50, "step": 0.005, "default": 0.04},
    "screen_distance_m": {"min": 0.20, "max": 5.00, "step": 0.05, "default": 1.00},
    "refractive_index": {"min": 1.00, "max": 2.00, "step": 0.01, "default": 1.00},
    "emission_rate": {"min": 1, "max": 5000, "step": 10, "default": 200},
}

# Display decimals for manual numeric entry fields (matches step precision)
PARAM_DECIMALS = {
    "wavelength_nm": 1,
    "fringe_spacing_mm": 4,
    "slit_distance_mm": 2,
    "slit_width_mm": 3,
    "screen_distance_m": 2,
    "refractive_index": 3,
    "emission_rate": 0,
}

# ==============================================================================
# Simulation & Visualization Presets
# ==============================================================================
PRESETS: Dict[str, Dict[str, Any]] = {
    "He-Ne Red Laser": {
        "wavelength_nm": 632.8,
        "slit_distance_mm": 0.25,
        "slit_width_mm": 0.04,
        "screen_distance_m": 1.00,
        "refractive_index": 1.00,
        "description": "Standard classroom laboratory Helium-Neon laser (632.8 nm red)."
    },
    "Argon-Ion Green": {
        "wavelength_nm": 514.5,
        "slit_distance_mm": 0.20,
        "slit_width_mm": 0.03,
        "screen_distance_m": 1.20,
        "refractive_index": 1.00,
        "description": "Argon-ion laser prominent green emission line (514.5 nm)."
    },
    "Violet Laser Diode": {
        "wavelength_nm": 405.0,
        "slit_distance_mm": 0.15,
        "slit_width_mm": 0.025,
        "screen_distance_m": 1.00,
        "refractive_index": 1.00,
        "description": "High-frequency violet semiconductor laser (405.0 nm)."
    },
    "Sodium D-Line": {
        "wavelength_nm": 589.3,
        "slit_distance_mm": 0.30,
        "slit_width_mm": 0.05,
        "screen_distance_m": 1.50,
        "refractive_index": 1.00,
        "description": "Classical monochromatic sodium doublet average (589.3 nm amber)."
    },
    "Water Medium (Underwater)": {
        "wavelength_nm": 632.8,
        "slit_distance_mm": 0.25,
        "slit_width_mm": 0.04,
        "screen_distance_m": 1.00,
        "refractive_index": 1.333,
        "description": "Red light passing through water (n = 1.333) with compressed fringes."
    },
    "High Diffraction (Close Slits)": {
        "wavelength_nm": 650.0,
        "slit_distance_mm": 0.08,
        "slit_width_mm": 0.015,
        "screen_distance_m": 1.50,
        "refractive_index": 1.00,
        "description": "Narrow slit configuration demonstrating wide angular fringe separation."
    }
}

# ==============================================================================
# UI & Theme Configurations
# ==============================================================================
APP_TITLE = "Thomas Young Double-Slit Experiment Simulator"
APP_SUBTITLE = "Classical Wave Optics & Quantum Mechanics Dashboard"
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800
WINDOW_DEFAULT_GEOMETRY = "1400x900"

APPEARANCE_MODE = "dark"           # "dark" or "light"
COLOR_THEME = "blue"               # "blue", "dark-blue", "green"

# Canvas dimensions (virtual logical coords)
SCREEN_VIEW_WIDTH = 640
SCREEN_VIEW_HEIGHT = 280

# Animation settings
TARGET_FPS = 60
ANIMATION_INTERVAL_MS = 16          # ~60 FPS
MAX_PARTICLES_BATCH = 2000
HISTOGRAM_BINS = 180
