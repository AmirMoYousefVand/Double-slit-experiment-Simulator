# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the Thomas Young Double-Slit Experiment Simulator.

Build (from the project root):
    pyinstaller --clean --noconfirm Young_Double_Slit_Simulator.spec

Produces a single windowed executable at:
    dist/Young_Double_Slit_Simulator.exe
"""

import os

ROOT = os.path.abspath(SPECPATH)

block_cipher = None

# Assets are resolved relative to each module's __file__, so they must land at
# the same relative locations inside the bundle.
datas = [
    (os.path.join(ROOT, "assets"), "assets"),
    (os.path.join(ROOT, "web", "templates"), "web/templates"),
    (os.path.join(ROOT, "web", "static"), "web/static"),
]

hiddenimports = [
    # Embedded Flask presentation (imported from a method at runtime)
    "web",
    "web.app",
    "werkzeug.serving",
    # Matplotlib GUI backend used by the 1D / 3D / history figures
    "matplotlib.backends.backend_tkagg",
    "matplotlib.backends.backend_agg",
    # Pillow Tk bridge used by the 2D detector screen
    "PIL.Image",
    "PIL.ImageTk",
    "PIL._tkinter_finder",
    # Persian RTL text pipeline
    "arabic_reshaper",
    "bidi",
    "bidi.algorithm",
    # Word report export
    "docx",
    "docx.oxml.ns",
    # Scientific stack
    "numpy",
    "tkinter",
    "tkinter.ttk",
    "tkinter.filedialog",
    "tkinter.messagebox",
]

excludes = [
    "tkinter.test",
    "matplotlib.tests",
    "PyQt5",
    "PyQt6",
    "PySide2",
    "PySide6",
    "pytest",
    "IPython",
    "setuptools",
]

a = Analysis(
    [os.path.join(ROOT, "main.py")],
    pathex=[ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Young_Double_Slit_Simulator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # windowed GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT, "assets", "Logo", "favicon.ico"),
)
