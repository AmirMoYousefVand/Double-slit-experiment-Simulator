"""
Microsoft Word (.docx) Laboratory Report Exporter with Native OMML Equations.
Exports full educational and analytical reports containing:
- Formatted editable OMML math equations (<m:oMath>) rendered natively in Word equation editor
- Formatted LaTeX source code blocks for academic citation
- Physical derivations and narratives
- Live numerical substitution tables matching current slider values
- Interactive Point Inspector evaluation table
"""

import os
import math
from datetime import datetime
from typing import Dict, Any, Optional
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

from physics.classical_engine import OpticalParameters
from physics.particle_types import de_broglie_substitution
from physics.quantum_engine import QuantumEngine
from utils.units import format_length

class DocxEquationExporter:
    """Generates professional scientific reports in Word format with native math equations."""

    @staticmethod
    def _add_omml_equation(paragraph, omml_inner_xml: str):
        """Appends a native Microsoft Office Math (OMML) block into a python-docx paragraph."""
        ns = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"'
        full_xml = f'<m:oMathPara {ns}><m:oMath>{omml_inner_xml}</m:oMath></m:oMathPara>'
        element = parse_xml(full_xml)
        paragraph._p.append(element)

    @classmethod
    def export_report_to_docx(
        cls,
        filepath: str,
        optical_params: OpticalParameters,
        quantum_engine: Optional[QuantumEngine],
        features: Dict[str, Any],
        inspector_y_mm: float = 0.0,
        is_persian: bool = False
    ) -> Dict[str, Any]:
        """
        Builds and saves the complete laboratory report.
        """
        try:
            doc = Document()

            # Set 1-inch margins
            sections = doc.sections
            for s in sections:
                s.top_margin = Inches(0.8)
                s.bottom_margin = Inches(0.8)
                s.left_margin = Inches(0.9)
                s.right_margin = Inches(0.9)

            # Colors
            col_primary = RGBColor(14, 116, 144)    # Deep Cyan
            col_secondary = RGBColor(51, 65, 85)   # Slate 700
            col_formula = RGBColor(30, 58, 138)    # Blue 900

            # ------------------------------------------------------------------
            # 1. Document Header & Title
            # ------------------------------------------------------------------
            title_p = doc.add_paragraph()
            title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run_title = title_p.add_run("Thomas Young Double-Slit Experiment" if not is_persian else "گزارش جامع آزمایش دو شکاف توماس یانگ")
            run_title.font.name = "Arial"
            run_title.font.size = Pt(20)
            run_title.font.bold = True
            run_title.font.color.rgb = col_primary

            sub_p = doc.add_paragraph()
            sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            sub_text = "Classical Wave Optics & Quantum Wave-Particle Duality Laboratory Report" if not is_persian else "گزارش آزمایشگاه اپتیک موجی کلاسیک و دوگانگی موج-ذره مکانیک کوانتومی"
            run_sub = sub_p.add_run(sub_text)
            run_sub.font.name = "Arial"
            run_sub.font.size = Pt(11)
            run_sub.font.italic = True
            run_sub.font.color.rgb = col_secondary

            date_p = doc.add_paragraph()
            date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_lbl = f"Generated: {now_str} | Simulator v2.0" if not is_persian else f"تاریخ صدور گزارش: {now_str} | نسخه شبیه‌ساز ۲.۰"
            run_date = date_p.add_run(date_lbl)
            run_date.font.size = Pt(9)
            run_date.font.color.rgb = RGBColor(100, 116, 139)

            doc.add_paragraph().paragraph_format.space_after = Pt(6)

            # ------------------------------------------------------------------
            # 2. Apparatus Parameters Table
            # ------------------------------------------------------------------
            h2_text = "1. Laboratory Apparatus Parameters" if not is_persian else "۱. مشخصات و پارامترهای چیدمان آزمایشگاهی"
            h2 = doc.add_heading(h2_text, level=2)
            h2.runs[0].font.color.rgb = col_primary
            if is_persian:
                h2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                h2._p.get_or_add_pPr().append(parse_xml(f'<w:bidi {nsdecls("w")}/>'))

            table = doc.add_table(rows=6, cols=3)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.style = 'Light Shading Accent 1'
            if is_persian:
                table._tbl.tblPr.append(parse_xml(f'<w:bidiVisual {nsdecls("w")}/>'))

            d_mm = optical_params.slit_distance_d_m * 1000.0
            a_mm = optical_params.slit_width_a_m * 1000.0
            L_m = optical_params.screen_distance_L_m
            n = optical_params.refractive_index_n

            if not is_persian:
                rows_data = [
                    ("Parameter", "Symbol & Formula", "Current Simulated Value"),
                    ("Optical Wavelength (Vacuum)", "λ₀", f"{format_length(optical_params.wavelength_m)} ({optical_params.wavelength_m:.4e} m)"),
                    ("Slit Separation (Center-to-Center)", "d", f"{d_mm:.3f} mm ({optical_params.slit_distance_d_m:.4e} m)"),
                    ("Slit Aperture Width", "a", f"{a_mm:.3f} mm ({optical_params.slit_width_a_m:.4e} m)"),
                    ("Slit-to-Screen Distance", "L", f"{L_m:.3f} m"),
                    ("Medium Refractive Index", "n", f"{n:.3f} (λ_med = {format_length(optical_params.medium_wavelength_m)})")
                ]
            else:
                rows_data = [
                    ("پارامتر فیزیکی", "نماد و رابطه", "مقدار شبیه‌سازی‌شده"),
                    ("طول موج نوری (در خلاء)", "λ₀", f"{format_length(optical_params.wavelength_m)} ({optical_params.wavelength_m:.4e} m)"),
                    ("فاصله دو شکاف (مرکز به مرکز)", "d", f"{d_mm:.3f} mm ({optical_params.slit_distance_d_m:.4e} m)"),
                    ("پهنای هر شکاف", "a", f"{a_mm:.3f} mm ({optical_params.slit_width_a_m:.4e} m)"),
                    ("فاصله شکاف‌ها تا پرده", "L", f"{L_m:.3f} m"),
                    ("ضریب شکست محیط انتشار", "n", f"{n:.3f} (λ_med = {format_length(optical_params.medium_wavelength_m)})")
                ]

            for r_idx, row in enumerate(rows_data):
                for c_idx, val in enumerate(row):
                    cell = table.cell(r_idx, c_idx)
                    cell.text = val
                    if is_persian:
                        p = cell.paragraphs[0]
                        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                        p._p.get_or_add_pPr().append(parse_xml(f'<w:bidi {nsdecls("w")}/>'))
                    if r_idx == 0:
                        cell.paragraphs[0].runs[0].font.bold = True

            doc.add_paragraph().paragraph_format.space_after = Pt(12)

            # ------------------------------------------------------------------
            # 3. Mathematical Formulations (Native Word OMML Equations + Live Substitution)
            # ------------------------------------------------------------------
            sec_h_text = "2. Physics Formulations & Live Analytical Substitution" if not is_persian else "۲. روابط تحلیلی فیزیک و جایگذاری عددی زنده"
            sec_h = doc.add_heading(sec_h_text, level=2)
            sec_h.runs[0].font.color.rgb = col_primary
            if is_persian:
                sec_h.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                sec_h._p.get_or_add_pPr().append(parse_xml(f'<w:bidi {nsdecls("w")}/>'))

            # Helper to add equation box without duplicate LaTeX code blocks
            def add_equation_section(title, narrative, omml_body, sub_text, latex_code=""):
                h3 = doc.add_heading(title, level=3)
                h3.runs[0].font.color.rgb = col_secondary
                if is_persian:
                    h3.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    h3._p.get_or_add_pPr().append(parse_xml(f'<w:bidi {nsdecls("w")}/>'))

                np_p = doc.add_paragraph(narrative)
                np_p.paragraph_format.space_after = Pt(4)
                if is_persian:
                    np_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    np_p._p.get_or_add_pPr().append(parse_xml(f'<w:bidi {nsdecls("w")}/>'))

                # Native OMML Equation
                eq_p = doc.add_paragraph()
                eq_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                cls._add_omml_equation(eq_p, omml_body)
                eq_p.paragraph_format.space_after = Pt(4)

                # Formatted Live Numerical Substitution (duplicate LaTeX source block removed per user request)
                sub_p = doc.add_paragraph()
                if is_persian:
                    sub_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    sub_p.paragraph_format.right_indent = Inches(0.4)
                    sub_p.paragraph_format.left_indent = Inches(0.0)
                    sub_p._p.get_or_add_pPr().append(parse_xml(f'<w:bidi {nsdecls("w")}/>'))
                else:
                    sub_p.paragraph_format.left_indent = Inches(0.4)

                lbl_sub = "Live Substitution:  " if not is_persian else "جایگذاری زنده مقادیر:  "
                r_lbl = sub_p.add_run(lbl_sub)
                r_lbl.font.bold = True
                r_lbl.font.size = Pt(9.5)
                r_lbl.font.color.rgb = col_formula

                r_sub = sub_p.add_run(sub_text)
                r_sub.font.bold = True
                r_sub.font.size = Pt(9.5)
                r_sub.font.color.rgb = RGBColor(30, 41, 59)
                sub_p.paragraph_format.space_after = Pt(8)

            # --- Formula 1: Optical Path Difference ---
            omml_1 = (
                '<m:r><m:t>Δr = </m:t></m:r>'
                '<m:sSub><m:e><m:r><m:t>r</m:t></m:r></m:e><m:sub><m:r><m:t>2</m:t></m:r></m:sub></m:sSub>'
                '<m:r><m:t> - </m:t></m:r>'
                '<m:sSub><m:e><m:r><m:t>r</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub>'
                '<m:r><m:t> = d · sin(θ) ≈ </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>d · y</m:t></m:r></m:num><m:den><m:r><m:t>L</m:t></m:r></m:den></m:f>'
            )
            title_1 = "A. Optical Path Difference & Geometry" if not is_persian else "الف. اختلاف راه نوری و هندسه آزمایش"
            narr_1 = "The geometric path difference between rays originating from slits S1 and S2 determines the relative phase at coordinate y on the detector screen." if not is_persian else "اختلاف راه هندسی بین پرتوهای خارج‌شده از دو شکاف S₁ و S₂ فاز نسبی امواج در مختصات y روی پرده آشکارساز را تعیین می‌کند."
            add_equation_section(
                title=title_1,
                narrative=narr_1,
                omml_body=omml_1,
                sub_text=f"Δr = ({d_mm:.3f} mm) × sin(θ) ≈ {d_mm:.3f} mm × (y / {L_m:.2f} m)"
            )

            # --- Formula 2: Interference Extrema ---
            omml_2 = (
                '<m:sSub><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sub><m:r><m:t>m</m:t></m:r></m:sub></m:sSub>'
                '<m:r><m:t> = m · </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>λ · L</m:t></m:r></m:num><m:den><m:r><m:t>d</m:t></m:r></m:den></m:f>'
                '<m:r><m:t>  (Bright Maxima),      </m:t></m:r>'
                "<m:sSub><m:e><m:r><m:t>y</m:t></m:r></m:e><m:sub><m:r><m:t>m'</m:t></m:r></m:sub></m:sSub>"
                '<m:r><m:t> = (m + 0.5) · </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>λ · L</m:t></m:r></m:num><m:den><m:r><m:t>d</m:t></m:r></m:den></m:f>'
                '<m:r><m:t>  (Dark Minima)</m:t></m:r>'
            )
            dy_m = features.get("fringe_spacing_dy_m", 0.0)
            title_2 = "B. Constructive & Destructive Interference Conditions" if not is_persian else "ب. شرایط تداخل سازنده و ویرانگر (موقعیت بیشینه‌ها و کمینه‌ها)"
            narr_2 = "Constructive interference occurs when path difference is an integer multiple of wavelength; destructive occurs for half-integer multiples." if not is_persian else "تداخل سازنده زمانی رخ می‌دهد که اختلاف راه مضرب درستی از طول موج باشد و تداخل ویرانگر در مضارب فرد نیم‌طول‌موج روی می‌دهد."
            sub_2 = f"Order 0: 0 | Order 1: ±{format_length(dy_m)} | Order 2: ±{format_length(2*dy_m)} | Order 3: ±{format_length(3*dy_m)}" if not is_persian else f"مرتبه صفر: 0 | مرتبه اول: ±{format_length(dy_m)} | مرتبه دوم: ±{format_length(2*dy_m)} | مرتبه سوم: ±{format_length(3*dy_m)}"
            add_equation_section(
                title=title_2,
                narrative=narr_2,
                omml_body=omml_2,
                sub_text=sub_2
            )

            # --- Formula 3: Fringe Spacing ---
            omml_3 = (
                '<m:r><m:t>Δy = </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>λ · L</m:t></m:r></m:num><m:den><m:r><m:t>n · d</m:t></m:r></m:den></m:f>'
            )
            title_3 = "C. Fringe Width / Spacing Formulation (Δy)" if not is_persian else "ج. رابطه فاصله نوارهای روشن متوالی (پهنای فرانژ Δy)"
            narr_3 = "The spatial separation between consecutive bright interference fringes on the screen." if not is_persian else "جدایی مکانی بین دو نوار روشن تداخلی متوالی روی پرده آشکارساز."
            add_equation_section(
                title=title_3,
                narrative=narr_3,
                omml_body=omml_3,
                sub_text=f"Δy = ({format_length(optical_params.wavelength_m)} × {L_m:.2f} m) / ({n:.3f} × {d_mm:.3f} mm) = {format_length(dy_m)}"
            )

            # --- Formula 4: Fraunhofer Diffraction & Missing Orders ---
            omml_4 = (
                '<m:r><m:t>I(y) = </m:t></m:r>'
                '<m:sSub><m:e><m:r><m:t>I</m:t></m:r></m:e><m:sub><m:r><m:t>0</m:t></m:r></m:sub></m:sSub>'
                '<m:r><m:t> · </m:t></m:r>'
                '<m:sSup><m:e><m:d><m:r><m:t>sinc(β)</m:t></m:r></m:d></m:e><m:sup><m:r><m:t>2</m:t></m:r></m:sup></m:sSup>'
                '<m:r><m:t> · </m:t></m:r>'
                '<m:sSup><m:e><m:d><m:r><m:t>cos(α)</m:t></m:r></m:d></m:e><m:sup><m:r><m:t>2</m:t></m:r></m:sup></m:sSup>'
            )
            env_m = features.get("central_envelope_width_m", 0.0)
            ratio = d_mm / max(a_mm, 1e-4)
            miss = features.get("missing_orders", [])
            miss_txt = "m = ±" + ", ±".join([str(abs(m)) for m in miss if m > 0][:4]) if miss else ("None" if not is_persian else "هیچ")
            title_4 = "D. Fraunhofer Diffraction Envelope & Missing Orders" if not is_persian else "د. پوش پراش فرانهوفر و مراتب تداخلی غایب"
            narr_4 = "The physical double-slit pattern is modulated by the single-slit diffraction envelope. Missing orders occur when d/a equals the ratio of orders." if not is_persian else "طرح تداخلی دو شکاف توسط پوش پراش تک‌شکاف تعدیل می‌شود. مراتب غایب زمانی رخ می‌دهند که نسبت d/a برابر نسبت مرتبه‌ها گردد."
            sub_4 = f"Central Envelope Width W = 2λL/a = {format_length(env_m)} | Ratio d/a = {ratio:.2f} => Missing Orders: {miss_txt}" if not is_persian else f"پهنای پوش مرکزی W = 2λL/a = {format_length(env_m)} | نسبت d/a = {ratio:.2f} => مراتب غایب: {miss_txt}"
            add_equation_section(
                title=title_4,
                narrative=narr_4,
                omml_body=omml_4,
                sub_text=sub_4
            )

            # --- Formula 5: De Broglie Matter Waves ---
            # Universal OMML core only — per-particle detail lives in the
            # substitution line (m·E_k form is wrong for photons and C60)
            omml_5 = (
                '<m:sSub><m:e><m:r><m:t>λ</m:t></m:r></m:e><m:sub><m:r><m:t>dB</m:t></m:r></m:sub></m:sSub>'
                '<m:r><m:t> = </m:t></m:r>'
                '<m:f><m:num><m:r><m:t>h</m:t></m:r></m:num><m:den><m:r><m:t>p</m:t></m:r></m:den></m:f>'
            )
            q_info = "Matter Wave: Photon hc/E | Relativistic Electron h/p | Buckyball h/(M·v)" if not is_persian else "موج مادی: فوتون hc/E | الکترون نسبیتی h/p | باکی‌بال h/(M·v)"
            if quantum_engine:
                p_name = quantum_engine.particle.name_en if not is_persian else quantum_engine.particle.name_fa
                q_info = de_broglie_substitution(
                    quantum_engine.particle.category,
                    p_name,
                    quantum_engine.energy_ev,
                    quantum_engine.velocity_ms,
                    quantum_engine.optical_params.wavelength_m
                )
            title_5 = "E. Quantum Mechanics & De Broglie Matter Waves" if not is_persian else "هـ. مکانیک کوانتومی و رابطه امواج مادی دوبروی"
            narr_5 = "Every quantum particle with momentum p possesses an intrinsic wave nature governing probability amplitude distribution across the slits." if not is_persian else "هر ذره مادی کوانتومی با تکانه p دارای ماهیت موجی ذاتی است که توزیع دامنه احتمال حضور در شکاف‌ها را تعیین می‌نماید."
            add_equation_section(
                title=title_5,
                narrative=narr_5,
                omml_body=omml_5,
                sub_text=q_info
            )

            # --- Formula 6: Superposition vs Collapse ---
            omml_6 = (
                '<m:r><m:t>P(y) = </m:t></m:r>'
                '<m:sSup><m:e><m:d><m:r><m:t>Ψ₁ + Ψ₂</m:t></m:r></m:d></m:e><m:sup><m:r><m:t>2</m:t></m:r></m:sup></m:sSup>'
                '<m:r><m:t> = </m:t></m:r>'
                '<m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>1</m:t></m:r></m:sub></m:sSub>'
                '<m:r><m:t> + </m:t></m:r>'
                '<m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>2</m:t></m:r></m:sub></m:sSub>'
                '<m:r><m:t> + 2√(P₁P₂) · cos(Δφ)</m:t></m:r>'
            )
            title_6 = "F. Quantum Superposition vs Wavefunction Collapse (Observer Effect)" if not is_persian else "و. برهم‌نهی کوانتومی در برابر فروپاشی تابع موج (اثر ناظر)"
            narr_6 = "When Which-Way path measurement is active, detector entanglement destroys the cross-term 2√(P₁P₂)cos(Δφ), reducing probability to classical particle addition." if not is_persian else "با فعال شدن آشکارساز مسیر، درهم‌تنیدگی با دستگاه اندازه‌گیری جمله تداخلی را از بین برده و توزیع احتمال به جمع ذرات کلاسیک کاهش می‌یابد."
            sub_6 = "Detector OFF: Visibility V = 1.0 (Coherent Fringes) | Detector ON: Visibility V = 0.0 (Collapsed)" if not is_persian else "آشکارساز خاموش: دیداری فرانژ V = 1.0 (تداخل همدوس) | آشکارساز روشن: دیداری V = 0.0 (فروپاشی)"
            add_equation_section(
                title=title_6,
                narrative=narr_6,
                omml_body=omml_6,
                sub_text=sub_6
            )

            # ------------------------------------------------------------------
            # 4. Point Inspector Evaluation at Coordinate y
            # ------------------------------------------------------------------
            doc.add_page_break()
            insp_pos_str = format_length(inspector_y_mm * 1e-3)
            h_insp_text = f"3. Interactive Point Inspector (Evaluation at y = {insp_pos_str})" if not is_persian else f"۳. کاوشگر نقطه‌ای روی پرده (محاسبه در مکان y = {insp_pos_str})"
            h_insp = doc.add_heading(h_insp_text, level=2)
            h_insp.runs[0].font.color.rgb = col_primary
            if is_persian:
                h_insp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                h_insp._p.get_or_add_pPr().append(parse_xml(f'<w:bidi {nsdecls("w")}/>'))

            y_m = inspector_y_mm * 1e-3
            r1 = (L_m**2 + (y_m - optical_params.slit_distance_d_m/2.0)**2)**0.5
            r2 = (L_m**2 + (y_m + optical_params.slit_distance_d_m/2.0)**2)**0.5
            dr_exact_nm = abs(r2 - r1) * 1e9
            sin_th = y_m / ((y_m**2 + L_m**2)**0.5)
            dr_parax_nm = abs(optical_params.slit_distance_d_m * sin_th) * 1e9
            phase_deg = (math.degrees(2.0 * math.pi * abs(r2 - r1) / optical_params.medium_wavelength_m)) % 360.0

            beta = (math.pi * optical_params.slit_width_a_m * sin_th) / optical_params.medium_wavelength_m
            sinc_sq = (math.sin(beta) / beta)**2 if abs(beta) > 1e-6 else 1.0
            alpha = (math.pi * optical_params.slit_distance_d_m * sin_th) / optical_params.medium_wavelength_m
            i_pct = sinc_sq * (math.cos(alpha)**2) * 100.0

            insp_table = doc.add_table(rows=7, cols=2)
            insp_table.style = 'Medium Shading 1 Accent 1'
            if is_persian:
                insp_table._tbl.tblPr.append(parse_xml(f'<w:bidiVisual {nsdecls("w")}/>'))

            if not is_persian:
                insp_data = [
                    ("Inspection Screen Coordinate (y)", f"{format_length(y_m)} ({y_m:.6e} m)"),
                    ("Ray Path Length r₁ (From Slit 1)", f"{r1:.6f} m"),
                    ("Ray Path Length r₂ (From Slit 2)", f"{r2:.6f} m"),
                    ("Exact Path Difference (Δr)", f"{dr_exact_nm:.2f} nm"),
                    ("Paraxial Approximation (d·y/L)", f"{dr_parax_nm:.2f} nm"),
                    ("Optical Phase Difference (Δφ)", f"{phase_deg:.1f}°"),
                    ("Normalized Relative Intensity (I / I₀)", f"{i_pct:.1f}%")
                ]
            else:
                insp_data = [
                    ("مختصات بازرسی روی پرده (y)", f"{format_length(y_m)} ({y_m:.6e} m)"),
                    ("طول مسیر پرتو r₁ (از شکاف ۱)", f"{r1:.6f} m"),
                    ("طول مسیر پرتو r₂ (از شکاف ۲)", f"{r2:.6f} m"),
                    ("اختلاف راه دقیق هندسی (Δr)", f"{dr_exact_nm:.2f} nm"),
                    ("تقریب پیرا-محوری (d·y/L)", f"{dr_parax_nm:.2f} nm"),
                    ("اختلاف فاز نوری (Δφ)", f"{phase_deg:.1f}°"),
                    ("شدت نسبی بهنجارشده (I / I₀)", f"{i_pct:.1f}%")
                ]

            for r_idx, (k, v) in enumerate(insp_data):
                cell_k = insp_table.cell(r_idx, 0)
                cell_v = insp_table.cell(r_idx, 1)
                cell_k.text = k
                cell_v.text = v
                if is_persian:
                    cell_k.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    cell_k.paragraphs[0]._p.get_or_add_pPr().append(parse_xml(f'<w:bidi {nsdecls("w")}/>'))
                    cell_v.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    cell_v.paragraphs[0]._p.get_or_add_pPr().append(parse_xml(f'<w:bidi {nsdecls("w")}/>'))

            # Save file
            doc.save(filepath)
            return {"success": True, "message": f"Successfully exported Word report to {os.path.basename(filepath)}"}

        except Exception as e:
            return {"success": False, "message": f"Word export error: {str(e)}"}
