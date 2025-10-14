import sys
from PyQt6.QtWidgets import QApplication
from login_window import LoginWindow

def main():
    # Create the application
    app = QApplication(sys.argv)

    # Create and show login window
    login_window = LoginWindow()
    login_window.show()

    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()