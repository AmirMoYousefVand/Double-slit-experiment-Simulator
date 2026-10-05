# Thomas Young Double-Slit Experiment Simulator

[![GitHub Repository](https://img.shields.io/badge/GitHub-AmirMoYousefVand%2FDouble--slit--experiment--Simulator-181717?logo=github&logoColor=white)](https://github.com/AmirMoYousefVand/Double-slit-experiment-Simulator)
[![Latest Release](https://img.shields.io/github/v/release/AmirMoYousefVand/Double-slit-experiment-Simulator?label=release&logo=github)](https://github.com/AmirMoYousefVand/Double-slit-experiment-Simulator/releases)

**Classical Wave Optics & Quantum Mechanics Dashboard**

A bilingual (English / فارسی) desktop laboratory that simulates Young's double-slit
experiment from both viewpoints: the classical Fraunhofer wave-optics solution and the
quantum wave-particle duality with live Monte Carlo detection — plus an interactive
web presentation deck served by Flask.

[Readme فارسی](Readme_Fa.md)

---

## Features

### Classical Wave Optics
- Exact Fraunhofer double-slit intensity distribution `I(θ) = I₀ cos²(β) sinc²(α)`
- Live metrics: fringe spacing `Δy`, angular separation, maxima/minima angles, missing-order detection (`d/a` ratio)
- Adjustable parameters: wavelength `λ` (380–780 nm), fringe spacing `Δy` (bidirectionally linked to λ via `Δy = λL/d` — moving either one updates the other live), slit separation `d`, slit width `a`, screen distance `L`, refractive index `n`
- 6 laboratory presets: He-Ne Red, Argon-Ion Green, Violet Diode, Sodium D-Line, Underwater, High-Diffraction
- Physically accurate color rendering (Dan Bruton wavelength → sRGB mapping)

### Quantum Mechanics
- Particle selector: **Photon**, **Electron**, **Buckyball C₆₀** with real de Broglie wavelengths
- Kinetic energy / velocity controls in SI and eV units
- **Which-way observer detector** — toggles decoherence from full coherent superposition (D = 0) to complete wavefunction collapse (D = 1), erasing the interference pattern
- Vectorized Monte Carlo sampling that builds the detection histogram particle-by-particle, exactly like the historical buildup experiments

### Views (7 tabs)
| Tab | Description |
|---|---|
| 2D Screen | Detector screen — continuous spectral fringes (classical) or particle hit accumulation (quantum) |
| 1D Profile | High-performance Matplotlib intensity profile with peak annotation |
| Schematic | 2D optical-bench layout showing wavefronts and path difference `Δr` |
| 3D Setup | Interactive 3D apparatus with mouse rotation and wheel zoom |
| Calculations | Step-by-step symbolic derivations with live numerical substitution |
| History | Animated classroom slide deck on Young's 1801 experiment + quiz |
| Guide | Interactive software tutorial for every feature |

### Export Suite
- **CSV** — 22-column scientific dataset
- **DOCX** — laboratory report with native OMML editable equations
- **OBJ/MTL** — 3D wavefront CAD model with 1024×512 screen texture
- **PNG** — 300 DPI figures (profile, setup, screen, schematic, calculations)
- **All-in-one ZIP** bundling every artifact above

### Localization
- Full English and Persian UI, with proper RTL rendering (Unicode RLM marks, Vazirmatn typography, `arabic-reshaper` + `python-bidi`)
- Dark / light appearance themes

### Web Presentation
- Flask server hosting a responsive HTML5 slide deck with LaTeX math (MathJAX), interactive canvas visualizers, and a quiz

---

## Requirements

- Python **3.10+** (developed and tested on 3.11)
- Tkinter (bundled with standard Python installs)

## Installation

```bash
git clone https://github.com/AmirMoYousefVand/Double-slit-experiment-Simulator.git
cd Double-slit-experiment-Simulator

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Usage

### Desktop GUI

```bash
python main.py
```

### Web presentation

```bash
python -m web.app
# then open http://127.0.0.1:5055
```

### Test suite

```bash
python test_simulator.py
```

The suite covers classical Fraunhofer analytics, missing-order detection, de Broglie
wavelengths, observer-induced collapse, Monte Carlo throughput, colorimetry, all export
formats, font registration, every view, bilingual string separation, and full GUI
initialization.

---

## Project Structure

```
├── main.py                  # GUI entry point
├── config.py                # Physical constants (CODATA 2018), presets, UI config
├── test_simulator.py        # Comprehensive verification suite
├── physics/
│   ├── classical_engine.py  # Fraunhofer wave-optics solver
│   ├── quantum_engine.py    # Probability density, decoherence, Monte Carlo sampler
│   └── particle_types.py    # Photon / Electron / Buckyball properties
├── ui/
│   ├── main_window.py       # CustomTkinter shell (sidebar + 7-tab view area)
│   ├── components/          # Control, metrics and quantum panels
│   ├── views/               # 2D, 1D, schematic, 3D, calculations, history, guide
│   └── content/             # Slide deck & tutorial content
├── utils/                   # Exports, localization, fonts, colors, stats
├── web/                     # Flask presentation app (static + templates)
├── assets/                  # Fonts (Vazirmatn, Space Grotesk) & historical images
└── tools/                   # Asset download helpers
```

## Physics Reference

- Fraunhofer, F. (1821) — *Über die Entstehung der Farben*
- Young, T. (1807) — *A Course of Lectures on Natural Philosophy*
- de Broglie, L. (1924) — matter-wave hypothesis
- Zehnder/Zourappan & Arndt et al. (1999) — wave interference of C₆₀ fullerenes
- CODATA 2018 fundamental constants

## Credits

Historical portrait and laboratory images credits are listed in
[`assets/images/history/CREDITS.md`](assets/images/history/CREDITS.md).

## License

© 2026 — Created by **Amir Mohammad Yousefvand**. All rights reserved.

Source code and releases: [github.com/AmirMoYousefVand/Double-slit-experiment-Simulator](https://github.com/AmirMoYousefVand/Double-slit-experiment-Simulator)
