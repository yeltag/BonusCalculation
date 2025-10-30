import sys


from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget,QStatusBar, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QLineEdit, QDialog, QComboBox, QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from pandas.io.formats.format import return_docstring
from employee_dialog import EmployeeDialog
from datetime import datetime, timedelta
import json
from config_manager import ConfigManager
from config_dialog import ConfigDialog

from employee_utils import create_employee_with_history, get_current_salary
from database import Database

from bonus_calculator import BonusCalculator




class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.config_manager = ConfigManager()
        self.database = Database()
        self.employees = []
        self.setup_ui()
        self.load_employees_from_db()  # Load from database
        self.test_kpi_system()

    def load_employees_from_db(self):
        """Load employees from database"""
        self.employees = self.database.get_all_employees()
        self.refresh_employee_table()

        # Update status bar
        self.statusBar().showMessage(f"Loaded {len(self.employees)} employees from database")

    def setup_ui(self):
        # Main window settings
        self.setWindowTitle(f"Employee Bonus System - Welcome {self.username}!")
        self.setGeometry(100,100,1000,700)  # z, y, width, height

        self.create_menu_bar()
        self.create_main_layout()
        self.create_status_bar()

    def create_menu_bar(self):
        menubar = self.menuBar()

        # file menu
        file_menu = menubar.addMenu("File")

        # Add Configuration menu

        config_menu = menubar.addMenu("Configuration")

        config_action = QAction("System Configuration", self)

        config_action = QAction("System Configurattion", self)
        config_action.triggered.connect(self.open_configuration)
        config_menu.addAction(config_action)

        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Employees menu
        employees_menu = menubar.addMenu("Employees")

        add_employee_action = QAction("Add Employee", self)
        add_employee_action.triggered.connect(self.add_employee)
        employees_menu.addAction(add_employee_action)

    def create_main_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Welcome message
        welcome_label = QLabel(f"Welcome to Employee Bonus System, {self.username}!")
        welcome_label.setStyleSheet("font-size:16px; font-weight: bold; margin:10px;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)

        # Create tabs for different sections

        self.tabs = QTabWidget()

        # Tab 1: Employee Management
        self.setup_employee_tab()

        # Tab 2: Bonus Calculation
        self.setup_bonus_calculation_tab()

        # Tab 3: Dashboard (placeholder for now)
        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout()
        dashboard_layout.addWidget(QLabel("Dashboard - Reports and analyitcs coming soon"))
        dashboard_tab.setLayout(dashboard_layout)
        self.tabs.addTab(dashboard_tab, "Dashboard")

        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)

    def setup_employee_tab(self):
        """Setup the employee management tab with table and controls"""


        employee_tab = QWidget()
        layout = QVBoxLayout()

        # Search and Add section
        controls_layout = QHBoxLayout()

        # Search box
        controls_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search employees...")
        self.search_input.textChanged.connect(self.filter_employees)
        controls_layout.addWidget(self.search_input)

        controls_layout.addStretch()  # Push buttons to the right

        # Delete Employee button
        delete_btn = QPushButton("Delete Employee")
        delete_btn.clicked.connect(self.delete_employee)
        controls_layout.addWidget(delete_btn)

        layout.addLayout(controls_layout)

        # Add Employee button
        add_btn = QPushButton ("Add New Employee")
        add_btn.clicked.connect(self.add_employee)
        controls_layout.addWidget(add_btn)

        layout.addLayout(controls_layout)

        # Test button

        test_kpi_btn = QPushButton("Test KPI System")
        test_kpi_btn.clicked.connect(self.test_kpi_system)
        controls_layout.addWidget(test_kpi_btn)

        layout.addLayout(controls_layout)

        # Employee table
        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(6)
        self.employee_table.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Department", "Salary", "Status"])

        # Make table headers stretch to fill available space
        header = self.employee_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Enable sorting
        self.employee_table.setSortingEnabled(True)

        # Double-click to edit
        self.employee_table.doubleClicked.connect(self.edit_employee)

        layout.addWidget(self.employee_table)

        employee_tab.setLayout(layout)
        self.tabs.addTab(employee_tab, "Employee Management")

    def setup_bonus_calculation_tab(self):
        """Setup the bonus calculation tab"""
        bonus_tab = QWidget()
        layout = QVBoxLayout()

        # Period selection
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Calculation Period:"))

        self.month_combo = QComboBox()
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October","November","December"]
        self.month_combo.addItems(months)
        self.month_combo.setCurrentIndex(datetime.now().month - 1)
        period_layout.addWidget(self.month_combo)

        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2030)
        self.year_spin.setValue(datetime.now().year)
        period_layout.addWidget(self.year_spin)

        period_layout.addStretch()

        # Calculate button
        calculate_btn = QPushButton("Calculate Bonuses")
        calculate_btn.clicked.connect(self.calculate_all_bonuses)
        period_layout.addWidget(calculate_btn)

        layout.addLayout(period_layout)

        #Result table
        self.bonus_table = QTableWidget()
        self.bonus_table.setColumnCount(5)
        self.bonus_table.setHorizontalHeaderLabels([
            "Employee ID", "Name", "base Salary", "Bonus Amount", "Total"
        ])

        header = self.bonus_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.bonus_table)

        bonus_tab.setLayout(layout)
        self.tabs.addTab(bonus_tab,"Bonus Calculation")

    def calculate_all_bonuses(self):
        """Calculate bonuses for all active employees"""
        month = self.month_combo.currentIndex() + 1
        year = self.year_spin.value()

        calculator = BonusCalculator(self.database, self.config_manager)

        results = []
        for employee in self.employees:
            if employee["status"] == "Active":
                result = calculator.calculate_monthly_bonus(employee["id"],year, month)
                if result:
                    results.append(result)

        # Display results
        self.bonus_table.setRowCount(len(results))
        for row, result in enumerate(results):
            self.bonus_table.setItem(row, 0, QTableWidgetItem(result["employee_id"]))
            self.bonus_table.setItem(row, 1, QTableWidgetItem(result["employee_name"]))
            self.bonus_table.setItem(row, 2, QTableWidgetItem(f"{result["base_salary"]:,.2f}"))
            self.bonus_table.setItem(row, 3, QTableWidgetItem(f"{result["calculated_bonus"]:,.2f}"))
            total = result["base_salary"] +result["calculated_bonus"]
            self.bonus_table.setItem(row, 4, QTableWidgetItem(f"{total:,.2f}"))
        self.statusBar().showMessage(f"Calculated bonuses for {len(results)} employees")

    def create_status_bar(self):
        status_bar = QStatusBar()
        status_bar.showMessage(f"Logged in as: {self.username} | Ready")
        self.setStatusBar(status_bar)

    def load_sample_data(self):
            """Load some sample employee data for testing"""
            sample_employees_data = [{"id": "EMP001", "first_name":"John", "last_name": "Smith","department":"Sales","salary":5000,"status": "Active"},
                              {"id": "EMP002", "first_name": "Sarah", "last_name": "Johnson", "department": "Marketing", "salary": 4500, "status": "Active"},
                              {"id": "EMP003", "first_name": "Mike", "last_name": "Brown", "department": "IT", "salary": 6000, "status": "Active"},
                              {"id": "EMP004", "first_name": "Emily", "last_name": "Davis", "department": "HR", "salary": 4800, "status": "Inactive"},
                              {"id": "EMP005", "first_name": "David", "last_name": "Wilson", "department": "Sales", "salary": 5200, "status": "Active"}
                              ]
            # Use create_employee_with_history for each sample employee
            self.employees = [create_employee_with_history(emp) for emp in sample_employees_data]

            self.refresh_employee_table()

    def refresh_employee_table(self):

        """Refresh the employee table with current data"""
        self.employee_table.setRowCount(len(self.employees))

        for row, employee in enumerate(self.employees):
            self.employee_table.setItem(row, 0, QTableWidgetItem(employee["id"]))
            self.employee_table.setItem(row, 1, QTableWidgetItem(employee["first_name"]))
            self.employee_table.setItem(row,2, QTableWidgetItem(employee["last_name"]))
            self.employee_table.setItem(row, 3, QTableWidgetItem(employee["department"]))


            # Use get_current_salary to display the correct salary
            current_salary = get_current_salary(employee)
            self.employee_table.setItem(row,4,QTableWidgetItem(f"{current_salary:,.2f}"))

            self.employee_table.setItem(row,5,QTableWidgetItem(employee["status"]))


    def filter_employees(self):
        """Filter employees based on search text"""
        search_text = self.search_input.text().lower()

        if not search_text:
            self.refresh_employee_table()
            return

        filtered_employees = [
            emp for emp in self.employees
            if (search_text in emp["id"].lower() or
                search_text in emp["first_name"].lower() or
                search_text in emp["last_name"].lower() or
                search_text in emp["department"].lower())
            ]

        self.employee_table.setRowCount(len(filtered_employees))
        for row, employee in enumerate(filtered_employees):
            self.employee_table.setItem(row, 0, QTableWidgetItem(employee["id"]))
            self.employee_table.setItem(row, 1, QTableWidgetItem(employee["first_name"]))
            self.employee_table.setItem(row, 2, QTableWidgetItem(employee["last_name"]))
            self.employee_table.setItem(row, 3, QTableWidgetItem(employee["department"]))
            self.employee_table.setItem(row, 4, QTableWidgetItem(f"${employee['salary']:,.2f}"))
            self.employee_table.setItem(row, 5, QTableWidgetItem(employee["status"]))

    def add_employee(self):
        """Open dialog to add new employee"""
        dialog = EmployeeDialog(self, None, self.config_manager)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_employee = dialog.get_employee_data()

            # Check if employee ID already exists
            existing_ids = [emp["id"] for emp in self.employees]
            if new_employee["id"] in existing_ids:
                QMessageBox.warning(self,"Error", f"Employee ID{new_employee["id"]} already exists!")
                return

            # Save to database

            self.database.save_employee(new_employee)

            # Reload from database
            self.load_employees_from_db()

            # Show success message
            QMessageBox.information(self,"Success",
                               f"Employee {new_employee['first_name']} {new_employee['last_name']} added successfully!")

            # Update status bar
            self.statusBar().showMessage(f"Added new employee:{new_employee["id"]}")

    def edit_employee(self, index):
        """Edit employee when double-clicked"""
        row = index.row()
        employee_id = self.employee_table.item(row, 0).text()

        #Find the employee in our list
        employee_to_edit = None
        for emp in self.employees:
            if emp["id"] == employee_id:
                employee_to_edit = emp
                break

        if employee_to_edit:
            # Load salary history for editing
            salary_history = self.database.get_employee_salary_history(employee_id)
            employee_to_edit['salary_history'] = salary_history

            dialog = EmployeeDialog(self, employee_to_edit, self.config_manager)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_data = dialog.get_employee_data()

               # Save to database
                self.database.save_employee(updated_data)

                # Reload from database

                self.load_employees_from_db()

                QMessageBox.information(self, "Success",
                                        f'Employee {updated_data["first_name"]}{updated_data['last_name']} updated successfully!')


        else:
            QMessageBox.warning(self,"Error","Employee not found!")

    def delete_employee(self):
        """Delete selected employee"""
        current_row = self.employee_table.currentRow()

        if current_row == -1:
            QMessageBox.warning(self,"Error", "Please select an employee to delete!")
            return

        employee_id = self.employee_table.item(current_row, 0).text()
        employee_name = f"{self.employee_table.item(current_row, 1).text()} {self.employee_table.item(current_row, 2).text()}"

        reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete employee:\n{employee_name}({employee_id})?",QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Delete from database

            self.database.delete_employee(employee_id)

            # Reload from database
            self.load_employees_from_db()

            QMessageBox.information(self,"Success",f"Employee {employee_name} deleted successfully!")
            self.statusBar().showMessage(f"Deleted employee: {employee_id}")

    def test_kpi_system(self):
        """Test the KPI system directly"""
        print("=== DIRECT KPI SYSTEM TEST ===")

        # Test 1: Check config manager directly
        print("1. Checking ConfigManager...")
        kpis = self.config_manager.get_kpis()
        print(f"   KPIs from config_manager: {len(kpis)}")
        for kpi in kpis:
            print(f"   - {kpi['name']} (Method: {kpi['calculation_method']})")

        # Test 2: Test bonus calculator directly
        print("2. Testing BonusCalculator directly...")
        calculator = BonusCalculator(self.database, self.config_manager)

        # Test on first employee
        if self.employees:
            employee = self.employees[0]
            print(f"   Testing on employee: {employee['first_name']} {employee['last_name']}")
            print(f"   Department: {employee['department']}")
            print(f"   Salary: ${employee['salary']:,.2f}")

            result = calculator.calculate_monthly_bonus(employee['id'], 2024, 10)
            if result:
                print(f"   Base Salary: ${result['base_salary']:,.2f}")
                print(f"   Bonus Amount: ${result['calculated_bonus']:,.2f}")
                print(f"   KPI Details: {result['kpi_details']}")
            else:
                print("   No result from bonus calculator!")
        else:
            print("   No employees to test!")

        print("=== END KPI TEST ===")

                

    def logout(self):
        """Logout and close application"""
        reply = QMessageBox.question(self, "Logout","Are you sure you want to logout?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.close()

    def open_configuration(self):
        """Open configuration management dialog"""
        dialog = ConfigDialog(self, self.config_manager)
        dialog.exec()


