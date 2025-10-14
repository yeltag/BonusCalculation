import sys


from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTabWidget,QStatusBar)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setup_ui()

    def setup_ui(self):
        # Main window settings
        self.setWindowTitle(f"Employee Bonus System - Welcome {self.username}!")
        self.setGeometry(100,100,900,600)  # z, y, width, height

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        layout = QVBoxLayout()

        # Welcome message
        welcome_label = QLabel(f"Welcome to Employee Bonus System, {self.username}!")
        welcome_label.setStyleSheet("font-size:16px; font-weight: bold; margin:10px;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)

        # Create tabs for different sections

        self.tabs = QTabWidget()

        # Tab 1: Dashboard
        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout()
        dashboard_layout.addWidget(QLabel("Dashboard - Overview of bonus calculation will be here"))
        dashboard_tab.setLayout(dashboard_layout)
        self.tabs.addTab(dashboard_tab, "Dashboard")

        # Tab 2: Employee Management (we'll build this next)
        employees_tab = QWidget()
        employees_layout = QVBoxLayout()
        employees_layout.addWidget(QLabel("Employee Management - Coming sson!"))
        employees_tab.setLayout(employees_layout)
        self.tabs.addTab(employees_tab, "Employees")

        # Tab 3: Reports
        reports_tab = QWidget()
        reports_layout = QVBoxLayout()
        reports_layout.addWidget(QLabel("Reports - Coming soon!"))
        reports_tab.setLayout(reports_layout)
        self.tabs.addTab(reports_tab, "Reports")

        layout.addWidget(self.tabs)

        # Logout button
        logout_btn = QPushButton ("Logout")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setFixedWidth(100)
        layout.addWidget(logout_btn, alignment = Qt.AlignmentFlag.AlignRight)

        central_widget.setLayout(layout)

        # Status bar
        status_bar = QStatusBar()
        status_bar.showMessage(f"Loggen in as: {self.username}")
        self.setStatusBar(status_bar)

    def logout(self):
        self.close()
        # We'll handle returning to login screen later
