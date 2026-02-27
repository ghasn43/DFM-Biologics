#!/usr/bin/env python3
"""
Quick validation script to verify DFM Biologics installation.
Run this to ensure everything is set up correctly.
"""

import sys
import importlib.util

def check_import(module_name: str, display_name: str) -> bool:
    """Check if a module can be imported."""
    try:
        __import__(module_name)
        print(f"✅ {display_name:30} OK")
        return True
    except ImportError as e:
        print(f"❌ {display_name:30} MISSING: {e}")
        return False

def main():
    """Run all checks."""
    print("\n🧬 DFM Biologics - Installation Verification\n")
    print("=" * 60)
    
    checks = [
        ("pydantic", "Pydantic"),
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn (FastAPI server)"),
        ("streamlit", "Streamlit"),
        ("pytest", "pytest (testing)"),
        ("dotenv", "python-dotenv"),
        ("yaml", "PyYAML"),
    ]
    
    results = []
    for module_name, display_name in checks:
        results.append(check_import(module_name, display_name))
    
    print("=" * 60)
    
    # Check backend modules
    print("\nBackend Modules:")
    print("-" * 60)
    
    backend_imports = [
        ("backend.core.models", "Models"),
        ("backend.core.scoring", "Scoring"),
        ("backend.core.checks_sequence", "Sequence Checks"),
        ("backend.core.checks_construct", "Construct Checks"),
        ("backend.api.routes", "API Routes"),
    ]
    
    for module_name, display_name in backend_imports:
        results.append(check_import(module_name, display_name))
    
    print("=" * 60)
    
    # Summary
    total = len(results)
    passed = sum(results)
    
    print(f"\nSummary: {passed}/{total} checks passed\n")
    
    if all(results):
        print("✅ All dependencies installed! Ready to run DFM Biologics.\n")
        print("Next steps:")
        print("1. Start backend:   cd backend && python main.py")
        print("2. Start frontend:  streamlit run app_ui/streamlit_app.py")
        print("3. Open browser:    http://localhost:8501")
        print()
        return 0
    else:
        print("❌ Some dependencies missing. Run: pip install -e .\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
