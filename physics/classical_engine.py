"""
Classical Wave Optics Engine for Fraunhofer Double-Slit Diffraction and Interference.
"""

from dataclasses import dataclass
import numpy as np

@dataclass
class OpticalParameters:
    wavelength_m: float = 632.8e-9     # Vacuum wavelength (lambda_0)
    slit_distance_d_m: float = 0.25e-3 # Center-to-center slit separation (d)
    slit_width_a_m: float = 0.04e-3    # Width of each slit aperture (a)
    screen_distance_L_m: float = 1.0   # Distance to detector screen (L)
    refractive_index_n: float = 1.000  # Medium refractive index (n)
    intensity_I0: float = 1.0          # Peak normalized intensity

    @property
    def medium_wavelength_m(self) -> float:
        """Wavelength inside the medium: lambda_med = lambda_0 / n"""
        return self.wavelength_m / max(self.refractive_index_n, 1e-6)

    @property
    def wave_number_k(self) -> float:
        """Wavenumber k = 2 * pi / lambda_med"""
        return (2.0 * np.pi) / self.medium_wavelength_m


def fringe_spacing_mm(wavelength_nm: float, slit_distance_mm: float,
                      screen_distance_m: float, refractive_index: float = 1.0) -> float:
    """Paraxial fringe spacing Δy in mm: Δy = λ·L/(n·d)."""
    if slit_distance_mm <= 0 or screen_distance_m <= 0:
        return 0.0
    lambda_med_m = (wavelength_nm * 1e-9) / max(refractive_index, 1e-6)
    d_m = slit_distance_mm * 1e-3
    return (lambda_med_m * screen_distance_m / d_m) * 1000.0


def wavelength_nm_from_fringe_spacing(dy_mm: float, slit_distance_mm: float,
                                      screen_distance_m: float,
                                      refractive_index: float = 1.0) -> float:
    """Inverse of fringe_spacing_mm: λ = Δy·n·d/L (in nm)."""
    if screen_distance_m <= 0 or slit_distance_mm <= 0:
        return 0.0
    n = max(refractive_index, 1e-6)
    dy_m = dy_mm * 1e-3
    d_m = slit_distance_mm * 1e-3
    return (dy_m * n * d_m / screen_distance_m) * 1e9


class ClassicalEngine:
    """
    Computes exact Fraunhofer double-slit interference modulated by
    single-slit diffraction envelope across arbitrary screen coordinates.
    """

    def __init__(self, params: OpticalParameters | None = None):
        self.params = params or OpticalParameters()

    def update_params(self, **kwargs):
        """Update one or more optical parameters in place."""
        for key, val in kwargs.items():
            if hasattr(self.params, key):
                setattr(self.params, key, val)

    def compute_sin_theta(self, y_grid_m: np.ndarray) -> np.ndarray:
        """
        Exact trigonometric deflection angle sine:
        sin(theta) = y / sqrt(y^2 + L^2)
        Avoids small-angle paraxial approximation breakdown at large screen angles.
        """
        L = self.params.screen_distance_L_m
        return y_grid_m / np.sqrt(y_grid_m ** 2 + L ** 2)

    def compute_intensity_profile(self, y_grid_m: np.ndarray) -> np.ndarray:
        """
        Computes total intensity I(y) = I_0 * [sin(beta)/beta]^2 * cos^2(alpha)
        where:
          beta  = (pi * a / lambda_med) * sin(theta)
          alpha = (pi * d / lambda_med) * sin(theta)

        Using np.sinc(x) = sin(pi * x) / (pi * x):
          [sin(beta)/beta]^2 = np.sinc((a / lambda_med) * sin(theta)) ** 2
        """
        sin_theta = self.compute_sin_theta(y_grid_m)
        lambda_med = self.params.medium_wavelength_m
        a = self.params.slit_width_a_m
        d = self.params.slit_distance_d_m
        I0 = self.params.intensity_I0

        # Single-slit diffraction factor sinc^2(beta)
        # Note: np.sinc(u) calculates sin(pi*u)/(pi*u).
        # We need sin(pi * a / lambda_med * sin_theta) / (pi * a / lambda_med * sin_theta)
        # Thus argument u = (a * sin_theta) / lambda_med
        diffraction_factor = np.sinc((a * sin_theta) / lambda_med) ** 2

        # Double-slit interference factor cos^2(alpha)
        # alpha = (pi * d / lambda_med) * sin_theta
        alpha = (np.pi * d * sin_theta) / lambda_med
        interference_factor = np.cos(alpha) ** 2

        return I0 * diffraction_factor * interference_factor

    def compute_diffraction_envelope(self, y_grid_m: np.ndarray) -> np.ndarray:
        """
        Computes the bounding single-slit diffraction envelope alone:
        I_env(y) = I_0 * sinc^2(beta)
        """
        sin_theta = self.compute_sin_theta(y_grid_m)
        lambda_med = self.params.medium_wavelength_m
        a = self.params.slit_width_a_m
        I0 = self.params.intensity_I0

        return I0 * (np.sinc((a * sin_theta) / lambda_med) ** 2)

    def compute_single_slit_profile(self, y_grid_m: np.ndarray, slit_offset_m: float) -> np.ndarray:
        """
        Computes the single-slit diffraction pattern from an aperture shifted by slit_offset_m:
        Used for incoherent / collapsed quantum state modeling.
        """
        L = self.params.screen_distance_L_m
        dy = y_grid_m - slit_offset_m
        sin_theta_shifted = dy / np.sqrt(dy ** 2 + L ** 2)
        lambda_med = self.params.medium_wavelength_m
        a = self.params.slit_width_a_m
        I0 = self.params.intensity_I0 * 0.5

        return I0 * (np.sinc((a * sin_theta_shifted) / lambda_med) ** 2)

    def get_analytical_features(self, max_order: int = 15) -> dict:
        """
        Calculates theoretical fringe positions, spacing, diffraction envelope zeros,
        and identifies missing orders (where interference peaks coincide with diffraction zeros).
        """
        p = self.params
        lambda_med = p.medium_wavelength_m
        d = p.slit_distance_d_m
        a = p.slit_width_a_m
        L = p.screen_distance_L_m

        # Fringe spacing in paraxial regime: Delta y = (lambda * L) / d
        fringe_spacing_dy = (lambda_med * L) / d if d > 0 else 0.0
        angular_separation_rad = lambda_med / d if d > 0 else 0.0

        # Central diffraction envelope width between first minima: 2 * (lambda * L) / a
        central_envelope_width_m = (2.0 * lambda_med * L) / a if a > 0 else 0.0

        # Theoretical interference maxima positions: y_m = m * (lambda * L) / d
        orders = np.arange(-max_order, max_order + 1)
        # Using exact angle: d * sin(theta) = m * lambda => sin(theta) = m * lambda / d
        # y = L * tan(theta) = L * (sin(theta) / sqrt(1 - sin^2(theta)))
        valid_orders = []
        maxima_y = []
        for m in orders:
            sin_th = (m * lambda_med) / d
            if abs(sin_th) < 0.999:
                y = L * (sin_th / np.sqrt(1.0 - sin_th ** 2))
                maxima_y.append(y)
                valid_orders.append(int(m))

        # Theoretical envelope zeros (single-slit diffraction minima):
        # a * sin(theta) = p * lambda (p != 0)
        envelope_zeros_y = []
        if a > 0:
            for p_order in range(-max_order, max_order + 1):
                if p_order == 0:
                    continue
                sin_th = (p_order * lambda_med) / a
                if abs(sin_th) < 0.999:
                    y = L * (sin_th / np.sqrt(1.0 - sin_th ** 2))
                    envelope_zeros_y.append(y)

        # Missing Orders Detection:
        # Occur when d / a = m / p => m = p * (d / a)
        ratio = d / a if a > 0 else 0.0
        missing_orders = []
        nearest_ratio = round(ratio)
        if abs(ratio - nearest_ratio) < 0.04 and nearest_ratio >= 1:
            for p_val in range(1, 5):
                m_missing = p_val * nearest_ratio
                if m_missing <= max_order:
                    missing_orders.extend([m_missing, -m_missing])
            missing_orders = sorted(list(set(missing_orders)))

        # Michelson Fringe Visibility V = (I_max - I_min) / (I_max + I_min)
        # At center, I_max = I0, I_min = 0 => V = 1.0
        visibility = 1.0

        return {
            "fringe_spacing_dy_m": fringe_spacing_dy,
            "fringe_spacing_dy_mm": fringe_spacing_dy * 1000.0,
            "angular_separation_rad": angular_separation_rad,
            "angular_separation_deg": np.degrees(angular_separation_rad),
            "central_envelope_width_m": central_envelope_width_m,
            "central_envelope_width_mm": central_envelope_width_m * 1000.0,
            "maxima_y_m": np.array(maxima_y),
            "maxima_orders": valid_orders,
            "envelope_zeros_y_m": np.array(envelope_zeros_y),
            "missing_orders": missing_orders,
            "ratio_d_over_a": ratio,
            "visibility": visibility
        }
