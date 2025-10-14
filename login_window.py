import sys
from PyQt6.QtWidgets import(QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt
from main_window import MainWindow # import the main window


class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.main_window = None # This will hold our main window
        self.setup_ui()

    def setup_ui(self):
        # Window settings
        self.setWindowTitle("Bonus System - Login")
        self.setFixedSize(350,250)

        # Create layout
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Employee Bonus System")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Username
        main_layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        main_layout.addWidget(self.username_input)

        # Password
        main_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        main_layout.addWidget(self.password_input)

        # Add some space
        main_layout.addSpacing(20)

        # Login button - Centered
        button_layout = QVBoxLayout()
        button_layout.addStretch()
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.check_login)
        button_layout.addWidget(login_btn)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        # Set the layout

        self.setLayout(main_layout)

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Simple autentication (we'll replace with database later)
        valid_users = {
            "admin": "password123",
            "manager": "manager123",
            "user": "user123"
        }
        if username in valid_users and password == valid_users[username]:
            QMessageBox.information(self, "Success", f"Login successful! Welcome {username}!")
            self.open_main_window(username)
            # Here we'll open the main application window later
        else:
            QMessageBox.warning(self, "Error", "Invalid username ot password")

    def open_main_window (self, username):
        # Hide login window
        self.hide()

        # Create and show main window
        self.main_window = MainWindow(username)
        self.main_window.show()

        # When main window closes, show login again
        self.main_window.destroyed.connect(self.show_login)

    def show_login(self):
        # Clear password field and show login window again
        self.password_input.clear()
        self.show()

