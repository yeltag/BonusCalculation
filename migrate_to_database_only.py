# migrate_to_database_only.py
import json
import sqlite3
from datetime import datetime


def clean_migration():
    """Migrate to database-only approach and clean up config.json"""

    # Step 1: Update config.json to remove unused fields
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

        # Remove unused fields
        config.pop('analysis fields', None)
        config.pop('cost centers', None)

        # Save cleaned config
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

        print("✓ Cleaned config.json")
    except Exception as e:
        print(f"✗ Error cleaning config.json: {e}")
        return

    # Step 2: Verify database has required tables
    try:
        db = sqlite3.connect('bonus_system.db')
        cursor = db.cursor()

        # Check if kpis table exists (main configuration table)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kpis'")
        if not cursor.fetchone():
            print("⚠ KPI table not found in database")
            print("⚠ Note: KPIs should be created through the GUI (KPI Editor)")
            print("⚠ They will be saved to the database automatically")

        # Check if custom_variables table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='custom_variables'")
        if not cursor.fetchone():
            print("⚠ Custom variables table not found")
            print("⚠ Run the application once to initialize the database")

        db.close()
        print("✓ Database check completed")

    except Exception as e:
        print(f"✗ Error checking database: {e}")

    print("\n✅ Migration complete!")
    print("\nNext steps:")
    print("1. Run the application to ensure all database tables are created")
    print("2. Use the GUI to manage KPIs (they will be saved to database)")
    print("3. Departments will still be loaded from config.json for now")
    print("4. All custom variables are already database-only")


if __name__ == "__main__":
    clean_migration()