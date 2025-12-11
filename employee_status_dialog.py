import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDoubleSpinBox,
    QGroupBox, QDateEdit, QFormLayout, QLineEdit  # Added QLineEdit
)
from PyQt6.QtCore import Qt
from datetime import datetime


class EmployeeStatusDialog(QDialog):
    def __init__(self, parent=None, database=None, config_manager=None, employee=None):
        super().__init__(parent)
        self.database = database
        self.config_manager = config_manager
        self.employee = employee
        self.setWindowTitle(f"Employee Details - {employee['first_name']} {employee['last_name']}")
        self.setFixedSize(500, 450)  # Increased height
        self.setup_ui()
        self.load_employee_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Employee info header
        info_label = QLabel(
            f"Editing: {self.employee['first_name']} {self.employee['last_name']} ({self.employee['id']})")
        info_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(info_label)

        # Edit form
        form_group = QGroupBox("Employee Details")
        form_layout = QFormLayout()

        # Form fields
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Terminated"])

        self.department_combo = QComboBox()
        departments = self.config_manager.get_departments()
        self.department_combo.addItems(departments)

        self.father_name_input = QLineEdit()  # NEW FIELD
        self.father_name_input.setPlaceholderText("Optional")

        self.salary_spin = QDoubleSpinBox()
        self.salary_spin.setRange(0, 999999)
        self.salary_spin.setDecimals(2)
        self.salary_spin.setPrefix("$ ")

        self.effective_date = QDateEdit()
        self.effective_date.setCalendarPopup(True)
        self.effective_date.setDate(datetime.now())

        # Add to form
        form_layout.addRow("Status:", self.status_combo)
        form_layout.addRow("Department:", self.department_combo)
        form_layout.addRow("Father's Name:", self.father_name_input)  # NEW FIELD
        form_layout.addRow("Salary:", self.salary_spin)
        form_layout.addRow("Effective Date:", self.effective_date)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()

        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_changes)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_employee_data(self):
        """Load current employee data into form"""
        self.status_combo.setCurrentText(self.employee["status"])
        self.department_combo.setCurrentText(self.employee["department"])
        self.father_name_input.setText(self.employee.get("father_name", ""))  # NEW FIELD
        self.salary_spin.setValue(self.employee["salary"])

    def save_changes(self):
        """Save changes to employee"""
        # Check if any changes were made
        changes_made = (
                self.employee["status"] != self.status_combo.currentText() or
                self.employee["department"] != self.department_combo.currentText() or
                self.employee.get("father_name", "") != self.father_name_input.text().strip() or  # NEW FIELD
                self.employee["salary"] != self.salary_spin.value()
        )

        if not changes_made:
            QMessageBox.information(self, "No Changes", "No changes were made.")
            self.reject()
            return

        # Update employee data
        updated_employee = self.employee.copy()
        updated_employee["status"] = self.status_combo.currentText()
        updated_employee["department"] = self.department_combo.currentText()
        updated_employee["father_name"] = self.father_name_input.text().strip()  # NEW FIELD

        # Handle salary change with history
        if self.employee["salary"] != self.salary_spin.value():
            # Get existing salary history
            salary_history = self.database.get_employee_salary_history(self.employee["id"])

            # End previous salary record
            for record in salary_history:
                if record.get("end_date") is None:
                    record["end_date"] = self.effective_date.date().toString("yyyy-MM-dd")

            # Add new salary record
            salary_history.append({
                "salary": self.salary_spin.value(),
                "effective_date": self.effective_date.date().toString("yyyy-MM-dd"),
                "end_date": None
            })

            updated_employee["salary_history"] = salary_history
            updated_employee["salary"] = self.salary_spin.value()

        # Save to database
        self.database.save_employee(updated_employee)
        self.accept()