import json
import os
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QListWidget, QMessageBox, QTabWidget, QWidget, QInputDialog, QComboBox)

from PyQt6.QtCore import Qt


class ConfigManager:
    def __init__(self, config_file = "config.json", database = None):
        self.config_file = config_file
        self.database = database
        self.config = self.load_config()


    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "departments": ["Sales","Marketing","IT","HR","Finance","Operations"],
            "cost centers": ["CC001","CC002","CC003"],
            "analysis fields":[
                {"name":"Performance Rating","type":"number","min": 1, "max":5},
                {"name": "Years of Service", "type":"number"},

            ],
            "kpis":[]

        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)

                # Merge with default config to ensure all required keys exist
                merged_config = default_config.copy()
                merged_config.update(user_config)

                if self.database:
                    db_kpis = self.database.get_all_kpis()
                    if db_kpis:
                        merged_config["kpis"] = db_kpis
                        print("INFO: Loaded KPIs from database")
                    elif "kpis" not in user_config or not user_config["kpis"]:
                        merged_config["kpis"] = default_config["kpis"]
                else:
                    print("WARNING: No database connection for KPIs")

                return merged_config

            else:
                # Create config file with defaults
                self.save_config(default_config)
                print("INFO: Created new config file")
                return default_config

        except Exception as e:
            print(f"Error loading config load_config line 58:{e}")
            return default_config



    def save_config(self, config = None):
        """Save configuration to JSON file"""
        if config:
            self.config = config
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent = 4)
            return True

        except Exception as e:
            print(f"Error saving config save_config line 73: {e}")
            return False


    def get_departments(self):
        return self.config.get("departments",[])

    def add_department(self,department):
        departments = self.get_departments()
        if department not in departments:
            departments.append(department)
            self.config["departments"] = departments
            return self.save_config()
        return False

    def remove_department(self, department):
        departments = self.get_departments()
        if department in departments:
            departments.remove(department)
            self.config["departments"] = departments
            return self.save_config()
        return False

    def get_kpis(self):
        """Get KPIs - prefer database, fallback to config file"""
        if self.database:
            # Try to get from database first
            try:
                db_kpis = self.database.get_all_kpis()
                if db_kpis:
                    # Update config with database KPIs
                    self.config["kpis"] = db_kpis
                    return db_kpis
            except Exception as e:
                print(f"Error getting KPIs from database get_kpis line 107: {e}")


        # Fallback to config file
        return self.config.get("kpis",[])


    def add_kpi(self, kpi_data):
        """Add KPI to both database and config"""
        # Add to database if available
        if self.database:
            try:
                self.database.save_kpi(kpi_data)
                print("INFO: KPI saved to database")
            except Exception as e:
                print(f"Error saving KPI to database add_kpi line 122:{e}")
                return False

        # Also update config file
        kpis = self.get_kpis()
        kpis.append(kpi_data)
        self.config["kpis"] = kpis
        return self.save_config()

    def update_kpi(self, index, kpi_data):
        """Update KPI in both database and config"""
        print(f"=== DEBUG UPDATE KPI ===")
        print(f"Updating KPI at index {index}")
        print(f"KPI data: {kpi_data}")

        kpis = self.get_kpis()
        print(f"Current KPIs count: {len(kpis)}")

        if 0 <= index < len(kpis):
            original_kpi = kpis[index]
            print(f"Original KPI: {original_kpi}")
            print(f"Original KPI ID: {original_kpi.get('id', 'NO ID')}")

            # Update in database if available
            if self.database:
                try:
                    # PRESERVE THE ORIGINAL ID FOR DATABASE UPDATE
                    if "id" in original_kpi:
                        kpi_data["id"] = original_kpi["id"]
                        print(f"Preserved ID for database update: {kpi_data['id']}")

                    # Save to database - this should update existing record due to ID
                    success = self.database.save_kpi(kpi_data)
                    print(f"Database save result: {success}")

                    if success:
                        print("KPI updated in database")
                        # Refresh KPIs from database to get the updated data
                        db_kpis = self.database.get_all_kpis()
                        if db_kpis:
                            self.config["kpis"] = db_kpis
                            if self.save_config():
                                print("Config updated with database KPIs")
                                return True
                            else:
                                print("Failed to save config after database update")
                                return False
                    else:
                        print("Database save failed")
                        return False

                except Exception as e:
                    print(f"Error updating KPI in database: {e}")
                    # Fall through to config update
            else:
                print("No database connection, updating config only")

            # Update in config (fallback if no database or database update failed)
            kpis[index] = kpi_data
            self.config["kpis"] = kpis
            result = self.save_config()
            print(f"Config save result: {result}")
            return result

        print(f"Invalid index: {index}")
        return False
