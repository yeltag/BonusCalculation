import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel

def main():
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("My First Bonus System Window")
    window.setGeometry(100,100,400,200)

    Label = QLabel("Hello! PyQt6 is working!", window)
    Label.move(100,80)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()