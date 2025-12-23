import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QDateEdit
)
from PyQt6.QtCore import Qt
import re
from datetime import datetime
from employee_utils import create_employee_with_history, get_current_salary
from config_manager import ConfigManager

class OrderDialog(QDialog):
    def __init__(self, parent = None, order_data = None, config_manager = None):
        super().__init__(parent)
        self.order_data = order_data
        self.config_manager = config_manager

        self.setup_ui()
        self.setFixedSize(500,550)

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("New Order Details"))

        # Order Date
        main_layout.addWidget(QLabel("Order Date:"))
        self.order_date_input = QDateEdit()
        self.order_date_input.setCalendarPopup(True)
        main_layout.addWidget(self.order_date_input)

        # Action Date

        main_layout.addWidget(QLabel("Order Date:"))
        self.action_date_input = QDateEdit()
        self.action_date_input.setCalendarPopup(True)
        main_layout.addWidget(self.action_date_input)

        # Order Type Selection
        main_layout.addWidget(QLabel("Type of Order:"))
        self.order_type_combo = QComboBox()
        order_types = ["employment","termination","salary change","department change"]
        self.order_type_combo.addItems(order_types)
        main_layout.addWidget(self.order_type_combo)

        # Current Department
        main_layout.addWidget(QLabel("Current Department:"))
        self.department_combo = QComboBox()
        departments = []
        if self.config_manager:
            departments = self.config_manager.get_departments()
            self.department_combo.addItems(departments)
        else:
            # Fallback departments if config_manager is not available
            print("Warning: config manager not available, using default departments")

        if not departments:
            # If still no departments, add a default
            departments = ["General"]
            print("Warning: No departments found, using 'General'")

        self.department_combo.addItems(departments)



        main_layout.addWidget(self.department_combo)

        self.setLayout(main_layout)


if __name__ =="__main__":
    dialog = OrderDialog()
