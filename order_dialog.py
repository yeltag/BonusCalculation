import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QDateEdit, QApplication
)
from PyQt6.QtCore import Qt
import re
from datetime import datetime
from employee_utils import create_employee_with_history, get_current_salary
from config_manager import ConfigManager
from database import Database

class OrderDialog(QDialog):
    def __init__(self, parent = None, order_data = None, config_manager = None):
        super().__init__(parent)
        self.order_data = order_data
        self.database = Database()
        self.config_manager = ConfigManager(database = self.database)

        self.setWindowTitle("Add New Order")

        self.setup_ui()
        self.setFixedSize(500,550)

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("New Order Details"))

        # Order Date
        main_layout.addWidget(QLabel("Order Date:"))
        self.order_date_input = QDateEdit()
        self.order_date_input.setCalendarPopup(True)
        self.order_date_input.setDate(datetime.now().date())
        main_layout.addWidget(self.order_date_input)

        # Order Number

        main_layout.addWidget(QLabel("Order Number:"))
        self.order_number_input = QLineEdit()
        self.order_number_input.setPlaceholderText("insert order number")
        main_layout.addWidget(self.order_number_input)

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


        # Order Type Selection
        main_layout.addWidget(QLabel("Type of Order:"))
        self.order_type_combo = QComboBox()
        order_types = ["employment","termination","salary change","department change"]
        self.order_type_combo.addItems(order_types)
        self.order_type_combo.currentTextChanged.connect(self.order_type_changed)
        main_layout.addWidget(self.order_type_combo)

        self.order_type_layout = QVBoxLayout()
        main_layout.addLayout(self.order_type_layout)
        main_layout.addStretch()




        self.setLayout(main_layout)
        self.order_type_changed(self.order_type_combo.currentText())

    def order_type_changed(self,text):
        # Clear existing widgets
        while self.order_type_layout.count():
            item = self.order_type_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for widget in self.create_layout_widgets(text):
            self.order_type_layout.addWidget(widget)

    def create_layout_widgets(self,text):
        widgets = []
        if text == "employment":
            widgets.append(QLabel("Enter new employee ID:"))
            widgets.append(QLineEdit(placeholderText = "FIN Kod"))
            widgets.append(QLabel("Last Name:"))
            widgets.append(QLineEdit(placeholderText="Filankəsov"))
            widgets.append(QLabel("First Name:"))
            widgets.append(QLineEdit(placeholderText = "Filankəs"))
            widgets.append(QLabel("Father's Name:"))
            widgets.append(QLineEdit(placeholderText = "Filankəs oğlu"))

            # Hire Date
            widgets.append(QLabel("Hire Date:"))
            widgets.append(QDateEdit())

            # Current Salary
            widgets.append(QLabel("Set Monthly Salary:"))
            widgets.append(QLineEdit(placeholderText="5000.00"))

        return widgets

if __name__ =="__main__":
    app = QApplication(sys.argv)
    dialog = OrderDialog()
    # Show the dialog
    dialog.show()  # Add this line to show the dialog

    # Start the application event loop
    sys.exit(app.exec())
