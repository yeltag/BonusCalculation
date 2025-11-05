import sys
from PyQt6.QtWidgets import ( QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QMessageBox, QComboBox,
    QTextEdit, QFormLayout, QGroupBox )

from PyQt6.QtCore import Qt
import re

class VariablesDialog(QDialog):
    def __init__(self, parent=None, variable_data=None, database = None):
        super().__init__(parent)
        self.variable_data = variable_data or {}
        self.database = database
        self.is_edit_mode = variable_data is not None

        if self.is_edit_mode:
            self.setWindowTitle("Edit Custom Variable")
        else:
            self.setWindowTitle("Create Custom Variable")

        self.setup_ui()
        self.setFixedSize(500,400)

    def setup_ui(self):
        layout = QVBoxLayout()

        # variable Information Group
        info_group = QGroupBox("Variable Information")
        form_layout = QFormLayout()

        # Display Name(user-friendly name)
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("e.g., Sales Terget Achievement")
        if self.is_edit_mode:
            self.display_name_input.setText(self.variable_data.get("display_name",""))
        form_layout.addRow("Display Name:",self.display_name_input)
        
        # Variable name (internal name for formulas)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., sales_target_achievement")
        if self.is_edit_mode:
            self.name_input.setText(self.variable_data.get("name",""))
            self.name_input.setEnabled(False)  # can't change internal name after creation
            
        form_layout.addRow("Variable Name*:",self.name_input)
        
        # Data type
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["number","percentage","currency","text"])
        if self.is_edit_mode:
            current_type = self.variable_data.get("data_type","number")
            index = self.data_type_combo.findText(current_type)
            if index >= 0:
                self.data_type_combo.setCurrentIndex(index)
        form_layout.addRow("Data Type:", self.data_type_combo)

        # Default Value
        self.default_value_input = QLineEdit()
        self.default_value_input.setPlaceholderText("e.g., 0.85 or 1000")
        if self.is_edit_mode:
            self.default_value_input.setText(str(self.variable_data.get("default_value","")))
        form_layout.addRow("Default Value:", self.default_value_input)

        #Description
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Describe what this variable represents...")
        if self.is_edit_mode:
            self.description_input.setText(self.variable_data.get("description",""))
        form_layout.addRow("Description:", self.description_input)

        info_group.setLayout(form_layout)
        layout.addWidget(info_group)

        # Example Group
        examples_group = QGroupBox("Examples")
        examples_layout = QVBoxLayout()
        examples_layout.addWidget(QLabel("In formulas, use:<b>sales_target_achievement</b>"))
        examples_layout.addWidget(QLabel("Example formula:<b>base_salary * sales(target_achievement * 0.1</b>"))
        examples_layout.setLayout(examples_layout)
        layout.addWidget(examples_group)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()

        if self.is_edit_mode:
            save_btn = QPushButton("Save Changes")
        else:
            save_btn = QPushButton("Create Variable")
        save_btn.clicked.connect(self.validate_and_save)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

        self.setLayout(button_layout)

    def validate_and_save(self):
        """Validate and save custom variable"""
        display_name = self.display_name_input.text().strip()
        name = self.name_input.text().strip()
        data_type = self.data_type_combo.currentText()
        default_value = self.default_value_input.text().strip()
        description = self.description_input.toPlainText().strip()

        errors = []

        # Validation
        if not display_name:
            errors.append("Display name is required")

        if not name:
            errors.append("Variable name is required")

        elif not re.match(r"^[a-z][a-z0-9]*$", name):
            errors.append("Variable name must contain only lowercase letters, numbers, and underscores, and start with a letter")

        # Validate default value based on data type
        if default_value:
            if data_type in["number","percentage","currency"]:
                try:
                    float(default_value)
                except ValueError:
                    errors.append(f"Default value must be a number for data type '{data_type}'")

        if errors:
            error_msg = "Please fix the following errors:\n\n" + "\n".join(f"- {error}" for error in errors)
            QMessageBox.warning(self,"validation Error", error_msg)
            return

        # prepare variable data
        self.variable_data = {
            "display_name": display_name,
            "name":name,
            "data_type": data_type,
            "default_value": default_value,
            "description": description,
            "is_active": True
        }

        self.accept()

    def get_variable_data(self):
        return self.variable_data

class VariablesManagerDialog(QDialog):
    def __init__(self, parent = None, database = None):
        super().__init__(parent)
        self.database = database
        self.setWindowTitle("Manage Custom Variables")
        self.setFixedSize(500,400)
        self.setup_ui()
        self.load_variables()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Title
        layout.addWidget(QLabel("manage Custom Variables for KPI Formulas"))

        # Variables List
        self.variables_list = QListWidget()
        layout.addWidget(self.variables_list)

        # Buttons
        buttons_layout = QHBoxLayout()

        add_btn = QPushButton("Add Variable")
        add_btn.clicked.connect(self.add_variable)

        edit_btn = QPushButton("Edit Selected")
        edit_btn.clicked.connect(self.edit_variable)

        remove_btn = QPushButton("Remobe Selected")
        remove_btn.clicked.connect(self.remove_variable)

        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(edit_btn)
        buttons_layout.addwidget(remove_btn)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def load_variables(self):
        """load customs variables from database"""
        self.variables_list.clear()
        if self.database:
            variables = self.database.get_all_custom_variables()
            for var in variables:
                display_text = f"{var['display_name']}({var['name']}) - {var['data_type']}"
                if var['default_value']:
                    display_text += f"[Default: {var['default_value']}]"
                self.variables_list.addItem(display_text)

    def add_variables(self):
        """Add new custom variable"""
        dialog = VariablesDialog(self, None, self.database)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_variable = dialog.get_variable_data()

            # Save to database
            if self.database:
                self.database.save_custom_variable(new_variable)
                self.load_variables()
                QMessageBox.information(self, "Success", "Custom variable added successfully!")

    def edit_variable(self):
        """Edit selected custom variable"""
        current_row = self.variables_list.currentRow()
        if current_row >= 0 and self.database:
            variables = self.database.get_all_custom_variables()
            if 0 <= current_row < len(variables):
                variable_to_edit = variables[current_row]

                dialog = VariablesDialog(self, variable_to_edit, self.database)

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    updated_variable = dialog.get_variable_data()

                    # Update in database
                    self.database.save_custom_variable(updated_variable)
                    self.load_variables()
                    QMessageBox.information(self, "Success", "Custom variable updated successfully!")
        else:
            QMessageBox.warning(self, "Error", "Please select a variable to edit")

    def remove_variable(self):
        """Remove selected custom variable"""
        current_row = self.variables_list.currentRow()
        if current_row >= 0 and self.database:
            variables = self.database.get_all_custom_variables()
            if 0 <= current_row < len(variables):
                variable_name = variables[current_row]['display_name']
                reply = QMessageBox.question(self, "Confirm Delete",
                                             f"Are you sure you want to remove variable: {variable_name}?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.database.delete_custom_variable(variables[current_row]['id'])
                    self.load_variables()
                    QMessageBox.information(self, "Success", f"Variable '{variable_name}' removed!")
                else:
                    QMessageBox.warning(self, "Error", "Please select a variable to remove")
