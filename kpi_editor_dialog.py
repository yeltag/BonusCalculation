import sys
from PyQt6.QtWidgets import(QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QListWidget, QListWidgetItem, QMessageBox,
    QGroupBox, QSplitter, QFrame)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QPalette
import re

class FormulaHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for KPI formulas"""
    def __init__(self, document):
        super().__init__(document)

        # Define formatting rules
        self.highlighting_rules = []

        # Variable format (blue)
        variable_format = QTextCharFormat()
        variable_format.setForeground(QColor(0,0,255))
        variable_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((r'\b(base_salary|performance_rating|years_of_service|sales_amount|completed_projects)\b', variable_format))

        # Operator format(red)
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
    def __init__(self, parent = None, kpi_data = None, config_manager = None):
        super().__init__(parent)
        self.kpi_data = kpi_data or {}
        self.config_manager = config_manager
        self.is_edit_mode = kpi_data is not None

        if self.is_edit_mode:
            self.setWindowTitle("Edit KPI formula")
        else:
            self.setWindowTitle("Create New KPI Formula")

        self.setup_ui()
        self.setFixedSize(800,600)

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
        splitter.setSizes([500,300])

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
        basic_layout.addlayout(name_layout)

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
        basic_layout.addlayout(method_layout)

        # Applicable Departments
        basic_layout.addwidget(QLabel("Applicable Departments (leave emplty for all):"))
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
            "• if sales_amount > 10000 then 500 else 200  # Conditional bonus"
        )

        # Set monospace forn for formula editor
        font = QFont("Courier", 10)
        self.formula_edit.setFont(font)

        # Apply syntax highlighting
        self.highlighter = FormulaHighlighter(self.formula_edit.documents())

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

        formula_layout.addlayout(self.simple_inputs_layout)

        formula_group.setLayout(formula_layout)
        layout.addWidget(formula_group)

        panel.setLayout(layout)
        return panel

    def create_variables_panel(self):
        """Create the variables and functions panel"""
        panel = QFrame()
        layout = QVBoxLayout()

        #Available Variables
        vars_group = QGroupBox("Available Variables")
        vars_layout = QVBoxLayout()

        variables = [
            ("base_salary", "Employee's monthly base salary"),
            ("performance_rating", "Performance rating (1-5 scale)"),
            ("years_of_service", "Years worked at company"),
            ("sales_amount", "Monthly sales amount"),
            ("completed_projects", "Number of completed projects"),
            ("attendance_rate", "Attendance percentage (0-1)"),
            ("team_size", "Number of people in team"),
            ("revenue_generated", "Revenue generated this month")
        ]

        for var_name, var_desc in variables:
            var_btn = QPushButton(f"{var_name}")
            var_btn.setToolTip(var_desc)
            var_btn.clicked.connect(lambda checked, v = var_name: self.insert_variable(v))
            vars_layout.addWidget(var_btn)

        vars_group.setLayout(vars_layout)
        layout.addWidget(vars_group)

        # mathematical Functions
        funcs_group = QGroupBox("Mathematical Functions")
        funcs_layout = QVBoxLayout()

        functions = [
            ("min(x, y)", "Returns smaller of two values"),
            ("max(x, y)", "Returns larger of two values"),
            ("round(x, 2)", "Rounds to 2 decimal places"),
            ("if condition then x else y", "Conditional expression")
        ]

        for func_name, func_desc in functions:
            func_btn = QPushButton(func_name)
            func_btn.setToolTip(func_desc)
            func_btn.clicked.connect(lambda checked, f = func_name:self.insert_function(f))
            funcs_layout.addWidget(func_btn)

            # Formula Templates
            templates_group = QGroupBox("Formula Templates")
            templates_layout = QVBoxLayout()

            templates = [
                ("10% of Base Salary", "base_salary * 0.1"),
                ("Performance Based", "base_salary * performance_rating * 0.05"),
                ("Sales Commission", "sales_amount * 0.15"),
                ("Seniority Bonus", "base_salary * years_of_service * 0.02"),
                ("Conditional Bonus", "if sales_amount > 10000 then 500 else 200")
            ]

            for template_name, template_formula in templates:
                template_btn = QPushButton(template_name)
                template_btn.setToolTip(template_formula)
                template_btn.clicked.connect(lambda checked, f=template_formula: self.insert_template(f))
                templates_layout.addWidget(template_btn)

            templates_group.setLayout(templates_layout)
            layout.addWidget(templates_group)

            panel.setLayout(layout)
            return panel


    def on_mehod_changed(self, method):
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
            self.percentage_input.setText(str(self.kpi_data.get("persentage","")))
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
                                    f"Years of Service: {test_data["years_if_service"]}\n\n"
                                    f"Result: {result:,.2f}")

        except Exception as e:
            QMessageBox.warning(self, "Formula Error",
                                f"Formula contains errors:\n\n{str(e)}")

    def sefe_eval_formula(self, formula, variables):
        """Safely evaluate a formula with given variables"""
        # Replace custom syntax with Python syntax
        formula = formula.replca(" then ", " if ").replace(" else ", " else ")

        # Create safe evaluation environment
        safe_dict = {
            "min": min,
            "max": max,
            "round": round,
            "sum": sum,
            "abs": abs,
            "__builtins__": {}

        }
        safe_dict.update(variables)

        # Evaluate the formula
        return eval(formula, {"__builtins__": {}}, safe_dict)

    def validate_and_save(self):
        """Validate inputs and save KPI data"""
        # Get basix information
        name = self.name_input.text().strip()
        description = self.desc_input.desc_input.text().strip()
        method = self.method_combo.currentText()

        # Validation
        errors = []
        if not name:
            errors.append("KPI name is required")

        # Get selected departments
        selected_depts = [item.text() for item in self.dept_list.selectedItems()]

        # prepare KPI data based on method
        kpi_data = {
            "name": name,
            "description": description,
            "calculation_method": method,
            "applicable_departments": selected_depts,
            "weight": 1.0, #Default weight
            "is_active": True
        }

        if method == "percentage":
            try:
                percentage = float(self.percentage_input.text())
                kpi_data["percentage"] = percentage
                kpi_data["formula"] = f"base_salary * {percentage}"
            except ValueError:
                errors.append("percentage must be a valid number")

        elif method == "fixed":
            try:
                fixed_amount = float(self.fixed_input.text())
                kpi_data["fixed_amount"] = fixed_amount
                kpi_data["formula"] = str(fixed_amount)
            except ValueError:
                errors.append("Fixed amount must be a valid number")

        else: #formula method
            formula = self.formula_edit.toPlainText().strip()
            if not formula:
                errors.apeend("Formula is required for formula calculation method")
            else:
                ("Test formula with sample data")
                try:
                    test_data = {"base_salary": 5000}
                    self.safe_eval_formula(formula, test_data)
                    kpi_data["formula"] = formula

                except Exception as e:
                    errors.append(f"Formula contains errors: {str(e)}")

        # Show errors if any
        if errors:
            error_msg = "Please fix the following errors:\n\n" + "\n".join(f"- {error}" for error in errors)
            QMessageBox.warning(self,"Validation Error", error_msg)
            return

        self.kpi_data = kpi_data
        self.accept()

    def get_kpi_data(self):
        """Return the KPI data"""
        return self kpi.data



