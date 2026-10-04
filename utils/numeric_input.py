"""
Numeric input parsing and clamping helper for manual parameter entry fields.

Single validation choke-point used by all parameter panels (optics, quantum,
point inspector): normalizes Persian/Arabic digits, tolerant of partial input,
and clamps to PARAM_LIMITS ranges.
"""

from typing import Optional

from config import PARAM_LIMITS

# Persian (۰-۹) + Arabic-Indic (٠-٩) digit translation to Latin digits
_FA_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

# Invisible directional controls that may leak from RTL copy/paste
_BIDI_CONTROLS = ("‎", "‏", "‪", "‫", "‬",
                  "‭", "‮", "⁦", "⁧", "⁨", "⁩")


def parse_number(raw: str) -> Optional[float]:
    """
    Parses a free-typed numeric string into float.

    Normalizes Persian/Arabic digits and separators (٫ → ., ٬ → nothing).
    Returns None for empty/partial input ("", "-", ".", "+") so the caller
    can soft-ignore without flashing an error mid-keystroke.
    """
    if raw is None:
        return None
    text = str(raw).strip()
    for ch in _BIDI_CONTROLS:
        text = text.replace(ch, "")
    text = text.translate(_FA_DIGITS)
    text = text.replace("٫", ".").replace("/", ".")
    text = text.replace("٬", "").replace(",", "").replace(" ", "")
    # Strip a trailing unit letter run is NOT done here; entries hold pure numbers.
    if text in ("", "-", "+", ".", "-.", "+."):
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    # Guard against NaN / infinities typed or pasted in
    if value != value or value in (float("inf"), float("-inf")):
        return None
    return value


def clamp(param_key: str, value: float) -> float:
    """
    Clamps value into PARAM_LIMITS[param_key] range.

    No step snapping: manual entries may hold exact values (e.g. 632.8 nm)
    that fall between slider step ticks. Unknown keys pass through unchanged.
    """
    cfg = PARAM_LIMITS.get(param_key)
    if cfg is None:
        return value
    if value < cfg["min"]:
        return float(cfg["min"])
    if value > cfg["max"]:
        return float(cfg["max"])
    return float(value)


def clamp_range(value: float, minimum: float, maximum: float) -> float:
    """Clamps value into an explicit [minimum, maximum] range."""
    if value < minimum:
        return float(minimum)
    if value > maximum:
        return float(maximum)
    return float(value)
