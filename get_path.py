import sys
import os

from pathlib import Path

def go(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def nuitka(relative_path: str) -> Path:
    """Return absolute path to a bundled resource (works in dev, standalone, and onefile)."""
    if getattr(sys, "frozen", False):
        # Nuitka onefile -> sys._MEIPASS points to temp extraction folder
        # Nuitka standalone -> sys.argv[0] is inside dist folder
        base_path = Path(getattr(sys, "_MEIPASS", Path(sys.argv[0]).parent))
    else:
        base_path = Path(__file__).parent
    return base_path / relative_path