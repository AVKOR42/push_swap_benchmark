#!/usr/bin/env python3
# bench.py
"""
  run with: python bench.py
  or
  ./bench.py
"""
import os
import sys

# Qt's Wayland text-input v3 backend logs harmless focus warnings
os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.wayland.textinput=false")

# Wayland ignores window positions requested by the client; XWayland honors them.
# Needs libxcb-cursor0 (Debian/Ubuntu). Delete this to go back to native Wayland.
if os.environ.get("WAYLAND_DISPLAY") and os.environ.get("DISPLAY"):
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

from PyQt6.QtWidgets import QApplication  # noqa: E402
from src.gui import MainWindow  # noqa: E402


if __name__ == "__main__":
	app = QApplication(sys.argv)
	win = MainWindow()
	win.show()
	sys.exit(app.exec())