#!/usr/bin/env python3
"""
Startup script for DFM Biologics Frontend
Runs Streamlit with automatic configuration.
"""

import os
import sys
import subprocess

def main():
    """Start the frontend."""
    
    # Check we're in the right directory
    if not os.path.exists("app_ui/streamlit_app.py"):
        print("❌ Error: app_ui/streamlit_app.py not found")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Run Streamlit
    print("\n🧬 DFM Biologics Frontend")
    print("=" * 60)
    
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "app_ui/streamlit_app.py"],
            check=True
        )
    except KeyboardInterrupt:
        print("\n\n✋ Frontend shutdown by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
