"""
Quantum Mechanics Engine for Young's Double-Slit Experiment.
Simulates single-particle emission, de Broglie matter waves, quantum superposition,
observer effect (which-way detector collapse), and vectorized Monte Carlo sampling.
"""

import numpy as np
from typing import Tuple, List, Optional
from physics.particle_types import ParticleCategory, ParticleProperties, PARTICLE_PRESETS
from physics.classical_engine import OpticalParameters, ClassicalEngine

class QuantumEngine:
    """
    Simulates single-particle quantum interference and wave-particle duality.
    Maintains particle buffers, probability distributions, and the observer detector state.
    """

    def __init__(
        self,
        particle_category: ParticleCategory = ParticleCategory.PHOTON,
        optical_params: Optional[OpticalParameters] = None,
        energy_ev: Optional[float] = None
    ):
        self.particle = PARTICLE_PRESETS[particle_category]
        self.optical_params = optical_params or OpticalParameters()
        self.energy_ev = energy_ev if energy_ev is not None else self.particle.default_energy_ev
        self.velocity_ms = self.particle.default_velocity_ms

        # Observer State
        self.which_way_active: bool = False
        self.decoherence_factor: float = 0.0  # 0.0 = coherent superposition, 1.0 = fully collapsed

        # Accumulated particle impact coordinates on detector screen (in meters)
        self.hits_y: List[float] = []
        self.hits_z: List[float] = []

        # Internal classical engine helper for optical calculations
        self.classical_engine = ClassicalEngine(self.optical_params)

        # CDF cache for high-speed inverse-transform Monte Carlo sampling
        self._cached_y_grid: Optional[np.ndarray] = None
        self._cached_cdf: Optional[np.ndarray] = None
        self._cache_dirty: bool = True

        self.update_wavelength()

    def set_particle(self, category: ParticleCategory, energy_ev: Optional[float] = None):
        """Switch particle type (Photon, Electron, Buckyball)."""
        self.particle = PARTICLE_PRESETS[category]
        self.energy_ev = energy_ev if energy_ev is not None else self.particle.default_energy_ev
        self.velocity_ms = self.particle.default_velocity_ms
        self.update_wavelength()
        self.invalidate_cache()

    def set_energy(self, energy_ev: float):
        """Update particle kinetic energy / accelerating voltage."""
        self.energy_ev = max(energy_ev, 1e-6)
        self.update_wavelength()
        self.invalidate_cache()

    def set_velocity(self, velocity_ms: float):
        """Update particle velocity (for massive particles like Buckyballs)."""
        self.velocity_ms = max(velocity_ms, 1.0)
        self.update_wavelength()
        self.invalidate_cache()

    def set_which_way_detector(self, active: bool, decoherence: float = 1.0):
        """
        Toggle the Which-Way detector (Observer Effect).
        When active=True, decoherence=1.0 causes complete wavefunction collapse.
        """
        self.which_way_active = active
        self.decoherence_factor = decoherence if active else 0.0
        self.invalidate_cache()

    def update_wavelength(self):
        """Calculate and set de Broglie wavelength into optical parameters."""
        wavelength = self.particle.calculate_de_broglie_wavelength(
            energy_ev=self.energy_ev,
            velocity_ms=self.velocity_ms
        )
        self.optical_params.wavelength_m = wavelength
        self.classical_engine.update_params(wavelength_m=wavelength)
        self.invalidate_cache()

    def invalidate_cache(self):
        """Flags that CDF distribution must be recomputed on next sample."""
        self._cache_dirty = True

    def compute_probability_density(self, y_grid_m: np.ndarray) -> np.ndarray:
        """
        Computes the theoretical probability density function P(y):
        - Coherent Superposition (Which-Way OFF):
            P(y) = |Psi_1(y) + Psi_2(y)|^2 propto sinc^2(beta) * cos^2(alpha)
        - Wavefunction Collapse (Which-Way ON):
            P(y) = 0.5 * |Psi_1(y)|^2 + 0.5 * |Psi_2(y)|^2 (sum of 2 single slits)
        - Partial Decoherence D in [0, 1]:
            P(y) = (1 - D) * P_coherent(y) + D * P_collapsed(y)
        """
        # 1. Coherent interference pattern
        p_coherent = self.classical_engine.compute_intensity_profile(y_grid_m)

        # 2. Incoherent / collapsed single-slit sum pattern
        d = self.optical_params.slit_distance_d_m
        p_slit1 = self.classical_engine.compute_single_slit_profile(y_grid_m, slit_offset_m=+d / 2.0)
        p_slit2 = self.classical_engine.compute_single_slit_profile(y_grid_m, slit_offset_m=-d / 2.0)
        p_collapsed = p_slit1 + p_slit2

        D = self.decoherence_factor if self.which_way_active else 0.0
        p_total = (1.0 - D) * p_coherent + D * p_collapsed

        # Numerical stabilization & normalization
        p_total = np.maximum(p_total, 1e-12)
        integral = np.trapz(p_total, y_grid_m)
        if integral > 0:
            p_total /= integral

        return p_total

    def _ensure_cdf(self, screen_half_span_m: float, grid_points: int = 2500):
        """Constructs and caches cumulative distribution function for inverse transform sampling."""
        if not self._cache_dirty and self._cached_y_grid is not None and self._cached_cdf is not None:
            # Check if grid span matches (relative tolerance — absolute 1e-7 m
            # would exceed a C60 half-span of ~9e-11 m by three orders of magnitude)
            tol = max(1e-30, abs(screen_half_span_m) * 1e-6)
            if abs(self._cached_y_grid[-1] - screen_half_span_m) <= tol:
                return

        y_grid = np.linspace(-screen_half_span_m, screen_half_span_m, grid_points)
        pdf = self.compute_probability_density(y_grid)

        # Compute cumulative integral via trapezoidal cumulative sum
        cdf = np.zeros_like(y_grid)
        cdf[1:] = np.cumsum(0.5 * (pdf[:-1] + pdf[1:]) * np.diff(y_grid))
        cdf /= cdf[-1]  # Ensure strictly normalized to [0, 1]
        cdf[0] = 0.0

        self._cached_y_grid = y_grid
        self._cached_cdf = cdf
        self._cache_dirty = False

    def sample_particles(
        self,
        count: int,
        screen_span_y_m: float,
        screen_span_z_m: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fast vectorized Monte Carlo inverse-CDF sampling:
        Samples `count` particle impact coordinates (batch_y, batch_z) in SI meters.
        """
        half_y = screen_span_y_m / 2.0
        self._ensure_cdf(half_y)

        # 1. Uniform random variates in [0, 1]
        u = np.random.uniform(0.0, 1.0, size=count)

        # 2. Monotonic inverse interpolation
        batch_y = np.interp(u, self._cached_cdf, self._cached_y_grid)

        # 3. Vertical z-coordinate (Gaussian beam height falloff along slit length)
        sigma_z = screen_span_z_m / 6.0  # 99.7% of impacts within slit height
        batch_z = np.random.normal(0.0, sigma_z, size=count)
        batch_z = np.clip(batch_z, -screen_span_z_m / 2.0, screen_span_z_m / 2.0)

        return batch_y, batch_z

    def accumulate_hits(self, batch_y: np.ndarray, batch_z: np.ndarray):
        """Appends new particle hits to the accumulator buffer."""
        self.hits_y.extend(batch_y.tolist())
        self.hits_z.extend(batch_z.tolist())

    def reset_hits(self):
        """Clears all accumulated particle hits."""
        self.hits_y.clear()
        self.hits_z.clear()

    @property
    def total_hits(self) -> int:
        """Returns total number of detected particle hits."""
        return len(self.hits_y)
