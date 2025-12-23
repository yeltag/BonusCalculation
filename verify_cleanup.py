# verify_cleanup.py
import json
import sqlite3


def verify_cleanup():
    print("=== VERIFYING CLEANUP ===")

    # Check config.json
    print("\n1. Checking config.json...")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

        # Should only have departments and kpis
        keys = list(config.keys())
        print(f"   Keys found: {keys}")

        if 'analysis fields' in config:
            print("   ⚠ WARNING: 'analysis fields' still in config.json")
        else:
            print("   ✓ 'analysis fields' removed")

        if 'cost centers' in config:
            print("   ⚠ WARNING: 'cost centers' still in config.json")
        else:
            print("   ✓ 'cost centers' removed")

        if 'departments' in config:
            print(f"   ✓ Departments found ({len(config['departments'])} items)")
        else:
            print("   ⚠ WARNING: 'departments' missing")

        if 'kpis' in config:
            print(f"   ✓ KPIs found ({len(config['kpis'])} items)")
        else:
            print("   ⚠ WARNING: 'kpis' missing")

    except Exception as e:
        print(f"   ✗ Error reading config.json: {e}")

    # Check database
    print("\n2. Checking database tables...")
    try:
        db = sqlite3.connect('bonus_system.db')
        cursor = db.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"   Tables found: {tables}")

        # Check for unwanted tables
        unwanted_tables = ['analysis_fields', 'cost_centers']
        for table in unwanted_tables:
            if table in tables:
                print(f"   ⚠ WARNING: '{table}' table exists in database")
            else:
                print(f"   ✓ '{table}' table not found (good)")

        db.close()
    except Exception as e:
        print(f"   ✗ Error checking database: {e}")

    print("\n=== CLEANUP VERIFICATION COMPLETE ===")


if __name__ == "__main__":
    verify_cleanup()