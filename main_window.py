import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStatusBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QLineEdit, QDialog, QComboBox, QSpinBox, QGroupBox,
    QMenu, QToolButton, QFormLayout, QStackedWidget, QDateEdit, QAbstractScrollArea, QListWidget, QInputDialog
)

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QAction, QColor, QTextCharFormat
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
from kpi_editor_dialog import KPIEditorDialog
from variables_dialog import VariablesDialog


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
        self.current_kpi = None
        #self.new_page = NewPageTemplate('')

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
        self.kpi_page = self.create_kpi_page()
        self.variable_page=self.create_variable_page()


        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.employees_page)
        self.stacked_widget.addWidget(self.variable_entry_page)
        self.stacked_widget.addWidget(self.bonus_calculation_page)
        self.stacked_widget.addWidget(self.orders_page)
        self.stacked_widget.addWidget(self.department_page)
        self.stacked_widget.addWidget(self.kpi_page)
        self.stacked_widget.addWidget(self.variable_page)


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


        if pre_calculated_results is False:

            pre_calculated_results = None

        if pre_calculated_results is not None:
            # Display pre-calculated results

            results = pre_calculated_results
        else:
            # Calculate bonuses normally

            month = self.calc_month_combo.currentIndex() + 1
            year = self.calc_year_spin.value()
            department_filter = self.calc_dept_combo.currentText()
            working_days = self.working_days_spin.value()

            calculator = BonusCalculator(self.database, self.config_manager)

            # Check for salary changes in the selected month
            employees_with_changes = calculator.get_employees_with_salary_changes(year, month)

            # DEBUG: Check what's returned

            for i, emp_data in enumerate(employees_with_changes):
                employee = emp_data['employee']
                changes = emp_data['changes']
                #print(
                #    f"  Employee {i + 1}: {employee['first_name']} {employee['last_name']} has {len(changes)} changes")
                #for j, change in enumerate(changes):
                 #   print(f"    Change {j + 1}: {change['change_date'].strftime('%Y-%m-%d')}, "
                  #        f"{change['old_salary']} -> {change['new_salary']}")

            salary_adjustments = None
            if employees_with_changes:

                for i, emp_data in enumerate(employees_with_changes):
                    employee = emp_data['employee']
                    changes = emp_data['changes']

                    #for j, change in enumerate(changes):
                      #  print(
                        #    f"    Change {j + 1}: {change['change_date'].strftime('%Y-%m-%d')}, {change['old_salary']} -> {change['new_salary']}")

                # Show advanced salary adjustment dialog
                dialog = AdvancedSalaryAdjustmentDialog(self, employees_with_changes, working_days)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    salary_adjustments = dialog.get_adjustments()

                else:

                    return

            results = calculator.calculate_bonuses_with_validation(
                year, month, department_filter, self, working_days, salary_adjustments
            )

            # Check for both None and False
            if results is None or results is False:

                return



        # Safety check - ensure results is a list
        if not isinstance(results, list):

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
        dialog = OrderDialog(self, None, self.config_manager,employee,order_type, self.username)
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

            except:

                order_date = None

            # Date range filter
            if order_date and (order_date < from_date or order_date > to_date):
                continue

            # Order type filter
            if order_type_filter != "All Types" and order["order_action"] != order_type_filter:


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

                    continue

            filtered_orders.append(order)



        self.display_orders(filtered_orders)

    def load_orders_from_db(self):
        """Load orders from database"""
        try:
            self.all_orders = self.database.get_all_orders()
            if self.all_orders is None:
                self.all_orders = []
        except Exception as e:

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
                return ""
        except Exception as e:

            return ""

    def open_departments(self):
        """Show department page"""
        self.stacked_widget.setCurrentIndex(5)
        self.statusBar().showMessage("Manage departments")


    def open_kpis(self):
        self.stacked_widget.setCurrentIndex(6)
        self.statusBar().showMessage("Manage KPIs")

    def open_variables(self):
        self.stacked_widget.setCurrentIndex(7)
        self.statusBar().showMessage("Manage Variables")

    def create_department_page(self):
        self.new_department_page = NewPageTemplate("Manage departments")

        # Central widgets

        self.departments_table = self.new_department_page.create_qtablewidget_tool(2,["Department","Status"],self.edit_department,[self.add_departments,self.edit_department,self.remove_departments])


        central_widgets = [self.departments_table]

        search_widgets = []
        list_to_filter = self.load_departments_inner()
        search_fields = ["Department","Status"]

        search_text_tool = self.new_department_page.create_search_text_tool(list_to_filter,search_fields,self.departments_table)


        # combo_box
        combo_list = ["All departments","active","closed"]
        combo_box_label = "Select department status:"
        combo_tool = self.new_department_page.combo_box_tool(combo_box_label,combo_list,self.departments_table,"Status",list_to_filter)

        search_widgets = search_text_tool + combo_tool

        # Department buttons

        add_dept_btn = QPushButton("Add Department")
        add_dept_btn.clicked.connect(self.add_departments)

        remove_dept_btn = QPushButton("Remove Selected")
        remove_dept_btn.clicked.connect(self.remove_departments)

        edit_dept_btn = QPushButton("Edit Selected")
        edit_dept_btn.clicked.connect(self.edit_department)

        close_dpt_btn = QPushButton("Close Selected")
        close_dpt_btn.clicked.connect(self.close_departments)

        button_widgets = [add_dept_btn,remove_dept_btn,edit_dept_btn,close_dpt_btn]


        self.new_department_page.search_widgets = search_widgets
        self.new_department_page.central_widgets = central_widgets
        self.new_department_page.button_widgets = button_widgets

        self.new_department_page.create_layout()
        #self.new_department_page = NewPageTemplate("Manage departments",search_widgets,central_widgets,button_widgets)

        self.load_departments()

        return self.new_department_page

    def create_kpi_page(self):

        self.new_kpi_page = NewPageTemplate("Manage KPIs")
        self.kpi_table = self.new_department_page.create_qtablewidget_tool(2, ["name", "formula"],
                                                                                   self.edit_kpi,
                                                                                   [self.add_kpi,
                                                                                    self.edit_kpi,
                                                                                    self.remove_kpi])

        central_widgets = [self.kpi_table]


        list_to_filter = self.config_manager.get_kpis()
        search_fields = ["Name","Formula"]

        search_kpi_tool = self.new_kpi_page.create_search_text_tool(list_to_filter,search_fields,self.kpi_table)
        search_widgets = search_kpi_tool

        # Buttons

        add_kpi_btn = QPushButton("Add KPI")
        add_kpi_btn.clicked.connect(self.pre_add_kpi)

        remove_kpi_btn = QPushButton("Remove Selected")

        edit_kpi_btn = QPushButton("Edit Selected")
        edit_kpi_btn.clicked.connect(self.edit_kpi)

        button_widgets = [add_kpi_btn,remove_kpi_btn,edit_kpi_btn]

        self.new_kpi_page.search_widgets = search_widgets
        self.new_kpi_page.central_widgets = central_widgets
        self.new_kpi_page.button_widgets = button_widgets

        self.new_kpi_page.create_layout()

        return self.new_kpi_page

    def create_variable_page(self):
        """ Creates "Manage variables" page at Main menu/Configuration/Variables"""
        self.new_variable_page = NewPageTemplate("Manage Variables")
        self.variable_table = self.new_variable_page.create_qtablewidget_tool(4, ["Name", "Default value", "Data type", "Is active"],self.edit_variable,[self.add_variable,self.edit_variable,self.remove_variable])

        central_widgets = [self.variable_table]

        list_to_filter = self.load_variables()

        search_fields = ["Name","Description","Is active"]

        search_variable_tool = self.new_variable_page.create_search_text_tool(list_to_filter,search_fields,self.variable_table)

        combo_list = ["All variables","active","closed"]
        combo_box_label = "Select variable status"
        combo_tool = self.new_variable_page.combo_box_tool(combo_box_label,combo_list,self.variable_table,"Is active",list_to_filter)

        search_widgets = search_variable_tool + combo_tool

        add_var_btn = QPushButton("Add Variable")
        add_var_btn.clicked.connect(self.pre_add_variable)

        edit_var_btn = QPushButton("Edit Variable")
        edit_var_btn.clicked.connect(self.edit_variable)

        deactive_var_btn = QPushButton("Deactive Variable")
        deactive_var_btn.clicked.connect(self.deactivate_variable)

        remove_var_btn = QPushButton("Remove Variable")
        remove_var_btn.clicked.connect(self.remove_variable)

        button_widgets = [add_var_btn,edit_var_btn,deactive_var_btn,remove_var_btn]

        self.new_variable_page.search_widgets = search_widgets
        self.new_variable_page.central_widgets = central_widgets
        self.new_variable_page.button_widgets = button_widgets

        self.new_variable_page.create_layout()

        return self.new_variable_page


    def load_departments(self):
        #self.departments_table.clearContents()

        self.load_departments_inner()

    def load_departments_inner(self):
        self.all_departments = self.config_manager.get_departments()

        self.departments_list = []
        for key, value in self.all_departments.items():
            self.departments_list.append({"department": key, "status": value})
        return self.departments_list


    def add_departments(self,table = None):
        department, ok = QInputDialog.getText(self, "Add Department", "Department name:")
        if ok and department:
            if self.config_manager.add_department(department.strip()):
                self.load_departments()
                self.new_department_page.refresh_with_filters(self.departments_list, self.departments_table)

                QMessageBox.information(self, "Success", "Department added successfully!")

            else:
                QMessageBox.warning(self, "Error", "Department already exists!")

    def remove_departments(self,table = None):
        current_item = self.departments_table.selectedItems()

        if current_item:
            department = current_item[0].text()
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
                        self.new_department_page.list_to_filter = self.departments_list
                        self.new_department_page.refresh_with_filters(self.departments_list, self.departments_table)
                        QMessageBox.information(self, "Success", "Department removed!")

        else:
            QMessageBox.warning(self, "Error", "Please select a department to remove!")


    def edit_department(self,table = None):
        current_item = self.departments_table.selectedItems()


        if current_item:
            department = current_item[0].text()
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
                        self.new_department_page.display_elements(self.departments_list, self.departments_table)
                        QMessageBox.information(self, "Success", "Department name changed successfully!")
                    else:
                        QMessageBox.warning(self, "Error", "Department already exists!")
        else:
            QMessageBox.warning(self, "Error", "Please select a department to edit!")


    def close_departments(self,department):
        current_item = self.departments_table.selectedItems()
        if current_item:
            reply = QMessageBox.question(self,"Confirm","The selected department will be restricted for employment if closed.  Do you want to continue?")
            if reply ==QMessageBox.StandardButton.Yes:
                department = current_item[0].text()
                if self.config_manager.close_department(department):
                    self.load_departments()
                    self.new_department_page.display_elements(self.departments_list, self.departments_table)
                    QMessageBox.information(self, "Success", "Department closed!")
        else:
            QMessageBox.warning(self,"Error", "Please select a department!")


    def edit_kpi(self,table):
        current_item = self.kpi_table.currentItem()

        # print("current item kpi: ",current_item.data(Qt.ItemDataRole.UserRole))

        if current_item:

            kpi_list = self.config_manager.get_kpis()
            for kpi in kpi_list:
                if kpi["id"] == current_item.data(Qt.ItemDataRole.UserRole):
                    self.current_kpi = kpi
                    self.add_kpi(self.kpi_table)
                    return
        else:
            QMessageBox.warning(self, "Error", "Please select a kpi!")


    def pre_add_kpi(self,table):
        self.current_kpi = None
        self.add_kpi()


    def add_kpi(self,table=None):
        """Open KPI editor to add new KPI"""


        dialog = KPIEditorDialog(self, self.current_kpi if self.current_kpi else None, self.config_manager, database=self.database,username = self.username)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_kpi = dialog.get_kpi_data()

            # Add to configuration
            #if self.config_manager.add_kpi(new_kpi):
            if new_kpi:
                self.config_manager.add_kpi()
                self.load_kpis()
                self.new_kpi_page.refresh_with_filters(self.all_kpi,self.kpi_table)
                QMessageBox.information(self, "Success", "KPI added successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to add KPI")

    def remove_kpi(self,table):
        pass

    def load_kpis(self):
        self.all_kpi = self.config_manager.get_kpis()

    def pre_add_variable(self):
        self.current_var = None
        self.add_variable()

    def add_variable(self,edit_mode=False):
        """Opens Create Custom Variable dialoq,
        sends created variable to database,
        initiates refreshing of variables table on "Manage variables" page"""

        var_dialog = VariablesDialog(username = self.username, variable_data = self.current_var, database = self.database, )

        if var_dialog.exec() == QDialog.DialogCode.Accepted:
            self.new_variable = var_dialog.get_variable_data()
        else:
            return

        if hasattr(self,'new_variable'):
            self.database.save_custom_variable(self.new_variable)
            list_to_filter = self.load_variables()
            self.new_variable_page.refresh_with_filters(list_to_filter, self.variable_table)
            if edit_mode:
                text = "Variable updated sucsessgully!"
            else:
                text = "Variable added successfully!"
            QMessageBox.information(self, "Success", text)
        else:
            if edit_mode:
                text = "Failed to update variable"
            else:
                text = "Failed to add variable"
            QMessageBox.warning(self, "Error", text)



    def edit_variable(self):
        current_row = self.variable_table.currentItem()
        if current_row:
            variables_list = self.load_variables()
            for var in variables_list:
                if var["id"] == current_row.data(Qt.ItemDataRole.UserRole):
                    self.current_var = var

                    self.add_variable(True)
                    return
        else:
            QMessageBox.warning(self,"Error","Please select a variable!")


    def remove_variable(self):
        separator = ["+", "-", "*", "/", "(", ")", "min", "max", "round", "if", "then", "else", " "]
        all_kpis = self.database.get_all_kpis()
        self.current_var = self.current_var_identification()
        used_kpi = []
        for kpi in all_kpis:
            if self.current_var["name"] in kpi["formula"]:
                used_kpi.append(kpi["name"])
        if len(used_kpi) > 0:
            msg = QMessageBox()
            msg.setWindowTitle("Variable is not removable")
            msg.setText(f"The selected variable is used in the following KPIs and cannot be removed:\n{'\n'.join(kpi for kpi in used_kpi)}\nDo you want to deactivate it instead?")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
            yes_button=msg.button(QMessageBox.StandardButton.Yes)
            yes_button.setText("Deactivate")
            result = msg.exec()
            if result == QMessageBox.StandardButton.Yes:
                self.deactivate_variable()
            else:
                return


        else:
            try:
                self.database.delete_custom_variable(self.current_var['id'])
                list_to_filter = self.load_variables()
                self.new_variable_page.refresh_with_filters(list_to_filter, self.variable_table)
                QMessageBox.information(self, "Success", "Variable deleted successfully!")
            except:
                QMessageBox.warning(self, "Error", "Failed to remove variable!")


        pass

    def current_var_identification(self):
        current_row = self.variable_table.currentItem()
        if current_row:
            variable_id = current_row.data(Qt.ItemDataRole.UserRole)
            variables_list = self.database.get_custom_variables()
            for var in variables_list:
                print(current_row.data(Qt.ItemDataRole.UserRole))
                if var["id"] == variable_id:
                    current_var = var
                    break

            if current_var is None:
                QMessageBox.warning(self, "Error", "Variable not found!")
                return

            return current_var
        else:
            QMessageBox.warning(self,"Error","Please, select a variable.")

    def deactivate_variable(self):
        """Makes variable inactive and prevents var from further usage in new kpis"""


        self.current_var = self.current_var_identification()

        var_deactive_dialog = QDialog(self)
        var_deactive_dialog.setWindowTitle("Deactivate variable")
        var_deactive_dialog.setFixedSize(250,100)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Deactivate variable {self.current_var['display_name']}"))

        date_layout = QHBoxLayout()
        date_label = QLabel("From date")
        date_layout.addWidget(date_label)
        deact_date = self.new_variable_page.date_widget_inner()
        calendar = deact_date.calendarWidget()

        #self.new_variable_page.create_inactive_calendar_style(deact_date)
        deact_date.dateChanged.connect(
            lambda date_val, widget=deact_date: self.on_calendar_date_change(
                            widget))
        forced_date = self.new_variable_page.enforce_first_of_the_month(deact_date.date())
        deact_date.setDate(forced_date)


        date_layout.addWidget(deact_date)
        layout.addLayout(date_layout)

        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        deact_button = QPushButton("Deactivate")
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(deact_button)
        #deact_button.clicked.connect(lambda date=deact_date: self.final_deactivate_custom_var(date))
        layout.addLayout(button_layout)

        var_deactive_dialog.setLayout(layout)

        cancel_button.clicked.connect(var_deactive_dialog.reject)
        deact_button.clicked.connect(var_deactive_dialog.accept)

        if var_deactive_dialog.exec() == QDialog.DialogCode.Accepted:
            success = self.final_deactivate_custom_var(deact_date.date())
            if success:
                QMessageBox.information(self, "Success", "Variable deactivated successfully!")
            else:
                QMessageBox.warning(self, "Error", "Variable deactivation has failed!")
        else:
            return


    def final_deactivate_custom_var(self,deact_date):
        """Passes variable data to databse for deactivation
        deact_date - date from which the variable would be deactivated"""
        print("deact_date: ", deact_date)
        deact_date = deact_date.toString("yyyy-MM-dd")
        variable_data = [deact_date,self.username,self.current_var["id"]]
        self.database.deactivate_custom_variable(variable_data)
        list_to_filter = self.load_variables()
        self.new_variable_page.refresh_with_filters(list_to_filter,self.variable_table)
        return True


    def on_calendar_date_change(self,date_widget):
        forced_date = self.new_variable_page.enforce_first_of_the_month(date_widget.date())
        date_widget.setDate(forced_date)
        #self.new_variable_page.create_inactive_calendar_style(date_widget)

    def load_variables(self):
        """Loads a list of custom variables from database"""
        list_to_filter = self.database.get_custom_variables()
        for var in list_to_filter:
            if var["data_type"] == "percentage":
                var["default_value"] = f"{float(var["default_value"])*100:.2f}%"
                print(var["default_value"])
            if var["is_active"] == True:
                var["is_active"] = "active"
            else:
                var["is_active"] = "closed"
        return list_to_filter




