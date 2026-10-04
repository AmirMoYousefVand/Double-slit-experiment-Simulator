"""
Unit-aware length formatting shared by views, metrics, calculations and exports.
Chooses a sensible metric prefix (mm / µm / nm / pm) for a length in meters so
sub-micron matter-wave quantities never render as "0.000 mm".
"""

from typing import Tuple

_DEFAULT_DECIMALS = {"mm": 3, "µm": 3, "nm": 4, "pm": 2}


def choose_length_scale(value_m: float) -> Tuple[float, str]:
    """Returns (scale, unit) to convert meters into a readable magnitude.

    The µm threshold is 1e-7 (not the SI 1e-6) so sub-micron fringe spacings
    read as "0.490 µm" rather than "490.4000 nm".
    """
    a = abs(value_m)
    if a >= 1e-3:
        return 1e3, "mm"
    if a >= 1e-7:
        return 1e6, "µm"
    if a >= 1e-10:
        return 1e9, "nm"
    return 1e12, "pm"


def format_length(value_m: float, decimals: int | None = None) -> str:
    """Formats a length given in meters, e.g. 4.904e-7 -> '0.490 µm'."""
    scale, unit = choose_length_scale(value_m)
    if decimals is None:
        decimals = _DEFAULT_DECIMALS[unit]
    return f"{value_m * scale:.{decimals}f} {unit}"
