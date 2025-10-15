import sys


from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget,QStatusBar, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon

class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.employees = []  #We'll replace this with database later
        self.setup_ui()
        self.load_sample_data()  # Load somesample employees for testing

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

        # Tab 2: Dashboard (placeholder for now)
        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout()
        dashboard_layout.addWidget(QLabel("Dashboard - Overview of bonus calculation will be here"))
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

        # Add Employee button
        add_btn = QPushButton ("Add New Employee")
        add_btn.clicked.connect(self.add_employee)
        controls_layout.addWidget(add_btn)

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

    def create_status_bar(self):
        status_bar = QStatusBar()
        status_bar.showMessage(f"Logged in as: {self.username} | Ready")
        self.setStatusBar(status_bar)

    def load_sample_data(self):
            """Load some sample employee data for testing"""
            self.employees = [{"id": "EMP001", "first_name":"John", "last_name": "Smith","department":"Sales","salary":5000,"status": "Active"},
                              {"id": "EMP002", "first_name": "Sarah", "last_name": "Johnson", "department": "Marketing", "salary": 4500, "status": "Active"},
                              {"id": "EMP003", "first_name": "Mike", "last_name": "Brown", "department": "IT", "salary": 6000, "status": "Active"},
                              {"id": "EMP004", "first_name": "Emily", "last_name": "Davis", "department": "HR", "salary": 4800, "status": "Inactive"},
                              {"id": "EMP005", "first_name": "David", "last_name": "Wilson", "department": "Sales", "salary": 5200, "status": "Active"}
                              ]
            self.refresh_employee_table()

    def refresh_employee_table(self):

        """Refresh the employee table with current data"""
        self.employee_table.setRowCount(len(self.employees))

        for row, employee in enumerate(self.employees):
            self.employee_table.setItem(row, 0, QTableWidgetItem(employee["id"]))
            self.employee_table.setItem(row, 1, QTableWidgetItem(employee["first_name"]))
            self.employee_table.setItem(row,2, QTableWidgetItem(employee["last_name"]))
            self.employee_table.setItem(row, 3, QTableWidgetItem(employee["department"]))
            self.employee_table.setItem(row, 4, QTableWidgetItem(f"${employee["salary"]:,.2f}"))
            self.employee_table.setItem(row, 5, QTableWidgetItem(employee["status"]))

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
        QMessageBox.information(self, "Add Employee", "Add employee feature coming soon!\n\n"
                                    "We'll build this in the next phase.")

    def edit_employee(self, index):
        """Edit employee when double-clicked"""
        row = index.row()
        employee_id = self.employee_table.item(row, 0).text()
        QMessageBox.information(self, "Edit Employee", f"Edit employee {employee_id} coming soon!\n\n"
                                    "We'll build this in the next phase.")

    def logout(self):
        """Logout and close application"""
        reply = QMessageBox.question(self, "Logout","Are you sure you want to logout?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.close()



