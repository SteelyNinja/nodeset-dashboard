#!/usr/bin/env python3
"""
NodeSet Validator Dashboard
Main application entry point with sync committee functionality
"""

if __name__ == "__main__":
    try:
        from dashboard import run_dashboard
        run_dashboard()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n🔧 Missing dependencies. Please ensure you have:")
        print("- dashboard.py (with run_dashboard function)")
        print("- tables.py (with all table functions)")  
        print("- data_loader.py (with all data loading functions)")
        print("- config.py, components.py, charts.py, analysis.py, utils.py")
        print("\n📄 Place sync_committee_participation.json in your directory")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        import traceback
        traceback.print_exc()
