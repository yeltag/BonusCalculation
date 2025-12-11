import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QSpinBox, QGroupBox, QScrollArea,
    QWidget, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator, QValidator
from datetime import datetime
from bonus_calculator import BonusCalculator
import math


class VariableEntryDialog(QDialog):
    def __init__(self, parent=None, database=None, config_manager=None):
        super().__init__(parent)
        self.database = database
        self.config_manager = config_manager
        self.employees = []
        self.custom_variables = []
        self.variable_data_types = {}  # Store data types for each variable
        self.selected_department = "All Departments"  # Default filter
        self._loading = False  # Add this flag to prevent recursion
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setWindowTitle("Enter Variable Values - Monthly")
        self.setFixedSize(1200, 700)

        layout = QVBoxLayout()

        # Period Selection
        period_group = QGroupBox("Period and Department Selection")
        period_layout = QHBoxLayout()

        period_layout.addWidget(QLabel("Period:"))

        self.month_combo = QComboBox()
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        self.month_combo.addItems(months)
        self.month_combo.setCurrentIndex(datetime.now().month - 1)
        period_layout.addWidget(self.month_combo)

        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2030)
        self.year_spin.setValue(datetime.now().year)
        period_layout.addWidget(self.year_spin)

        period_layout.addWidget(QLabel("Department:"))
        self.dept_combo = QComboBox()
        self.dept_combo.addItem("All Departments")
        departments = self.config_manager.get_departments()
        self.dept_combo.addItems(departments)
        self.dept_combo.currentTextChanged.connect(self.on_department_changed)
        period_layout.addWidget(self.dept_combo)

        period_layout.addStretch()

        load_btn = QPushButton("Load Data")
        load_btn.clicked.connect(self.load_data)
        period_layout.addWidget(load_btn)

        period_group.setLayout(period_layout)
        layout.addWidget(period_group)

        # Instructions
        info_label = QLabel(
            "Enter monthly values for custom variables. Only variables used in KPIs applicable to each employee are shown. "
            "Use the department filter to focus on specific departments."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background-color: #e6f3ff; padding: 8px; border-radius: 4px;")
        layout.addWidget(info_label)

        # Employee count label
        self.employee_count_label = QLabel()
        layout.addWidget(self.employee_count_label)

        # Create a scroll area for the table to handle many columns
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Variables Table Container
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)

        # Variables Table
        self.variables_table = QTableWidget()
        self.variables_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.variables_table)

        scroll_area.setWidget(table_container)
        layout.addWidget(scroll_area)

        # Buttons
        button_layout = QHBoxLayout()

        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save All Values")
        save_btn.clicked.connect(self.save_all_values)
        button_layout.addWidget(save_btn)

        self.calculate_bonus_btn = QPushButton("Calculate Bonuses")
        self.calculate_bonus_btn.clicked.connect(self.on_calculate_bonuses_clicked)
        self.calculate_bonus_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        button_layout.addWidget(self.calculate_bonus_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_department_changed(self, department):
        """Handle department filter change"""
        self.selected_department = department
        self.load_data()

    def load_data(self):
        """Load employees, variables, and setup the table"""
        # Check if we're already in the middle of loading
        if hasattr(self, '_loading') and self._loading:
            return

        self._loading = True
        try:
            # Clear current table first
            self.variables_table.clear()
            self.variables_table.setRowCount(0)
            self.variables_table.setColumnCount(0)

            # Load data
            self.employees = self.database.get_all_employees()
            self.custom_variables = self.database.get_custom_variables()

            # Build variable data type dictionary
            self.variable_data_types.clear()
            for var in self.custom_variables:
                var_name = var.get('name')
                var_display_name = var.get('display_name', var_name)
                data_type = var.get('data_type', 'number')
                default_value = var.get('default_value', '0')
                self.variable_data_types[var_name] = {
                    'display_name': var_display_name,
                    'data_type': data_type,
                    'default_value': default_value  # Store default value here
                }

            month = self.month_combo.currentIndex() + 1
            year = self.year_spin.value()

            # Get applicable variables for each employee
            self.employee_applicable_variables = {}
            kpis = self.config_manager.get_kpis()

            for employee in self.employees:
                # Apply department filter
                if self.selected_department != "All Departments" and employee['department'] != self.selected_department:
                    continue

                applicable_vars = self.get_applicable_variables_for_employee(employee, kpis)
                self.employee_applicable_variables[employee['id']] = applicable_vars

            # Setup table
            self.setup_variables_table(month, year)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")
        finally:
            self._loading = False

    def get_applicable_variables_for_employee(self, employee, kpis):
        """Get variables used in KPIs applicable to this employee"""
        applicable_vars = {}

        for kpi in kpis:
            # Check if KPI applies to employee's department
            applicable_depts = kpi.get('applicable_departments', [])
            if not applicable_depts or employee['department'] in applicable_depts:
                # Check which variables are used in this KPI's formula
                formula = kpi.get('formula', '')
                for var in self.custom_variables:
                    var_name = var['name']
                    if var_name in formula:
                        applicable_vars[var_name] = var  # Store the whole variable object

        return applicable_vars

    def setup_variables_table(self, month, year):
        """Setup the variables entry table"""
        # Clear existing table completely
        self.variables_table.clear()
        self.variables_table.setRowCount(0)
        self.variables_table.setColumnCount(0)

        # Get filtered employees based on department
        filtered_employees = []
        for employee in self.employees:
            if self.selected_department == "All Departments" or employee['department'] == self.selected_department:
                filtered_employees.append(employee)

        # Update employee count
        total_employees = len(filtered_employees)
        self.employee_count_label.setText(
            f"Showing {total_employees} employees from {self.selected_department}"
        )

        # Get all unique variables used by any employee in the filtered list
        all_variables = {}
        for employee_id, vars_dict in self.employee_applicable_variables.items():
            for var_name, var_info in vars_dict.items():
                if var_name not in all_variables:
                    all_variables[var_name] = var_info

        # Sort variables by display name
        sorted_variables = sorted(all_variables.items(), key=lambda x: x[1].get('display_name', x[0]))

        # Set table dimensions
        self.variables_table.setRowCount(len(filtered_employees))
        self.variables_table.setColumnCount(3 + len(sorted_variables))

        # Set headers
        headers = ["Employee ID", "Name", "Department"]
        for var_name, var_info in sorted_variables:
            display_name = var_info.get('display_name', var_name)
            data_type = var_info.get('data_type', 'number')
            headers.append(f"{display_name} ({data_type})")
        self.variables_table.setHorizontalHeaderLabels(headers)

        # Set fixed column widths for better control
        header = self.variables_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Department

        # Set specific widths for fixed columns
        self.variables_table.setColumnWidth(0, 100)  # ID column
        self.variables_table.setColumnWidth(1, 150)  # Name column
        self.variables_table.setColumnWidth(2, 120)  # Department column

        # Variable columns - resize to content but with minimum width
        for col in range(3, 3 + len(sorted_variables)):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
            # Set minimum width for variable columns
            self.variables_table.setColumnWidth(col, 100)

        # Populate employee data and variable inputs
        for row, employee in enumerate(filtered_employees):
            # Basic employee info
            self.variables_table.setItem(row, 0, QTableWidgetItem(employee['id']))
            self.variables_table.setItem(row, 1, QTableWidgetItem(
                f"{employee['first_name']} {employee['last_name']}"
            ))
            self.variables_table.setItem(row, 2, QTableWidgetItem(employee['department']))

            # Make basic info read-only
            for col in range(3):
                item = self.variables_table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            # Variable value inputs
            applicable_vars = self.employee_applicable_variables.get(employee['id'], {})

            for col_idx, (var_name, var_info) in enumerate(sorted_variables, 3):
                if var_name in applicable_vars:
                    var_data_type = var_info.get('data_type', 'number')

                    # Use QLineEdit for input
                    line_edit = QLineEdit()
                    line_edit.setFixedWidth(90)
                    line_edit.setStyleSheet("QLineEdit { padding: 2px; margin: 1px; }")

                    # Set placeholder based on data type
                    if var_data_type == 'percentage':
                        line_edit.setPlaceholderText("e.g., 85% or 0.85")
                    elif var_data_type == 'currency':
                        line_edit.setPlaceholderText("e.g., 1000.50")
                    else:
                        line_edit.setPlaceholderText("Enter value")

                    # Set validator based on data type
                    if var_data_type in ['number', 'percentage', 'currency']:
                        validator = CustomDoubleValidator()
                        validator.setDecimals(2)
                        validator.setBottom(-9999999)
                        validator.setTop(9999999)
                        line_edit.setValidator(validator)
                    # For text type, no validator needed

                    # Load existing value from database
                    existing_value = self.database.get_employee_variable_value(
                        employee['id'], var_name, year, month
                    )

                    if existing_value is not None:
                        # Format the saved value for display
                        display_value = self.format_value_for_display(existing_value, var_data_type)
                        line_edit.setText(display_value)
                        line_edit.setStyleSheet("QLineEdit { background-color: #e6ffe6; }")
                    else:
                        # Use default value from variable definition
                        default_val = self.variable_data_types.get(var_name, {}).get('default_value', '0')
                        if default_val and str(default_val).strip():
                            # Format default value for display
                            display_value = self.format_value_for_display(default_val, var_data_type)
                            line_edit.setText(display_value)
                        else:
                            # Set empty for no default value
                            line_edit.setText("")

                    # Store data type and var name in line edit properties
                    line_edit.setProperty('data_type', var_data_type)
                    line_edit.setProperty('var_name', var_name)

                    # Connect signals for saving
                    line_edit.editingFinished.connect(
                        lambda r=row, c=col_idx, le=line_edit: self.on_line_edit_finished(r, c, le)
                    )

                    line_edit.returnPressed.connect(
                        lambda r=row, c=col_idx, le=line_edit: self.on_line_edit_return_pressed(r, c, le)
                    )

                    self.variables_table.setCellWidget(row, col_idx, line_edit)
                else:
                    # Variable not applicable - show as disabled
                    item = QTableWidgetItem("N/A")
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    item.setBackground(Qt.GlobalColor.lightGray)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.variables_table.setItem(row, col_idx, item)

    def format_value_for_display(self, value, data_type):
        """Format value for display based on data type"""
        if value is None or str(value).strip() == '':
            return ""

        value_str = str(value).strip()

        try:
            if data_type == 'percentage':
                # Convert decimal to percentage for display
                float_val = float(value_str)
                return f"{float_val * 100:.2f}%"
            elif data_type == 'currency':
                float_val = float(value_str)
                return f"${float_val:,.2f}"
            elif data_type == 'number':
                float_val = float(value_str)
                return f"{float_val:.2f}"
            else:  # text
                return value_str
        except (ValueError, TypeError):
            # If conversion fails, return original string
            return value_str

    def parse_input_for_storage(self, input_text, data_type):
        """Parse input text for storage based on data type"""
        input_text = str(input_text).strip()

        if not input_text:
            # Return empty string for text, "0" for numeric types
            if data_type == 'text':
                return ''
            else:
                return '0'

        if data_type == 'percentage':
            # Remove % sign if present
            clean_text = input_text.replace('%', '')
            try:
                float_val = float(clean_text)

                # Check if input had % sign
                had_percent_sign = '%' in input_text

                if had_percent_sign:
                    # User entered with % sign (e.g., "0.5%" or "50%")
                    # Convert to decimal: 0.5% → 0.005, 50% → 0.5
                    return str(float_val / 100.0)
                else:
                    # User entered without % sign
                    # If value <= 1, assume it's already decimal (0.5 → 0.5)
                    # If value > 1, assume it's percentage (85 → 0.85)
                    if float_val > 1.0:
                        return str(float_val / 100.0)
                    else:
                        return str(float_val)
            except ValueError:
                return '0'

        elif data_type == 'currency':
            # Remove $ and commas
            clean_text = input_text.replace('$', '').replace(',', '')
            try:
                float_val = float(clean_text)
                return str(float_val)
            except ValueError:
                return '0'

        elif data_type == 'number':
            try:
                float_val = float(input_text)
                return str(float_val)
            except ValueError:
                return '0'

        else:  # text
            return input_text

    def save_all_values(self):
        """Save all variable values"""
        try:
            month = self.month_combo.currentIndex() + 1
            year = self.year_spin.value()

            saved_count = 0

            for row in range(self.variables_table.rowCount()):
                employee_id_item = self.variables_table.item(row, 0)
                if not employee_id_item:
                    continue

                employee_id = employee_id_item.text()

                for col in range(3, self.variables_table.columnCount()):
                    widget = self.variables_table.cellWidget(row, col)
                    if widget and isinstance(widget, QLineEdit):
                        data_type = widget.property('data_type')
                        var_name = widget.property('var_name')

                        if data_type and var_name:
                            input_text = widget.text()
                            value_for_storage = self.parse_input_for_storage(input_text, data_type)

                            # Save to database
                            value_data = {
                                "employee_id": employee_id,
                                "variable_name": var_name,
                                "period_year": year,
                                "period_month": month,
                                "value": value_for_storage
                            }

                            if self.database.save_employee_variable_value(value_data):
                                saved_count += 1

                                # Update display to show formatted value
                                display_value = self.format_value_for_display(value_for_storage, data_type)
                                widget.setText(display_value)

            QMessageBox.information(self, "Success",
                                    f"Saved {saved_count} variable values for {self.variables_table.rowCount()} employees!")

            # Reload to show updated values
            self.load_data()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save values: {str(e)}")

    def set_period(self, year, month):
        """Set the period for variable entry"""
        self.year_spin.setValue(year)
        self.month_combo.setCurrentIndex(month - 1)
        self.load_data()

    def set_department_filter(self, department):
        """Set department filter"""
        if department != "All Departments":
            index = self.dept_combo.findText(department)
            if index >= 0:
                self.dept_combo.setCurrentIndex(index)
        else:
            self.dept_combo.setCurrentIndex(0)

    def on_calculate_bonuses_clicked(self):
        """Handle Calculate Bonuses button click"""
        month = self.month_combo.currentIndex() + 1
        year = self.year_spin.value()
        department = self.dept_combo.currentText()

        calculator = BonusCalculator(self.database, self.config_manager)
        results = calculator.validate_and_calculate_bonuses(year, month, department, self)

        if results is not None and results is not False:
            self.redirect_to_main_window(year, month, department, results)

    def redirect_to_main_window(self, year, month, department, results):
        """Redirect to main window and display results"""
        try:
            main_window = self.find_main_window()
            if main_window:
                self.accept()  # Close variable entry dialog
                main_window.show_bonus_calculation()
                main_window.calc_year_spin.setValue(year)
                main_window.calc_month_combo.setCurrentIndex(month - 1)

                index = main_window.calc_dept_combo.findText(department)
                if index >= 0:
                    main_window.calc_dept_combo.setCurrentIndex(index)

                main_window.calculate_bonuses(pre_calculated_results=results)
            else:
                QMessageBox.warning(self, "Error", "Cannot find main window")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to redirect: {str(e)}")

    def find_main_window(self):
        """Find the main window parent"""
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'show_bonus_calculation') and hasattr(parent, 'calculate_bonuses'):
                return parent
            parent = parent.parent()
        return None

    def on_line_edit_finished(self, row, col, line_edit):
        """Handle when line edit loses focus"""
        self.save_cell_value(row, col, line_edit.text())

    def on_line_edit_return_pressed(self, row, col, line_edit):
        """Handle when Enter is pressed in line edit"""
        # Clear focus to trigger editingFinished
        line_edit.clearFocus()
        self.save_cell_value(row, col, line_edit.text())

    def save_cell_value(self, row, col, text_value):
        """Save a cell value to database"""
        widget = self.variables_table.cellWidget(row, col)
        if not widget or not isinstance(widget, QLineEdit):
            return

        data_type = widget.property('data_type')
        var_name = widget.property('var_name')

        if not data_type or not var_name:
            return

        employee_id_item = self.variables_table.item(row, 0)
        if not employee_id_item:
            return

        employee_id = employee_id_item.text()

        month = self.month_combo.currentIndex() + 1
        year = self.year_spin.value()

        # Parse input based on data type
        value_for_storage = self.parse_input_for_storage(text_value, data_type)

        value_data = {
            "employee_id": employee_id,
            "variable_name": var_name,
            "period_year": year,
            "period_month": month,
            "value": value_for_storage
        }

        if self.database.save_employee_variable_value(value_data):
            # Update display with formatted value
            display_value = self.format_value_for_display(value_for_storage, data_type)
            widget.setText(display_value)
            widget.setStyleSheet("QLineEdit { background-color: #e6ffe6; }")


class CustomDoubleValidator(QDoubleValidator):
    def validate(self, input_str, pos):
        # Allow empty input
        if not input_str:
            return (QValidator.State.Acceptable, input_str, pos)

        # Try to convert to float
        try:
            # Replace comma with dot for conversion
            test_str = input_str.replace(',', '.')
            # Remove $ and % for validation (they can be present for display)
            test_str = test_str.replace('$', '').replace('%', '')
            value = float(test_str)

            # Check range
            if self.bottom() <= value <= self.top():
                return (QValidator.State.Acceptable, input_str, pos)
            else:
                return (QValidator.State.Invalid, input_str, pos)
        except ValueError:
            return (QValidator.State.Invalid, input_str, pos)

