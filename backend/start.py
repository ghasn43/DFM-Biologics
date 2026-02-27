#!/usr/bin/env python3
"""
Startup script for DFM Biologics Backend
Runs the FastAPI server with automatic configuration.
"""

import os
import sys
import subprocess

def main():
    """Start the backend."""
    
    # Check we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Error: backend/main.py not found")
        print("Please run this script from the backend/ directory:")
        print("  cd backend")
        print("  python main.py")
        sys.exit(1)
    
    # Run FastAPI
    print("\n🧬 DFM Biologics Backend")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n✋ Backend shutdown by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
