"""
Flask Web Application for Thomas Young Experiment Presentation & Simulator Guide.
Serves an interactive, responsive HTML5/CSS3 presentation deck with LaTeX math (MathJax/KaTeX),
Vazirmatn typography, and interactive canvas/SVG physics visualizers.
"""

import os
import json
from flask import Flask, render_template, jsonify, send_from_directory, request

from ui.content.history_content import SLIDES, QUIZ, SECTIONS, SECTION_TITLES
from ui.content.guide_content import GUIDE_MODULES
from config import (
    DEFAULT_WAVELENGTH_NM,
    DEFAULT_SLIT_DISTANCE_MM,
    DEFAULT_SLIT_WIDTH_MM,
    DEFAULT_SCREEN_DISTANCE_M,
    DEFAULT_REFRACTIVE_INDEX,
    PARAM_LIMITS,
    PRESETS
)
from physics.classical_engine import OpticalParameters, ClassicalEngine
from utils.color_utils import ColorUtils

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images", "history")


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"),
        static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    )
    app.config["JSON_AS_ASCII"] = False

    @app.route("/")
    def index():
        payload = {
            "slides": SLIDES,
            "quiz": QUIZ,
            "sections": SECTIONS,
            "section_titles": SECTION_TITLES,
            "guide_modules": GUIDE_MODULES,
            "defaults": {
                "wavelength_nm": DEFAULT_WAVELENGTH_NM,
                "slit_distance_mm": DEFAULT_SLIT_DISTANCE_MM,
                "slit_width_mm": DEFAULT_SLIT_WIDTH_MM,
                "screen_distance_m": DEFAULT_SCREEN_DISTANCE_M,
                "refractive_index": DEFAULT_REFRACTIVE_INDEX
            },
            "presets": PRESETS,
            "param_limits": PARAM_LIMITS
        }
        return render_template("index.html", initial_data=json.dumps(payload, ensure_ascii=False))

    @app.route("/api/data")
    def api_data():
        return jsonify({
            "slides": SLIDES,
            "quiz": QUIZ,
            "sections": SECTIONS,
            "section_titles": SECTION_TITLES,
            "guide_modules": GUIDE_MODULES,
            "defaults": {
                "wavelength_nm": DEFAULT_WAVELENGTH_NM,
                "slit_distance_mm": DEFAULT_SLIT_DISTANCE_MM,
                "slit_width_mm": DEFAULT_SLIT_WIDTH_MM,
                "screen_distance_m": DEFAULT_SCREEN_DISTANCE_M,
                "refractive_index": DEFAULT_REFRACTIVE_INDEX
            }
        })

    @app.route("/api/calculate")
    def api_calculate():
        wl_nm = float(request.args.get("wavelength_nm", DEFAULT_WAVELENGTH_NM))
        d_mm = float(request.args.get("slit_distance_mm", DEFAULT_SLIT_DISTANCE_MM))
        a_mm = float(request.args.get("slit_width_mm", DEFAULT_SLIT_WIDTH_MM))
        L_m = float(request.args.get("screen_distance_m", DEFAULT_SCREEN_DISTANCE_M))
        n = float(request.args.get("refractive_index", DEFAULT_REFRACTIVE_INDEX))

        opt = OpticalParameters(
            wavelength_m=wl_nm * 1e-9,
            slit_distance_d_m=d_mm * 1e-3,
            slit_width_a_m=a_mm * 1e-3,
            screen_distance_L_m=L_m,
            refractive_index_n=n
        )
        engine = ClassicalEngine(opt)
        features = engine.get_analytical_features()
        # jsonify cannot serialize numpy arrays (maxima_y_m, envelope_zeros_y_m)
        for key, val in list(features.items()):
            if hasattr(val, "tolist"):
                features[key] = val.tolist()
        hex_col = ColorUtils.wavelength_to_hex(wl_nm)

        return jsonify({
            "features": features,
            "color_hex": hex_col
        })

    @app.route("/assets/fonts/<path:filename>")
    def serve_font(filename):
        return send_from_directory(FONTS_DIR, filename, mimetype="font/ttf")

    @app.route("/assets/images/history/<path:filename>")
    def serve_image(filename):
        return send_from_directory(IMAGES_DIR, filename)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5055, debug=True)
