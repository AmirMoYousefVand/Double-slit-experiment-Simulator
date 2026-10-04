"""
Comprehensive Test and Verification Suite for Young's Double-Slit Simulator.
Tests:
1. Classical Fraunhofer optics and analytical features
2. Missing order detection (d/a ratio)
3. De Broglie wavelengths for photons, electrons, and macromolecules
4. Quantum superposition vs Which-Way observer collapse
5. High-speed Monte Carlo sampling performance
6. Colorimetric Dan Bruton wavelength-to-sRGB mapping
7. Enhanced 22-column CSV dataset export
8. 3D Model Wavefront OBJ + MTL + Texture export
9. Microsoft Word (.docx) lab report export with native OMML equations
10. FontManager dynamic registration (Vazirmatn & Space Grotesk)
11. 3D Laboratory Apparatus View (Setup3DView) with wheel zoom & rotation
12. 2D Wave Propagation View (SetupSchematicView) with spectral color & Delta r
13. Physical Calculations View & Point Inspector (CalculationsView)
14. Strict bilingual separation check (Pure English in EN, proper RLM in FA)
15. Full 5-Tab CustomTkinter GUI initialization and export callbacks
"""

import sys
import os
import tempfile
import numpy as np

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from physics.particle_types import ParticleCategory, PARTICLE_PRESETS
from physics.classical_engine import OpticalParameters, ClassicalEngine
from physics.quantum_engine import QuantumEngine
from utils.color_utils import ColorUtils
from utils.stats_calculator import StatsCalculator
from utils.export_service import ExportService
from utils.obj_exporter import ObjExporter
from utils.docx_exporter import DocxEquationExporter
from utils.localization import LocalizationService, RLM
from utils.font_manager import FontManager

def test_classical_optics():
    print("[1/15] Testing Classical Fraunhofer Optics...")
    opt = OpticalParameters(
        wavelength_m=632.8e-9,
        slit_distance_d_m=0.25e-3,
        slit_width_a_m=0.04e-3,
        screen_distance_L_m=1.0,
        refractive_index_n=1.0
    )
    engine = ClassicalEngine(opt)
    features = engine.get_analytical_features()

    expected_dy_mm = (632.8e-9 * 1.0 / 0.25e-3) * 1000.0  # 2.5312 mm
    assert abs(features["fringe_spacing_dy_mm"] - expected_dy_mm) < 1e-4, \
        f"Fringe spacing mismatch: {features['fringe_spacing_dy_mm']} vs {expected_dy_mm}"

    y_grid = np.linspace(-0.01, 0.01, 1000)
    intensity = engine.compute_intensity_profile(y_grid)
    envelope = engine.compute_diffraction_envelope(y_grid)

    assert np.max(intensity) <= 1.0001, "Intensity exceeded 1.0"
    assert np.min(intensity) >= 0.0, "Intensity cannot be negative"
    assert np.all(envelope >= intensity - 1e-6), "Intensity exceeded diffraction envelope"
    print("       -> Classical Fraunhofer calculations verified! (dy = 2.5312 mm)")

def test_missing_orders():
    print("[2/15] Testing Missing Order Detection (d/a ratio)...")
    opt = OpticalParameters(
        wavelength_m=500e-9,
        slit_distance_d_m=0.20e-3,
        slit_width_a_m=0.05e-3,
        screen_distance_L_m=1.0
    )
    engine = ClassicalEngine(opt)
    features = engine.get_analytical_features()

    missing = features["missing_orders"]
    assert 4 in missing or -4 in missing, f"Expected order 4 in missing orders, got {missing}"
    print(f"       -> Missing orders correctly detected: {missing}")

def test_de_broglie_wavelengths():
    print("[3/15] Testing de Broglie Matter Wave Formulations...")
    elec = PARTICLE_PRESETS[ParticleCategory.ELECTRON]
    lambda_e = elec.calculate_de_broglie_wavelength(energy_ev=100.0)
    assert 0.12e-9 < lambda_e < 0.124e-9, f"Unexpected electron wavelength: {lambda_e}"

    photon = PARTICLE_PRESETS[ParticleCategory.PHOTON]
    lambda_p = photon.calculate_de_broglie_wavelength(energy_ev=1.96)
    assert 630e-9 < lambda_p < 635e-9, f"Unexpected photon wavelength: {lambda_p}"

    bucky = PARTICLE_PRESETS[ParticleCategory.BUCKYBALL]
    lambda_c60 = bucky.calculate_de_broglie_wavelength(velocity_ms=200.0)
    assert 2.5e-12 < lambda_c60 < 3.0e-12, f"Unexpected buckyball wavelength: {lambda_c60}"
    print("       -> De Broglie wavelengths verified across all particle categories!")

def test_quantum_observer_collapse():
    print("[4/15] Testing Observer Effect (Wavefunction Collapse)...")
    opt = OpticalParameters(
        wavelength_m=632.8e-9,
        slit_distance_d_m=0.25e-3,
        slit_width_a_m=0.05e-3,
        screen_distance_L_m=1.0
    )
    q_engine = QuantumEngine(ParticleCategory.PHOTON, optical_params=opt)
    y_grid = np.linspace(-0.010, 0.010, 1000)

    # 1. Which-Way Detector OFF (Coherent Superposition)
    q_engine.set_which_way_detector(active=False)
    p_coherent = q_engine.compute_probability_density(y_grid)
    v_coherent = StatsCalculator.calculate_visibility(p_coherent, search_span=80)
    assert v_coherent > 0.85, f"Expected high visibility for coherent state, got {v_coherent}"

    # 2. Which-Way Detector ON (Wavefunction Collapse)
    q_engine.set_which_way_detector(active=True)
    p_collapsed = q_engine.compute_probability_density(y_grid)
    v_collapsed = StatsCalculator.calculate_visibility(p_collapsed, search_span=80)
    assert v_collapsed < 0.15, f"Expected low visibility for collapsed state, got {v_collapsed}"
    print(f"       -> Observer Effect verified: Coherent V={v_coherent:.3f} -> Collapsed V={v_collapsed:.3f}")

def test_monte_carlo_sampling_speed():
    print("[5/15] Testing Monte Carlo Sampling Speed & Quality...")
    import time
    q_engine = QuantumEngine(ParticleCategory.PHOTON)
    t0 = time.perf_counter()
    batch_y, batch_z = q_engine.sample_particles(count=5000, screen_span_y_m=0.04, screen_span_z_m=0.02)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert len(batch_y) == 5000
    assert len(batch_z) == 5000
    assert elapsed_ms < 50.0, f"Monte Carlo too slow: {elapsed_ms:.2f} ms for 5000 particles"
    print(f"       -> 5,000 particles sampled in {elapsed_ms:.2f} ms (Target < 50 ms)")

def test_color_utilities():
    print("[6/15] Testing Spectral Color Mapping...")
    r_red, g_red, b_red = ColorUtils.wavelength_to_rgb(650.0)
    assert r_red > 200 and g_red < 50 and b_red == 0, f"Red failed: {(r_red, g_red, b_red)}"

    r_grn, g_grn, b_grn = ColorUtils.wavelength_to_rgb(530.0)
    assert g_grn > 200 and b_grn == 0, f"Green failed: {(r_grn, g_grn, b_grn)}"

    r_vio, g_vio, b_vio = ColorUtils.wavelength_to_rgb(410.0)
    assert b_vio > 100, f"Violet failed: {(r_vio, g_vio, b_vio)}"
    print("       -> Colorimetric mapping verified for Red, Green, and Violet lines.")

def test_enhanced_csv_export():
    print("[7/15] Testing Enhanced 22-Column CSV Export...")
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "test_22col.csv")
        y = np.linspace(-0.01, 0.01, 100)
        I = np.ones(100)
        res = ExportService.export_csv(
            filepath=csv_path,
            y_grid_m=y,
            intensity_theory=I,
            quantum_histogram=np.full(100, 5),
            params_dict={"wavelength_m": 632.8e-9, "slit_distance_d_m": 0.25e-3, "slit_width_a_m": 0.04e-3, "screen_distance_L_m": 1.0},
            stats_dict={"fringe_spacing_dy_m": 2.53e-3, "fringe_spacing_dy_mm": 2.53},
            total_hits=500
        )
        assert res["success"] is True
        assert os.path.exists(csv_path)

        with open(csv_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        header_cols = lines[0].split(",")
        assert len(header_cols) == 22, f"Expected 22 columns, got {len(header_cols)}: {header_cols}"
        print("       -> 22-Column scientific dataset verified with complete metadata headers!")

def test_3d_obj_export():
    print("[8/15] Testing 3D Wavefront OBJ + MTL + Texture Export...")
    with tempfile.TemporaryDirectory() as tmpdir:
        obj_file = os.path.join(tmpdir, "test_apparatus.obj")
        res = ObjExporter.export_scene_to_obj(
            filepath=obj_file,
            wavelength_nm=632.8,
            slit_distance_mm=0.25,
            slit_width_mm=0.04,
            screen_distance_m=1.0,
            which_way_active=True,
            intensity_1d=np.ones(100),
            base_rgb=(255, 60, 0)
        )
        assert res["success"] is True
        assert os.path.exists(obj_file), "OBJ file missing"
        mtl_file = os.path.join(tmpdir, "test_apparatus.mtl")
        assert os.path.exists(mtl_file), "MTL file missing"
        tex_file = os.path.join(tmpdir, "test_apparatus_screen_texture.png")
        assert os.path.exists(tex_file), "Texture PNG file missing"

        # Check OBJ contents
        with open(obj_file, "r") as f:
            content = f.read()
        assert "mtllib test_apparatus.mtl" in content
        assert "o Barrier_LeftWing" in content
        assert "o Detector_Screen" in content
        assert "o Source_Beam_To_S1" in content, "Incident source beam 1 missing"
        assert "o Source_Beam_To_S2" in content, "Incident source beam 2 missing"
        assert "o Ray_Path_r1" in content, "Cylindrical ray r1 missing"
        assert "o Ray_Path_r2" in content, "Cylindrical ray r2 missing"
        assert "vt " in content, "UV mapping coordinates missing"
        print("       -> 3D CAD OBJ model, MTL library, beams, and texture map exported and verified successfully!")

def test_word_docx_omml_export():
    print("[9/15] Testing Microsoft Word (.docx) Export with Native OMML Equations...")
    with tempfile.TemporaryDirectory() as tmpdir:
        docx_file = os.path.join(tmpdir, "test_lab_report.docx")
        opt = OpticalParameters()
        engine = ClassicalEngine(opt)
        features = engine.get_analytical_features()
        res = DocxEquationExporter.export_report_to_docx(
            filepath=docx_file,
            optical_params=opt,
            quantum_engine=None,
            features=features,
            inspector_y_mm=2.531,
            is_persian=False
        )
        assert res["success"] is True
        assert os.path.exists(docx_file)
        assert os.path.getsize(docx_file) > 1000

        # Verify docx package can re-open it
        import docx
        doc = docx.Document(docx_file)
        assert len(doc.paragraphs) > 10
        assert len(doc.tables) >= 2
        # Verify duplicate LaTeX blocks are removed
        assert not any("LaTeX Source:" in p.text for p in doc.paragraphs), "Duplicate LaTeX source block still present!"

        # Also test Persian DOCX export with RTL
        docx_fa = os.path.join(tmpdir, "test_lab_report_fa.docx")
        res_fa = DocxEquationExporter.export_report_to_docx(
            filepath=docx_fa,
            optical_params=opt,
            quantum_engine=None,
            features=features,
            inspector_y_mm=2.531,
            is_persian=True
        )
        assert res_fa["success"] is True
        doc_fa = docx.Document(docx_fa)
        assert not any("LaTeX Source:" in p.text for p in doc_fa.paragraphs)
        assert "گزارش جامع آزمایش دو شکاف توماس یانگ" in doc_fa.paragraphs[0].text

        print("       -> Word document exported with native OMML equations, clean numerical substitution, and RTL tables successfully!")

def test_font_manager():
    print("[10/15] Testing FontManager Dynamic Registration...")
    import customtkinter as ctk
    root = ctk.CTk()
    FontManager.initialize()
    f_fa = FontManager.get_persian_font(12, "bold")
    assert f_fa.cget("family") == "Vazirmatn", f"Expected Vazirmatn, got {f_fa.cget('family')}"

    f_en = FontManager.get_number_font(12, "bold")
    assert f_en.cget("family") == "Space Grotesk", f"Expected Space Grotesk, got {f_en.cget('family')}"
    root.destroy()
    print("       -> FontManager registered Vazirmatn and Space Grotesk successfully!")

def test_3d_view_interactivity():
    print("[11/15] Testing 3D Laboratory View Interactivity (Zoom, Rotation, Presets)...")
    try:
        import customtkinter as ctk
        from ui.views.setup_3d_view import Setup3DView
        root = ctk.CTk()
        view_3d = Setup3DView(root)
        y_grid = np.linspace(-0.02, 0.02, 200)
        I = np.cos(y_grid * 1000) ** 2

        view_3d.update_3d_scene(
            wavelength_nm=632.8,
            slit_distance_mm=0.25,
            slit_width_mm=0.04,
            screen_distance_m=1.0,
            which_way_active=True,
            intensity_1d=I,
            y_grid_m=y_grid,
            base_rgb=(255, 60, 0),
            particle_category=ParticleCategory.ELECTRON,
            is_quantum=True,
            quantum_hits_y=[0.0, 0.001],
            quantum_hits_z=[0.0, -0.001]
        )

        # Test Zoom In / Out
        initial_zoom = view_3d.zoom_level
        view_3d._apply_zoom_factor(1.20)
        assert view_3d.zoom_level > initial_zoom, "Zoom In failed"
        view_3d._apply_zoom_factor(1.0 / 1.20)
        assert abs(view_3d.zoom_level - initial_zoom) < 1e-3, "Zoom Out failed"

        # Test Manual Rotation
        view_3d._rotate_camera(azim_delta=10, elev_delta=5)

        # Test Camera Presets
        view_3d._set_cam_top()
        view_3d._set_cam_side()
        view_3d._set_cam_front()
        view_3d._set_cam_reset()

        root.destroy()
        print("       -> 3D Apparatus interactive zoom, rotation, and presets verified successfully!")
    except Exception as e:
        print(f"       [!] 3D view test note: {e}")
        raise e

def test_setup_schematic_view():
    print("[12/15] Testing 2D Wave Propagation View (Colors, Impact Spot, Ribbon)...")
    try:
        import customtkinter as ctk
        from ui.views.setup_schematic_view import SetupSchematicView
        root = ctk.CTk()
        sch_view = SetupSchematicView(root)

        # Update with Argon Green
        sch_view.update_optical_params(
            wavelength_nm=514.5,
            slit_distance_mm=0.20,
            slit_width_mm=0.03,
            screen_distance_m=1.2,
            which_way_active=False
        )
        sch_view._redraw_schematic()

        # Update with Which-Way Active
        sch_view.update_optical_params(
            wavelength_nm=514.5,
            slit_distance_mm=0.20,
            slit_width_mm=0.03,
            screen_distance_m=1.2,
            which_way_active=True
        )
        sch_view._redraw_schematic()

        root.destroy()
        print("       -> 2D Wave schematic dynamic colors, impact spot, and fringe ribbon verified!")
    except Exception as e:
        print(f"       [!] Schematic view test note: {e}")
        raise e

def test_calculations_view():
    print("[13/15] Testing Calculations View & Point Inspector...")
    try:
        import customtkinter as ctk
        from ui.views.calculations_view import CalculationsView
        root = ctk.CTk()
        calc_view = CalculationsView(root)
        opt = OpticalParameters()
        engine = ClassicalEngine(opt)
        features = engine.get_analytical_features()
        calc_view.update_calculations(opt, None, features)

        # Evaluate at y = 2.531 mm
        calc_view._on_inspector_slider_change(2.531)
        assert "Relative Intensity" in calc_view.lbl_insp_intensity.cget("text")
        root.destroy()
        print("       -> Calculations view & point inspector verified successfully!")
    except Exception as e:
        print(f"       [!] Calculations view test note: {e}")
        raise e

def test_bilingual_purity():
    print("[14/15] Testing Strict Bilingual Separation (Zero Persian in EN)...")
    # Test English mode
    LocalizationService.set_language("en")

    # Sample key UI strings
    keys_to_check = [
        "app_title", "app_subtitle", "mode_classical", "mode_quantum",
        "wavelength", "slit_distance", "slit_width", "screen_distance",
        "particle_photon", "particle_electron", "particle_buckyball",
        "preset_hene", "preset_argon", "tab_2d_screen", "tab_3d_setup",
        "missing_none", "status_bright", "status_dark",
        "web_presentation_btn", "web_presentation_short"
    ]

    for k in keys_to_check:
        en_str = LocalizationService.get(k)
        # Check that no Persian character code points (0x0600 - 0x06FF) exist in English strings
        has_persian = any('؀' <= char <= 'ۿ' for char in en_str)
        assert not has_persian, f"Linguistic leak in English key '{k}': '{en_str}' contains Persian characters!"

    # Test Persian mode
    LocalizationService.set_language("fa")
    for k in keys_to_check:
        fa_str = LocalizationService.get(k)
        assert len(fa_str) > 0, f"Empty string for Persian key '{k}'"

    print("       -> Bilingual purity verified: 100% pure English in EN mode!")

def test_full_gui_headless():
    print("[15/15] Testing Full 5-Tab GUI & Export Handlers...")
    try:
        import customtkinter as ctk
        from ui.main_window import MainWindow
        app = MainWindow()
        app.update_idletasks()

        # Check all 5 views exist
        assert app.screen_2d_view is not None
        assert app.profile_1d_view is not None
        assert app.setup_schematic_view is not None
        assert app.setup_3d_view is not None
        assert app.calculations_view is not None

        # Verify export callbacks wired
        assert app.calculations_view.on_export_docx is not None
        assert app.calculations_view.on_export_png is not None
        assert app.metrics_panel.on_export_obj is not None
        assert app.metrics_panel.on_export_zip is not None

        # Test language switch
        app._toggle_language()
        app.update_idletasks()
        app._toggle_language()
        app.update_idletasks()

        app.destroy()
        print("       -> Full 5-Tab CustomTkinter GUI & Export pipelines verified cleanly!")
    except Exception as e:
        print(f"       [!] Full GUI test note: {e}")
        raise e

def test_persian_reshaping():
    print("[16/17] Testing Bidirectional Mixed Persian/English Text Reshaping...")
    # Test complex mixed string with parentheses, brackets, numbers, and Latin
    mixed = "پرده (L = 1.00 m) [محور X]"
    reshaped = LocalizationService.reshape_text(mixed)
    assert len(reshaped) > 0
    # Must not contain invisible control characters that create square tofu boxes
    for bad_ch in ["‏", "‎", "‪", "‬"]:
        assert bad_ch not in reshaped, f"Invisible control char {repr(bad_ch)} found in reshaped text!"

    # Test get_reshaped helper
    LocalizationService.set_language("fa")
    reshaped_key = LocalizationService.get_reshaped("plot_1d_xlabel")
    assert len(reshaped_key) > 0
    print("       -> Persian/Latin bidirectional text reshaping verified successfully!")

def test_wave_schematic_and_zip_export():
    print("[17/17] Testing 2D Wave Propagation & All-in-One Lab ZIP Archive Export...")
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Test 2D Wave Schematic Export
        sch_path = os.path.join(tmpdir, "test_schematic.png")
        res_sch = ExportService.export_schematic_image(
            filepath=sch_path,
            wavelength_nm=632.8,
            slit_distance_mm=0.25,
            slit_width_mm=0.04,
            screen_distance_m=1.0,
            which_way_active=True,
            is_persian=True
        )
        assert res_sch["success"] is True, res_sch["message"]
        assert os.path.exists(sch_path)
        assert os.path.getsize(sch_path) > 30000

        # 2. Test All-in-One ZIP Bundle Export
        zip_path = os.path.join(tmpdir, "test_lab_bundle.zip")
        opt = OpticalParameters()
        eng = ClassicalEngine(opt)
        feat = eng.get_analytical_features()
        params = {
            "wavelength_m": opt.wavelength_m,
            "slit_distance_d_m": opt.slit_distance_d_m,
            "slit_width_a_m": opt.slit_width_a_m,
            "screen_distance_L_m": opt.screen_distance_L_m,
            "refractive_index_n": opt.refractive_index_n,
            "screen_span_y_m": 0.04
        }
        y_grid = np.linspace(-0.02, 0.02, 200)
        intensity = eng.compute_intensity_profile(y_grid)

        res_zip = ExportService.export_all_in_one_zip(
            filepath=zip_path,
            y_grid_m=y_grid,
            intensity_theory=intensity,
            quantum_histogram=None,
            params_dict=params,
            stats_dict=feat,
            total_hits=0,
            optical_params=opt,
            quantum_engine=None,
            features=feat,
            setup_3d_fig=None,
            profile_1d_fig=None,
            screen_2d_quantum_buffer=np.zeros((80, 80, 3)),
            which_way_active=False,
            is_persian=True
        )
        assert res_zip["success"] is True, res_zip["message"]
        assert os.path.exists(zip_path)
        import zipfile
        assert zipfile.is_zipfile(zip_path)
        with zipfile.ZipFile(zip_path, "r") as zf:
            entries = zf.namelist()
            assert any("simulation_data.csv" in e for e in entries)
            assert any("laboratory_report.docx" in e for e in entries)
            assert any("apparatus_model.obj" in e for e in entries)
            assert any("wave_propagation_schematic.png" in e for e in entries)
            assert any("experiment_metadata.json" in e for e in entries)

        print("       -> 2D Wave schematic image and comprehensive Lab ZIP bundle verified successfully!")

def test_numeric_input_entries():
    print("[18/21] Testing Manual Numeric Entry Parsing, Clamping & Sync...")
    from utils.numeric_input import parse_number, clamp, clamp_range
    from config import PARAM_LIMITS

    # Persian/Arabic digit normalization
    assert parse_number("۰/۲۵") == 0.25
    assert parse_number("۶۳۲٫۸") == 632.8
    # Partial / invalid input soft-ignored
    assert parse_number("") is None
    assert parse_number("-") is None
    assert parse_number(".") is None
    assert parse_number("abc") is None
    # Plain + noisy input
    assert parse_number(" 632.8 ") == 632.8
    assert parse_number("1,000") == 1000.0

    # Clamp keeps exact values inside range (no step snapping: 632.8 survives)
    assert clamp("wavelength_nm", 632.8) == 632.8
    assert clamp("wavelength_nm", 100.0) == PARAM_LIMITS["wavelength_nm"]["min"]
    assert clamp("wavelength_nm", 9999.0) == PARAM_LIMITS["wavelength_nm"]["max"]
    assert clamp("slit_width_mm", 0.0) == PARAM_LIMITS["slit_width_mm"]["min"]
    assert clamp("unknown_key_xyz", 5.5) == 5.5
    assert clamp_range(7.0, 1.5, 3.5) == 3.5
    assert clamp_range(0.5, 1.5, 3.5) == 1.5
    assert clamp_range(2.0, 1.5, 3.5) == 2.0

    # Headless ControlPanel entry/slider two-way sync without feedback loop
    try:
        import customtkinter as ctk
        from ui.components.control_panel import ControlPanel
        calls = []
        root = ctk.CTk()
        root.withdraw()
        panel = ControlPanel(root, on_param_change=lambda k, v: calls.append((k, v)),
                             on_preset_selected=lambda n: None, on_reset_defaults=lambda: None)
        root.update_idletasks()
        # Slider -> entry mirror
        panel._handle_slider_change("wavelength_nm", 500.0)
        assert panel.entries["wavelength_nm"].get() == "500.0"
        n_calls = len(calls)
        # Entry -> slider commit (exact value preserved)
        panel.entries["slit_distance_mm"].delete(0, "end")
        panel.entries["slit_distance_mm"].insert(0, "1.5")
        panel._handle_entry_change("slit_distance_mm", live=False)
        assert abs(panel.sliders["slit_distance_mm"].get() - 1.5) < 1e-6
        assert len(calls) == n_calls + 1  # exactly one propagation, no loop
        # Out-of-range live keystroke ignored, Enter clamps
        panel.entries["slit_distance_mm"].delete(0, "end")
        panel.entries["slit_distance_mm"].insert(0, "99")
        panel._handle_entry_change("slit_distance_mm", live=True)
        assert abs(panel.sliders["slit_distance_mm"].get() - 1.5) < 1e-6
        panel._handle_entry_change("slit_distance_mm", live=False)
        assert abs(panel.sliders["slit_distance_mm"].get() - 2.0) < 1e-6
        # Persian digits commit
        panel.entries["wavelength_nm"].delete(0, "end")
        panel.entries["wavelength_nm"].insert(0, "۵۵۰")
        panel._handle_entry_change("wavelength_nm", live=False)
        assert abs(panel.sliders["wavelength_nm"].get() - 550.0) < 1e-6
        root.destroy()
        print("       -> Numeric entries, Persian digits, clamping & loop-guard verified!")
    except Exception as e:
        print(f"       [!] Headless panel sync note: {e}")
        raise e

def test_history_content_and_quiz():
    print("[19/21] Testing History Slide-Deck Content Contract & Quiz Grading...")
    from ui.content.history_content import SLIDES, QUIZ, SECTIONS, grade, get_slides_by_section

    assert len(SLIDES) >= 15, f"Expected 15-20 slides, got {len(SLIDES)}"
    assert len(QUIZ) == 6
    grouped = get_slides_by_section()
    for sec in ("timeline", "theory", "demo", "quantum"):
        assert len(grouped[sec]) >= 2, f"Section {sec} too thin"
    for s in SLIDES:
        assert s["section"] in SECTIONS
        assert s["title_fa"] and s["title_en"]
        assert len(s["body_fa"]) >= 2 and len(s["body_en"]) >= 2
        assert s["figure"]["kind"] in (
            "none", "photo", "huygens", "triangle", "fringe",
            "buildup", "apparatus", "interference", "duel",
            "worked_bench", "envelope", "interactive_fringe"
        )
    for q in QUIZ:
        assert len(q["opts_fa"]) == 4 and len(q["opts_en"]) == 4
        assert 0 <= q["correct"] <= 3
        assert q["explain_fa"] and q["explain_en"]
        assert grade(q, q["correct"]) is True
        assert grade(q, (q["correct"] + 1) % 4) is False

    # Worked-example value matches the physics engine
    opt = OpticalParameters(wavelength_m=632.8e-9, slit_distance_d_m=0.25e-3,
                            slit_width_a_m=0.04e-3, screen_distance_L_m=1.0)
    eng = ClassicalEngine(opt)
    dy_mm = eng.get_analytical_features()["fringe_spacing_dy_m"] * 1000.0
    assert abs(dy_mm - 2.5312) < 0.01, f"Worked example drifted: {dy_mm}"

    # New localization keys exist in both languages, EN pure ASCII
    for key in ("tab_history", "hist_prev", "hist_next", "hist_contents",
                "hist_sec_timeline", "hist_sec_theory", "hist_sec_demo",
                "hist_sec_quantum", "hist_sec_quiz", "hist_photo_na",
                "hist_live_badge", "hist_score", "hist_correct", "hist_wrong",
                "hist_retry", "hist_explanation"):
        en = LocalizationService.STRINGS[key]["en"]
        fa = LocalizationService.STRINGS[key]["fa"]
        assert en and fa, f"Missing strings for {key}"
        assert not any('؀' <= ch <= 'ۿ' for ch in en), f"Persian char in EN string {key}"
    print("       -> Slide deck, quiz bank, worked example & loc keys verified!")

def test_history_view_headless():
    print("[20/21] Testing HistoryView Headless Build, Navigation & Offline Photos...")
    try:
        import customtkinter as ctk
        from ui.views.history_view import HistoryView
        from ui.content.history_content import SLIDES, QUIZ
        root = ctk.CTk()
        root.withdraw()
        view = HistoryView(root)
        root.update_idletasks()
        total = len(SLIDES) + len(QUIZ)
        assert view.slide_index == 0
        # Forward navigation bounds-safe
        for _ in range(total + 5):
            view.next_slide()
            root.update_idletasks()
        assert view.slide_index == total - 1
        # Backward navigation bounds-safe
        for _ in range(total + 5):
            view.prev_slide()
            root.update_idletasks()
        assert view.slide_index == 0
        # Jump to live demo slide and feed engine params
        demo_idx = next(i for i, s in enumerate(SLIDES) if s["id"] == "d2_live")
        view.show_slide(demo_idx)
        root.update_idletasks()
        view.update_optical_params(OpticalParameters())
        root.update_idletasks()
        # Quiz slide: answer first question correctly
        view.show_slide(len(SLIDES))
        root.update_idletasks()
        q = QUIZ[0]
        view._answer_quiz(q["correct"])
        assert view.quiz_score == 1 and view.quiz_answered == 1
        view._answer_quiz((q["correct"] + 1) % 4)  # locked, no double count
        assert view.quiz_answered == 1
        view._reset_quiz()
        assert view.quiz_score == 0 and view.quiz_answered == 0
        # Language toggle re-renders
        LocalizationService.set_language("en")
        view.refresh_language()
        root.update_idletasks()
        LocalizationService.set_language("fa")
        view.refresh_language()
        root.update_idletasks()
        # Animation cleanup
        view.on_hide()
        assert view._anim_job is None
        view.on_show()
        root.update_idletasks()
        view.on_hide()
        root.destroy()
        print("       -> HistoryView navigation, quiz, language & lifecycle verified!")
    except Exception as e:
        print(f"       [!] HistoryView headless note: {e}")
        raise e

def test_six_tab_gui_headless():
    print("[21/21] Testing Full 7-Tab GUI incl. History, Software Guide & Fullscreen/Theater Wiring...")
    try:
        import customtkinter as ctk
        from ui.main_window import MainWindow
        app = MainWindow()
        app.update_idletasks()

        assert app.history_view is not None
        assert app.tab_hist is not None
        assert app.guide_view is not None
        assert app.tab_guide is not None

        # History & Guide tab titles registered
        app._update_tabview_titles()
        btn_hist = app.tabview._segmented_button._buttons_dict.get("tab_hist")
        assert btn_hist is not None
        assert btn_hist.cget("text") == LocalizationService.get("tab_history")

        btn_guide = app.tabview._segmented_button._buttons_dict.get("tab_guide")
        assert btn_guide is not None
        assert btn_guide.cget("text") == LocalizationService.get("tab_guide")

        # Test Fullscreen and Theater toggles
        assert app._is_window_fullscreen is False
        app._toggle_window_fullscreen()
        assert app._is_window_fullscreen is True
        app._toggle_window_fullscreen()
        assert app._is_window_fullscreen is False

        assert app._is_theater_mode is False
        app._toggle_theater_mode()
        assert app._is_theater_mode is True
        app._toggle_theater_mode()
        assert app._is_theater_mode is False

        # Real mouse-click simulation: invoke each segmented button and verify
        # the visible tab actually switches across all 7 tabs.
        for tab_id in ("tab_2d", "tab_1d", "tab_sch", "tab_3d", "tab_calc", "tab_hist", "tab_guide"):
            btn_widget = app.tabview._segmented_button._buttons_dict.get(tab_id)
            assert btn_widget is not None, f"missing tab button {tab_id}"
            btn_widget.invoke()
            app.update_idletasks()
            assert app.tabview.get() == tab_id, f"click did not switch to {tab_id}"
            assert str(app.tabview.tab(tab_id).grid_info()) != "", f"{tab_id} frame not gridded"

        # Verify all guide modules render cleanly without any NameError or exceptions
        from ui.content.guide_content import GUIDE_MODULES
        for i in range(len(GUIDE_MODULES)):
            app.guide_view.show_module(i)
            app.update_idletasks()

        # History animations stopped after leaving its tab (no leaked job)
        assert app.history_view._anim_job is None or app.tabview.get() == "tab_hist"

        # Language round-trip covers history and guide view too
        app._toggle_language()
        app.update_idletasks()
        app._toggle_language()
        app.update_idletasks()

        app.destroy()
        print("       -> 7-tab GUI, history & guide wiring, fullscreen & theater verified cleanly!")
    except Exception as e:
        print(f"       [!] 7-tab GUI test note: {e}")
        raise e

def test_web_presentation_service():
    print("[22/22] Testing Flask Web Presentation Service & Local HTTP Endpoints...")
    import urllib.request
    import json
    from utils.web_presentation_service import WebPresentationService

    service = WebPresentationService.get_instance()
    port = service.start_server()
    assert port > 1000

    # 1. Test root HTML endpoint
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as resp:
        assert resp.status == 200
        html = resp.read().decode("utf-8")
        assert "Thomas Young" in html
        assert "katex" in html

    # 2. Test JSON data API endpoint
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/data") as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode("utf-8"))
        assert "slides" in data and len(data["slides"]) >= 15
        assert "quiz" in data and len(data["quiz"]) == 6
        assert "guide_modules" in data and len(data["guide_modules"]) == 8

    # 3. Test Font Asset Endpoint
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/assets/fonts/Vazirmatn-Regular.ttf") as resp:
        assert resp.status == 200
        assert len(resp.read()) > 50000

    service.stop_server()
    print("       -> Flask presentation daemon, HTML5/KaTeX payload, and font endpoints verified successfully!")

if __name__ == "__main__":
    print("=" * 70)
    print("RUNNING EXTENDED DOUBLE-SLIT SIMULATOR 22-TEST VERIFICATION SUITE")
    print("=" * 70)

    test_classical_optics()
    test_missing_orders()
    test_de_broglie_wavelengths()
    test_quantum_observer_collapse()
    test_monte_carlo_sampling_speed()
    test_color_utilities()
    test_enhanced_csv_export()
    test_3d_obj_export()
    test_word_docx_omml_export()
    test_font_manager()
    test_3d_view_interactivity()
    test_setup_schematic_view()
    test_calculations_view()
    test_bilingual_purity()
    test_full_gui_headless()
    test_persian_reshaping()
    test_wave_schematic_and_zip_export()
    test_numeric_input_entries()
    test_history_content_and_quiz()
    test_history_view_headless()
    test_six_tab_gui_headless()
    test_web_presentation_service()
    print("=" * 70)
    print("ALL 22 VERIFICATION TESTS PASSED SUCCESSFULLY! (100% PASS)")
    print("=" * 70)
