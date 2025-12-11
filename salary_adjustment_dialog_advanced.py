import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHeaderView, QSpinBox, QGroupBox, QComboBox
)
from PyQt6.QtCore import Qt
from datetime import datetime, timedelta


class AdvancedSalaryAdjustmentDialog(QDialog):
    def __init__(self, parent=None, employees_with_changes=None, total_working_days=22):
        super().__init__(parent)
        self.employees = employees_with_changes or []  # Use passed data, default to empty list
        self.total_working_days = total_working_days
        self.adjustments = {}

        self.setWindowTitle("Salary Change Adjustment (Multiple Changes)")
        self.setFixedSize(1000, 600)
        self.setup_ui()

        # Only populate if we have real data
        if self.employees and len(self.employees) > 0:
            print(f"DEBUG: Dialog initialized with {len(self.employees)} employees")
            self.populate_table()
        else:
            print("DEBUG: Dialog initialized with NO employees")
            # Show message and close
            QMessageBox.information(self, "No Changes",
                                    "No employees with salary changes found for this period.")
            self.reject()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Instructions
        info_label = QLabel(
            f"One or more employees had salary changes during this month. "
            f"Please specify how many working days were at each salary rate.\n"
            f"Total working days in month: {self.total_working_days}\n"
            f"Note: You can have multiple salary changes per employee."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background-color: #f0f8ff; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)

        # Table for adjustments
        self.adjustment_table = QTableWidget()
        self.adjustment_table.setColumnCount(9)
        self.adjustment_table.setHorizontalHeaderLabels([
            "Employee ID", "Name", "Department", "Change #",
            "Change Date", "Salary Rate", "Days at this Rate",
            "From Date", "To Date"
        ])
        header = self.adjustment_table.horizontalHeader()
        for i in range(self.adjustment_table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.adjustment_table)

        # Summary group
        summary_group = QGroupBox("Summary")
        summary_layout = QHBoxLayout()
        self.summary_label = QLabel("")
        summary_layout.addWidget(self.summary_label)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        # Validation message
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.validation_label)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        auto_btn = QPushButton("Auto-Calculate Days")
        auto_btn.clicked.connect(self.auto_calculate_days)
        button_layout.addWidget(auto_btn)

        button_layout.addStretch()

        calculate_btn = QPushButton("Calculate Proportional Salaries")
        calculate_btn.clicked.connect(self.calculate_proportional_salaries)
        button_layout.addWidget(calculate_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def populate_table(self):
        """Populate table with actual employees and their multiple salary changes"""
        print(f"DEBUG populate_table: Starting with {len(self.employees)} employees")

        row_count = 0
        for emp_idx, emp_data in enumerate(self.employees):
            employee = emp_data['employee']
            changes = emp_data['changes']

            print(f"DEBUG: Processing employee {emp_idx + 1}: {employee['first_name']} {employee['last_name']} "
                  f"with {len(changes)} changes")

            # For each change, create a period
            periods = self.create_periods_for_employee(employee, changes)

            # Add rows for each period
            for period_idx, period in enumerate(periods):
                self.adjustment_table.insertRow(row_count)

                # Fill employee info for EVERY row
                self.adjustment_table.setItem(row_count, 0, QTableWidgetItem(employee['id']))
                self.adjustment_table.setItem(row_count, 1, QTableWidgetItem(
                    f"{employee['first_name']} {employee['last_name']}"
                ))
                self.adjustment_table.setItem(row_count, 2, QTableWidgetItem(employee['department']))

                # Change number
                self.adjustment_table.setItem(row_count, 3, QTableWidgetItem(str(period_idx + 1)))

                # Change date (for changes) or period info
                if 'change_date' in period:
                    self.adjustment_table.setItem(row_count, 4,
                                                  QTableWidgetItem(period['change_date'].strftime("%Y-%m-%d")))
                else:
                    self.adjustment_table.setItem(row_count, 4, QTableWidgetItem("Initial"))

                # Salary rate
                self.adjustment_table.setItem(row_count, 5, QTableWidgetItem(f"${period['salary']:,.2f}"))

                # Days at this rate (spin box)
                days_spin = QSpinBox()
                days_spin.setRange(0, self.total_working_days)
                days_spin.setValue(period.get('days', 0))
                days_spin.valueChanged.connect(self.validate_and_update)
                self.adjustment_table.setCellWidget(row_count, 6, days_spin)

                # Store employee info in the spinbox
                days_spin.setProperty('employee_id', employee['id'])
                days_spin.setProperty('employee_name', f"{employee['first_name']} {employee['last_name']}")
                days_spin.setProperty('period_idx', period_idx)

                # From date and To date
                from_date_str = period.get('from_date', '').strftime("%Y-%m-%d") if period.get('from_date') else ""
                to_date_str = period.get('to_date', '').strftime("%Y-%m-%d") if period.get('to_date') else ""
                self.adjustment_table.setItem(row_count, 7, QTableWidgetItem(from_date_str))
                self.adjustment_table.setItem(row_count, 8, QTableWidgetItem(to_date_str))

                print(f"DEBUG: Added row {row_count} for {employee['first_name']}, Period {period_idx + 1}, "
                      f"${period['salary']:,.2f}, {period.get('days', 0)} days")

                row_count += 1

        print(f"DEBUG: Total rows in table: {self.adjustment_table.rowCount()}")
        self.validate_and_update()

    def create_periods_for_employee(self, employee, changes):
        """Create salary periods for an employee with multiple changes"""
        periods = []

        if not changes or len(changes) == 0:
            return periods

        # Get month/year from first change
        first_change_date = changes[0]['change_date']
        month = first_change_date.month
        year = first_change_date.year

        print(
            f"\nDEBUG create_periods: Processing {employee['first_name']} for {month}/{year} with {len(changes)} changes")

        # Calculate month boundaries
        first_day = datetime(year, month, 1)
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)

        print(f"  Month boundaries: {first_day.strftime('%Y-%m-%d')} to {last_day.strftime('%Y-%m-%d')}")
        print(f"  Total days in month: {(last_day - first_day).days + 1}")

        # Sort changes by date
        changes.sort(key=lambda x: x['change_date'])

        # Handle initial period (before first change)
        first_change = changes[0]
        initial_from = first_day
        initial_to = first_change['change_date'] - timedelta(days=1)
        initial_days = self.calculate_working_days(initial_from, initial_to)

        if initial_days > 0:
            periods.append({
                'salary': first_change['old_salary'],
                'from_date': initial_from,
                'to_date': initial_to,
                'days': initial_days
            })
            print(
                f"  Initial period: ${first_change['old_salary']:,.2f} from {initial_from.strftime('%Y-%m-%d')} to {initial_to.strftime('%Y-%m-%d')} = {initial_days} working days")

        # Add periods for each change
        for i, change in enumerate(changes):
            from_date = change['change_date']

            # Determine to_date
            if i < len(changes) - 1:
                # Next change is the to_date
                next_change = changes[i + 1]
                to_date = next_change['change_date'] - timedelta(days=1)
            else:
                # Last change goes to end of month
                to_date = last_day

            period_days = self.calculate_working_days(from_date, to_date)
            if period_days > 0:
                periods.append({
                    'salary': change['new_salary'],
                    'change_date': change['change_date'],
                    'from_date': from_date,
                    'to_date': to_date,
                    'days': period_days
                })
                print(
                    f"  Change {i + 1}: ${change['new_salary']:,.2f} from {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')} = {period_days} working days")

        # If no periods created (shouldn't happen), create one period for the whole month
        if not periods:
            total_days = self.calculate_working_days(first_day, last_day)
            periods.append({
                'salary': employee['salary'],
                'from_date': first_day,
                'to_date': last_day,
                'days': total_days
            })
            print(f"  Single period: ${employee['salary']:,.2f} for {total_days} days")

        print(f"  Total periods: {len(periods)}")

        # Calculate total working days
        total_working_days = sum(p['days'] for p in periods)
        print(f"  Total working days in all periods: {total_working_days}")

        return periods

    def calculate_working_days(self, from_date, to_date):
        """Calculate exact working days between two dates (inclusive)"""
        if not from_date or not to_date or from_date > to_date:
            print(f"  ERROR: Invalid dates - from_date: {from_date}, to_date: {to_date}")
            return 0

        # Calculate exact working days (Monday-Friday)
        total_calendar_days = (to_date - from_date).days + 1

        # Count each day, check if it's a weekend (Monday=0, Sunday=6)
        working_days = 0
        weekend_days = 0
        for i in range(total_calendar_days):
            current_date = from_date + timedelta(days=i)
            # Monday=0, Friday=4, Saturday=5, Sunday=6
            if current_date.weekday() < 5:  # Monday to Friday
                working_days += 1
            else:
                weekend_days += 1

        print(
            f"    {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}: {total_calendar_days} calendar days, {working_days} working days, {weekend_days} weekend days")

        return working_days

    def validate_and_update(self):
        """Validate days allocation and update summary"""
        self.update_summary()
        return self.validate_days()

    def update_summary(self):
        """Update the summary label"""
        employee_totals = {}
        employee_names = {}

        # Collect data from ALL rows
        for row in range(self.adjustment_table.rowCount()):
            # Get employee ID from column 0
            emp_id_item = self.adjustment_table.item(row, 0)
            # Get employee name from column 1
            name_item = self.adjustment_table.item(row, 1)
            # Get days spinbox from column 6
            days_spin = self.adjustment_table.cellWidget(row, 6)

            # Check if all data is present
            if emp_id_item and name_item and days_spin:
                emp_id = emp_id_item.text()
                emp_name = name_item.text()

                if emp_id and emp_name:
                    if emp_id not in employee_totals:
                        employee_totals[emp_id] = 0
                        employee_names[emp_id] = emp_name

                    employee_totals[emp_id] += days_spin.value()

        # Build summary text
        if employee_totals:
            summary_text = "Days allocated per employee:\n"
            all_valid = True

            for emp_id, total_days in employee_totals.items():
                status = "✓" if total_days == self.total_working_days else "✗"
                if total_days != self.total_working_days:
                    all_valid = False

                emp_name = employee_names.get(emp_id, emp_id)
                summary_text += f"  {emp_name}: {total_days}/{self.total_working_days} days {status}\n"

            # Add overall status
            if all_valid:
                summary_text += f"\n✅ All employees have exactly {self.total_working_days} days allocated."
            else:
                summary_text += f"\n⚠️ Some employees don't have {self.total_working_days} days allocated."
        else:
            summary_text = "No data available."

        self.summary_label.setText(summary_text)
        return all_valid

    def validate_days(self):
        """Validate that days sum equals total working days for each employee"""
        employee_totals = {}
        employee_names = {}
        invalid_employees = []

        # Collect data from ALL rows
        for row in range(self.adjustment_table.rowCount()):
            # Get employee ID from column 0
            emp_id_item = self.adjustment_table.item(row, 0)
            # Get employee name from column 1
            name_item = self.adjustment_table.item(row, 1)
            # Get days spinbox from column 6
            days_spin = self.adjustment_table.cellWidget(row, 6)

            # Check if all data is present
            if emp_id_item and name_item and days_spin:
                emp_id = emp_id_item.text()
                emp_name = name_item.text()

                if emp_id and emp_name:
                    if emp_id not in employee_totals:
                        employee_totals[emp_id] = 0
                        employee_names[emp_id] = emp_name

                    employee_totals[emp_id] += days_spin.value()

        # Check each employee
        for emp_id, total_days in employee_totals.items():
            if total_days != self.total_working_days:
                emp_name = employee_names.get(emp_id, emp_id)
                invalid_employees.append(f"{emp_name}: {total_days} days (should be {self.total_working_days})")

        if invalid_employees:
            self.validation_label.setText(
                f"ERROR: Days must sum to {self.total_working_days} for all employees!\n"
                f"Invalid:\n" + "\n".join(f"  • {emp}" for emp in invalid_employees)
            )
            return False
        else:
            self.validation_label.setText(f"✅ All employees have exactly {self.total_working_days} days allocated.")
            return True

    def auto_calculate_days(self):
        """Automatically calculate days based on change dates"""
        # Create a mapping of employee data by ID
        employee_data_by_id = {}
        for emp_data in self.employees:
            employee = emp_data['employee']
            employee_data_by_id[employee['id']] = emp_data

        # For each row, recalculate based on the employee's changes
        for row in range(self.adjustment_table.rowCount()):
            emp_id_item = self.adjustment_table.item(row, 0)
            if not emp_id_item:
                continue

            employee_id = emp_id_item.text()

            if employee_id in employee_data_by_id:
                emp_data = employee_data_by_id[employee_id]
                employee = emp_data['employee']
                changes = emp_data['changes']

                periods = self.create_periods_for_employee(employee, changes)

                # Get period index from column 3
                period_item = self.adjustment_table.item(row, 3)
                if period_item:
                    try:
                        period_idx = int(period_item.text()) - 1
                        if period_idx < len(periods):
                            days_spin = self.adjustment_table.cellWidget(row, 6)
                            if days_spin:
                                days_spin.setValue(periods[period_idx].get('days', 0))
                    except ValueError:
                        continue

        self.validate_and_update()

    def calculate_proportional_salaries(self):
        """Calculate proportional salaries based on working days"""
        if not self.validate_days():
            QMessageBox.warning(self, "Validation Error",
                                f"Please ensure days sum to {self.total_working_days} for all employees.")
            return

        self.adjustments = {}
        employee_periods = {}
        employee_names = {}

        # Collect all periods for each employee
        for row in range(self.adjustment_table.rowCount()):
            emp_id_item = self.adjustment_table.item(row, 0)
            name_item = self.adjustment_table.item(row, 1)
            salary_item = self.adjustment_table.item(row, 5)
            days_spin = self.adjustment_table.cellWidget(row, 6)

            if not emp_id_item or not name_item or not salary_item or not days_spin:
                continue

            emp_id = emp_id_item.text()
            emp_name = name_item.text()
            salary_str = salary_item.text().replace('$', '').replace(',', '')

            try:
                salary = float(salary_str) if salary_str else 0
                days = days_spin.value()

                if emp_id not in employee_periods:
                    employee_periods[emp_id] = []
                    employee_names[emp_id] = emp_name

                employee_periods[emp_id].append({
                    'salary': salary,
                    'days': days
                })
            except ValueError:
                continue

        # Calculate proportional salary for each employee
        for emp_id, periods in employee_periods.items():
            total_weighted = 0
            total_days = 0

            for period in periods:
                total_weighted += period['salary'] * period['days']
                total_days += period['days']

            if total_days > 0:
                proportional_salary = total_weighted / total_days

                self.adjustments[emp_id] = {
                    'proportional_salary': proportional_salary,
                    'employee_name': employee_names[emp_id],
                    'periods': periods,
                    'total_days': total_days,
                    'total_weighted': total_weighted
                }
                print(
                    f"DEBUG: Calculated proportional salary for {employee_names[emp_id]}: ${proportional_salary:,.2f}")

        if self.adjustments:
            self.accept()
        else:
            QMessageBox.warning(self, "No Data", "No salary adjustments were calculated.")

    def get_adjustments(self):
        return self.adjustments

    def get_month_from_employee_data(self):
        """Extract month from employee data if available"""
        if self.employees and len(self.employees) > 0:
            # Check if we can get month from changes
            first_change = self.employees[0]['changes'][0] if self.employees[0]['changes'] else None
            if first_change:
                return first_change['change_date'].month
        return None

    def get_year_from_employee_data(self):
        """Extract year from employee data if available"""
        if self.employees and len(self.employees) > 0:
            # Check if we can get year from changes
            first_change = self.employees[0]['changes'][0] if self.employees[0]['changes'] else None
            if first_change:
                return first_change['change_date'].year
        return None

    def debug_print_table_contents(self):
        """Print table contents for debugging"""
        print(f"\nDEBUG: Table has {self.adjustment_table.rowCount()} rows")
        for row in range(self.adjustment_table.rowCount()):
            emp_id = self.adjustment_table.item(row, 0).text() if self.adjustment_table.item(row, 0) else "EMPTY"
            name = self.adjustment_table.item(row, 1).text() if self.adjustment_table.item(row, 1) else "EMPTY"
            days_spin = self.adjustment_table.cellWidget(row, 6)
            days = days_spin.value() if days_spin else "NO_SPIN"
            print(f"Row {row}: ID={emp_id}, Name={name}, Days={days}")