"""
Comprehensive Export Service for Double-Slit Simulator.
Supports:
1. Enhanced 22-column scientific CSV dataset with full parameter metadata
2. High-resolution Matplotlib figures (PNG, PDF, SVG at 300 DPI)
3. 2D Detector Screen image export with calibrated millimeter ruler
4. High-resolution Calculations & Equations summary image export (PNG)
5. 3D Wavefront OBJ + MTL + Texture model export
6. Microsoft Word (.docx) lab reports with native OMML editable equations
"""

import csv
import os
import math
import zipfile
import json
import tempfile
from typing import Dict, Any, Optional, Tuple, List
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

from utils.color_utils import ColorUtils
from utils.obj_exporter import ObjExporter
from utils.docx_exporter import DocxEquationExporter
from utils.font_manager import FontManager
from utils.localization import LocalizationService
from utils.units import format_length, choose_length_scale
from physics.particle_types import de_broglie_formula, de_broglie_substitution

class ExportService:
    """Coordinates all scientific data, 3D model, document, and image export pipelines."""

    @staticmethod
    def export_csv(
        filepath: str,
        y_grid_m: np.ndarray,
        intensity_theory: np.ndarray,
        quantum_histogram: Optional[np.ndarray],
        params_dict: Dict[str, Any],
        stats_dict: Dict[str, Any],
        total_hits: int = 0
    ) -> Dict[str, Any]:
        """
        Exports simulation data table with 22 analytical columns and comprehensive metadata header.
        """
        try:
            L = params_dict.get("screen_distance_L_m", 1.0)
            d = params_dict.get("slit_distance_d_m", 0.25e-3)
            a = params_dict.get("slit_width_a_m", 0.04e-3)
            wl_vac = params_dict.get("wavelength_m", 632.8e-9)
            n = params_dict.get("refractive_index_n", 1.0)
            wl_med = wl_vac / max(n, 1e-6)

            with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # --------------------------------------------------------------
                # 1. Metadata Header Block
                # --------------------------------------------------------------
                writer.writerow(["# =============================================================================="])
                writer.writerow(["# Thomas Young Double-Slit Experiment Simulation Dataset"])
                writer.writerow(["# Software: Comprehensive Classical & Quantum Double-Slit Simulator v2.0"])
                writer.writerow([f"# Simulation Mode: {params_dict.get('simulation_mode', 'classical').capitalize()}"])
                writer.writerow([f"# Vacuum Wavelength (lambda_0): {wl_vac:.6e} m ({format_length(wl_vac)})"])
                writer.writerow([f"# Medium Refractive Index (n): {n:.4f}"])
                writer.writerow([f"# Medium Wavelength (lambda_med): {wl_med:.6e} m ({format_length(wl_med)})"])
                writer.writerow([f"# Slit Separation (d): {d:.6e} m ({d*1000.0:.4f} mm)"])
                writer.writerow([f"# Slit Aperture Width (a): {a:.6e} m ({a*1000.0:.4f} mm)"])
                writer.writerow([f"# Slit-to-Screen Distance (L): {L:.4f} m"])
                writer.writerow([f"# Slit Geometry Ratio (d/a): {d/max(a, 1e-7):.4f}"])
                writer.writerow([f"# Theoretical Fringe Spacing (Delta_y): {stats_dict.get('fringe_spacing_dy_m', 0.0):.6e} m ({format_length(stats_dict.get('fringe_spacing_dy_m', 0.0))})"])
                writer.writerow([f"# Angular Separation (theta): {stats_dict.get('angular_separation_rad', 0.0):.6e} rad ({stats_dict.get('angular_separation_rad', 0.0)*1000.0:.4f} mrad)"])
                writer.writerow([f"# Central Envelope Width: {stats_dict.get('central_envelope_width_m', 0.0):.6e} m ({format_length(stats_dict.get('central_envelope_width_m', 0.0))})"])
                writer.writerow([f"# Missing Interference Orders: {stats_dict.get('missing_orders', 'None')}"])
                writer.writerow([f"# Michelson Fringe Visibility (V): {stats_dict.get('visibility', 1.0):.4f}"])
                writer.writerow([f"# Which-Way Observer Active: {params_dict.get('which_way_observer_active', False)}"])
                writer.writerow([f"# Total Accumulated Quantum Hits (N): {total_hits}"])
                writer.writerow(["# =============================================================================="])
                writer.writerow([])

                # --------------------------------------------------------------
                # 2. 22 Column Headers
                # --------------------------------------------------------------
                headers = [
                    "Point_Index",
                    "Screen_Position_y_m",
                    "Screen_Position_y_mm",
                    "Deflection_Angle_theta_rad",
                    "Deflection_Angle_theta_mrad",
                    "Path_Length_r1_m",
                    "Path_Length_r2_m",
                    "Exact_Path_Difference_Delta_r_m",
                    "Exact_Path_Difference_Delta_r_nm",
                    "Paraxial_Path_Difference_nm",
                    "Path_Difference_Error_nm",
                    "Phase_Difference_Delta_phi_rad",
                    "Phase_Difference_Delta_phi_deg",
                    "Diffraction_Beta_rad",
                    "Diffraction_Envelope_sinc2",
                    "Interference_Alpha_rad",
                    "Interference_Factor_cos2",
                    "Theoretical_Intensity_Normalized",
                    "Theoretical_Probability_Density_P_y",
                    "Expected_Quantum_Counts",
                    "Simulated_Quantum_Counts",
                    "Standardized_Residual_Z"
                ]
                writer.writerow(headers)

                # Probability density normalization
                dy = abs(y_grid_m[1] - y_grid_m[0]) if len(y_grid_m) > 1 else 1.0
                norm_integral = np.trapz(intensity_theory, y_grid_m)
                pdf_theory = (intensity_theory / norm_integral) if norm_integral > 0 else intensity_theory

                has_quantum = quantum_histogram is not None and len(quantum_histogram) == len(y_grid_m)

                for i in range(len(y_grid_m)):
                    y_m = y_grid_m[i]
                    y_mm = y_m * 1000.0

                    sin_th = y_m / math.sqrt(y_m**2 + L**2)
                    th_rad = math.asin(sin_th)
                    th_mrad = th_rad * 1000.0

                    r1 = math.sqrt(L**2 + (y_m - d/2.0)**2)
                    r2 = math.sqrt(L**2 + (y_m + d/2.0)**2)
                    dr_exact_m = abs(r2 - r1)
                    dr_exact_nm = dr_exact_m * 1e9

                    dr_parax_nm = abs(d * sin_th) * 1e9
                    dr_err_nm = abs(dr_exact_nm - dr_parax_nm)

                    phase_rad = (2.0 * math.pi * dr_exact_m) / wl_med
                    phase_deg = math.degrees(phase_rad) % 360.0

                    beta = (math.pi * a * sin_th) / wl_med
                    sinc2 = (math.sin(beta) / beta)**2 if abs(beta) > 1e-6 else 1.0

                    alpha = (math.pi * d * sin_th) / wl_med
                    cos2 = math.cos(alpha)**2

                    i_norm = intensity_theory[i]
                    p_y = pdf_theory[i]

                    exp_counts = p_y * dy * total_hits if total_hits > 0 else 0.0
                    sim_counts = int(quantum_histogram[i]) if has_quantum else 0

                    denom_z = math.sqrt(max(exp_counts, 1.0))
                    z_res = (sim_counts - exp_counts) / denom_z if total_hits > 0 else 0.0

                    row = [
                        i,
                        f"{y_m:.6e}",
                        f"{y_mm:.6e}",
                        f"{th_rad:.6e}",
                        f"{th_mrad:.4f}",
                        f"{r1:.6f}",
                        f"{r2:.6f}",
                        f"{dr_exact_m:.6e}",
                        f"{dr_exact_nm:.3f}",
                        f"{dr_parax_nm:.3f}",
                        f"{dr_err_nm:.4f}",
                        f"{phase_rad:.4f}",
                        f"{phase_deg:.2f}",
                        f"{beta:.4f}",
                        f"{sinc2:.6f}",
                        f"{alpha:.4f}",
                        f"{cos2:.6f}",
                        f"{i_norm:.6f}",
                        f"{p_y:.6e}",
                        f"{exp_counts:.2f}",
                        sim_counts,
                        f"{z_res:.3f}"
                    ]
                    writer.writerow(row)

            return {"success": True, "message": f"Successfully exported 22-column dataset to {os.path.basename(filepath)}"}
        except Exception as e:
            return {"success": False, "message": f"CSV export error: {str(e)}"}

    @staticmethod
    def export_figure(filepath: str, figure: Figure, dpi: int = 300) -> Dict[str, Any]:
        """Exports a Matplotlib figure at 300 DPI."""
        try:
            figure.savefig(filepath, dpi=dpi, bbox_inches="tight", facecolor=figure.get_facecolor())
            return {"success": True, "message": f"Saved figure to {os.path.basename(filepath)}"}
        except Exception as e:
            return {"success": False, "message": f"Figure save error: {str(e)}"}

    @staticmethod
    def export_screen_image(
        filepath: str,
        intensity_1d: np.ndarray,
        base_rgb: Tuple[int, int, int],
        span_y_m: float,
        quantum_buffer: Optional[np.ndarray] = None,
        is_quantum: bool = False
    ) -> Dict[str, Any]:
        """
        Exports high-resolution annotated 2D screen detector image with calibrated millimeter ruler.
        """
        try:
            w, h = 1600, 600
            if is_quantum and quantum_buffer is not None:
                # Resize quantum buffer to high-res
                clipped = np.clip(quantum_buffer, 0, 255).astype(np.uint8)
                base_img = Image.fromarray(clipped).resize((w, h), Image.Resampling.BILINEAR)
            else:
                img_array = ColorUtils.generate_screen_image_array(intensity_1d, base_rgb, height=h, width=w)
                base_img = Image.fromarray(img_array)

            # Draw millimeter ruler markings
            draw = ImageDraw.Draw(base_img)
            y_ruler = h - 35
            draw.line([(30, y_ruler), (w - 30, y_ruler)], fill=(120, 120, 120), width=2)

            half_span_m = span_y_m / 2.0
            scale, unit = choose_length_scale(half_span_m)
            half_disp = half_span_m * scale
            mid_x = w // 2

            ticks = [
                (mid_x, f"0.0 {unit}", True),
                (mid_x - w // 4, f"-{half_disp/2:.2f} {unit}", False),
                (mid_x + w // 4, f"+{half_disp/2:.2f} {unit}", False),
                (60, f"-{half_disp:.2f} {unit}", False),
                (w - 100, f"+{half_disp:.2f} {unit}", False),
            ]

            for x_pos, label, is_center in ticks:
                tick_len = 14 if is_center else 8
                col = (0, 240, 255) if is_center else (160, 160, 160)
                draw.line([(x_pos, y_ruler - tick_len), (x_pos, y_ruler + tick_len)], fill=col, width=2)
                draw.text((x_pos - 20, y_ruler + 10), label, fill=col)

            base_img.save(filepath, dpi=(300, 300))
            return {"success": True, "message": f"Saved 2D Screen image to {os.path.basename(filepath)}"}
        except Exception as e:
            return {"success": False, "message": f"Screen image save error: {str(e)}"}

    @staticmethod
    def export_calculations_image(
        filepath: str,
        optical_params: Any,
        features: Dict[str, Any],
        inspector_y_mm: float = 0.0,
        is_persian: bool = False,
        quantum_engine: Any = None
    ) -> Dict[str, Any]:
        """
        Renders complete mathematical derivations and Point Inspector summary into a publication image.
        Fully supports Persian text reshaping and typography.
        """
        try:
            fig = Figure(figsize=(11, 8.5), dpi=300, facecolor="#0F172A")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#0F172A")
            ax.axis("off")

            # Title
            if is_persian:
                title_text = LocalizationService.reshape_text("فرمول‌ها و محاسبات تحلیلی آزمایش دو شکاف یانگ")
                fprop_title = FontManager.get_mpl_persian_prop(16)
            else:
                title_text = "Thomas Young Double-Slit Physics Formulations"
                fprop_title = FontManager.get_mpl_number_prop(16)
            ax.text(0.5, 0.95, title_text, color="#38BDF8", fontsize=16, weight="bold", ha="center", fontproperties=fprop_title)

            wl_nm = optical_params.wavelength_m * 1e9
            d_mm = optical_params.slit_distance_d_m * 1000.0
            a_mm = optical_params.slit_width_a_m * 1000.0
            L_m = optical_params.screen_distance_L_m
            n = optical_params.refractive_index_n
            dy_str = format_length(features.get("fringe_spacing_dy_m", 0.0))
            env_str = format_length(features.get("central_envelope_width_m", 0.0))

            # De Broglie equation block — per-particle when a quantum engine is
            # supplied, generic λ_dB = h/p otherwise (universally correct)
            if quantum_engine is not None:
                _cat = quantum_engine.particle.category
                _q_name = quantum_engine.particle.name_fa if is_persian else quantum_engine.particle.name_en
                db_formula = de_broglie_formula(_cat)["mathtext"]
                db_sub = de_broglie_substitution(
                    _cat, _q_name, quantum_engine.energy_ev,
                    quantum_engine.velocity_ms, quantum_engine.optical_params.wavelength_m
                )
                if is_persian:
                    db_sub = LocalizationService.reshape_text(db_sub)
            else:
                db_formula = r"$\lambda_{dB} = \frac{h}{p}$"
                db_sub = (LocalizationService.reshape_text("پراکندگی نسبیتی برای الکترون‌ها، فوتون‌ها و باکی‌بال‌ها")
                          if is_persian else
                          r"Photon hc/E | Relativistic electron h/p | Buckyball h/(M·v)")

            # Equations blocks with bilingual support
            if not is_persian:
                eqs = [
                    ("1. Optical Path Difference:", r"$\Delta r = r_2 - r_1 = d \sin\theta \approx d \frac{y}{L}$",
                     f"Δr = ({d_mm:.3f} mm) × sin(θ) ≈ {d_mm:.3f} mm × (y / {L_m:.2f} m)"),
                    ("2. Interference Fringes:", r"$y_m = m \frac{\lambda L}{n \cdot d}, \quad y'_m = \left(m + \frac{1}{2}\right) \frac{\lambda L}{n \cdot d}$",
                     f"Fringe Spacing Δy = {dy_str} | Central Max y₀ = 0 | Order 1: ±{dy_str}"),
                    ("3. Combined Fraunhofer Intensity:", r"$I(y) = I_0 \left[\frac{\sin(\beta)}{\beta}\right]^2 \cos^2(\alpha), \quad \beta = \frac{\pi a}{\lambda}\sin\theta, \quad \alpha = \frac{\pi d}{\lambda}\sin\theta$",
                     f"Central Envelope Width W = 2λL/a = {env_str} | Slit Ratio d/a = {d_mm/max(a_mm, 1e-4):.2f}"),
                    ("4. De Broglie Matter Waves:", db_formula, db_sub),
                    ("5. Quantum Superposition vs Collapse:", r"$P_{\text{coherent}}(y) = |\Psi_1 + \Psi_2|^2, \quad P_{\text{collapsed}}(y) = \frac{1}{2}|\Psi_1|^2 + \frac{1}{2}|\Psi_2|^2$",
                     "Detector OFF: Coherent Interference (V = 1.0) | Detector ON: Wavefunction Collapse (V = 0.0)"),
                ]
            else:
                eqs = [
                    (LocalizationService.reshape_text("۱. اختلاف راه نوری و هندسه آزمایش:"), r"$\Delta r = r_2 - r_1 = d \sin\theta \approx d \frac{y}{L}$",
                     f"Δr = ({d_mm:.3f} mm) × sin(θ) ≈ {d_mm:.3f} mm × (y / {L_m:.2f} m)"),
                    (LocalizationService.reshape_text("۲. شرایط تداخل بیشینه‌ها و کمینه‌ها:"), r"$y_m = m \frac{\lambda L}{n \cdot d}, \quad y'_m = \left(m + \frac{1}{2}\right) \frac{\lambda L}{n \cdot d}$",
                     LocalizationService.reshape_text(f"فاصله فرانژها Δy = {dy_str} | بیشینه مرکزی: 0 | مرتبه اول: ±{dy_str}")),
                    (LocalizationService.reshape_text("۳. شدت ترکیبی تداخل و پوش فرانهوفر:"), r"$I(y) = I_0 \left[\frac{\sin(\beta)}{\beta}\right]^2 \cos^2(\alpha), \quad \beta = \frac{\pi a}{\lambda}\sin\theta, \quad \alpha = \frac{\pi d}{\lambda}\sin\theta$",
                     LocalizationService.reshape_text(f"پهنای پوش مرکزی W = 2λL/a = {env_str} | نسبت d/a = {d_mm/max(a_mm, 1e-4):.2f}")),
                    (LocalizationService.reshape_text("۴. امواج مادی دوبروی در مکانیک کوانتومی:"), db_formula, db_sub),
                    (LocalizationService.reshape_text("۵. برهم‌نهی کوانتومی در برابر فروپاشی (اثر ناظر):"), r"$P_{\text{coherent}}(y) = |\Psi_1 + \Psi_2|^2, \quad P_{\text{collapsed}}(y) = \frac{1}{2}|\Psi_1|^2 + \frac{1}{2}|\Psi_2|^2$",
                     LocalizationService.reshape_text("آشکارساز خاموش: تداخل همدوس (V = 1.0) | آشکارساز روشن: فروپاشی تابع موج (V = 0.0)")),
                ]

            y_pos = 0.86
            fprop_head = FontManager.get_mpl_persian_prop(11) if is_persian else FontManager.get_mpl_number_prop(11)
            fprop_sub = FontManager.get_mpl_persian_prop(9.5) if is_persian else FontManager.get_mpl_number_prop(9.5)

            for heading, formula, sub in eqs:
                ax.text(0.06, y_pos, heading, color="#F8FAFC", fontsize=11, weight="bold", fontproperties=fprop_head)
                ax.text(0.06, y_pos - 0.045, formula, color="#00F0FF", fontsize=11)
                ax.text(0.06, y_pos - 0.085, sub, color="#94A3B8", fontsize=9.5, fontproperties=fprop_sub)
                y_pos -= 0.125

            # Point Inspector Box at Bottom
            y_m = inspector_y_mm * 1e-3
            r1 = math.sqrt(L_m**2 + (y_m - optical_params.slit_distance_d_m/2.0)**2)
            r2 = math.sqrt(L_m**2 + (y_m + optical_params.slit_distance_d_m/2.0)**2)
            dr_nm = abs(r2 - r1) * 1e9
            phase_deg = math.degrees(2.0 * math.pi * abs(r2 - r1) / optical_params.medium_wavelength_m) % 360.0

            insp_pos_str = format_length(inspector_y_mm * 1e-3)
            insp_title = f"Point Inspector Evaluation at y = {insp_pos_str}" if not is_persian else LocalizationService.reshape_text(f"کاوشگر نقطه‌ای روی پرده در مکان y = {insp_pos_str}")
            ax.text(0.5, 0.18, insp_title, color="#FBBF24", fontsize=11, weight="bold", ha="center", fontproperties=fprop_head)

            if not is_persian:
                insp_summary = (
                    f"r₁ = {r1:.6f} m   |   r₂ = {r2:.6f} m   |   Δr = {dr_nm:.2f} nm\n"
                    f"Phase Difference Δφ = {phase_deg:.1f}°   |   Optical Medium n = {n:.3f}"
                )
            else:
                insp_summary = (
                    f"r₁ = {r1:.6f} m   |   r₂ = {r2:.6f} m   |   Δr = {dr_nm:.2f} nm\n"
                    + LocalizationService.reshape_text(f"اختلاف فاز نوری Δφ = {phase_deg:.1f}°   |   ضریب شکست محیط n = {n:.3f}")
                )

            ax.text(0.5, 0.10, insp_summary, color="#E2E8F0", fontsize=9.5, ha="center", fontproperties=fprop_sub,
                    bbox=dict(boxstyle="round,pad=0.5", fc="#1E293B", ec="#3B82F6", lw=1))

            fig.savefig(filepath, dpi=300, bbox_inches="tight", facecolor="#0F172A")
            return {"success": True, "message": f"Saved calculations image to {os.path.basename(filepath)}"}
        except Exception as e:
            return {"success": False, "message": f"Calculations image error: {str(e)}"}

    @staticmethod
    def export_schematic_image(
        filepath: str,
        wavelength_nm: float,
        slit_distance_mm: float,
        slit_width_mm: float,
        screen_distance_m: float,
        which_way_active: bool = False,
        particle_category: Any = None,
        is_quantum: bool = False,
        target_y_offset: float = 0.0,
        is_persian: bool = False
    ) -> Dict[str, Any]:
        """
        Renders the complete 2D apparatus setup, expanding Huygens wavelets, rays,
        path difference triangle, and detector interference ribbon to a 300 DPI publication image.
        """
        try:
            fig = Figure(figsize=(12, 6.8), dpi=300, facecolor="#0B0F19")
            ax = fig.add_subplot(111)
            ax.set_facecolor("#0B0F19")
            ax.set_xlim(-32, 108)
            ax.set_ylim(-48, 48)
            ax.set_aspect("equal")
            ax.axis("off")

            # Typography helpers
            fprop_title = FontManager.get_mpl_persian_prop(14) if is_persian else FontManager.get_mpl_number_prop(14)
            fprop_lbl = FontManager.get_mpl_persian_prop(9) if is_persian else FontManager.get_mpl_number_prop(9)
            fprop_small = FontManager.get_mpl_persian_prop(8) if is_persian else FontManager.get_mpl_number_prop(8)

            # Colors
            laser_hex = ColorUtils.get_particle_hex(particle_category, wavelength_nm) if is_quantum else ColorUtils.wavelength_to_hex(wavelength_nm)
            laser_rgb = ColorUtils.hex_to_rgb(laser_hex)
            r_norm, g_norm, b_norm = [c / 255.0 for c in laser_rgb]

            # 1. Title Banner
            title_txt = "Young's Double-Slit Optical Wave Propagation & Interference" if not is_persian else LocalizationService.reshape_text("انتشار موج و چیدمان هندسی تداخل آزمایش دو شکاف یانگ")
            ax.text(38, 43, title_txt, color="#38BDF8", fontsize=14, weight="bold", ha="center", fontproperties=fprop_title)

            # 2. Source Housing (Laser / Particle Gun)
            src_x0, src_x1 = -28.0, -14.0
            src_y0, src_y1 = -8.0, 8.0
            ax.add_patch(plt.Rectangle((src_x0, src_y0), src_x1 - src_x0, src_y1 - src_y0,
                                       facecolor="#1E293B", edgecolor="#38BDF8", linewidth=1.5, zorder=4))
            src_lbl = "LASER" if not is_persian else LocalizationService.reshape_text("لیزر چشمه")
            ax.text((src_x0 + src_x1)/2.0, 0, src_lbl, color="#38BDF8", fontsize=8, weight="bold", ha="center", va="center", fontproperties=fprop_small)

            # Beams from source aperture to barrier plate at X = 0
            ax.plot([src_x1, 0], [0, 10.0], color=laser_hex, lw=2.0, alpha=0.85, zorder=3)
            ax.plot([src_x1, 0], [0, -10.0], color=laser_hex, lw=2.0, alpha=0.85, zorder=3)

            # 3. Double-Slit Barrier Plate at X = 0
            y_s1 = +10.0
            y_s2 = -10.0
            half_slit = 1.6
            bar_w = 2.4

            # Barrier sections
            ax.add_patch(plt.Rectangle((-bar_w, y_s1 + half_slit), bar_w, 36.0 - (y_s1 + half_slit), facecolor="#334155", edgecolor="#64748B", lw=1.2, zorder=5))
            ax.add_patch(plt.Rectangle((-bar_w, y_s2 + half_slit), bar_w, (y_s1 - half_slit) - (y_s2 + half_slit), facecolor="#334155", edgecolor="#64748B", lw=1.2, zorder=5))
            ax.add_patch(plt.Rectangle((-bar_w, -36.0), bar_w, (y_s2 - half_slit) - (-36.0), facecolor="#334155", edgecolor="#64748B", lw=1.2, zorder=5))

            ax.text(-bar_w/2.0, 38.0, "BARRIER" if not is_persian else LocalizationService.reshape_text("مانع"), color="#94A3B8", fontsize=8, weight="bold", ha="center", fontproperties=fprop_small)
            ax.text(-4.0, y_s1, "S₁", color="#00E676", fontsize=9, weight="bold", ha="right", va="center")
            ax.text(-4.0, y_s2, "S₂", color="#00E676", fontsize=9, weight="bold", ha="right", va="center")

            # 4. Expanding Circular Huygens Wavelets
            theta = np.linspace(-np.pi/2.5, np.pi/2.5, 120)
            wave_radii = np.linspace(6.0, 78.0, 10)
            for r in wave_radii:
                alpha_val = float(np.clip(0.65 * (1.0 - (r / 90.0)), 0.08, 0.65))
                # Arc from Slit 1
                arc_x1 = r * np.cos(theta)
                arc_y1 = y_s1 + r * np.sin(theta)
                valid1 = (arc_x1 >= 0) & (arc_x1 <= 88) & (np.abs(arc_y1) <= 36)
                if np.any(valid1):
                    ax.plot(arc_x1[valid1], arc_y1[valid1], color=laser_hex, lw=1.2, alpha=alpha_val, zorder=2)

                # Arc from Slit 2
                arc_x2 = r * np.cos(theta)
                arc_y2 = y_s2 + r * np.sin(theta)
                valid2 = (arc_x2 >= 0) & (arc_x2 <= 88) & (np.abs(arc_y2) <= 36)
                if np.any(valid2):
                    ax.plot(arc_x2[valid2], arc_y2[valid2], color=laser_hex, lw=1.2, alpha=alpha_val, zorder=2)

            # 5. Detector Screen at X = 88
            scr_x = 88.0
            scr_w = 4.0
            scr_h = 72.0
            ax.add_patch(plt.Rectangle((scr_x, -scr_h/2.0), scr_w, scr_h, facecolor="#020617", edgecolor="#64748B", lw=1.5, zorder=5))

            # Render fine interference fringe ribbon on screen
            n_fringe = 180
            y_ribbon = np.linspace(-scr_h/2.0, scr_h/2.0, n_fringe)
            # Analytical Fraunhofer simulation for ribbon
            k_val = 2.0 * np.pi / max(wavelength_nm * 1e-9, 1e-9)
            d_real = slit_distance_mm * 1e-3
            a_real = slit_width_mm * 1e-3
            L_real = screen_distance_m
            theta_rib = np.arctan(y_ribbon * (0.015 / (scr_h/2.0)) / L_real)
            beta_rib = 0.5 * k_val * a_real * np.sin(theta_rib)
            alpha_rib = 0.5 * k_val * d_real * np.sin(theta_rib)
            sinc_rib = np.where(np.abs(beta_rib) < 1e-7, 1.0, np.sin(beta_rib)/beta_rib)**2
            int_rib = sinc_rib * (np.cos(alpha_rib)**2)
            int_rib = np.clip(int_rib, 0.0, 1.0)

            for i in range(n_fringe - 1):
                y_a = y_ribbon[i]
                y_b = y_ribbon[i+1]
                ival = float(int_rib[i])
                f_col = (r_norm * ival, g_norm * ival, b_norm * ival, min(ival * 0.9 + 0.1, 1.0))
                ax.fill([scr_x + 0.5, scr_x + scr_w - 0.5, scr_x + scr_w - 0.5, scr_x + 0.5],
                        [y_a, y_a, y_b, y_b], color=f_col, zorder=6)

            scr_lbl = "SCREEN (L)" if not is_persian else LocalizationService.reshape_text(f"پرده (L={screen_distance_m:.1f}m)")
            ax.text(scr_x + scr_w/2.0, 38.0, scr_lbl, color="#94A3B8", fontsize=8, weight="bold", ha="center", fontproperties=fprop_small)

            # 6. Target Point P and Rays r1, r2
            y_target = float(np.clip(target_y_offset * 0.22, -30.0, 30.0))
            p_target = (scr_x, y_target)

            # Ray paths (r1 and r2)
            ax.plot([0, p_target[0]], [y_s1, p_target[1]], color="#00E676", lw=1.6, ls="--", alpha=0.9, zorder=7)
            ax.plot([0, p_target[0]], [y_s2, p_target[1]], color="#FFD600", lw=1.6, ls="--", alpha=0.9, zorder=7)

            # Impact point on screen with radiant glow
            ax.scatter([p_target[0]], [p_target[1]], color="#FF1744", s=55, edgecolors="#FFFFFF", lw=1.2, zorder=8)
            ax.text(p_target[0] + 5.5, p_target[1], "P", color="#FF1744", fontsize=10, weight="bold", va="center")

            # 7. Path difference right triangle construction
            dx = p_target[0]
            dy = p_target[1] - y_s2
            ray_len = math.sqrt(dx**2 + dy**2)
            if ray_len > 1e-3:
                u_ray = np.array([dx, dy]) / ray_len
                # Projected perpendicular point from S1 onto ray 2
                v_s1s2 = np.array([0, y_s1 - y_s2])
                proj = np.dot(v_s1s2, u_ray) * u_ray
                hx = float(proj[0])
                hy = float(y_s2 + proj[1])
                # Draw perpendicular drop
                ax.plot([0, hx], [y_s1, hy], color="#00F0FF", lw=1.4, ls=":", zorder=7)
                # Highlight path difference segment Delta r on ray 2
                ax.plot([0, hx], [y_s2, hy], color="#00F0FF", lw=3.0, zorder=8)
                ax.text(-3.0, (y_s2 + hy)/2.0, "Δr", color="#00F0FF", fontsize=9, weight="bold", ha="right", va="center")

            # 8. Physical telemetry summary card at bottom
            y_real_m = y_target * (0.015 / (scr_h/2.0))
            r1_real = math.sqrt(screen_distance_m**2 + (y_real_m - d_real/2.0)**2)
            r2_real = math.sqrt(screen_distance_m**2 + (y_real_m + d_real/2.0)**2)
            dr_real_nm = abs(r2_real - r1_real) * 1e9
            wl_real_m = wavelength_nm * 1e-9
            phase_deg = math.degrees(2.0 * math.pi * abs(r2_real - r1_real) / wl_real_m) % 360.0
            order_m = dr_real_nm / wavelength_nm
            nearest_m = round(order_m)
            is_const = abs(order_m - nearest_m) < 0.08
            is_dest = abs(order_m - (nearest_m + 0.5)) < 0.08

            cond_str = ""
            if is_const:
                cond_str = f" [Max: Order m={nearest_m}]" if not is_persian else LocalizationService.reshape_text(f" [بیشینه: مرتبه m={nearest_m}]")
            elif is_dest:
                cond_str = " [Min: Destructive Dark]" if not is_persian else LocalizationService.reshape_text(" [کمینه تاریک]")

            telemetry_text = (
                f"λ = {wavelength_nm:.1f} nm   |   d = {slit_distance_mm:.3f} mm   |   L = {screen_distance_m:.2f} m\n"
                f"Δr = {dr_real_nm:.1f} nm   |   Δφ = {phase_deg:.1f}°{cond_str}"
            )
            ax.text(38, -42, telemetry_text, color="#E2E8F0", fontsize=9.0, ha="center", fontproperties=fprop_lbl,
                    bbox=dict(boxstyle="round,pad=0.5", fc="#1E293B", ec="#38BDF8", lw=1.2))

            # 9. Which-way observer effect alert if active
            if which_way_active:
                for ys in [y_s1, y_s2]:
                    ax.add_patch(plt.Rectangle((1.5, ys - 2.5), 4.5, 5.0, facecolor="#311B92", edgecolor="#FF1744", lw=1.5, zorder=8))
                alert_msg = "⚡ OBSERVER EFFECT ACTIVE: WAVEFUNCTION COLLAPSED" if not is_persian else LocalizationService.reshape_text("⚡ اثر ناظر فعال: فروریزش تابع موج کوانتومی")
                ax.text(38, 36, alert_msg, color="#F87171", fontsize=8.5, weight="bold", ha="center", fontproperties=fprop_lbl,
                        bbox=dict(boxstyle="round,pad=0.3", fc="#450A0A", ec="#DC2626", lw=1.2))

            fig.savefig(filepath, dpi=300, bbox_inches="tight", facecolor="#0B0F19")
            return {"success": True, "message": f"Saved 2D wave schematic image to {os.path.basename(filepath)}"}
        except Exception as e:
            return {"success": False, "message": f"Schematic image error: {str(e)}"}


    @classmethod
    def export_3d_model(cls, filepath: str, **kwargs) -> Dict[str, Any]:
        """Delegates to ObjExporter."""
        return ObjExporter.export_scene_to_obj(filepath, **kwargs)

    @classmethod
    def export_word_report(cls, filepath: str, **kwargs) -> Dict[str, Any]:
        """Delegates to DocxEquationExporter."""
        return DocxEquationExporter.export_report_to_docx(filepath, **kwargs)

    @classmethod
    def export_all_in_one_zip(
        cls,
        filepath: str,
        y_grid_m: np.ndarray,
        intensity_theory: np.ndarray,
        quantum_histogram: Optional[np.ndarray],
        params_dict: Dict[str, Any],
        stats_dict: Dict[str, Any],
        total_hits: int,
        optical_params: Any,
        quantum_engine: Any,
        features: Dict[str, Any],
        setup_3d_fig: Any,
        profile_1d_fig: Any,
        screen_2d_quantum_buffer: Any,
        which_way_active: bool,
        target_y_offset: float = 0.0,
        inspector_y_mm: float = 0.0,
        is_persian: bool = False,
        is_quantum: bool = False
    ) -> Dict[str, Any]:
        """
        Creates a comprehensive ZIP laboratory archive package:
        1. 22-column scientific simulation dataset (.csv)
        2. Microsoft Word report with native OMML editable equations (.docx)
        3. 3D Wavefront CAD model (.obj, .mtl, and 1024x512 screen texture .png)
        4. Publication-ready 300 DPI figures (1D profile, 2D screen, wave propagation, calculations, 3D setup)
        5. Machine-readable experiment metadata (.json)
        """
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                # 1. Scientific CSV Dataset
                csv_path = os.path.join(tmp_dir, "simulation_data.csv")
                cls.export_csv(
                    filepath=csv_path,
                    y_grid_m=y_grid_m,
                    intensity_theory=intensity_theory,
                    quantum_histogram=quantum_histogram,
                    params_dict=params_dict,
                    stats_dict=stats_dict,
                    total_hits=total_hits
                )

                # 2. Word Lab Report
                docx_path = os.path.join(tmp_dir, "laboratory_report.docx")
                cls.export_word_report(
                    filepath=docx_path,
                    optical_params=optical_params,
                    quantum_engine=quantum_engine,
                    features=features,
                    inspector_y_mm=inspector_y_mm,
                    is_persian=is_persian
                )

                # 3. 3D Wavefront CAD Model folder
                model_dir = os.path.join(tmp_dir, "apparatus_3d_model")
                os.makedirs(model_dir, exist_ok=True)
                wl_nm = optical_params.wavelength_m * 1e9
                if is_quantum and quantum_engine is not None:
                    rgb = ColorUtils.get_particle_color(quantum_engine.particle.category, wl_nm)
                else:
                    rgb = ColorUtils.wavelength_to_rgb(wl_nm)
                obj_path = os.path.join(model_dir, "apparatus_model.obj")
                cls.export_3d_model(
                    filepath=obj_path,
                    wavelength_nm=wl_nm,
                    slit_distance_mm=optical_params.slit_distance_d_m * 1000.0,
                    slit_width_mm=optical_params.slit_width_a_m * 1000.0,
                    screen_distance_m=optical_params.screen_distance_L_m,
                    which_way_active=which_way_active,
                    intensity_1d=intensity_theory,
                    base_rgb=rgb
                )

                # 4. Publication Figures (300 DPI)
                fig_dir = os.path.join(tmp_dir, "figures_300dpi")
                os.makedirs(fig_dir, exist_ok=True)
                if profile_1d_fig is not None:
                    cls.export_figure(os.path.join(fig_dir, "1_profile_1d_intensity.png"), profile_1d_fig, dpi=300)
                if setup_3d_fig is not None:
                    cls.export_figure(os.path.join(fig_dir, "2_apparatus_3d_setup.png"), setup_3d_fig, dpi=300)

                span_y_m = params_dict.get("screen_span_y_m", 0.04)
                cls.export_screen_image(
                    filepath=os.path.join(fig_dir, "3_detector_screen_2d.png"),
                    intensity_1d=intensity_theory,
                    base_rgb=rgb,
                    span_y_m=span_y_m,
                    quantum_buffer=screen_2d_quantum_buffer,
                    is_quantum=is_quantum
                )
                cls.export_schematic_image(
                    filepath=os.path.join(fig_dir, "4_wave_propagation_schematic.png"),
                    wavelength_nm=wl_nm,
                    slit_distance_mm=optical_params.slit_distance_d_m * 1000.0,
                    slit_width_mm=optical_params.slit_width_a_m * 1000.0,
                    screen_distance_m=optical_params.screen_distance_L_m,
                    which_way_active=which_way_active,
                    is_quantum=is_quantum,
                    target_y_offset=target_y_offset,
                    is_persian=is_persian
                )
                cls.export_calculations_image(
                    filepath=os.path.join(fig_dir, "5_calculations_and_formulas.png"),
                    optical_params=optical_params,
                    features=features,
                    inspector_y_mm=inspector_y_mm,
                    is_persian=is_persian,
                    quantum_engine=quantum_engine if is_quantum else None
                )

                # 5. Metadata JSON
                meta = {
                    "experiment": "Thomas Young Double-Slit Experiment",
                    "wavelength_nm": wl_nm,
                    "slit_distance_mm": optical_params.slit_distance_d_m * 1000.0,
                    "slit_width_mm": optical_params.slit_width_a_m * 1000.0,
                    "screen_distance_m": optical_params.screen_distance_L_m,
                    "refractive_index": optical_params.refractive_index_n,
                    "fringe_spacing_mm": features.get("fringe_spacing_dy_mm", 0.0),
                    "visibility": stats_dict.get("visibility", 1.0),
                    "which_way_active": which_way_active,
                    "is_quantum": is_quantum,
                    "total_hits": total_hits
                }
                with open(os.path.join(tmp_dir, "experiment_metadata.json"), "w", encoding="utf-8") as f_json:
                    json.dump(meta, f_json, indent=2, ensure_ascii=False)

                # Archive all into output zipfile
                with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as zf:
                    for root, _, files in os.walk(tmp_dir):
                        for file in files:
                            full_path = os.path.join(root, file)
                            arcname = os.path.relpath(full_path, tmp_dir)
                            zf.write(full_path, arcname=arcname)

            return {"success": True, "message": f"Successfully exported complete Lab Bundle to {os.path.basename(filepath)}"}
        except Exception as e:
            return {"success": False, "message": f"Lab Bundle ZIP export error: {str(e)}"}

