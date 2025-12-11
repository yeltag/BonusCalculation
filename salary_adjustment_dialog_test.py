import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHeaderView, QSpinBox, QGroupBox
)
from PyQt6.QtCore import Qt
from datetime import datetime, timedelta


class TestSalaryAdjustmentDialog(QDialog):
    def __init__(self, parent=None, total_working_days=22):
        super().__init__(parent)
        self.total_working_days = total_working_days

        self.setWindowTitle("TEST Salary Change Adjustment")
        self.setFixedSize(800, 400)
        self.setup_ui()
        self.populate_test_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Instructions
        info_label = QLabel(
            f"TEST: This is a test dialog to debug the validation issue.\n"
            f"Total working days in month: {self.total_working_days}"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background-color: #ffffe0; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)

        # Table for adjustments
        self.adjustment_table = QTableWidget()
        self.adjustment_table.setColumnCount(4)
        self.adjustment_table.setHorizontalHeaderLabels([
            "Employee ID", "Name", "Days at Rate", "Salary Rate"
        ])
        header = self.adjustment_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.adjustment_table)

        # Buttons
        button_layout = QHBoxLayout()

        test_btn = QPushButton("Test Validation")
        test_btn.clicked.connect(self.test_validation)
        button_layout.addWidget(test_btn)

        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def populate_test_data(self):
        """Populate with test data"""
        self.adjustment_table.setRowCount(3)

        # First employee, 2 periods
        self.adjustment_table.setItem(0, 0, QTableWidgetItem("EMP001"))
        self.adjustment_table.setItem(0, 1, QTableWidgetItem("John Doe"))
        days_spin1 = QSpinBox()
        days_spin1.setRange(0, 31)
        days_spin1.setValue(10)
        self.adjustment_table.setCellWidget(0, 2, days_spin1)
        self.adjustment_table.setItem(0, 3, QTableWidgetItem("$5,000"))

        self.adjustment_table.setItem(1, 0, QTableWidgetItem("EMP001"))  # SAME EMPLOYEE
        self.adjustment_table.setItem(1, 1, QTableWidgetItem("John Doe"))
        days_spin2 = QSpinBox()
        days_spin2.setRange(0, 31)
        days_spin2.setValue(12)  # Total 22 days
        self.adjustment_table.setCellWidget(1, 2, days_spin2)
        self.adjustment_table.setItem(1, 3, QTableWidgetItem("$6,000"))

        # Second employee, 1 period
        self.adjustment_table.setItem(2, 0, QTableWidgetItem("EMP002"))
        self.adjustment_table.setItem(2, 1, QTableWidgetItem("Jane Smith"))
        days_spin3 = QSpinBox()
        days_spin3.setRange(0, 31)
        days_spin3.setValue(22)  # Exactly 22 days
        self.adjustment_table.setCellWidget(2, 2, days_spin3)
        self.adjustment_table.setItem(2, 3, QTableWidgetItem("$7,000"))

    def test_validation(self):
        """Test the validation logic"""
        employee_totals = {}

        for row in range(self.adjustment_table.rowCount()):
            emp_id_item = self.adjustment_table.item(row, 0)
            name_item = self.adjustment_table.item(row, 1)
            days_spin = self.adjustment_table.cellWidget(row, 2)

            if not emp_id_item or not name_item or not days_spin:
                continue

            emp_id = emp_id_item.text()
            emp_name = name_item.text()

            if emp_id and emp_name:
                if emp_id not in employee_totals:
                    employee_totals[emp_id] = {
                        'name': emp_name,
                        'total_days': 0
                    }

                employee_totals[emp_id]['total_days'] += days_spin.value()

        # Build result message
        result_msg = "Validation Test Results:\n\n"
        all_valid = True

        for emp_id, data in employee_totals.items():
            total_days = data['total_days']
            name = data['name']
            is_valid = total_days == self.total_working_days

            result_msg += f"{name} ({emp_id}): {total_days} days "
            result_msg += f"{'✅ VALID' if is_valid else '❌ INVALID'}\n"

            if not is_valid:
                all_valid = False

        result_msg += f"\nExpected: {self.total_working_days} days per employee\n"
        result_msg += f"Overall: {'✅ ALL VALID' if all_valid else '❌ SOME INVALID'}"

        QMessageBox.information(self, "Test Results", result_msg)