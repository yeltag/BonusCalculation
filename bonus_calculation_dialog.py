import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QComboBox, QSpinBox,
    QGroupBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt
from datetime import datetime
from bonus_calculator import BonusCalculator
from variable_entry_dialog import VariableEntryDialog


class BonusCalculationDialog(QDialog):
    def __init__(self, parent=None, database=None, config_manager=None):
        super().__init__(parent)
        self.database = database
        self.config_manager = config_manager
        self.setWindowTitle("Bonus Calculation")
        self.setFixedSize(1200, 700)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Create tabs
        self.tabs = QTabWidget()

        # Tab 1: Enter Variable Values
        self.setup_variables_tab()

        # Tab 2: Calculate Bonuses
        self.setup_calculation_tab()

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def setup_variables_tab(self):
        """Setup the variable entry tab"""
        variables_tab = QWidget()
        layout = QVBoxLayout()

        # Period selection
        period_group = QGroupBox("Calculation Period")
        period_layout = QHBoxLayout()

        period_layout.addWidget(QLabel("Month:"))
        self.vars_month_combo = QComboBox()
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        self.vars_month_combo.addItems(months)
        self.vars_month_combo.setCurrentIndex(datetime.now().month - 1)
        period_layout.addWidget(self.vars_month_combo)

        period_layout.addWidget(QLabel("Year:"))
        self.vars_year_spin = QSpinBox()
        self.vars_year_spin.setRange(2020, 2030)
        self.vars_year_spin.setValue(datetime.now().year)
        period_layout.addWidget(self.vars_year_spin)

        period_layout.addStretch()

        # Department filter
        period_layout.addWidget(QLabel("Department:"))
        self.vars_dept_combo = QComboBox()
        self.vars_dept_combo.addItem("All Departments")
        departments = self.config_manager.get_departments()
        self.vars_dept_combo.addItems(departments)
        period_layout.addWidget(self.vars_dept_combo)

        period_group.setLayout(period_layout)
        layout.addWidget(period_group)

        # Open variable entry button
        open_vars_btn = QPushButton("Open Variable Entry Form")
        open_vars_btn.clicked.connect(self.open_variable_entry_form)
        layout.addWidget(open_vars_btn)

        layout.addStretch()
        variables_tab.setLayout(layout)
        self.tabs.addTab(variables_tab, "Enter Variable Values")

    def setup_calculation_tab(self):
        """Setup the bonus calculation tab"""
        calculation_tab = QWidget()
        layout = QVBoxLayout()

        # Period selection
        period_group = QGroupBox("Calculation Period")
        period_layout = QHBoxLayout()

        period_layout.addWidget(QLabel("Month:"))
        self.calc_month_combo = QComboBox()
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        self.calc_month_combo.addItems(months)
        self.calc_month_combo.setCurrentIndex(datetime.now().month - 1)
        period_layout.addWidget(self.calc_month_combo)

        period_layout.addWidget(QLabel("Year:"))
        self.calc_year_spin = QSpinBox()
        self.calc_year_spin.setRange(2020, 2030)
        self.calc_year_spin.setValue(datetime.now().year)
        period_layout.addWidget(self.calc_year_spin)

        period_layout.addStretch()

        # Department filter
        period_layout.addWidget(QLabel("Department:"))
        self.calc_dept_combo = QComboBox()
        self.calc_dept_combo.addItem("All Departments")
        departments = self.config_manager.get_departments()
        self.calc_dept_combo.addItems(departments)
        period_layout.addWidget(self.calc_dept_combo)

        period_group.setLayout(period_layout)
        layout.addWidget(period_group)

        # Calculate button
        calculate_btn = QPushButton("Calculate Bonuses")
        calculate_btn.clicked.connect(self.calculate_bonuses)
        layout.addWidget(calculate_btn)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Employee ID", "Name", "Department", "Base Salary", "Bonus Amount", "Total"
        ])
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.results_table)

        calculation_tab.setLayout(layout)
        self.tabs.addTab(calculation_tab, "Calculate Bonuses")

    def open_variable_entry_form(self):
        """Open variable entry with current period and department"""
        month = self.vars_month_combo.currentIndex() + 1
        year = self.vars_year_spin.value()
        department = self.vars_dept_combo.currentText()

        # Create and configure variable entry dialog
        dialog = VariableEntryDialog(self, self.database, self.config_manager)

        # Set the period in the dialog (you'll need to add these methods to VariableEntryDialog)
        if hasattr(dialog, 'set_period'):
            dialog.set_period(year, month)
        if hasattr(dialog, 'set_department_filter'):
            dialog.set_department_filter(department)

        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            # Switch to calculation tab after saving variables
            self.tabs.setCurrentIndex(1)

    def calculate_bonuses(self):
        """Calculate bonuses using the centralized logic"""
        month = self.calc_month_combo.currentIndex() + 1
        year = self.calc_year_spin.value()
        department_filter = self.calc_dept_combo.currentText()

        # Use the centralized bonus calculator
        calculator = BonusCalculator(self.database, self.config_manager)
        results = calculator.calculate_bonuses_with_validation(year, month, department_filter, self)

        if results is not None:  # Only proceed if validation passed
            self.display_results(results)

    def display_results(self, results):
        """Display results in the table"""
        self.results_table.setRowCount(len(results))
        for row, result in enumerate(results):
            self.results_table.setItem(row, 0, QTableWidgetItem(result["employee_id"]))
            self.results_table.setItem(row, 1, QTableWidgetItem(result["employee_name"]))
            self.results_table.setItem(row, 2, QTableWidgetItem(result.get("department", "")))
            self.results_table.setItem(row, 3, QTableWidgetItem(f"{result['base_salary']:,.2f}"))
            self.results_table.setItem(row, 4, QTableWidgetItem(f"{result['calculated_bonus']:,.2f}"))
            total = result["base_salary"] + result["calculated_bonus"]
            self.results_table.setItem(row, 5, QTableWidgetItem(f"{total:,.2f}"))

        QMessageBox.information(self, "Calculation Complete",
                                f"Calculated bonuses for {len(results)} employees")