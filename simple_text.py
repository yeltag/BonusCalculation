# Create test_dialog.py to test basic functionality
import sys
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton


class TestDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Dialog")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        # Simple test fields
        layout.addWidget(QLabel("Test Field 1:"))
        layout.addWidget(QLineEdit())
        layout.addWidget(QLabel("Test Field 2:"))
        layout.addWidget(QLineEdit())

        layout.addWidget(QPushButton("Test Button"))

        self.setLayout(layout)


def main():
    app = QApplication(sys.argv)
    dialog = TestDialog()
    dialog.exec()


if __name__ == "__main__":
    main()