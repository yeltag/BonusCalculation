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
                {"name":"Education Level", "type":"dropdown", "opetions":["Bachelor","Master","PhD"]}
            ],
            "kips":[
                {
                    "name": "Sales Performance",
                    "departments":["Sales"],
                    "calculation_method":"persentage",
                    "formula":"base_salary * 0.1 * (sales_achivement / 100)",
                    "weight": 0.3
                },
                {
                    "name": "project Completion",
                    "departments": ["IT", "Operaions"],
                    "calculation_method": "fixed",
                    "formula": "500 * completed_projects",
                    "weight": 0.4
                }
            ]

        }

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    return json.load(f)

            else:
                self.save_config(default_config)
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
        return self.config.get("kpis",[])

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

