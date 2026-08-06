import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
                             QPushButton, QComboBox, QListWidget, QListWidgetItem, QMessageBox,
                             QGroupBox, QSplitter, QFrame, QScrollArea, QDialogButtonBox, QDateEdit, QTableWidgetItem)

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QPalette
import re
from employees_selection_for_kpi import EmployeeSelectionForKPI
from datetime import datetime
from new_page_template import NewPageTemplate
from database import Database
import json



class FormulaHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for KPI formulas"""

    def __init__(self, document):
        super().__init__(document)

        # Define formatting rules
        self.highlighting_rules = []

        # Variable format (blue) - only base_salary
        variable_format = QTextCharFormat()
        variable_format.setForeground(QColor(0, 0, 255))
        variable_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((r'\b(base_salary)\b', variable_format))

        # Operator format (red)
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor(255, 0, 0))
        operator_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((r'[+\-*/=<>!&|]', operator_format))

        # Number format (green)
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(0, 128, 0))
        self.highlighting_rules.append((r'\b\d+\.?\d*\b', number_format))

        # Function format (purple)
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(128, 0, 128))
        function_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((r'\b(if|else|min|max|sum|avg)\b', function_format))

    def highlightBlock(self, text):
        """Apply syntax highlighting to the current text block"""
        for pattern, format in self.highlighting_rules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)

class KPIEditorDialog(QDialog):
    def __init__(self, parent = None, kpi_data = None, config_manager = None, database = None,username = None):
        super().__init__(parent)
        self.kpi_data = kpi_data or {}
        self.config_manager = config_manager
        self.username = username
        self.database = database
        self.employee_selection = EmployeeSelectionForKPI
        self.is_edit_mode = kpi_data is not None
        self.selected_departments = self.database.get_kpi_departments(self.kpi_data['id']) if (self.kpi_data and self.kpi_data['id']) else []
        print("self.selected-departments: ",self.selected_departments)
        self.selected_employees = self.database.get_kpi_employees(self.kpi_data['id']) if (self.kpi_data and self.kpi_data['id']) else []
        print("self.selected_employees: ",self.selected_employees)

        # If database is None, try to get it from parent (ConfigDialog)
        if self.database is None and parent is not None:
            if hasattr(parent, 'database'):
                self.database = parent.database

            elif hasattr(parent, 'config_manager') and hasattr(parent.config_manager, 'database'):
                self.database = parent.config_manager.database


        self.is_edit_mode = kpi_data is not None
        self.order_required = False

        if self.is_edit_mode:
            self.setWindowTitle("Edit KPI formula")
        else:
            self.setWindowTitle("Create New KPI Formula")

        self.setup_ui()
        self.setFixedSize(900,650)
        self.resize(1000,700)
        if self.is_edit_mode:

            QTimer.singleShot(100, self.show_edit_mode_warning)


    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Formula builder
        left_panel = self.create_formula_panel()
        splitter.addWidget(left_panel)

        # Right panel: Variable and functions
        right_panel = self.create_variables_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([600,400])

        # Set stretch factors to make left panel more important
        splitter.setStretchFactor(0, 2)  # Left panel gets 2/3 of space
        splitter.setStretchFactor(1, 1)  # Right panel gets 1/3 of space

        main_layout.addWidget(splitter)

        # Buttons
        button_layout= QHBoxLayout()

        test_btn = QPushButton("Test Formula")
        test_btn.clicked.connect(self.test_formula)
        button_layout.addWidget(test_btn)

        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save KPI")
        save_btn.clicked.connect(self.validate_and_save)
        button_layout.addWidget(save_btn)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Load existing data if editing
        if self.is_edit_mode:
            self.load_existing_data()

    def show_edit_mode_warning(self):
        """Show warning about edit mode restrictions"""
        QMessageBox.warning(None,"You are in KPI edit mode","Only the 'Description' field and employee applicability list can be modified while in KPI edit mode.")


    def create_formula_panel(self):
        """Create the formula editing panel"""
        panel = QFrame()
        layout = QVBoxLayout()

        # KPI Basic information
        basic_group = QGroupBox("KPI Basic Information")
        basic_layout = QVBoxLayout()

        # name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("KPI Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Sales Performance Bonus")
        name_layout.addWidget(self.name_input)
        basic_layout.addLayout(name_layout)

        #Description
        basic_layout.addWidget(QLabel("Description:"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Brief Description of this KPI")
        basic_layout.addWidget(self.desc_input)

        # Calculation Method
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Calculation Method:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["formula","percentage","fixed"])
        self.method_combo.currentTextChanged.connect(self.on_method_changed)
        method_layout.addWidget(self.method_combo)
        basic_layout.addLayout(method_layout)

        #Selection status Label

        if self.is_edit_mode or self.selected_departments or self.selected_employees:
            self.selection_status_label = QLabel(f"Selected: {len(self.selected_departments)} department(s), {len(self.selected_employees)} employee(s)")
            self.selection_status_label.setStyleSheet("color: green;font-style: italic; margin-top: 5px;")
        else:
            self.selection_status_label = QLabel("⚠ No departments or employees selected")
            self.selection_status_label.setStyleSheet("color: orange; font-style: italic; margin-top: 5px;")
        basic_layout.addWidget(self.selection_status_label)

        select_emp = QPushButton("Select applicable employees")
        select_emp.clicked.connect(self.open_employee_selection)
        basic_layout.addWidget(select_emp)

        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)

        # Formula Editor
        formula_group = QGroupBox("Formula Editor")
        formula_layout = QVBoxLayout()

        formula_layout.addWidget(QLabel("Formula:"))

        self.formula_edit = QTextEdit()
        self.formula_edit.setPlaceholderText(
            "Enter formula using available variables and functions.\n"
            "Examples:\n"
            "• base_salary * 0.1  # 10% of base salary\n"
            "• base_salary * performance_rating * 0.05  # Performance-based\n"
            "• if sales_amount > 10000 then 500 else 200  # Conditional bonus\n\n"
            "Note: Only 'base_salary' is built-in. Other variables like\n"
            "'performance_rating', 'sales_amount', etc. must be created\n"
            "as custom variables in Configuration."
        )

        # Set monospace forn for formula editor
        font = QFont("Courier", 10)
        self.formula_edit.setFont(font)

        # Apply syntax highlighting
        self.highlighter = FormulaHighlighter(self.formula_edit.document())

        formula_layout.addWidget(self.formula_edit)

        #Simple method inputs (shown/hidden based on method)
        self.simple_inputs_layout = QHBoxLayout()
        self.simple_inputs_layout.addWidget(QLabel("percentage:"))
        self.percentage_input = QLineEdit()
        self.percentage_input.setPlaceholderText("0.1 for 10%")
        self.simple_inputs_layout.addWidget(self.percentage_input)

        self.simple_inputs_layout.addWidget(QLabel("Fixed Amount:"))
        self.fixed_input = QLineEdit()
        self.fixed_input.setPlaceholderText("e.g., 500")
        self.simple_inputs_layout.addWidget(self.fixed_input)

        formula_layout.addLayout(self.simple_inputs_layout)

        formula_group.setLayout(formula_layout)
        layout.addWidget(formula_group)

        panel.setLayout(layout)
        return panel

    def create_variables_panel(self):
        """Create the variables and functions panel"""


        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumWidth(400)  # Limit maximum width

        panel = QFrame()
        layout = QVBoxLayout()

        # Set spacing and margins to be more compact
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # Available Variables - ONLY base_salary is built-in
        vars_group = QGroupBox("Built-in Variables")
        vars_layout = QVBoxLayout()
        vars_layout.setSpacing(3)  # Reduced spacing between buttons

        # ONLY base_salary is truly built-in from employee data
        variables = [
            ("base_salary", "Employee's monthly base salary (from employee record)"),
        ]

        for var_name, var_desc in variables:
            var_btn = QPushButton(f"{var_name}")
            var_btn.setToolTip(var_desc)
            var_btn.setMaximumHeight(25)  # Set fixed height for buttons
            var_btn.clicked.connect(lambda checked, v=var_name: self.insert_variable(v))
            vars_layout.addWidget(var_btn)

        vars_group.setLayout(vars_layout)
        layout.addWidget(vars_group)

        # Custom Variables Section
        custom_vars_group = QGroupBox("Custom Variables")
        custom_vars_layout = QVBoxLayout()
        custom_vars_layout.setSpacing(3)

        custom_variables = []

        if self.database:  # Only if we have database access
            try:
                custom_variables = self.database.get_custom_variables()

                for i, var in enumerate(custom_variables):
                    print(f"  {i}: {var}")
            except Exception as e:

                # Add a label to show error or empty state
                error_label = QLabel("Unable to load custom variables")
                custom_vars_layout.addWidget(error_label)
        else:
            no_db_label = QLabel("No database connection")
            custom_vars_layout.addWidget(no_db_label)

        if not custom_variables:
            no_vars_label = QLabel("No custom variables defined.\nCreate them in Configuration → Custom Variables.")
            custom_vars_layout.addWidget(no_vars_label)
        else:
            for var in custom_variables:
                # Use get() method with default values to avoid KeyError
                display_name = var.get('display_name', var.get('name', 'Unknown'))
                description = var.get('description', 'No description available')
                data_type = var.get('data_type', 'unknown')
                default_value = var.get('default_value', 'Not set')

                var_btn = QPushButton(f"{display_name}")
                var_btn.setToolTip(f"{description}\nType: {data_type}\nDefault: {default_value}")
                var_btn.setMaximumHeight(25)  # Fixed height
                var_btn.clicked.connect(lambda checked, v=var.get('name', 'unknown'): self.insert_variable(v))
                custom_vars_layout.addWidget(var_btn)

        custom_vars_group.setLayout(custom_vars_layout)
        layout.addWidget(custom_vars_group)

        # Mathematical Functions
        funcs_group = QGroupBox("Functions")
        funcs_layout = QVBoxLayout()
        funcs_layout.setSpacing(3)

        functions = [
            ("min(x, y)", "Returns smaller of two values"),
            ("max(x, y)", "Returns larger of two values"),
            ("round(x, 2)", "Rounds to 2 decimal places"),
            ("if condition then x else y", "Conditional expression")
        ]

        for func_name, func_desc in functions:
            func_btn = QPushButton(func_name)
            func_btn.setToolTip(func_desc)
            func_btn.clicked.connect(lambda checked, f=func_name: self.insert_function(f))
            funcs_layout.addWidget(func_btn)

        funcs_group.setLayout(funcs_layout)
        layout.addWidget(funcs_group)

        # Formula Templates - Updated to only use base_salary
        templates_group = QGroupBox("Templates")
        templates_layout = QVBoxLayout()
        templates_layout.setSpacing(3)

        templates = [
            ("10% of Base Salary", "base_salary * 0.1"),
            ("Performance Based", "base_salary * performance_rating * 0.05"),
            ("Sales Commission", "sales_amount * 0.15"),
            ("Seniority Bonus", "base_salary * years_of_service * 0.02"),
            ("Conditional Bonus", "if sales_target > 10000 then 500 else 200")
        ]

        for template_name, template_formula in templates:
            template_btn = QPushButton(template_name)
            template_btn.setToolTip(template_formula)
            template_btn.setMaximumHeight(25)
            template_btn.clicked.connect(lambda checked, f=template_formula: self.insert_template(f))
            templates_layout.addWidget(template_btn)

        templates_group.setLayout(templates_layout)
        layout.addWidget(templates_group)

        # Add stretch to push everything to the top
        layout.addStretch()

        panel.setLayout(layout)
        scroll_area.setWidget(panel)
        return scroll_area


    def on_method_changed(self, method):
        """Show/hide simple inputs based on calculation method"""
        if method == "percentage":
            self.percentage_input.show()
            self.fixed_input.hide()
        elif method == "fixed":
            self.percentage_input.hide()
            self.fixed_input.show()
        else:  #formula
            self.percentage_input.hide()
            self.fixed_input.hide()

    def insert_variable(self, variable):
        """Insert a variable into the formula editor"""
        cursor = self.formula_edit.textCursor()
        cursor.insertText(variable)
        self.formula_edit.setFocus()

    def insert_function(self, function):
        """Insert a function into the formula editor"""
        cursor = self.formula_edit.textCursor()
        cursor.insertText(function)
        self.formula_edit.setFocus()

    def insert_template(self, template):
        """Insert a template formula"""
        self.formula_edit.setPlainText(template)
        self.formula_edit.setFocus()

    def load_existing_data(self):
        """Load existing KPI data into the form"""
        if not self.kpi_data:
            return

        self.name_input.setText(self.kpi_data.get("name",""))
        self.name_input.setReadOnly(True)
        self.name_input.setStyleSheet("color: gray")
        self.desc_input.setText(self.kpi_data.get("description",""))
        self.method_combo.setCurrentText(self.kpi_data.get("calculation_method","formula"))
        self.method_combo.setEnabled(False)
        self.method_combo.setStyleSheet("color: gray")

        # Set formula or simple values
        if self.kpi_data.get("calculation_method") == "percentage":
            self.percentage_input.setText(str(self.kpi_data.get("percentage","")))
            self.percentage_input.setReadOnly(True)
        elif self.kpi_data.get("calculation_method") == "fixed":
            self.fixed_input.setText(str(self.kpi_data.get("fixed_amount","")))
            self.fixed_input.setReadOnly(True)
        else:
            self.formula_edit.setPlainText(self.kpi_data.get("formula",""))
            self.formula_edit.setReadOnly(True)
            self.highlighter.setDocument(None)
            self.formula_edit.setStyleSheet("QTextEdit{color: gray}")


        # Select applicable deartments
        applicable_depts = self.kpi_data.get("applicable_departments",[])
        applicable_empls = self.kpi_data.get('applicable_employees',[])
        #for i in range(self.dept_list.count()):
            #pass
            # item = self.dept_list.item(i)
            # if item.text() in applicable_depts:
            #     item.setSelected(True)

    def test_formula(self):
        """Test the current formula with sample data"""
        formula = self.formula_edit.toPlainText().strip()
        if not formula:
            QMessageBox.warning(self,"Test Formula", "Please enter a formula to test.")

            return

        # Sample test data
        test_data = {
            "base_salary": 5000,
            "performance_rating": 4,
            "years_of_service": 3,
            "sales_amount": 15000,
            "completed_projects": 5,
            "attendance_rate": 0.95,
            "team_size": 8,
            "revenue_generated": 25000

        }

        try:

            # Safe formula evaluation
            result = self.safe_eval_formula(formula,test_data)
            formula1 = str(formula)
            for sign in ["+","-","*","/"]:
                formula1 = formula1.replace(sign," ")
            formula_list = formula1.split()

            custom_variables =[]

            if self.database:
                try:
                    custom_variables = self.database.get_custom_variables()
                except Exception as e:
                    print(f"Error loading custom variables for evaluation:{e}")

            msg_text = ''

            for i in formula_list[1:]:
                for j in custom_variables:
                    if j["name"] == i:

                        test_data[i]=j["default_value"]
                        msg_text = msg_text + f"{i}: {test_data[i]}\n"



            QMessageBox.information(self, "Formula Test",
                               f"Formula tested successfully!\n\n"
                                    f"test Data:\n"
                                    f"Base Salary: {test_data['base_salary']:,.2f}\n"
                                    f"{msg_text}"
                                    f"Result: {result}")

        except Exception as e:
            QMessageBox.warning(self, "Formula Error",
                                f"Formula contains errors:\n\n{str(e)}")

    def safe_eval_formula(self, formula, variables):
        """Safely evaluate a formula with given variables"""
        # Replace custom syntax with Python syntax
        formula = formula.replace(" then ", " if ").replace(" else ", " else ")

        # Create safe evaluation environment
        safe_dict = {
            "min": min,
            "max": max,
            "round": round,
            "sum": sum,
            "abs": abs,
            "__builtins__": {}
        }

        # Add base_salary from test data (if provided) or use default
        safe_dict.update(variables)

        # If base_salary not provided, use default
        if "base_salary" not in safe_dict:
            safe_dict["base_salary"] = 5000  # Default for testing

        # Add custom variables from database with their default values
        custom_variables = []
        if self.database:
            try:
                custom_variables = self.database.get_custom_variables()
            except Exception as e:
                print(f"Error loading custom variables for evaluation:{e}")

        for var in custom_variables:
            var_name = var.get('name')
            # Don't overwrite base_salary
            if var_name != "base_salary":
                data_type = var.get('data_type', 'number')
                if data_type in ['number', 'percentage', 'currency']:
                    try:
                        # Clean the value
                        default_val = var.get('default_value', '0')
                        clean_val = str(default_val).replace('$', '').replace(',', '').replace('%', '')
                        safe_dict[var_name] = float(clean_val) if clean_val else 0.0
                    except (ValueError, TypeError):
                        safe_dict[var_name] = 0.0
                else:
                    safe_dict[var_name] = var.get('default_value', '')

        # Evaluate the formula
        try:
            return eval(formula, {"__builtins__": {}}, safe_dict)
        except Exception as e:

            raise

    def validate_and_save(self):
        """Validate inputs and save KPI data"""
        # Get basic information
        name = self.name_input.text().strip()
        description = self.desc_input.text().strip()
        method = self.method_combo.currentText()

        # Validation
        errors = []
        if not name:
            errors.append("KPI name is required")

        # Get selected departments
        #selected_depts = [item.text() for item in self.dept_list.selectedItems()]
        #print("self.result: ",type(self.result) )
        #selected_depts = self.result["departments"]
        #selected_employees = self.result["employees"]

        # Prepare KPI data based on method
        kpi_data = {
            "name": name,
            "description": description,
            "calculation_method": method,
            "applicable_departments": [d['department_name'] for d in self.selected_departments],
            "applicable_employees": [e['employee_id'] for e in self.selected_employees],
            "weight": 1.0,  # Default weight
            "is_active": True,
            "created_by": self.username,

        }

        # PRESERVE THE ID IF WE'RE IN EDIT MODE
        if self.is_edit_mode and "id" in self.kpi_data:
            kpi_data["id"] = self.kpi_data["id"]


        if method == "percentage":
            try:
                percentage = float(self.percentage_input.text())
                kpi_data["percentage"] = percentage
                kpi_data["formula"] = f"base_salary * {percentage}"
            except ValueError:
                errors.append("Percentage must be a valid number")

        elif method == "fixed":
            try:
                fixed_amount = float(self.fixed_input.text())
                kpi_data["fixed_amount"] = fixed_amount
                kpi_data["formula"] = str(fixed_amount)
            except ValueError:
                errors.append("Fixed amount must be a valid number")

        else:  # formula method
            formula = self.formula_edit.toPlainText().strip()
            if not formula:
                errors.append("Formula is required for formula calculation method")
            else:

                try:
                    # Test with only base_salary (custom variables added automatically)
                    test_data = {"base_salary": 5000}
                    result = self.safe_eval_formula(formula, test_data)

                    kpi_data["formula"] = formula

                except Exception as e:

                    errors.append(f"Formula contains errors: {str(e)}")

        # Show errors if any
        if errors:
            error_msg = "Please fix the following errors:\n\n" + "\n".join(f"- {error}" for error in errors)
            QMessageBox.warning(self, "Validation Error", error_msg)
            return

        # Check if any departments or employees were selected
        if not self.selected_departments and not self.selected_employees:
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "No Applicability Selected",
                "This KPI has no departments or employees selected.\n\n"
                "It will be saved but won't apply to anyone.\n\n"
                "Do you want to:\n"
                "Click 'Yes' to save without applicability (can add later)\n"
                "Click 'No' to go back and select departments/employees",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,

                QMessageBox.StandardButton.No

            )

            if reply == QMessageBox.StandardButton.No:
                # User wants to select departments/employees
                self.open_employee_selection()
                return



        if self.order_required:
            order_reply = QMessageBox()
            order_reply.setWindowTitle("Order details required")
            order_reply.setText("New KPI applicability should be based on order.  Please, enter order details.")
            order_reply.setStandardButtons(QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
            yes_button = order_reply.button(QMessageBox.StandardButton.Yes)
            yes_button.setText("Add order")
            no_button = order_reply.button(QMessageBox.StandardButton.No)
            no_button.setText("Cancel")
            order_result = order_reply.exec()

            if order_result == QMessageBox.StandardButton.Yes:
                success = self.database.save_kpi_with_applicability(
                    kpi_data,
                    departments=self.selected_departments if self.selected_departments else None,
                    employees=self.selected_employees if self.selected_employees else None,

                    excluded_employees=None,
                    new_order = True,
                    username = self.username)

                if success:
                    self.kpi_data = kpi_data
                    self.accept()
                else:
                    QMessageBox.critical(self,"Save Error", "Failed to save KPI to database")

                self.kpi_applicability_order()

            else:
                print("Order cancelled")

        else:

            success = self.database.save_kpi_with_applicability(
                kpi_data,
                departments=self.selected_departments if self.selected_departments else None,
                employees=self.selected_employees if self.selected_employees else None,

                excluded_employees=None,
                new_order = False,
                username = self.username)

            if success:
                self.kpi_data = kpi_data
                self.accept()
            else:
                QMessageBox.critical(self, "Save Error", "Failed to save KPI to database")



    def get_kpi_data(self):
        """Return the KPI data"""
        return self.kpi_data

    def open_employee_selection(self,exclusion = False):
        """Open the employee selection dialog with existing selections"""
        # Covert selected_departments to the format expected by the dialog
        existing_depts = []
        for dept in self.selected_departments:
            existing_depts.append({
                "department_name": dept.get('department_name'),
                'start_date': dept.get('start_date'),
                'apply_to_all':dept.get('apply_to_all'),
                'check_state':dept.get('check_state'),
                'check_box_state':dept.get('check_box_state'),
                'end_date':dept.get('end_date'),
                'enddate_combobox':dept.get('enddate_combobox'),
                'enddate_check':dept.get('enddate_check'),
                'created_by':dept.get('created_by'),
                'version': dept.get('version')
            })
        existing_emps = []
        for emp in self.selected_employees:
            existing_emps.append({
                'employee_id': emp.get('employee_id'),
                'start_date':emp.get('start_date'),
                'check_state':emp.get('check_state'),
                'end_date':emp.get('end_date'),
                'combo_text':emp.get('combo_text'),
                'version':emp.get('version')
            })

        selection_dialog = EmployeeSelectionForKPI(

            existing_departments = existing_depts,
            existing_employees = existing_emps,
            exclusion = exclusion
        )

        #if hasattr(self, "selected_departments") and self.selected_departments:

            # Pass the existing selections to pre-populate the dialog
            #selection_dialog.set_selected_data(departments=self.selected_departments,
                                               #employees = self.selected_employees)

        selection_dialog.data_saved.connect(self.on_employee_data_saved)

        selection_dialog.exec()

    def load_existing_applicability(self):
        """Load existing department/employee selections for edit mode"""
        if self.database and self.kpi_data.get("id"):
            kpi_with_applicability = self.database.get_kpi_with_applicability(self.kpi_data['id'])
            if kpi_with_applicability:
                self.selected_departments = kpi_with_applicability.get("departments",[])
                self.selected_employees = kpi_with_applicability.get("employees",[])

    def on_employee_data_saved(self,data,order=False,dept_changes=[],emp_changes=[]):
        """Handle the saved employee selection data"""
        # Clear existing selections
        self.selected_departments = []
        self.selected_employees = []
        self.order_required = order
        self.dept_changes = dept_changes
        self.emp_changes = emp_changes

        # Process departments that are checked
        for dept_data in data.get('departments', []):

            #if dept_data.get('check_state') == Qt.CheckState.Checked.value:
            if dept_data.get('check_state') != 0:
                # Get the date properly
                date_value = dept_data.get('start_date')
                start_date = None

                if date_value:
                    # If it's a QDate object
                    if hasattr(date_value, 'toString'):
                        start_date = date_value.toString("yyyy-MM-dd")
                    # If it's a string already
                    elif isinstance(date_value, str):
                        start_date = date_value
                    # If it's something else, try to convert
                    else:
                        start_date = str(date_value)
                else:
                    start_date = datetime.now().strftime("%Y-%m-%d")

                # Get the checkbox state (Apply to all)
                check_box_state = dept_data.get('check_box_state')
                apply_to_all = False
                if check_box_state:
                    # Check if it's Qt.CheckState.Checked (value 2) or True
                    if check_box_state == Qt.CheckState.Checked or check_box_state == 2:
                        apply_to_all = True
                    elif hasattr(check_box_state, 'value'):
                        apply_to_all = check_box_state == Qt.CheckState.Checked


                self.selected_departments.append({
                    'check_state': dept_data.get('check_state'),
                    'department_name': dept_data.get('department'),
                    'start_date': start_date,  # Store as string
                    'end_date': dept_data.get('end_date'),
                    'apply_to_all': apply_to_all,
                    'check_box_state': check_box_state,
                    'version':dept_data.get('version'),
                    'enddate_combobox': dept_data.get('enddate_combobox'),
                    'enddate_check':dept_data.get('enddate_check')



                })

                # Process employees that are checked
                for emp_list in dept_data.get('employees', []):
                    #for emp_data in emp_list:
                    if emp_list.get('check_state') == 2:
                        date_value = emp_list.get('start_date')
                        start_date = None

                        if date_value:
                            if hasattr(date_value, 'toString'):
                                start_date = date_value.toString("yyyy-MM-dd")
                            elif isinstance(date_value, str):
                                start_date = date_value
                            else:
                                start_date = str(date_value)
                        else:
                            start_date = datetime.now().strftime("%Y-%m-%d")

                        if emp_list.get('version'):
                            version = emp_list.get('version')
                        else:
                            version = 1

                        self.selected_employees.append({
                            'employee_id': emp_list.get('id'),
                            'start_date': start_date,  # Store as string
                            'end_date': emp_list.get('end_date'),
                            'check_state':emp_list.get('check_state'),
                            'combo_text':emp_list.get('combo_text'),
                            'created_by':self.username,
                            'version':version

                        })

        # Update UI to show selection count
        self.update_selection_display()


    def update_selection_display(self):
        """Update the UI to show current selections"""
        dept_count = len(self.selected_departments)
        emp_count = len(self.selected_employees)

        if dept_count > 0 or emp_count > 0:
            status_text = f"Selected: {dept_count} department(s), {emp_count} employee(s)"
            self.selection_status_label.setStyleSheet("color: green;")
        else:
            status_text = "⚠ No departments or employees selected"
            self.selection_status_label.setStyleSheet("color: orange;")
            # You would need to add a Label widget to display this
        if hasattr(self, 'selection_status_label'):
            self.selection_status_label.setText(status_text)

    def kpi_applicability_order(self):

        dialog = QDialog(self)
        dialog.setWindowTitle("Add KPI Applicability Order")
        dialog.resize(600, 700)

        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Order Number"))
        input_field = QLineEdit()
        layout.addWidget(input_field)
        layout.addWidget(QLabel("Order date"))
        order_date = NewPageTemplate.date_widget_inner(self,None,None,None,None)
        layout.addWidget(order_date)
        header_labels = ["Department/Employee","Changed field","Old value","New value"]
        table_elements = []

        for dept in self.dept_changes:
            table_elements.append({header_labels[0].lower():dept[0],header_labels[1].lower():dept[1],header_labels[2].lower():dept[2],header_labels[3].lower():dept[3],"id":dept[0],"type":"department"})
        for emp in self.emp_changes:
            table_elements.append({header_labels[0].lower():emp[0],header_labels[1].lower():emp[1],header_labels[2].lower():emp[2],header_labels[3].lower():emp[3],"id":emp[4],"type":"employee"})

        print("table_elements: ",table_elements)
        kpi_changes_table = NewPageTemplate.create_qtablewidget_tool(self,4,header_labels,None,None)
        NewPageTemplate.display_elements(self,table_elements,kpi_changes_table)
        layout.addWidget(kpi_changes_table)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                      QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            if input_field.text() == '':
                QMessageBox.information(self, "Error", "Please enter order number")
                return
            else:

                order_number = input_field.text()
                order_date_str = order_date.date().toString("yyyy-MM-dd")
                for line in table_elements:
                    if line['type'] == 'department':
                        department = line['id']
                        employee = ''
                        new_applicability = json.dumps([line['changed field'], line['new value'], department])
                    else:

                        employee = line["id"]
                        department = self.database.get_employee_by_id(employee)['department']
                        new_applicability = json.dumps([line['changed field'], line['new value'], employee])
                    order_action = "new kpi applicability"

                    Database.save_order_record(self,order_number,employee, department, order_date_str,order_date_str,order_action,"","",new_applicability)




                print(f"You typed: {input_field.text()}{order_date.date().toString('yyyy-MM-dd')}")
        else:
            print("Dialog cancelled")




