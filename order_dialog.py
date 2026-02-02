import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QMessageBox, QDateEdit, QApplication,QWidget
)
from PyQt6.QtCore import Qt
import re
from datetime import datetime
from employee_utils import create_employee_with_history, get_current_salary
from config_manager import ConfigManager
from database import Database
import sqlite3

class OrderDialog(QDialog):
    def __init__(self, parent = None, order_data = None, config_manager = None,employee = None,order_type = None):
        super().__init__(parent)
        self.order_data = order_data
        self.order_type = order_type
        self.database = Database()
        self.config_manager = config_manager or ConfigManager(database=self.database)
        self.employee = employee

        self.employee_combo = None
        self.employee_id_input = None
        self.last_name_input = None
        self.first_name_input = None
        self.father_name_input = None
        self.hire_date_input = None
        self.salary_input = None
        self.new_salary_input = None
        self.departments_combo = None
        self.effective_date_input = None
        self.new_departments_combo = None

        self.setWindowTitle("Add New Order")

        self.setup_ui()
        self.setFixedSize(500,600)

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("New Order Details"))

        # Create a widget for the form content
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_widget.setContentsMargins(0,0,0,0)

        # Order Date
        form_layout.addWidget(QLabel("Order Date:"))
        self.order_date_input = self.create_date_edit()
        form_layout.addWidget(self.order_date_input)

        # Order Number

        form_layout.addWidget(QLabel("Order Number:"))
        self.order_number_input = QLineEdit()
        self.order_number_input.setPlaceholderText("Insert order number")
        form_layout.addWidget(self.order_number_input)

        # Current Department
        form_layout.addWidget(QLabel("Current Department:"))
        self.department_combo = QComboBox()

        self.department_combo.currentTextChanged.connect(self.on_department_changed)
        departments = []
        if self.employee:
            self.department_combo.setCurrentText(self.employee["department"])
            departments.append(self.employee["department"])
        else:
            if self.config_manager:
                departments = self.config_manager.get_departments()
                #self.department_combo.addItems(departments)
            else:
                # Fallback departments if config_manager is not available
                print("Warning: config manager not available, using default departments")

        if not departments:
            # If still no departments, add a default
            departments = ["General"]
            print("Warning: No departments found, using 'General'")

        self.department_combo.addItems(departments)


        form_layout.addWidget(self.department_combo)


        # Order Type Selection
        form_layout.addWidget(QLabel("Type of Order:"))
        self.order_type_combo = QComboBox()
        order_types = ["employment","termination","salary change","department change"]
        self.order_type_combo.addItems(order_types)
        if self.order_type:
            self.order_type_combo.setCurrentText(self.order_type)

        self.order_type_combo.currentTextChanged.connect(self.order_type_changed)
        form_layout.addWidget(self.order_type_combo)

        self.order_type_layout = QVBoxLayout()
        form_layout.addLayout(self.order_type_layout)

        # Dynamic layout for order type specific widgets
        self.order_type_layout = QVBoxLayout()
        form_layout.addLayout(self.order_type_layout)

        # Add form widget to main layout
        main_layout.addWidget(form_widget,0)

        # Add a stretchable spacer to push buttons to bottom
        main_layout.addStretch(1)

        # Add buttons
        self.buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Save new order")
        self.cancel_button = QPushButton("Cancel")
        self.buttons_layout.addWidget(self.save_button)
        self.buttons_layout.addWidget(self.cancel_button)
        self.buttons_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        main_layout.addLayout(self.buttons_layout)

        # Connect button signals
        self.save_button.clicked.connect(self.show_summary_dialog)
        self.cancel_button.clicked.connect(self.reject)


        self.setLayout(main_layout)

        self.order_type_changed(self.order_type_combo.currentText())



    def order_type_changed(self,text):
        self.text = text
        # Clear existing widgets safely
        for i in reversed(range(self.order_type_layout.count())):
            widget = self.order_type_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Reset employee_combo reference
        self.employee_combo = None


        for widget in self.create_layout_widgets(self.text):
            self.order_type_layout.addWidget(widget)

    def create_layout_widgets(self,text):
        self.widgets = []
        if text == "employment":
            self.widgets.append(QLabel("Enter new employee ID:"))
            self.employee_id_input = QLineEdit(placeholderText = "FIN Kod")
            self.widgets.append(self.employee_id_input)
            self.widgets.append(QLabel("Last Name:"))
            self.last_name_input = QLineEdit(placeholderText="Filankəsov")
            self.widgets.append(self.last_name_input)

            self.widgets.append(QLabel("First Name:"))
            self.first_name_input = QLineEdit(placeholderText = "Filankəs")
            self.widgets.append(self.first_name_input)
            self.widgets.append(QLabel("Father's Name:"))
            self.father_name_input = QLineEdit(placeholderText = "Filankəs oğlu")
            self.widgets.append(self.father_name_input)

            # Hire Date
            self.widgets.append(QLabel("Hire Date:"))
            self.hire_date_input = self.create_date_edit()
            self.widgets.append(self.hire_date_input)

            # Current Salary
            self.widgets.append(QLabel("Set Monthly Salary:"))
            self.salary_input = QLineEdit(placeholderText="5000.00")
            self.widgets.append(self.salary_input)

        else:
            self.widgets.append(QLabel("Select employee:"))

            # Create employee combo box and store reference
            self.employee_combo = QComboBox()
            self.update_employee_combo()  # Initial population
            self.widgets.append(self.employee_combo)  # Append the combo box widget


            if text == "termination":

                self.widgets.append(QLabel("Termination date:"))
            elif text == "salary change":
                self.widgets.append(QLabel("Salary change date:"))
            else:
                self.widgets.append(QLabel("Department change date:"))
            self.effective_date_input = self.create_date_edit()
            self.widgets.append(self.effective_date_input)
            if text == "salary change":
                self.widgets.append(QLabel("Enter new salary:"))
                self.new_salary_input = QLineEdit(placeholderText = "5000.00")
                self.widgets.append(self.new_salary_input)
            elif text == "department change":
                self.widgets.append(QLabel("Select new department:"))
                self.new_departments_combo = QComboBox()
                departments = []
                if self.config_manager:
                    departments = self.config_manager.get_departments()
                    # self.department_combo.addItems(departments)
                else:
                    # Fallback departments if config_manager is not available
                    print("Warning: config manager not available, using default departments")

                if not departments:
                    # If still no departments, add a default
                    departments = ["General"]
                    print("Warning: No departments found, using 'General'")

                self.new_departments_combo.addItems(departments)

                self.widgets.append(self.new_departments_combo)


        return self.widgets

    def on_department_changed(self):
        """Update employee combo when department changes"""
        if self.employee_combo is not None:
            self.update_employee_combo()

    def update_employee_combo(self):
        """Update the employee combo box with employees from current department"""
        if self.employee_combo is None:
            return

        department = self.department_combo.currentText()
        employees = self.employees_by_department(department)

        self.employee_combo.clear()

        if employees:
            for employee in employees:
                display_text = f"{employee['last_name']} {employee['first_name']} {employee.get('father_name', '')}"
                self.employee_combo.addItem(display_text.strip(),employee["id"])
        else:
            self.employee_combo.addItem("No employees in this department")

    def employees_by_department(self,department):
        self.department = department
        self.employees = self.database.get_all_employees()

        self.employees_list = []
        if self.employee:
            self.employees_list.append(self.employee)
        else:
            for employee in self.employees:

                if employee["department"] == self.department and employee["status"].lower() == 'active':
                    self.employees_list.append(employee)



        return self.employees_list

    def create_date_edit(self):
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(datetime.now().date())
        return date_edit

    def show_summary_dialog(self):
        """Show a summary of the entered order and ask for confirmation"""
        # First validate basic requirements
        if not hasattr(self, 'order_number_input') or not self.order_number_input.text().strip():
            QMessageBox.warning(self, "Missing Information", "Order number is required!")
            return

        order_type = self.order_type_combo.currentText()

        # Validate based on order type
        if order_type == "employment":
            if not hasattr(self,'employee_id_input') or not self.employee_id_input or not self.employee_id_input.text().strip():
                QMessageBox.warning(self, "Missing Information", "Employee ID is required for employment orders!")
                return
            elif not self.last_name_input or not self.last_name_input.text().strip():
                QMessageBox.warning(self, "Missing Information", "Employee Last Name is required for employment orders!")
                return
            elif not self.first_name_input or not self.first_name_input.text().strip():
                QMessageBox.warning(self, "Missing Information","Employee First Name is required for employment orders!")
                return
            elif not self.salary_input or not self.salary_input.text().strip():
                QMessageBox.warning(self, "Missing Information","Employee Salary is required for employment orders!")
                return

        # Generate summary
        summary_text = self.generate_summary_text()

        # Create custom message box
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Order Summary")
        msg_box.setText("Please review the order details:")
        msg_box.setInformativeText(summary_text)

        # Add custom buttons
        save_button = msg_box.addButton("Save Order", QMessageBox.ButtonRole.AcceptRole)
        edit_button = msg_box.addButton("Edit Order", QMessageBox.ButtonRole.RejectRole)
        msg_box.setDefaultButton(save_button)

        # Show the message box
        msg_box.exec()

        # Check which button was clicked
        if msg_box.clickedButton() == save_button:
            try:
                # Try to save the order
                self.save_order()
                QMessageBox.information(self, "Success", "Order saved successfully!")
                self.accept()  # Close the dialog only on success
            except ValueError as e:
                # This catches the "active employee exists" error
                QMessageBox.warning(self, "Error", str(e))
                # Don't close the dialog - stay in edit mode
                return
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save order: {str(e)}")
                # Don't close the dialog - stay in edit mode
                return
        # If Edit button is clicked, just close the message box and stay in the dialog

    def generate_summary_text(self):
        """Generate a summary text of the entered order"""
        order_type = self.order_type_combo.currentText()
        summary = []

        # Common fields
        if hasattr(self, 'order_date_input'):
            summary.append(f"Order Date: {self.order_date_input.date().toString('yyyy-MM-dd')}")
        else:
            summary.append("Order Date: Not set")

        summary.append(
            f"Order Number: {self.order_number_input.text() if hasattr(self, 'order_number_input') and self.order_number_input else 'Not set'}")
        summary.append(
            f"Department: {self.department_combo.currentText() if hasattr(self, 'department_combo') and self.department_combo else 'Not set'}")
        summary.append(f"Order Type: {order_type}")
        summary.append("")  # Empty line

        if order_type == "employment":
            # Employment specific fields
            summary.append("New Employee Details:")
            summary.append(
                f"  Employee ID: {self.employee_id_input.text() if hasattr(self, 'employee_id_input') and self.employee_id_input else 'Not set'}")
            summary.append(
                f"  Last Name: {self.last_name_input.text() if hasattr(self, 'last_name_input') and self.last_name_input else 'Not set'}")
            summary.append(
                f"  First Name: {self.first_name_input.text() if hasattr(self, 'first_name_input') and self.first_name_input else 'Not set'}")
            summary.append(
                f"  Father's Name: {self.father_name_input.text() if hasattr(self, 'father_name_input') and self.father_name_input else 'Not set'}")

            if hasattr(self, 'hire_date_input') and self.hire_date_input:
                summary.append(f"  Hire Date: {self.hire_date_input.date().toString('yyyy-MM-dd')}")
            else:
                summary.append("  Hire Date: Not set")

            summary.append(
                f"  Monthly Salary: {self.salary_input.text() if hasattr(self, 'salary_input') and self.salary_input else 'Not set'}")
        else:
            # Non-employment orders
            if hasattr(self, 'employee_combo') and self.employee_combo and self.employee_combo.currentText():
                summary.append(f"Employee: {self.employee_combo.currentText()}")
            else:
                summary.append("Employee: Not selected")

            if hasattr(self, 'effective_date_input') and self.effective_date_input:
                if order_type == "termination":
                    summary.append(f"Termination Date: {self.effective_date_input.date().toString('yyyy-MM-dd')}")
                elif order_type == "salary change":
                    summary.append(f"Salary Change Date: {self.effective_date_input.date().toString('yyyy-MM-dd')}")
                    if hasattr(self, 'new_salary_input') and self.new_salary_input:
                        summary.append(f"New Salary: {self.new_salary_input.text()}")
                elif order_type == "department change":
                    summary.append(f"Department Change Date: {self.effective_date_input.date().toString('yyyy-MM-dd')}")
                    if hasattr(self, 'new_departments_combo') and self.new_departments_combo:
                        summary.append(f"New Department: {self.new_departments_combo.currentText()}")

        return "\n".join(summary)

    def save_order(self):
        """Save the order to the database"""
        order_type = self.order_type_combo.currentText()

        if order_type == "employment":
            self.save_employment_order()
        else:
            self.save_non_employment_order(order_type)

    def save_employment_order(self):
        """Save employment order and create new employee"""
        employee_id = self.employee_id_input.text()

        # Check if employee with this ID already exists
        existing_employee = self.database.get_employee_by_id(employee_id)

        if existing_employee:
            if existing_employee["status"].lower() == "active":
                # Case 1: Active employee exists - raise an exception
                raise ValueError(
                    f"An active employee with ID '{employee_id}' already exists.\nPlease enter a different employee ID.")
            else:
                # Case 2: Terminated employee being re-employed
                # Ask for confirmation
                reply = QMessageBox.question(
                    self,
                    "Re-employ Terminated Employee",
                    f"Employee with ID '{employee_id}' was previously terminated.\n"
                    f"Do you want to re-employ this employee?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply != QMessageBox.StandardButton.Yes:
                    raise ValueError("Operation cancelled by user.")

                # Update the existing employee record
                employee_data = {
                    "id": employee_id,
                    "first_name": self.first_name_input.text(),
                    "last_name": self.last_name_input.text(),
                    "father_name": self.father_name_input.text(),
                    "hire_date": self.hire_date_input.date().toString("yyyy-MM-dd"),
                    "department": self.department_combo.currentText(),
                    "salary": float(self.salary_input.text()) if self.salary_input.text() else 0.0,
                    "status": "active"
                }

                # Get existing history to preserve it
                if "salary_history" in existing_employee:
                    employee_data["salary_history"] = existing_employee["salary_history"]
                if "department_history" in existing_employee:
                    employee_data["department_history"] = existing_employee["department_history"]

                # Add new salary history entry for re-employment
                new_salary_record = {
                    "salary": float(self.salary_input.text()) if self.salary_input.text() else 0.0,
                    "effective_date": self.hire_date_input.date().toString("yyyy-MM-dd"),
                    "end_date": None
                }

                if "salary_history" not in employee_data:
                    employee_data["salary_history"] = []
                employee_data["salary_history"].append(new_salary_record)

                # Add new department history entry for re-employment
                new_department_record = {
                    "department": self.department_combo.currentText(),
                    "effective_date": self.hire_date_input.date().toString("yyyy-MM-dd"),
                    "end_date": None
                }

                if "department_history" not in employee_data:
                    employee_data["department_history"] = []
                employee_data["department_history"].append(new_department_record)

                # Save updated employee
                self.database.save_employee(employee_data)
        else:
            # New employee - create fresh record
            employee_data = {
                "id": employee_id,
                "first_name": self.first_name_input.text(),
                "last_name": self.last_name_input.text(),
                "father_name": self.father_name_input.text(),
                "hire_date": self.hire_date_input.date().toString("yyyy-MM-dd"),
                "department": self.department_combo.currentText(),
                "salary": float(self.salary_input.text()) if self.salary_input.text() else 0.0,
                "status": "active"
            }

            # Save employee
            self.database.save_employee(employee_data)

        # Save order record
        self.save_order_record(
            order_number=self.order_number_input.text(),
            employee_id=employee_id,
            order_date=self.order_date_input.date().toString("yyyy-MM-dd"),
            effective_date=employee_data["hire_date"],
            order_action="employment",
            new_department = self.department_combo.currentText(),
            new_salary = self.salary_input.text().strip()
        )

    def save_non_employment_order(self, order_type):
        """Save non-employment order"""
        print(self.employee_combo.currentData())
        if not self.employee_combo or self.employee_combo.currentData() is None:
            QMessageBox.warning(self, "Error", "No employee selected!")
            return

        employee_id = self.employee_combo.currentData()

        # Get the employee
        employee = self.database.get_employee_by_id(employee_id)
        if not employee:
            QMessageBox.warning(self, "Error", "Employee not found!")
            return

        # Update employee based on order type
        if order_type == "termination":
            employee["status"] = "terminated"
        elif order_type == "salary change" and self.new_salary_input:
            employee["salary"] = float(self.new_salary_input.text()) if self.new_salary_input.text() else employee[
                "salary"]
        elif order_type == "department change" and self.new_departments_combo:
            employee["department"] = self.new_departments_combo.currentText()

        # Save updated employee
        self.database.save_employee(employee)

        # Save order record
        self.save_order_record(
            order_number=self.order_number_input.text(),
            employee_id=employee_id,
            order_date=self.order_date_input.date().toString("yyyy-MM-dd"),
            effective_date=self.effective_date_input.date().toString(
                "yyyy-MM-dd") if self.effective_date_input else self.order_date_input.date().toString("yyyy-MM-dd"),
            order_action=order_type,
            new_department = self.new_departments_combo.currentText() if order_type == "department change" else '',
            new_salary = self.new_salary_input.text().strip() if order_type == "salary change" else ''
        )

    def save_order_record(self, order_number, employee_id, order_date, effective_date, order_action,new_department,new_salary):
        """Save order to the orders table"""
        conn = None
        try:
            conn = sqlite3.connect(self.database.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                           INSERT INTO orders (order_number, employee_id, order_date, effective_date, order_action, new_department, new_salary)
                           VALUES (?, ?, ?, ?, ?,?,?)
                           """, (order_number, employee_id, order_date, effective_date, order_action, new_department, new_salary))

            conn.commit()
            print(f"DEBUG: Order saved - Number: {order_number}, Employee: {employee_id}, Action: {order_action}")
            return True
        except Exception as e:
            print(f"Error saving order: {e}")
            return False
        finally:
            if conn:
                conn.close()

if __name__ =="__main__":
    app = QApplication(sys.argv)
    dialog = OrderDialog()
    # Show the dialog
    dialog.show()  # Add this line to show the dialog

    # Start the application event loop
    sys.exit(app.exec())
