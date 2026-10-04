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

from ui.main_window import MainWindow

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
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
