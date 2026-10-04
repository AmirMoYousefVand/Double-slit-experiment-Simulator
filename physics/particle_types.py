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
from utils.units import format_length

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


def de_broglie_formula(category: ParticleCategory) -> dict:
    """Single source of truth for the de Broglie relation shown per particle.

    Returns {"plain": <label text>, "mathtext": <matplotlib mathtext>}.
    """
    if category == ParticleCategory.PHOTON:
        return {
            "plain": "λ_dB = h / p = h·c / E",
            "mathtext": r"$\lambda_{dB} = \frac{h}{p} = \frac{h c}{E}$",
        }
    if category == ParticleCategory.ELECTRON:
        return {
            "plain": "λ_dB = h / p = h / √(2·m_e·E_k·(1 + E_k/(2·m_e·c²)))",
            "mathtext": r"$\lambda_{dB} = \frac{h}{p} = \frac{h}{\sqrt{2 m_e E_k\left(1+\frac{E_k}{2 m_e c^2}\right)}}$",
        }
    if category == ParticleCategory.BUCKYBALL:
        return {
            "plain": "λ_dB = h / p = h / (M·v)",
            "mathtext": r"$\lambda_{dB} = \frac{h}{p} = \frac{h}{M v}$",
        }
    raise ValueError(f"Unknown particle category: {category}")


def de_broglie_substitution(
    category: ParticleCategory,
    name_label: str,
    energy_ev: float,
    velocity_ms: float,
    lambda_m: float,
) -> str:
    """Live numerical substitution line for the de Broglie relation.

    C60 derives E_k from the actual velocity (½Mv²) — never from a stale
    energy_ev that set_velocity does not update.
    """
    wl = format_length(lambda_m)
    if category == ParticleCategory.PHOTON:
        return f"{name_label} | E = {energy_ev:.2f} eV => λ_dB = h·c/E = {wl}"
    if category == ParticleCategory.ELECTRON:
        return f"{name_label} | E_k = {energy_ev:.1f} eV => λ_dB = {wl}"
    if category == ParticleCategory.BUCKYBALL:
        props = PARTICLE_PRESETS[category]
        ek_ev = 0.5 * props.mass_kg * (velocity_ms ** 2) / ELEMENTARY_CHARGE
        return f"{name_label} | v = {velocity_ms:.1f} m/s => E_k = ½Mv² = {ek_ev:.3f} eV => λ_dB = {wl}"
    raise ValueError(f"Unknown particle category: {category}")
