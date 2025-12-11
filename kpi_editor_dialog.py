import sys
from PyQt6.QtWidgets import(QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QListWidget, QListWidgetItem, QMessageBox,
    QGroupBox, QSplitter, QFrame, QScrollArea)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QPalette
import re

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
    def __init__(self, parent = None, kpi_data = None, config_manager = None, database = None):
        super().__init__(parent)
        self.kpi_data = kpi_data or {}
        self.config_manager = config_manager
        self.database = database
        self.is_edit_mode = kpi_data is not None

        # If database is None, try to get it from parent (ConfigDialog)
        if self.database is None and parent is not None:
            if hasattr(parent, 'database'):
                self.database = parent.database
                print(f"DEBUG: Got database from parent: {self.database}")
            elif hasattr(parent, 'config_manager') and hasattr(parent.config_manager, 'database'):
                self.database = parent.config_manager.database
                print(f"DEBUG: Got database from parent.config_manager: {self.database}")

        self.is_edit_mode = kpi_data is not None

        if self.is_edit_mode:
            self.setWindowTitle("Edit KPI formula")
        else:
            self.setWindowTitle("Create New KPI Formula")

        self.setup_ui()
        self.setFixedSize(900,650)
        self.resize(1000,700)

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

        # Applicable Departments
        basic_layout.addWidget(QLabel("Applicable Departments (leave emplty for all):"))
        self.dept_list = QListWidget()
        if self.config_manager:
            departments = self.config_manager.get_departments()
            self.dept_list.addItems(departments)
        self.dept_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        basic_layout.addWidget(self.dept_list)

        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)

        # Formula Editor
        formula_group = QGroupBox("Formula Editor")
        formula_layout = QVBoxLayout()

        formula_layout.addWidget(QLabel("Formula (Python syntax):"))

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
        print(f"DEBUG create_variables_panel kpi_editor line 207: self.database = {self.database}")

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
                print("DEBUG: Custom variables from database kpi_editor_dialog create_variable panel line 235:")
                for i, var in enumerate(custom_variables):
                    print(f"  {i}: {var}")
            except Exception as e:
                print(f"Error loading custom variables:{e} kpi_editor_dialog.py create_variables_panel line 236")
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
        self.desc_input.setText(self.kpi_data.get("description",""))
        self.method_combo.setCurrentText(self.kpi_data.get("calculation_method","formula"))

        # Set formula or simple values
        if self.kpi_data.get("calculation_method") == "percentage":
            self.percentage_input.setText(str(self.kpi_data.get("percentage","")))
        elif self.kpi_data.get("calculation_method") == "fixed":
            self.fixed_input.setText(str(self.kpi_data.get("fixed_amount","")))
        else:
            self.formula_edit.setPlainText(self.kpi_data.get("formula",""))

        # Select applicable deartments
        applicable_depts = self.kpi_data.get("applicable_departments",[])
        for i in range(self.dept_list.count()):
            item = self.dept_list.item(i)
            if item.text() in applicable_depts:
                item.setSelected(True)

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
            QMessageBox.information(self, "Formula Test",
                               f"Formula tested successfully!\n\n"
                                    f"test Data:\n"
                                    f"Base Salary: {test_data["base_salary"]:,.2f}\n"
                                    f"Performance Rating: {test_data["performance_rating"]}\n"
                                    f"Years of Service: {test_data["years_of_service"]}\n\n"
                                    f"Result: {result:,.2f}")

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
            print(f"Error evaluating formula: {e}")
            print(f"Formula: {formula}")
            print(f"Available variables: {list(safe_dict.keys())}")
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
        selected_depts = [item.text() for item in self.dept_list.selectedItems()]

        # Prepare KPI data based on method
        kpi_data = {
            "name": name,
            "description": description,
            "calculation_method": method,
            "applicable_departments": selected_depts,
            "weight": 1.0,  # Default weight
            "is_active": True
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
                print("Testing formula with sample data")
                try:
                    # Test with only base_salary (custom variables added automatically)
                    test_data = {"base_salary": 5000}
                    result = self.safe_eval_formula(formula, test_data)
                    print(f"DEBUG: Formula test passed with result: {result}")
                    kpi_data["formula"] = formula

                except Exception as e:
                    print(f"DEBUG: Formula test failed with error: {e}")
                    errors.append(f"Formula contains errors: {str(e)}")

        # Show errors if any
        if errors:
            error_msg = "Please fix the following errors:\n\n" + "\n".join(f"- {error}" for error in errors)
            QMessageBox.warning(self, "Validation Error", error_msg)
            return

        self.kpi_data = kpi_data
        self.accept()

    def get_kpi_data(self):
        """Return the KPI data"""
        return self.kpi_data



