"""
Entry point for Thomas Young's Double-Slit Experiment Simulator.
Run this script to launch the interactive application:
    python main.py
"""

import sys
import os

# Ensure project root is in Python module search path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Configure Windows terminal stdout for UTF-8 compatibility
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import traceback


def report_fatal(message: str) -> None:
    """Best-effort crash report for the no-console packaged executable.

    Windowed builds have no terminal, so fatal errors are appended to a log in
    the temp directory and surfaced with a native message box.
    """
    try:
        import tempfile
        from datetime import datetime
        log_path = os.path.join(tempfile.gettempdir(), "young_double_slit_error.log")
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}]\n{message}\n")
    except Exception:
        pass

    if getattr(sys, "frozen", False):
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                None,
                "The simulator failed to start.\nDetails were written to:\n"
                "%TEMP%\\young_double_slit_error.log",
                "Young Double-Slit Simulator — Startup Error",
                0x10,
            )
        except Exception:
            pass


try:
    from ui.main_window import MainWindow
except Exception:
    report_fatal("Import failed:\n" + traceback.format_exc())
    raise


def main():
    """Initializes and runs the main CustomTkinter application loop."""
    print("=" * 70)
    print("  Thomas Young Double-Slit Experiment Simulator")
    print("  شبیه‌ساز جامع آزمایش دو شکاف یانگ (اپتیک موجی و مکانیک کوانتومی)")
    print("=" * 70)
    print("Launching GUI application...")

    try:
        app = MainWindow()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nSimulation terminated by user.")
    except Exception as e:
        print(f"\nError running application: {e}")
        traceback.print_exc()
        report_fatal(traceback.format_exc())

if __name__ == "__main__":
    main()
