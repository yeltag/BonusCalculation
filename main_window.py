import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStatusBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QLineEdit, QDialog, QComboBox, QSpinBox, QGroupBox,
    QMenu, QToolButton, QFormLayout, QStackedWidget, QDateEdit, QAbstractScrollArea, QListWidget, QInputDialog
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
from new_page_template import NewPageTemplate


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
        self.all_orders = []
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
        # config_menu = menubar.addMenu("Configuration")
        # config_action = QAction("System Configuration", self)
        # config_action.triggered.connect(self.open_configuration)
        # config_menu.addAction(config_action)

        config_menu = menubar.addMenu("Configuration")
        department_action = QAction("Departments",self)
        department_action.triggered.connect(self.open_departments)
        config_menu.addAction(department_action)

        kpi_action = QAction("KPIs", self)
        kpi_action.triggered.connect(self.open_kpis)
        config_menu.addAction(kpi_action)

        variable_action = QAction("Variables", self)
        variable_action.triggered.connect(self.open_variables)
        config_menu.addAction(variable_action)



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
        self.department_page=self.create_department_page()
        #self.kpi_page = self.create_kpi_page()
        #self.manage_variable_page=self.create_variable_page()


        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.employees_page)
        self.stacked_widget.addWidget(self.variable_entry_page)
        self.stacked_widget.addWidget(self.bonus_calculation_page)
        self.stacked_widget.addWidget(self.orders_page)
        self.stacked_widget.addWidget(self.department_page)
        #self.stacked_widget.addWidget(self.kpi_page)
        #self.stacked_widget.addWidget(self.manage_variable_page)


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
        add_employee_btn.clicked.connect(self.add_order)
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
        self.employee_table.setColumnCount(6)  # Changed from 7 to 8
        self.employee_table.setHorizontalHeaderLabels([
            "ID", "Name", "Department", "Salary", "Status", "Actions"
            # Added Father's Name
        ])
        header = self.employee_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # First Name

        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Department
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Salary
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Actions

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
        self.results_table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
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
        order_filter_layout = QHBoxLayout()

        order_filter_layout.addWidget(QLabel("Search:"))
        self.orders_search_input = QLineEdit()
        self.orders_search_input.setPlaceholderText("Search by name, ID, or order type...")
        self.orders_search_input.textChanged.connect(self.filter_orders)
        self.orders_search_input.setMinimumWidth(200)
        order_filter_layout.addWidget(self.orders_search_input)
        layout.addLayout(order_filter_layout)

        # Date range filter - REPLACED the month/year combo boxes
        date_range_group = QGroupBox("Date Range Filter")
        date_range_layout = QHBoxLayout()

        # From date
        date_range_layout.addWidget(QLabel("From:"))
        self.from_date_edit = QDateEdit()
        self.from_date_edit.setCalendarPopup(True)
        self.from_date_edit.setDate(datetime.now().date().replace(day=1))  # First day of current month
        self.from_date_edit.dateChanged.connect(self.filter_orders)
        date_range_layout.addWidget(self.from_date_edit)

        # To date
        date_range_layout.addWidget(QLabel("To:"))
        self.to_date_edit = QDateEdit()
        self.to_date_edit.setCalendarPopup(True)
        # Set to last day of current month
        today = datetime.now().date()
        import calendar
        last_day = calendar.monthrange(today.year, today.month)[1]
        self.to_date_edit.setDate(today.replace(day=last_day))
        self.to_date_edit.dateChanged.connect(self.filter_orders)
        date_range_layout.addWidget(self.to_date_edit)

        # Reset button
        reset_date_btn = QPushButton("Reset Date Range")
        reset_date_btn.clicked.connect(self.reset_date_range)
        date_range_layout.addWidget(reset_date_btn)

        date_range_layout.addStretch()

        # Add order type filter
        date_range_layout.addWidget(QLabel("Order Type:"))
        self.order_type_filter_combo = QComboBox()
        self.order_type_filter_combo.addItem("All Types")
        self.order_type_filter_combo.addItems(["employment", "termination", "salary change", "department change"])
        self.order_type_filter_combo.currentTextChanged.connect(self.filter_orders)
        date_range_layout.addWidget(self.order_type_filter_combo)

        date_range_group.setLayout(date_range_layout)

        layout.addWidget(date_range_group)

        # Orders table
        self.orders_table = EmployeeTableWidget(self)
        self.orders_table.setColumnCount(8)
        self.orders_table.setHorizontalHeaderLabels((["Number","Order Date", "Effective Date", "Employee ID", "Name", "Order Type","Department", "Salary"]))

        header = self.orders_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # Number
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) # Order Date
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Effective Date
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Employee ID
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents) # Name
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents) # Order Type
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents) # Department
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents) # Salary

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

        # Reset employee name dictionary
        if hasattr(self, 'employee_name_dict'):
            delattr(self, 'employee_name_dict')

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

            self.employee_table.setItem(row, 2, QTableWidgetItem(str(employee["department"])))

            # Get employee name - fetch directly from database
            employee_name = self.get_employee_name_from_db(employee["id"])
            self.employee_table.setItem(row, 1, QTableWidgetItem(employee_name))

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
            self.employee_table.setItem(row, 3, salary_item)

            # Status with color coding
            status_item = QTableWidgetItem(employee["status"])
            if employee["status"] == "Terminated":
                status_item.setForeground(Qt.GlobalColor.red)
                status_item.setBackground(Qt.GlobalColor.lightGray)
            else:
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.employee_table.setItem(row, 4, status_item)

            # Action menu button
            action_btn = QToolButton()
            action_btn.setText("⋮")  # Three dots menu
            action_btn.setStyleSheet("QToolButton { padding: 5px; border: 1px solid #ccc; border-radius: 3px; }")
            action_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

            # Create menu
            menu = QMenu(self)

            change_salary_action = QAction("📝 Change Salary", self)

            change_salary_action.triggered.connect(lambda checked, emp=employee:self.terminate_employee(emp,"salary change"))
            menu.addAction(change_salary_action)

            change_department_action = QAction("📝 Change Department", self)

            change_department_action.triggered.connect(lambda checked, emp=employee:self.terminate_employee(emp,"department change"))
            menu.addAction(change_department_action)

            terminate_action = QAction("🔴 Terminate Employee", self)
            terminate_action.triggered.connect(lambda checked, emp=employee: self.terminate_employee(emp,"termination"))

            menu.addAction(terminate_action)

            action_btn.setMenu(menu)

            # Add button to table - column index changed from 6 to 7
            self.employee_table.setCellWidget(row, 5, action_btn)
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


    def terminate_employee(self, employee,order_type):
        """Terminate an employee"""
        if employee["status"].lower() == "terminated":
            QMessageBox.information(self, "Already Terminated",
                                    f"Employee {employee['first_name']} {employee['last_name']} is already terminated.")
            return
        else:
            self.add_order(employee,order_type)



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

    def add_order(self,employee=None,order_type = None):
        """Open dialog to add new order"""
        dialog = OrderDialog(self, None, self.config_manager,employee,order_type)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Refresh employees list in case a new employee was added
            self.load_employees_from_db()

            # Refresh orders list after adding new order
            self.load_orders_from_db()
            QMessageBox.information(self, "Success", "Order added successfully!")
        else:
            print("DEBUG: Order dialog cancelled or closed")

    def filter_orders(self):
        """Filter orders based on search criteria and date range"""
        print(f"DEBUG filter_orders: all_orders length = {len(self.all_orders) if hasattr(self, 'all_orders') else 'no attr'}")

        if not hasattr(self, 'all_orders') or not self.all_orders:
            # If no orders, clear the table and return
            self.orders_table.setRowCount(0)
            # Show placeholder
            self.orders_table.setRowCount(1)
            placeholder_item = QTableWidgetItem("No orders found")
            placeholder_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.orders_table.setSpan(0, 0, 1, 6)
            self.orders_table.setItem(0, 0, placeholder_item)
            return

        search_text = self.orders_search_input.text().lower()
        from_date = self.from_date_edit.date().toPyDate()
        to_date = self.to_date_edit.date().toPyDate()
        order_type_filter = self.order_type_filter_combo.currentText()

        filtered_orders = []
        for index, order in enumerate(self.all_orders):
            # Convert order_date string to datetime.date object
            try:
                order_date = datetime.strptime(order["order_date"], "%Y-%m-%d").date()
                print(f"DEBUG: Order {index} date: {order_date} (string: {order['order_date']})")
            except:
                print(f"DEBUG: Error parsing date for order {index}: {order['order_date']}, Error: {e}")
                order_date = None

            # Date range filter
            if order_date and (order_date < from_date or order_date > to_date):
                continue

            # Order type filter
            if order_type_filter != "All Types" and order["order_action"] != order_type_filter:
                print(f"DEBUG: Order {index} filtered out by type")

                continue

            # Search text filter
            if search_text:
                # Search in various fields
                matches = (
                        search_text in order["order_number"].lower() or
                        search_text in order["employee_id"].lower() or
                        search_text in order["order_action"].lower()
                )

                # Also search in employee name if available
                employee_name = self.get_employee_name(order["employee_id"])
                if employee_name and search_text in employee_name.lower():
                    matches = True

                if not matches:
                    print(f"DEBUG: Order {index} filtered out by search text")
                    continue

            filtered_orders.append(order)
            print(f"DEBUG: Order {index} passed filters")

        print(f"DEBUG: Total filtered orders: {len(filtered_orders)}")
        self.display_orders(filtered_orders)

    def load_orders_from_db(self):
        """Load orders from database"""
        try:
            self.all_orders = self.database.get_all_orders()
            if self.all_orders is None:
                self.all_orders = []
        except Exception as e:
            print(f"Error loading orders: {e}")
            self.all_orders = []

        self.filter_orders()  # Apply current filters

        # Update status bar
        total_orders = len(self.all_orders)
        displayed_orders = self.orders_table.rowCount()
        self.statusBar().showMessage(f"Loaded {total_orders} total orders, showing {displayed_orders} after filtering")

    def display_orders(self, orders):
        """Display orders in table"""
        if orders:
            self.orders_table.setRowCount(len(orders))

            for row, order in enumerate(orders):
                # Order data
                self.orders_table.setItem(row, 0, QTableWidgetItem(order["order_number"]))
                self.orders_table.setItem(row, 1, QTableWidgetItem(order["order_date"]))
                self.orders_table.setItem(row, 2, QTableWidgetItem(order.get("effective_date", "")))
                self.orders_table.setItem(row, 3, QTableWidgetItem(order["employee_id"]))
                self.orders_table.setItem(row, 5, QTableWidgetItem(order["order_action"]))
                self.orders_table.setItem(row,6,QTableWidgetItem(order["new_department"]))
                self.orders_table.setItem(row,7,QTableWidgetItem(order["new_salary"]))

                # Get employee name - fetch directly from database
                employee_name = self.get_employee_name_from_db(order["employee_id"])
                self.orders_table.setItem(row, 4, QTableWidgetItem(employee_name))
        else:
            # Clear the table if no orders
            self.orders_table.setRowCount(0)

            # Show a placeholder message
            self.orders_table.setRowCount(1)
            placeholder_item = QTableWidgetItem("No orders found for the selected criteria")
            placeholder_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.orders_table.setSpan(0, 0, 1, 6)  # Span all columns
            self.orders_table.setItem(0, 0, placeholder_item)

    def reset_date_range(self):
        """Reset the date range to current month"""
        today = datetime.now().date()
        import calendar

        # Set from date to first day of current month
        self.from_date_edit.setDate(today.replace(day=1))

        # Set to date to last day of current month
        last_day = calendar.monthrange(today.year, today.month)[1]
        self.to_date_edit.setDate(today.replace(day=last_day))

        # Trigger filter update
        self.filter_orders()

    def get_employee_name(self, employee_id):
        """Get employee full name from ID"""
        # Create a dictionary for fast lookup if not exists
        if not hasattr(self, 'employee_name_dict'):
            self.employee_name_dict = {}
            for emp in self.employees:
                self.employee_name_dict[emp["id"]] = f"{emp['first_name']} {emp['last_name']}"

        return self.employee_name_dict.get(employee_id, "Unknown")

    def get_employee_name_from_db(self, employee_id):
        """Get employee name directly from database"""
        try:
            # Get the employee directly from database
            employee = self.database.get_employee_by_id(employee_id)
            if employee:
                return f"{employee['last_name']} {employee['first_name']} {employee['father_name']}"
            else:
                # Try to find in current employees list as fallback
                for emp in self.employees:
                    if emp["id"] == employee_id:
                        return f"{emp['first_name']} {emp['last_name']} {employee['father_name']}"
                return "Unknown"
        except Exception as e:
            print(f"Error getting employee name for {employee_id}: {e}")
            return "Unknown"

    def open_departments(self):
        """Show department page"""
        self.stacked_widget.setCurrentIndex(5)
        self.statusBar().showMessage("Manage departments")


    def open_kpis(self):
        pass

    def open_variables(self):
        pass

    def create_department_page(self):

        # Central widgets

        # self.dept_list = QListWidget()
        # self.load_departments()
        self.departments_table = QTableWidget()
        self.departments_table.setColumnCount(2)
        self.departments_table.setHorizontalHeaderLabels(["Department Name","Status"])
        header = self.departments_table.horizontalHeader()
        header.setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents) #Department Name
        header.setSectionResizeMode(1,QHeaderView.ResizeMode.ResizeToContents) #Department status

        self.departments_table.setSelectionBehaviour(QTableWidget.SelectionBehaviour.SelectRows)

        central_widgets = []
        central_widgets.append(self.departments_table)

        # Department buttons

        add_dept_btn = QPushButton("Add Department")
        add_dept_btn.clicked.connect(self.add_departments)

        remove_dept_btn = QPushButton("Remove Selected")
        remove_dept_btn.clicked.connect(self.remove_departments)

        edit_dept_btn = QPushButton("Edit Selected")
        edit_dept_btn.clicked.connect(self.edit_department)

        button_widgets = []
        button_widgets.append(add_dept_btn)
        button_widgets.append(remove_dept_btn)
        button_widgets.append(edit_dept_btn)

        self.new_department_page = NewPageTemplate("Manage departments",[],central_widgets,button_widgets)

        return self.new_department_page

    def create_kpi_page(self):
        pass

    def create_variable_page(self):
        pass

    def load_departments(self):
        self.dept_list.clear()
        departments = self.config_manager.get_departments()
        self.dept_list.addItems(departments)

    def add_departments(self):
        department, ok = QInputDialog.getText(self, "Add Department", "Department name:")
        if ok and department:
            if self.config_manager.add_department(department.strip()):
                self.load_departments()
                QMessageBox.information(self, "Success", "Department added successfully!")

            else:
                QMessageBox.warning(self, "Error", "Department already exists!")

    def remove_departments(self):
        current_item = self.dept_list.currentItem()
        if current_item:
            department = current_item.text()
            reply = QMessageBox.question(self, "Confirm", f"Remove department:{department}?")
            if reply == QMessageBox.StandardButton.Yes:
                employees = self.database.get_all_employees()
                emp_in_department = []
                for emp in employees:
                    if emp["department"] == department:
                        emp_in_department.append(emp)
                orders = self.database.get_all_orders()
                dept_orders = []
                for order in orders:
                    if order["new_department"] == department:
                        dept_orders.append(department)
                if emp_in_department or dept_orders:
                    message = QMessageBox(self)
                    message.setWindowTitle("Employment history exists")
                    message.setText("The selected deprtment has employment history, so cannot be removed.  The department may be closed for further employment.")
                    close_button = QPushButton("Close department")
                    message.addButton(close_button,QMessageBox.ButtonRole.ActionRole)
                    message.setStandardButtons(QMessageBox.StandardButton.Cancel)
                    message.exec()
                    if message.clickedButton() == close_button:
                        self.close_departments(department)

                else:

                    if self.config_manager.remove_department(department):
                        self.load_departments()
                        QMessageBox.information(self, "Success", "Department removed!")

        else:
            QMessageBox.warning(self, "Error", "Please select a department to remove!")


    def edit_department(self):
        current_item = self.dept_list.currentItem()


        if current_item:
            department = current_item.text()
            new_department, ok = QInputDialog.getText(self, "Edit Department", "Change department name to:",
                                                      QLineEdit.EchoMode.Normal, f"{department}")
            if ok and new_department:
                reply = QMessageBox.question(self, "Confirm", f"Change department name to: {new_department}?")
                if reply == QMessageBox.StandardButton.Yes:
                    if self.config_manager.save_edited_department(department,new_department):
                        employees = self.database.get_all_employees()
                        for emp in employees:
                            if emp["department"] == department:
                                emp["department"] = new_department
                                self.database.save_employee(emp)
                        self.load_departments()
                        QMessageBox.information(self, "Success", "Department name changed successfully!")
                    else:
                        QMessageBox.warning(self, "Error", "Department already exists!")
        else:
            QMessageBox.warning(self, "Error", "Please select a department to edit!")


    def close_departments(self,department):
        current_item = self.dept_list.currentItem()
        if current_item:
            reply = QMessageBox.question(self,"Confirm","The selected department will be restricted for employment if closed.  Do you want to continue?")
            if reply ==QMessageBox.StandardButton.Yes:
                department = current_item.text()
                if self.config_manager.close_department(department):
                    QMessageBox.information(self, "Success", "Department closed!")
        else:
            QMessageBox.warning(self,"Error", "Please select a department!")




