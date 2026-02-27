#!/usr/bin/env python3
"""
Root entry point for Streamlit Cloud deployment.
Loads the main app from app_ui/
"""

import sys
from pathlib import Path

# Add app_ui to path
sys.path.insert(0, str(Path(__file__).parent / "app_ui"))

# Import and run the main app
exec(open(Path(__file__).parent / "app_ui" / "streamlit_app.py").read())
