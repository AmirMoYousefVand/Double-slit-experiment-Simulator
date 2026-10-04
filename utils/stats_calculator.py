"""
Statistical calculations and physics validation metrics for Young's experiment.
"""

from typing import Dict, Any, List, Optional
import numpy as np

class StatsCalculator:
    """
    Computes fringe contrast (Michelson visibility), missing order analysis,
    and Pearson chi-square goodness-of-fit for quantum particle convergence.
    """

    @staticmethod
    def calculate_visibility(intensity_profile: np.ndarray, search_span: Optional[int] = None) -> float:
        """
        Calculates Michelson Fringe Visibility:
        V = (I_max - I_min) / (I_max + I_min)
        Evaluates contrast between central peak and adjacent first interference minimum.
        In coherent state: V ~ 1.0. In collapsed / observer state: V ~ 0.0 (no fringes).
        """
        if len(intensity_profile) == 0:
            return 1.0

        mid = len(intensity_profile) // 2
        i_max = float(intensity_profile[mid])
        if i_max <= 1e-12:
            i_max = float(np.max(intensity_profile))

        # Look for first interference minimum starting from center to the right
        limit = search_span if search_span is not None else max(len(intensity_profile) // 16, 8)
        limit = min(limit, len(intensity_profile) - mid - 1)
        right_half = intensity_profile[mid : mid + limit]

        if len(right_half) < 3:
            return 1.0

        # Find first local minimum where slope turns upwards
        diffs = np.diff(right_half)
        min_indices = np.where(diffs > 0)[0]
        if len(min_indices) > 0:
            i_min = float(right_half[min_indices[0]])
        else:
            i_min = float(right_half[-1])

        denom = i_max + i_min
        if denom <= 1e-12:
            return 0.0
        return float(np.clip((i_max - i_min) / denom, 0.0, 1.0))

    @staticmethod
    def compute_chi_square(
        observed_counts: np.ndarray,
        expected_prob: np.ndarray,
        total_hits: int
    ) -> Dict[str, float]:
        """
        Calculates Pearson Chi-Square test comparing observed quantum histogram
        counts against the theoretical probability density.
        """
        if total_hits < 50 or len(observed_counts) == 0:
            return {"chi2": 0.0, "chi2_reduced": 0.0, "p_value_indicator": 1.0}

        # Expected counts per bin
        expected_counts = expected_prob * total_hits
        # Mask out bins with very low expectation to avoid division instability
        valid_mask = expected_counts > 2.0

        if np.sum(valid_mask) < 3:
            return {"chi2": 0.0, "chi2_reduced": 0.0, "p_value_indicator": 1.0}

        obs = observed_counts[valid_mask]
        exp = expected_counts[valid_mask]

        chi2 = float(np.sum(((obs - exp) ** 2) / exp))
        dof = max(int(np.sum(valid_mask)) - 1, 1)
        chi2_red = chi2 / dof

        # Empirical quality indicator: chi2_red close to 1 indicates excellent convergence
        quality = 1.0 / (1.0 + abs(chi2_red - 1.0))

        return {
            "chi2": chi2,
            "chi2_reduced": chi2_red,
            "convergence_quality": float(np.clip(quality, 0.0, 1.0))
        }

    @staticmethod
    def format_missing_orders(missing_orders: List[int], is_persian: bool = False) -> str:
        """Formats list of missing interference orders for UI display."""
        if not missing_orders:
            return "هیچ" if is_persian else "None"
        pos_orders = [str(abs(m)) for m in missing_orders if m > 0]
        if not pos_orders:
            return "هیچ" if is_persian else "None"
        return "m = ±" + ", ±".join(pos_orders[:4])
