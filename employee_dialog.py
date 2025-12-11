import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QDateEdit
)
from PyQt6.QtCore import Qt
import re
from datetime import datetime
from employee_utils import create_employee_with_history, get_current_salary


class EmployeeDialog(QDialog):
    def __init__(self, parent=None, employee_data=None, config_manager=None):
        super().__init__(parent)
        self.employee_data = employee_data
        self.is_edit_mode = employee_data is not None
        self.config_manager = config_manager

        if self.is_edit_mode:
            self.setWindowTitle("Edit Employee")
        else:
            self.setWindowTitle("Add New Employee")

        self.setup_ui()
        self.setFixedSize(500, 550)  # Increased height to accommodate new field

    def setup_ui(self):
        # Debug information
        print(f"DEBUG: Config manager available:{self.config_manager is not None}")
        if self.config_manager:
            departments = self.config_manager.get_departments()
            print(f"DEBUG: Departments from config:{departments}")
        else:
            print("DEBUG: No config manager provided")

        # Main layout - using simple QVBoxLayout that works
        main_layout = QVBoxLayout()

        # Basic Information Section
        main_layout.addWidget(QLabel("Basic Information"))

        # Employee ID
        main_layout.addWidget(QLabel("Employee ID:"))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("EMP001")
        if self.is_edit_mode:
            self.id_input.setText(self.employee_data.get("id", ""))
            self.id_input.setEnabled(False)
        main_layout.addWidget(self.id_input)

        # Names
        main_layout.addWidget(QLabel("First Name:"))
        self.first_name_input = QLineEdit()
        self.first_name_input.setPlaceholderText("John")
        if self.is_edit_mode:
            self.first_name_input.setText(self.employee_data.get("first_name", ""))
        main_layout.addWidget(self.first_name_input)

        main_layout.addWidget(QLabel("Last Name:"))
        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Smith")
        if self.is_edit_mode:
            self.last_name_input.setText(self.employee_data.get("last_name", ""))
        main_layout.addWidget(self.last_name_input)

        # Father's Name - NEW FIELD
        main_layout.addWidget(QLabel("Father's Name:"))
        self.father_name_input = QLineEdit()
        self.father_name_input.setPlaceholderText("Optional")
        if self.is_edit_mode:
            self.father_name_input.setText(self.employee_data.get("father_name", ""))
        main_layout.addWidget(self.father_name_input)

        # Hire Date
        main_layout.addWidget(QLabel("Hire Date:"))
        self.hire_date_input = QDateEdit()
        self.hire_date_input.setCalendarPopup(True)
        if self.is_edit_mode and self.employee_data.get("hire_date"):
            self.hire_date_input.setDate(datetime.strptime(self.employee_data["hire_date"], "%Y-%m-%d"))
        else:
            self.hire_date_input.setDate(datetime.now())
        main_layout.addWidget(self.hire_date_input)

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

        if self.is_edit_mode:
            current_dept = self.employee_data.get("department", "")
            if current_dept:
                index = self.department_combo.findText(current_dept)
                if index >= 0:
                    self.department_combo.setCurrentIndex(index)
                else:
                    # If department doesn't exist in list, add it and select it
                    self.department_combo.addItem(current_dept)
                    self.department_combo.setCurrentIndex(self.department_combo.count() - 1)
            else:
                # If no current department, select first one
                self.department_combo.setCurrentIndex(0)

        main_layout.addWidget(self.department_combo)

        # Current Salary
        main_layout.addWidget(QLabel("Current Monthly Salary ($):"))
        self.salary_input = QLineEdit()
        self.salary_input.setPlaceholderText("5000.00")
        if self.is_edit_mode:
            current_salary = get_current_salary(self.employee_data)
            self.salary_input.setText(str(current_salary))
        main_layout.addWidget(self.salary_input)

        # Salary Effective Date (for changes)
        if self.is_edit_mode:
            main_layout.addWidget(QLabel("Salary Effective Date:"))
            self.salary_effective_date = QDateEdit()
            self.salary_effective_date.setCalendarPopup(True)
            self.salary_effective_date.setDate(datetime.now())
            main_layout.addWidget(self.salary_effective_date)

        # Status
        main_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Active", "Terminated"])
        if self.is_edit_mode:
            current_status = self.employee_data.get("status", "Active")
            index = self.status_combo.findText(current_status)
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        main_layout.addWidget(self.status_combo)

        # Add some space
        main_layout.addSpacing(20)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        if self.is_edit_mode:
            save_btn = QPushButton("Save Changes")
        else:
            save_btn = QPushButton("Add Employee")

        save_btn.clicked.connect(self.validate_and_save)

        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def validate_and_save(self):
        """Validate inputs and save employee data"""
        # Get values from form
        employee_id = self.id_input.text().strip()
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        father_name = self.father_name_input.text().strip()  # NEW FIELD
        department = self.department_combo.currentText()
        salary_text = self.salary_input.text().strip()
        status = self.status_combo.currentText()

        # Validation checks
        errors = []

        # Employee ID validation
        if not employee_id:
            errors.append("Employee ID is required")
        elif not re.match(r'^[A-Za-z0-9_-]+$', employee_id):
            errors.append("Employee ID can only contain letters, numbers, hyphens, and underscores")

        # Name validation
        if not first_name:
            errors.append("First name is required")
        elif not re.match(r'^[A-Za-z\s\-]+$', first_name):
            errors.append("First name can only contain letters, spaces, and hyphens")

        if not last_name:
            errors.append("Last name is required")
        elif not re.match(r'^[A-Za-z\s\-]+$', last_name):
            errors.append("Last name can only contain letters, spaces, and hyphens")

        # Father's name is optional, but validate format if provided
        if father_name and not re.match(r'^[A-Za-z\s\-\.]+$', father_name):
            errors.append("Father's name can only contain letters, spaces, hyphens, and periods")

        # Salary validation
        if not salary_text:
            errors.append("Salary is required")
        else:
            try:
                salary = float(salary_text)
                if salary <= 0:
                    errors.append("Salary must be greater than 0")
            except ValueError:
                errors.append("Salary must be a valid number")

        # Show errors if any
        if errors:
            error_msg = "Please fix the following errors:\n\n" + "\n".join(f"- {error}" for error in errors)
            QMessageBox.warning(self, "Validation Error", error_msg)
            return

        # Store the validated data
        self.employee_data = {
            "id": employee_id,
            "first_name": first_name,
            "last_name": last_name,
            "father_name": father_name,  # NEW FIELD
            "department": department,
            "salary": float(salary_text),
            "status": status,
            "hire_date": self.hire_date_input.date().toString("yyyy-MM-dd")
        }

        # Handle salary/department history for edits
        if self.is_edit_mode:
            # Check if salary changes
            old_salary = get_current_salary(self.employee_data)
            if float(salary_text) != old_salary:
                # Update history - end previous salary record
                for record in self.employee_data.get("salary_history", []):
                    if record["end date"] is None:
                        record["end_date"] = self.salary_effective_date.date().toString("yyy-MM-dd")

                # Add new salary record
                self.employee_data["salary_history"].append({
                    "salary": float(salary_text),
                    "effective_date": self.salary_effective_date.date().toString("yyyy-MM-dd"),
                    "end_date": None
                })

            # Update current data
            self.employee_data.update(self.employee_data)
        else:
            # New employee - create with history
            self.employee_data = create_employee_with_history(self.employee_data)

        # Close dialog with success
        self.accept()

    def get_employee_data(self):
        """Return the employee data entered in the form"""
        print(f"DEBUG: Returning employee data: {self.employee_data}")
        return self.employee_data