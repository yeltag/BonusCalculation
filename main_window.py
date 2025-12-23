import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStatusBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QLineEdit, QDialog, QComboBox, QSpinBox, QGroupBox,
    QMenu, QToolButton, QFormLayout, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from datetime import datetime, date
import calendar
from employee_dialog import EmployeeDialog
from config_manager import ConfigManager
from config_dialog import ConfigDialog
from employee_utils import create_employee_with_history, get_current_salary
from database import Database
from bonus_calculator import BonusCalculator
from variable_entry_dialog import VariableEntryDialog
from employee_status_dialog import EmployeeStatusDialog
from salary_adjustment_dialog import SalaryAdjustmentDialog
import sqlite3
from salary_adjustment_dialog_advanced import AdvancedSalaryAdjustmentDialog
from salary_adjustment_dialog_test import TestSalaryAdjustmentDialog
from variable_entry_widget import VariableEntryWidget
from order_dialog import OrderDialog


class EmployeeTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent


class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.database = Database()
        self.config_manager = ConfigManager(database=self.database)
        self.employees = []
        self.setup_ui()
        self.load_employees_from_db()

    def setup_ui(self):
        # Main window settings
        self.setWindowTitle(f"Employee Bonus System - Welcome {self.username}!")
        self.setGeometry(100, 100, 1200, 800)

        self.create_menu_bar()
        self.create_main_layout()
        self.create_status_bar()

        # Show dashboard by default
        self.show_dashboard()

    def create_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Employees menu
        employees_menu = menubar.addMenu("Employees")

        # Submenu items for Employees
        employees_action = QAction("Employees", self)
        employees_action.triggered.connect(self.show_employees)
        employees_menu.addAction(employees_action)

        orders_action = QAction("Orders", self)
        orders_action.triggered.connect(self.show_orders)
        employees_menu.addAction(orders_action)

        # Dashboard menu
        dashboard_menu = menubar.addMenu("Dashboard")
        dashboard_action = QAction("Dashboard", self)
        dashboard_action.triggered.connect(self.show_dashboard)
        dashboard_menu.addAction(dashboard_action)

        # Bonus Calculation menu - with submenu items
        bonus_menu = menubar.addMenu("Bonus Calculation")

        # Submenu items for Bonus Calculation
        enter_variables_action = QAction("Enter Variable Values", self)
        enter_variables_action.triggered.connect(self.show_variable_entry)
        bonus_menu.addAction(enter_variables_action)

        calculate_bonus_action = QAction("Calculate Bonuses", self)
        calculate_bonus_action.triggered.connect(self.open_bonus_calculation)
        bonus_menu.addAction(calculate_bonus_action)

        # Configuration menu
        config_menu = menubar.addMenu("Configuration")
        config_action = QAction("System Configuration", self)
        config_action.triggered.connect(self.open_configuration)
        config_menu.addAction(config_action)

        # Help menu
        help_menu = menubar.addMenu("Help")
        help_action = QAction("User Guide", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_main_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)

        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Create pages
        self.dashboard_page = self.create_dashboard_page()
        self.employees_page = self.create_employees_page()
        self.variable_entry_page = self.create_variable_entry_page()
        self.bonus_calculation_page = self.create_bonus_calculation_page()
        self.orders_page = self.create_orders_page()

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.employees_page)
        self.stacked_widget.addWidget(self.variable_entry_page)
        self.stacked_widget.addWidget(self.bonus_calculation_page)
        self.stacked_widget.addWidget(self.orders_page)


    def create_dashboard_page(self):
        """Create the dashboard page"""
        page = QWidget()
        layout = QVBoxLayout()

        # Welcome message
        welcome_label = QLabel(f"Welcome to Employee Bonus System, {self.username}!")
        welcome_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 15px; color: #2c3e50;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)

        # Quick stats section
        stats_layout = QHBoxLayout()

        total_employees = len(self.employees)
        active_employees = len([emp for emp in self.employees if emp["status"] == "Active"])

        stats_group = QGroupBox("Quick Statistics")
        stats_form = QFormLayout()

        stats_form.addRow("Total Employees:", QLabel(str(total_employees)))
        stats_form.addRow("Active Employees:", QLabel(str(active_employees)))
        stats_form.addRow("Terminated Employees:", QLabel(str(total_employees - active_employees)))
        stats_form.addRow("Departments:", QLabel(str(len(self.config_manager.get_departments()))))

        kpis = self.config_manager.get_kpis()
        stats_form.addRow("Active KPIs:", QLabel(str(len(kpis))))

        stats_group.setLayout(stats_form)
        stats_layout.addWidget(stats_group)

        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout()

        view_employees_btn = QPushButton("View Employees")
        view_employees_btn.clicked.connect(self.show_employees)
        actions_layout.addWidget(view_employees_btn)

        enter_vars_btn = QPushButton("Enter Variable Values")
        enter_vars_btn.clicked.connect(self.open_variable_entry)
        actions_layout.addWidget(enter_vars_btn)

        calc_bonus_btn = QPushButton("Calculate Bonuses")
        calc_bonus_btn.clicked.connect(self.open_bonus_calculation)
        actions_layout.addWidget(calc_bonus_btn)

        config_btn = QPushButton("System Configuration")
        config_btn.clicked.connect(self.open_configuration)
        actions_layout.addWidget(config_btn)

        actions_group.setLayout(actions_layout)
        stats_layout.addWidget(actions_group)

        layout.addLayout(stats_layout)

        # Recent activity placeholder
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout()
        activity_layout.addWidget(QLabel("Recent system activity and notifications will be shown here."))
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)

        layout.addStretch()
        page.setLayout(layout)
        return page

    def create_employees_page(self):
        """Create the employees page"""
        page = QWidget()
        layout = QVBoxLayout()

        # Header with Add Employee button and title
        header_layout = QHBoxLayout()

        title_label = QLabel("Employee Management")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        add_employee_btn = QPushButton("Add New Employee")
        add_employee_btn.setStyleSheet("QPushButton { padding: 8px 16px; font-weight: bold; }")
        add_employee_btn.clicked.connect(self.add_employee)
        header_layout.addWidget(add_employee_btn)

        layout.addLayout(header_layout)

        # Search and filters
        filter_group = QGroupBox("Search and Filters")
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, ID, or department...")
        self.search_input.textChanged.connect(self.filter_employees)
        self.search_input.setMinimumWidth(200)
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
        self.status_combo.addItems(["All", "Active", "Terminated"])
        self.status_combo.currentTextChanged.connect(self.filter_employees)
        filter_layout.addWidget(self.status_combo)

        filter_layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_employees_from_db)
        filter_layout.addWidget(refresh_btn)

        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Employee count
        self.employee_count_label = QLabel()
        layout.addWidget(self.employee_count_label)

        # Employee table
        self.employee_table = EmployeeTableWidget(self)
        self.employee_table.setColumnCount(8)  # Changed from 7 to 8
        self.employee_table.setHorizontalHeaderLabels([
            "ID", "First Name", "Last Name", "Father's Name", "Department", "Salary", "Status", "Actions"
            # Added Father's Name
        ])
        header = self.employee_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # First Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Last Name
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Father's Name - NEW
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Department
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Salary
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Actions

        self.employee_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.employee_table)

        page.setLayout(layout)
        return page

    def create_variable_entry_page(self):
        """Create the variable entry page"""
        widget = VariableEntryWidget(self,self.database,self.config_manager)
        return widget

    def create_bonus_calculation_page(self):
        """Create the bonus calculation page - Simplified version"""
        page = QWidget()
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Bonus Calculation")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Period selection
        period_group = QGroupBox("Calculation Period")
        period_layout = QVBoxLayout()

        # Month and Year
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Month:"))
        self.calc_month_combo = QComboBox()
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        self.calc_month_combo.addItems(months)
        self.calc_month_combo.setCurrentIndex(datetime.now().month - 1)
        self.calc_month_combo.currentIndexChanged.connect(self.update_working_days)
        date_layout.addWidget(self.calc_month_combo)

        date_layout.addWidget(QLabel("Year:"))
        self.calc_year_spin = QSpinBox()
        self.calc_year_spin.setRange(2000, 2050)
        self.calc_year_spin.setValue(datetime.now().year)
        self.calc_year_spin.valueChanged.connect(self.update_working_days)
        date_layout.addWidget(self.calc_year_spin)

        date_layout.addStretch()
        period_layout.addLayout(date_layout)

        # Working days and department
        working_days_layout = QHBoxLayout()
        working_days_layout.addWidget(QLabel("Total Working Days in Month:"))
        self.working_days_spin = QSpinBox()
        self.working_days_spin.setRange(1, 31)

        # Calculate actual working days for current month
        current_month = datetime.now().month
        current_year = datetime.now().year
        actual_working_days = self.calculate_actual_working_days(current_year, current_month)
        self.working_days_spin.setValue(actual_working_days)

        working_days_layout.addWidget(self.working_days_spin)

        working_days_layout.addWidget(QLabel("Department:"))
        self.calc_dept_combo = QComboBox()
        self.calc_dept_combo.addItem("All Departments")
        departments = self.config_manager.get_departments()
        self.calc_dept_combo.addItems(departments)
        working_days_layout.addWidget(self.calc_dept_combo)

        period_layout.addLayout(working_days_layout)
        period_group.setLayout(period_layout)
        layout.addWidget(period_group)

        # Information section - moved up
        info_group = QGroupBox("How Bonus Calculation Works")
        info_layout = QVBoxLayout()
        info_text = QLabel(
            "1. Make sure you have entered variable values for the selected period using 'Enter Variable Values' in the menu\n"
            "2. Select the period and department for which you want to calculate bonuses\n"
            "3. Enter the total number of working days in the month (for proportional salary calculation)\n"
            "4. Click 'Calculate Bonuses' to run the calculation\n"
            "5. The system will use the actual variable values you entered instead of defaults"
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Employee ID", "Name", "Department", "Base Salary", "Bonus Amount", "Total"
        ])
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.results_table)

        # Action buttons at the bottom
        buttons_layout = QHBoxLayout()

        # Edit Variables button - returns to variable entry
        edit_vars_btn = QPushButton("Edit Variables")
        edit_vars_btn.clicked.connect(self.open_variable_entry)
        buttons_layout.addWidget(edit_vars_btn)

        buttons_layout.addStretch()

        # Save Calculated Bonuses button (empty for now)
        save_bonuses_btn = QPushButton("Save Calculated Bonuses")
        save_bonuses_btn.clicked.connect(lambda: QMessageBox.information(
            self, "Not Implemented", "Save functionality will be implemented in a future update."))
        buttons_layout.addWidget(save_bonuses_btn)

        # Calculate Bonuses button - moved to bottom
        calculate_btn = QPushButton("Calculate Bonuses")
        calculate_btn.setStyleSheet("QPushButton { padding: 10px; font-size: 14px; font-weight: bold; }")
        calculate_btn.clicked.connect(lambda: self.calculate_bonuses())
        buttons_layout.addWidget(calculate_btn)

        layout.addLayout(buttons_layout)

        layout.addStretch()
        page.setLayout(layout)
        return page

    def create_orders_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("Orders")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        new_order_btn = QPushButton("Add New Order")
        new_order_btn.setStyleSheet("QPushButton {padding: 8px 16 px; font-weight: bold;}")
        new_order_btn.clicked.connect(self.add_order)
        header_layout.addWidget(new_order_btn)

        layout.addLayout(header_layout)

        # Search and filters
        filter_group = QGroupBox("Search and Filters")
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, ID, or order type...")
        self.search_input.textChanged.connect(self.filter_orders)
        self.search_input.setMinimumWidth(200)
        filter_layout.addWidget(self.search_input)

        period_group = QGroupBox("Calculation Period")
        period_layout = QHBoxLayout()

        period_layout.addWidget(QLabel("Month:"))
        self.calc_month_combo = QComboBox()
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        self.calc_month_combo.addItems(months)
        self.calc_month_combo.setCurrentIndex(datetime.now().month - 1)
        period_layout.addWidget(self.calc_month_combo)

        period_layout.addWidget(QLabel("Year:"))
        self.calc_year_spin = QSpinBox()
        self.calc_year_spin.setRange(2000, 2050)
        self.calc_year_spin.setValue(datetime.now().year)
        period_layout.addWidget(self.calc_year_spin)

        period_layout.addStretch()

        filter_group.setLayout(period_layout)

        layout.addWidget(filter_group)

        # Orders table
        self.orders_table = EmployeeTableWidget(self)
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels((["Number","Date","ID","Name","Order Type"]))

        header = self.orders_table.horizontalHeader()
        header.setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents) #Number
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  #Date
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  #ID
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  #Name
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  #Order Type

        self.orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.orders_table)

        page.setLayout(layout)
        return page


    def create_status_bar(self):
        status_bar = QStatusBar()
        status_bar.showMessage(f"Logged in as: {self.username} | Ready")
        self.setStatusBar(status_bar)

    # Navigation methods
    def show_dashboard(self):
        """Show the dashboard page"""
        self.stacked_widget.setCurrentIndex(0)
        self.statusBar().showMessage("Dashboard - System Overview")

    def show_employees(self):
        """Show the employees page"""
        self.stacked_widget.setCurrentIndex(1)
        self.load_employees_from_db()  # Refresh data when showing employees
        self.statusBar().showMessage("Employee Management")

    def show_variable_entry(self):
        """Show the variable entry page"""
        self.stacked_widget.setCurrentIndex(2)  # Adjust index based on your stack order
        self.statusBar().showMessage("Variable Entry - Enter monthly variable values")

    def show_bonus_calculation(self):
        """Show the bonus calculation page"""
        self.stacked_widget.setCurrentIndex(3)
        self.statusBar().showMessage("Bonus Calculation")

    def load_employees_from_db(self):
        """Load employees from database"""
        self.employees = self.database.get_all_employees()
        self.display_employees(self.employees)
        self.update_employee_count()

    def update_employee_count(self):
        """Update the employee count label"""
        total = len(self.employees)
        active = len([emp for emp in self.employees if emp["status"] == "Active"])
        terminated = total - active

        self.employee_count_label.setText(
            f"Showing {total} employees ({active} active, {terminated} terminated)"
        )

    def display_employees(self, employees):
        """Display employees in table with action menus"""
        self.employee_table.setRowCount(len(employees))

        for row, employee in enumerate(employees):
            # Employee data
            self.employee_table.setItem(row, 0, QTableWidgetItem(employee["id"]))
            self.employee_table.setItem(row, 1, QTableWidgetItem(employee["first_name"]))
            self.employee_table.setItem(row, 2, QTableWidgetItem(employee["last_name"]))
            self.employee_table.setItem(row, 3, QTableWidgetItem(employee.get("father_name", "")))  # NEW FIELD
            self.employee_table.setItem(row, 4, QTableWidgetItem(str(employee["department"])))

            # In display_employees method, around line 447:
            try:
                # Get salary value and ensure it's a float
                salary_value = employee['salary']
                if not isinstance(salary_value, (int, float)):
                    # Try to convert if it's a string
                    try:
                        salary_value = float(str(salary_value).replace('$', '').replace(',', '').strip())
                    except:
                        salary_value = 0.0

                salary_item = QTableWidgetItem(f"${salary_value:,.2f}")
            except Exception as e:
                print(f"ERROR formatting salary for employee {employee.get('id', 'unknown')}: {e}")

            salary_item = QTableWidgetItem(f"${employee['salary']:,.2f}")
            salary_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.employee_table.setItem(row, 5, salary_item)

            # Status with color coding
            status_item = QTableWidgetItem(employee["status"])
            if employee["status"] == "Terminated":
                status_item.setForeground(Qt.GlobalColor.red)
                status_item.setBackground(Qt.GlobalColor.lightGray)
            else:
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.employee_table.setItem(row, 6, status_item)

            # Action menu button
            action_btn = QToolButton()
            action_btn.setText("⋮")  # Three dots menu
            action_btn.setStyleSheet("QToolButton { padding: 5px; border: 1px solid #ccc; border-radius: 3px; }")
            action_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

            # Create menu
            menu = QMenu(self)

            change_details_action = QAction("📝 Change Status/Details", self)
            change_details_action.triggered.connect(lambda checked, emp=employee: self.change_employee_details(emp))
            menu.addAction(change_details_action)

            terminate_action = QAction("🔴 Terminate Employee", self)
            terminate_action.triggered.connect(lambda checked, emp=employee: self.terminate_employee(emp))
            menu.addAction(terminate_action)

            action_btn.setMenu(menu)

            # Add button to table - column index changed from 6 to 7
            self.employee_table.setCellWidget(row, 7, action_btn)
    def filter_employees(self):
        """Filter employees based on search criteria"""
        search_text = self.search_input.text().lower()
        dept_filter = self.dept_combo.currentText()
        status_filter = self.status_combo.currentText()

        filtered_employees = []
        for emp in self.employees:
            # Search text filter
            matches_search = (not search_text or
                              search_text in emp["id"].lower() or
                              search_text in emp["first_name"].lower() or
                              search_text in emp["last_name"].lower() or
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

        # Update count for filtered results
        total = len(filtered_employees)
        active = len([emp for emp in filtered_employees if emp["status"] == "Active"])
        terminated = total - active

        if total == len(self.employees):
            self.update_employee_count()
        else:
            self.employee_count_label.setText(
                f"Showing {total} of {len(self.employees)} employees ({active} active, {terminated} terminated)"
            )

    def change_employee_details(self, employee):
        """Open dialog to change employee details"""
        dialog = EmployeeStatusDialog(self, self.database, self.config_manager, employee)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_employees_from_db()
            QMessageBox.information(self, "Success", "Employee details updated successfully!")

    def terminate_employee(self, employee):
        """Terminate an employee"""
        if employee["status"] == "Terminated":
            QMessageBox.information(self, "Already Terminated",
                                    f"Employee {employee['first_name']} {employee['last_name']} is already terminated.")
            return

        reply = QMessageBox.question(self, "Confirm Termination",
                                     f"Are you sure you want to terminate {employee['first_name']} {employee['last_name']}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Update employee status to Terminated
            updated_employee = employee.copy()
            updated_employee["status"] = "Terminated"

            # Save to database
            self.database.save_employee(updated_employee)
            self.load_employees_from_db()

            QMessageBox.information(self, "Employee Terminated",
                                    f"{employee['first_name']} {employee['last_name']} has been terminated.")

    # Employee Management Methods
    def add_employee(self):
        """Open dialog to add new employee"""
        dialog = EmployeeDialog(self, None, self.config_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_employee = dialog.get_employee_data()
            existing_ids = [emp["id"] for emp in self.employees]
            if new_employee["id"] in existing_ids:
                QMessageBox.warning(self, "Error", f"Employee ID {new_employee['id']} already exists!")
                return
            self.database.save_employee(new_employee)
            self.load_employees_from_db()
            QMessageBox.information(self, "Success",
                                    f"Employee {new_employee['first_name']} {new_employee['last_name']} added successfully!")

    # Bonus Calculation Methods
    def open_variable_entry(self):
        """Open variable entry page (now deprecated - use show_variable_entry instead)"""
        self.show_variable_entry()

    def open_bonus_calculation(self):
        """Open bonus calculation dialog - now just navigates to the page"""
        self.show_bonus_calculation()

    def calculate_bonuses(self, pre_calculated_results=None):
        """Calculate bonuses or display pre-calculated results"""
        import traceback
        print("DEBUG: calculate_bonuses called with:", pre_calculated_results)

        if pre_calculated_results is False:
            print("DEBUG: pre_calculated_results is False, treating as validation failure")
            pre_calculated_results = None

        if pre_calculated_results is not None:
            # Display pre-calculated results
            print("DEBUG: Displaying pre-calculated results")
            results = pre_calculated_results
        else:
            # Calculate bonuses normally
            print("DEBUG: Calculating bonuses from scratch")
            month = self.calc_month_combo.currentIndex() + 1
            year = self.calc_year_spin.value()
            department_filter = self.calc_dept_combo.currentText()
            working_days = self.working_days_spin.value()

            calculator = BonusCalculator(self.database, self.config_manager)

            # Check for salary changes in the selected month
            employees_with_changes = calculator.get_employees_with_salary_changes(year, month)

            # DEBUG: Check what's returned
            print(f"DEBUG: Found {len(employees_with_changes)} employees with salary changes")
            for i, emp_data in enumerate(employees_with_changes):
                employee = emp_data['employee']
                changes = emp_data['changes']
                print(
                    f"  Employee {i + 1}: {employee['first_name']} {employee['last_name']} has {len(changes)} changes")
                for j, change in enumerate(changes):
                    print(f"    Change {j + 1}: {change['change_date'].strftime('%Y-%m-%d')}, "
                          f"{change['old_salary']} -> {change['new_salary']}")

            salary_adjustments = None
            if employees_with_changes:
                print(f"\nDEBUG main_window: Found {len(employees_with_changes)} employees with changes")
                for i, emp_data in enumerate(employees_with_changes):
                    employee = emp_data['employee']
                    changes = emp_data['changes']
                    print(f"  Employee {i + 1}: {employee['first_name']} {employee['last_name']} ({employee['id']})")
                    for j, change in enumerate(changes):
                        print(
                            f"    Change {j + 1}: {change['change_date'].strftime('%Y-%m-%d')}, {change['old_salary']} -> {change['new_salary']}")

                # Show advanced salary adjustment dialog
                dialog = AdvancedSalaryAdjustmentDialog(self, employees_with_changes, working_days)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    salary_adjustments = dialog.get_adjustments()
                    print(f"DEBUG: Got salary adjustments for {len(salary_adjustments)} employees")
                else:
                    print("DEBUG: Salary adjustment dialog cancelled")
                    return

            results = calculator.calculate_bonuses_with_validation(
                year, month, department_filter, self, working_days, salary_adjustments
            )

            # Check for both None and False
            if results is None or results is False:
                print("DEBUG: Validation failed, returning early")
                return

        print("main_window calculate_bonuses results: ", results)

        # Safety check - ensure results is a list
        if not isinstance(results, list):
            print(f"ERROR main_window calculate_bonuses line 554: Expected list but got {type(results)}: {results}")
            QMessageBox.critical(self, "Error", f"Unexpected result type: {type(results)}")
            return

        # Display results
        self.results_table.setRowCount(len(results))
        for row, result in enumerate(results):
            self.results_table.setItem(row, 0, QTableWidgetItem(result["employee_id"]))
            self.results_table.setItem(row, 1, QTableWidgetItem(result["employee_name"]))
            self.results_table.setItem(row, 2, QTableWidgetItem(result.get("department", "")))
            self.results_table.setItem(row, 3, QTableWidgetItem(f"{result['base_salary']:,.2f}"))
            self.results_table.setItem(row, 4, QTableWidgetItem(f"{result['calculated_bonus']:,.2f}"))
            total = result["base_salary"] + result["calculated_bonus"]
            self.results_table.setItem(row, 5, QTableWidgetItem(f"{total:,.2f}"))

        if pre_calculated_results is None:
            QMessageBox.information(self, "Calculation Complete",
                                    f"Calculated bonuses for {len(results)} employees")

    # Other Menu Actions
    def open_configuration(self):
        """Open configuration management dialog"""
        dialog = ConfigDialog(self, self.config_manager, self.database)
        dialog.exec()

    def show_help(self):
        """Show help dialog"""
        QMessageBox.information(self, "Help",
                                "Employee Bonus System User Guide\n\n"
                                "1. Dashboard: Overview and quick access to common tasks\n"
                                "2. Employees: Manage employee information and status\n"
                                "3. Bonus Calculation: Enter variable values and calculate bonuses\n"
                                "4. Configuration: Set up departments, KPIs, and custom variables\n\n"
                                "Use the menu bar to navigate between different sections.")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Employee Bonus System",
                          "Employee Bonus System\n\n"
                          "A comprehensive system for managing employee bonuses "
                          "based on performance metrics and custom KPIs.\n\n"
                          "Version 1.0")

    def logout(self):
        """Logout and close application"""
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to logout?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.close()

    def calculate_actual_working_days(self, year, month):
        """Calculate actual working days (Mon-Fri) for a given month/year"""

        # Get the month's calendar
        cal = calendar.monthcalendar(year, month)

        # Count working days (Monday=0, Friday=4)
        working_days = 0
        for week in cal:
            for day in week[:5]:  # Monday to Friday (0-4)
                if day != 0:  # 0 means day is not in this month
                    working_days += 1

        return working_days

    def update_working_days(self):
        """Update working days based on selected month/year"""
        month = self.calc_month_combo.currentIndex() + 1
        year = self.calc_year_spin.value()
        actual_working_days = self.calculate_actual_working_days(year, month)
        self.working_days_spin.setValue(actual_working_days)

    def show_orders(self):
        self.stacked_widget.setCurrentIndex(4)
        self.load_orders_from_db()

    def add_order(self):
        dialog = OrderDialog(self, None, self.config_manager)

    def filter_orders(self):
        pass

    def load_orders_from_db(self):
        """Load orders from database"""
        self.orders = self.database.get_all_orders()
        self.display_orders(self.orders)

    def display_orders(self,orders):
        """Display orders in table"""
        if orders:
            self.orders_table.setRowCount(len(orders))

            for row, order in enumerate(orders):
                # Order data
                self.orders_table.setItem(row, 0,QTableWidgetItem(orders["order_number"]))
                self.orders_table.setItem(row, 1, QTableWidgetItem(orders["order_date"]))
                self.orders_table.setItem(row, 2, QTableWidgetItem(orders["employee_id"]))
                self.orders_table.setItem(row, 4, QTableWidgetItem(orders["order_action"]))
                employee_name = self.database.get_all_employees()[orders["employee_id"]]["first_name"]
                self.orders_table.setItem(row, 3, QTableWidgetItem(employee_name))

        else:
            return

