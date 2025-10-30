import json
import os
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QListWidget, QMessageBox, QTabWidget, QWidget, QInputDialog, QComboBox)

from PyQt6.QtCore import Qt


class ConfigManager:
    def __init__(self, config_file = "config.json"):
        self.config_file = config_file
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
            "kpis":[
                {
                    "name": "Basic Performance Bonus",
                    "description": "Standard performance bonus for all employees",
                    "departments":[],
                    "calculation_method":"persentage",
                    "percentage":0.10, # 10% bonus
                    "weight": 1.0,
                    "is_active": True
                },
                {
                    "name": "Sales Achievement Bonus",
                    "description": "Additional bonus for sales team performance",
                    "departments": ["Sales"],
                    "calculation_method": "percentage",
                    "percentage": 0.05, # 5% bonus for sales
                    "weight": 1.0,
                    "is_active": True
                },
                {
                    "name": "Quarterly Fixed Bonus",
                    "description": "Fixed quarterly performance bonus",
                    "departments": [],  # All departments
                    "calculation_method": "fixed",
                    "fixed_amount": 250,  # $250 fixed bonus
                    "weight": 1.0,
                    "is_active": True
                }
            ]

        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)

                # Merge with default config to ensure all required keys exist
                merged_config = default_config.copy()
                merged_config.update(user_config)

                # Ensure kpis key exists and has content
                if 'kpis' not in user_config or not user_config['kpis']:
                    merged_config['kpis'] = default_config['kpis']
                    print("INFO: Added default KPIs to configuration")

                return merged_config
            else:
                # Create config file with defaults
                self.save_config(default_config)
                print("INFO: Created new config file with default KPIs")
                return default_config

        except Exception as e:
            print(f"Error loading config: {e}")
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
            print(f"Error saving config: {e}")
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
        kpis = self.config.get("kpis", [])
        print(f"DEBUG: ConfigManager returning {len(kpis)} KPIs")
        for kpi in kpis:
            print(f"  - {kpi['name']} ({kpi['calculation_method']})")
        return kpis

    def add_kpi(self, kpi_data):
        kpis = self.get_kpis()
        kpis.append(kpi_data)
        self.config["kpis"] = kpis
        return self.save_config()

    def update_kpi(self, index, kpi_data):
        kpis = self.get_kpis()
        if 0 <= index < len(kpis):
            kpis[index] = kpi_data
            self.config["kpis"] = kpis
            return self.save_config()
        return False

