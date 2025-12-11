import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHeaderView, QSpinBox, QGroupBox
)
from PyQt6.QtCore import Qt
from datetime import datetime, timedelta


class SalaryAdjustmentDialog(QDialog):
    def __init__(self, parent=None, employees_with_changes=None, total_working_days=22):
        super().__init__(parent)
        self.employees = employees_with_changes
        self.total_working_days = total_working_days
        self.adjustments = {}

        self.setWindowTitle("Salary Change Adjustment")
        self.setFixedSize(800, 500)
        self.setup_ui()
        self.populate_table()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Instructions
        info_label = QLabel(
            f"One or more employees had salary changes during this month. "
            f"Please specify how many working days each salary was effective for.\n"
            f"Total working days in month: {self.total_working_days}"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background-color: #f0f8ff; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)

        # Table for adjustments
        self.adjustment_table = QTableWidget()
        self.adjustment_table.setColumnCount(8)
        self.adjustment_table.setHorizontalHeaderLabels([
            "Employee ID", "Name", "Department", "Effective Date",
            "Old Salary", "New Salary", "Days at Old", "Days at New"
        ])
        header = self.adjustment_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.adjustment_table)

        # Validation message
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.validation_label)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()

        calculate_btn = QPushButton("Calculate Proportional Salaries")
        calculate_btn.clicked.connect(self.calculate_proportional_salaries)
        button_layout.addWidget(calculate_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def populate_table(self):
        """Populate table with employees who had salary changes"""
        self.adjustment_table.setRowCount(len(self.employees))

        for row, change_dict in enumerate(self.employees):
            employee = change_dict['employee']
            change_date = change_dict['change_date']
            old_salary = change_dict['old_salary']
            new_salary = change_dict['new_salary']

            # Calculate days at each salary (pre-fill with reasonable defaults)
            change_day = change_date.day
            days_at_old = max(1, change_day - 1)  # Days before change
            days_at_new = self.total_working_days - days_at_old

            # Employee info
            self.adjustment_table.setItem(row, 0, QTableWidgetItem(employee['id']))
            self.adjustment_table.setItem(row, 1, QTableWidgetItem(
                f"{employee['first_name']} {employee['last_name']}"
            ))
            self.adjustment_table.setItem(row, 2, QTableWidgetItem(employee['department']))
            self.adjustment_table.setItem(row, 3, QTableWidgetItem(change_date.strftime("%Y-%m-%d")))

            # Salaries
            self.adjustment_table.setItem(row, 4, QTableWidgetItem(f"${old_salary:,.2f}"))
            self.adjustment_table.setItem(row, 5, QTableWidgetItem(f"${new_salary:,.2f}"))

            # Spin boxes for days
            days_old_spin = QSpinBox()
            days_old_spin.setRange(0, self.total_working_days)
            days_old_spin.setValue(days_at_old)
            days_old_spin.valueChanged.connect(self.validate_days)
            self.adjustment_table.setCellWidget(row, 6, days_old_spin)

            days_new_spin = QSpinBox()
            days_new_spin.setRange(0, self.total_working_days)
            days_new_spin.setValue(days_at_new)
            days_new_spin.valueChanged.connect(self.validate_days)
            self.adjustment_table.setCellWidget(row, 7, days_new_spin)

    def validate_days(self):
        """Validate that days sum equals total working days for each employee"""
        all_valid = True
        invalid_employees = []

        for row in range(self.adjustment_table.rowCount()):
            days_old_spin = self.adjustment_table.cellWidget(row, 6)
            days_new_spin = self.adjustment_table.cellWidget(row, 7)

            if days_old_spin and days_new_spin:
                total = days_old_spin.value() + days_new_spin.value()
                if total != self.total_working_days:
                    all_valid = False
                    employee_name = self.adjustment_table.item(row, 1).text()
                    invalid_employees.append(
                        f"{employee_name}: {days_old_spin.value()} + {days_new_spin.value()} = {total}")

        if not all_valid:
            self.validation_label.setText(
                f"ERROR: Days must sum to {self.total_working_days} for all employees!\n"
                f"Invalid: {', '.join(invalid_employees)}"
            )
            return False
        else:
            self.validation_label.setText("✓ All day allocations are valid")
            return True

    def calculate_proportional_salaries(self):
        """Calculate proportional salaries based on working days"""
        if not self.validate_days():
            QMessageBox.warning(self, "Validation Error",
                                f"Please ensure days sum to {self.total_working_days} for all employees.")
            return

        self.adjustments = {}

        for row in range(self.adjustment_table.rowCount()):
            employee_id = self.adjustment_table.item(row, 0).text()
            old_salary_str = self.adjustment_table.item(row, 4).text().replace('$', '').replace(',', '')
            new_salary_str = self.adjustment_table.item(row, 5).text().replace('$', '').replace(',', '')

            old_salary = float(old_salary_str)
            new_salary = float(new_salary_str)

            days_old_spin = self.adjustment_table.cellWidget(row, 6)
            days_new_spin = self.adjustment_table.cellWidget(row, 7)

            days_old = days_old_spin.value()
            days_new = days_new_spin.value()

            # Calculate proportional salary
            proportional_salary = (old_salary * days_old + new_salary * days_new) / self.total_working_days

            self.adjustments[employee_id] = {
                'proportional_salary': proportional_salary,
                'days_old': days_old,
                'days_new': days_new,
                'old_salary': old_salary,
                'new_salary': new_salary
            }

        self.accept()

    def get_adjustments(self):
        return self.adjustments