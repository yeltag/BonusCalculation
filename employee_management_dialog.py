import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QComboBox,
    QGroupBox
)
from PyQt6.QtCore import Qt


class EmployeeManagementDialog(QDialog):
    def __init__(self, parent=None, database=None, config_manager=None):
        super().__init__(parent)
        self.database = database
        self.config_manager = config_manager
        self.setWindowTitle("Employee Management")
        self.setFixedSize(1100, 600)
        self.setup_ui()
        self.load_employees()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Search and filters
        filter_group = QGroupBox("Search and Filters")
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, ID, or department...")
        self.search_input.textChanged.connect(self.filter_employees)
        filter_layout.addWidget(self.search_input)

        filter_layout.addWidget(QLabel("Department:"))
        self.dept_combo = QComboBox()
        self.dept_combo.addItem("All Departments")
        departments = self.config_manager.get_departments()
        self.dept_combo.addItems(departments)
        self.dept_combo.currentTextChanged.connect(self.filter_employees)
        filter_layout.addWidget(self.dept_combo)

        filter_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Active", "Inactive"])
        self.status_combo.currentTextChanged.connect(self.filter_employees)
        filter_layout.addWidget(self.status_combo)

        filter_layout.addStretch()
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Employee table
        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(8)
        self.employee_table.setHorizontalHeaderLabels([
            "ID", "First Name", "Last Name", "Department", "Salary", "Status", "Hire Date"
        ])
        header = self.employee_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.employee_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.employee_table)

        # Buttons
        button_layout = QHBoxLayout()

        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_selected_employee)
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_employees)
        button_layout.addWidget(refresh_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_employees(self):
        """Load employees into table"""
        self.all_employees = self.database.get_all_employees()
        self.display_employees(self.all_employees)

    def display_employees(self, employees):
        """Display employees in table"""
        self.employee_table.setRowCount(len(employees))
        for row, employee in enumerate(employees):
            self.employee_table.setItem(row, 0, QTableWidgetItem(employee["id"]))
            self.employee_table.setItem(row, 1, QTableWidgetItem(employee["first_name"]))
            self.employee_table.setItem(row, 2, QTableWidgetItem(employee["last_name"]))
            self.employee_table.setItem(row, 3, QTableWidgetItem(employee.get("father_name", "")))  # NEW FIELD
            self.employee_table.setItem(row, 4, QTableWidgetItem(employee["department"]))
            self.employee_table.setItem(row, 5, QTableWidgetItem(f"{employee['salary']:,.2f}"))
            self.employee_table.setItem(row, 6, QTableWidgetItem(employee["status"]))
            self.employee_table.setItem(row, 7, QTableWidgetItem(employee["hire_date"]))

    def filter_employees(self):
        """Filter employees based on search criteria"""
        search_text = self.search_input.text().lower()
        dept_filter = self.dept_combo.currentText()
        status_filter = self.status_combo.currentText()

        filtered_employees = []
        for emp in self.all_employees:
            # Search text filter
            matches_search = (not search_text or
                              search_text in emp["id"].lower() or
                              search_text in emp["first_name"].lower() or
                              search_text in emp["last_name"].lower() or
                              search_text in emp.get("father_name", "").lower() or
                              search_text in emp["department"].lower())

            # Department filter
            matches_dept = (dept_filter == "All Departments" or
                            emp["department"] == dept_filter)

            # Status filter
            matches_status = (status_filter == "All" or
                              emp["status"] == status_filter)

            if matches_search and matches_dept and matches_status:
                filtered_employees.append(emp)

        self.display_employees(filtered_employees)

    def delete_selected_employee(self):
        """Delete selected employee"""
        current_row = self.employee_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Error", "Please select an employee to delete!")
            return

        employee_id = self.employee_table.item(current_row, 0).text()
        employee_name = f"{self.employee_table.item(current_row, 1).text()} {self.employee_table.item(current_row, 2).text()}"

        reply = QMessageBox.question(self, "Confirm Delete",
                                     f"Are you sure you want to delete employee:\n{employee_name} ({employee_id})?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.database.delete_employee(employee_id)
            self.load_employees()
            QMessageBox.information(self, "Success", f"Employee {employee_name} deleted successfully!")