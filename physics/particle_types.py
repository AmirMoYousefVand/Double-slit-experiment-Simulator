"""
Particle types and physical properties for quantum double-slit simulation.
"""

from dataclasses import dataclass
from enum import Enum
import math
from config import (
    PLANCK_CONSTANT,
    SPEED_OF_LIGHT,
    ELEMENTARY_CHARGE,
    ELECTRON_MASS,
    BUCKYBALL_MASS
)

class ParticleCategory(Enum):
    PHOTON = "photon"
    ELECTRON = "electron"
    BUCKYBALL = "buckyball"

@dataclass
class ParticleProperties:
    category: ParticleCategory
    name_en: str
    name_fa: str
    symbol: str
    mass_kg: float
    charge_c: float
    default_energy_ev: float
    default_velocity_ms: float
    min_energy_ev: float
    max_energy_ev: float
    color_hex: str
    description_en: str
    description_fa: str

    def calculate_de_broglie_wavelength(self, energy_ev: float | None = None, velocity_ms: float | None = None) -> float:
        """
        Calculates the de Broglie wavelength lambda = h / p (in meters).
        Supports relativistic energy-momentum dispersion where relevant.
        """
        if self.category == ParticleCategory.PHOTON:
            # E = hc / lambda => lambda = hc / E
            ev = energy_ev if energy_ev is not None else self.default_energy_ev
            energy_joules = ev * ELEMENTARY_CHARGE
            return (PLANCK_CONSTANT * SPEED_OF_LIGHT) / energy_joules

        elif self.category == ParticleCategory.ELECTRON:
            # Relativistic electron de Broglie wavelength:
            # E_k = V_0 * e
            # p = sqrt(2 * m_e * E_k * (1 + E_k / (2 * m_e * c^2)))
            ev = energy_ev if energy_ev is not None else self.default_energy_ev
            energy_joules = ev * ELEMENTARY_CHARGE
            rest_energy = ELECTRON_MASS * (SPEED_OF_LIGHT ** 2)
            rel_factor = 1.0 + (energy_joules / (2.0 * rest_energy))
            p = math.sqrt(2.0 * ELECTRON_MASS * energy_joules * rel_factor)
            return PLANCK_CONSTANT / p

        elif self.category == ParticleCategory.BUCKYBALL:
            # Thermal molecule: p = M * v
            v = velocity_ms if velocity_ms is not None else self.default_velocity_ms
            p = self.mass_kg * v
            return PLANCK_CONSTANT / p

        else:
            raise ValueError(f"Unknown particle category: {self.category}")


# Standard Particle Presets
PARTICLE_PRESETS = {
    ParticleCategory.PHOTON: ParticleProperties(
        category=ParticleCategory.PHOTON,
        name_en="Photon (Single Light Quantum)",
        name_fa="فوتون (کوانتوم منفرد نور)",
        symbol="γ",
        mass_kg=0.0,
        charge_c=0.0,
        default_energy_ev=1.96,       # ~ 632.8 nm (Red)
        default_velocity_ms=SPEED_OF_LIGHT,
        min_energy_ev=1.5,
        max_energy_ev=3.5,
        color_hex="#FF3B30",
        description_en="Zero rest-mass electromagnetic quantum traveling at speed c.",
        description_fa="کوانتوم الکترومغناطیسی با جرم سکون صفر که با سرعت نور c حرکت می‌کند."
    ),
    ParticleCategory.ELECTRON: ParticleProperties(
        category=ParticleCategory.ELECTRON,
        name_en="Electron (Matter Wave)",
        name_fa="الکترون (موج مادی)",
        symbol="e⁻",
        mass_kg=ELECTRON_MASS,
        charge_c=-ELEMENTARY_CHARGE,
        default_energy_ev=100.0,      # 100 eV accelerating potential => lambda ~ 0.123 nm
        default_velocity_ms=5.93e6,   # ~ 2% of c
        min_energy_ev=10.0,
        max_energy_ev=1000.0,
        color_hex="#00F0FF",          # Phosphor cyan
        description_en="Fundamental fermion demonstrating de Broglie matter wave interference.",
        description_fa="فرمیون بنیادی حامل بار منفی؛ نمایش‌دهنده امواج مادی دوبروی."
    ),
    ParticleCategory.BUCKYBALL: ParticleProperties(
        category=ParticleCategory.BUCKYBALL,
        name_en="Buckyball C₆₀ (Macromolecule)",
        name_fa="باکی‌بال C₆₀ (درشت‌مولکول کربنی)",
        symbol="C₆₀",
        mass_kg=BUCKYBALL_MASS,
        charge_c=0.0,
        default_energy_ev=0.15,
        default_velocity_ms=200.0,    # ~ 200 m/s thermal velocity => lambda ~ 2.8 pm
        min_energy_ev=0.05,
        max_energy_ev=0.50,
        color_hex="#00E676",          # Emerald jade
        description_en="Massive complex molecule (720 amu) verified by Zeilinger's 1999 experiment.",
        description_fa="مولکول بزرگ ۷۲۰ واحد جرمی (آزمایش تاریخی تسایلینگر در سال ۱۹۹۹)."
    )
}
