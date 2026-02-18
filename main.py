import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from login_window import LoginWindow
import os
import json
from database import Database



def exception_hook(exctype, value, traceback_obj):
    """
    Function to catch unhandled exceptions and display them in a message box
    """

    error_msg = "".join(traceback.format_exception(exctype, value, traceback_obj))
    print(f"Unhandled exception: {error_msg}")

    # Show error in a message box
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setText("An error occured while starting the application.")
    msg.setInformativeText(f"Error:{str(value)}")
    msg.setWindowTitle("A pplication Error")
    msg.exec()

    # Call the default exception hook
    sys.__excepthook__(exctype, value, traceback_obj)


def main():
    try:
        # Set the exception hook
        sys.excepthook = exception_hook

        # Enable high DPI scaling (helps with graphics issues)
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

        # Create the application
        app = QApplication(sys.argv)


        # System initialization
        initialize_system()


        # Create and show login window
        login_window = LoginWindow()
        login_window.show()

        # Run the application
        sys.exit(app.exec())

    except Exception as e:
        print(f"Application failed to start: {e}")
        input("press Enter to exit...")  #Keep console open to see error


def initialize_system():
    """Initialize the system with clean configuration"""
    print("Initializing Employee Bonus System...")

    # Check if config.json exists
    if not os.path.exists('config.json'):
        print("Creating default configuration...")
        default_config = {
            "departments": {"Sales":"active", "Marketing":"active", "IT":"active", "HR":"active", "Finance":"active", "Operations":"active"},
            "kpis": []
        }
        with open('config.json', 'w') as f:
            json.dump(default_config, f, indent=4)

    # Initialize database

    db = Database()

    # Verify no unwanted tables exist
    db.check_schema()

    print("System initialized successfully!")
    return db

if __name__ == "__main__":
    main()