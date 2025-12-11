import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QMessageBox, QTabWidget,
    QWidget, QInputDialog, QComboBox, QTextEdit)
from kpi_editor_dialog import KPIEditorDialog
from variables_dialog import VariablesManagerDialog

class ConfigDialog(QDialog):
    def __init__(self, parent = None, config_manager = None, database = None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.database = database
        self.setWindowTitle("System Configuration")
        self.setFixedSize(700, 500)
        self.setup_ui()
        self.test_buttons()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Create tabs
        self.tabs = QTabWidget()

        # Set up both tabs
        self.setup_departments_tab()
        self.setup_kpis_tab()

        main_layout.addWidget(self.tabs)

        # Variables Tab
        variables_tab = QWidget()
        variables_layout = QVBoxLayout()

        variables_layout.addWidget(QLabel("Manage Custom Variables for KPI Formulas"))

        # Info text
        info_label = QLabel(
            "Custom variables allow you to create flexible KPI formulas."
            "Define variables like 'sales_target', 'customer_satisfaction', etc."
            "Then use the in your KPI formulas."
        )
        info_label.setWordWrap(True)
        variables_layout.addWidget(info_label)

        # Manage Variables button
        manage_vars_btn = QPushButton("Manage Custom Variables")
        manage_vars_btn.clicked.connect(self.manage_variables)
        variables_layout.addWidget(manage_vars_btn)

        variables_layout.addStretch()
        variables_tab.setLayout(variables_layout)
        self.tabs.addTab(variables_tab, "Custom Variables")

        # Close button

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        main_layout.addWidget(close_btn)
        self.setLayout(main_layout)

    def setup_departments_tab(self):
        """Setup the departments management tab"""

        dept_tab = QWidget()
        dept_layout = QVBoxLayout()

        dept_layout.addWidget(QLabel("Manage Departments"))

        self.dept_list = QListWidget()
        self.load_department()

        dept_layout.addWidget(self.dept_list)

        # Department buttons

        dept_buttons_layout = QHBoxLayout()
        add_dept_btn = QPushButton("Add Department")
        add_dept_btn.clicked.connect(self.add_department)

        remove_dept_btn = QPushButton("Remove Selected")
        remove_dept_btn.clicked.connect(self.remove_department)

        dept_buttons_layout.addWidget(add_dept_btn)
        dept_buttons_layout.addWidget(remove_dept_btn)
        dept_buttons_layout.addStretch()

        dept_layout.addLayout(dept_buttons_layout)

        dept_tab.setLayout(dept_layout)
        self.tabs.addTab(dept_tab, "Departments")

    def setup_kpis_tab(self):
        """Setup the KPIs management tab"""

        kpi_tab = QWidget()
        kpi_layout = QVBoxLayout()

        kpi_layout.addWidget(QLabel("Manage KPIs (Key Performance Indicators)"))

        self.kpi_list = QListWidget()
        self.load_kpis()
        kpi_layout.addWidget(self.kpi_list)

        kpi_buttons_layout = QHBoxLayout()

        # ADD KPI BUTTON

        add_kpi_btn = QPushButton("Add KPI")
        add_kpi_btn.clicked.connect(self.add_kpi)
        kpi_buttons_layout.addWidget(add_kpi_btn)

        # Edit KPI button
        edit_kpi_btn = QPushButton("Edit Selected")
        edit_kpi_btn.clicked.connect(self.edit_kpi)
        kpi_buttons_layout.addWidget(edit_kpi_btn)

        # Remove KPI button
        remove_kpi_btn = QPushButton("Remove Selected")
        remove_kpi_btn.clicked.connect(self.remove_kpi)
        kpi_buttons_layout.addWidget(remove_kpi_btn)

        # Add stretch to push buttons to the left
        kpi_buttons_layout.addStretch()

        kpi_layout.addLayout(kpi_buttons_layout)

        kpi_tab.setLayout(kpi_layout)
        self.tabs.addTab(kpi_tab, "KPIs")

    def load_department(self):
        self.dept_list.clear()
        departments = self.config_manager.get_departments()
        self.dept_list.addItems(departments)

    def load_kpis(self):
        self.kpi_list.clear()
        kips = self.config_manager.get_kpis()
        for kpi in kips:
            self.kpi_list.addItem(f"{kpi["name"]} ({kpi["calculation_method"]})")

    def add_department(self):
        department, ok = QInputDialog.getText(self, "Add Department", "Department name:")
        if ok and department:
            if self.config_manager.add_department(department.strip()):
                self.load_department()
                QMessageBox.information(self,"Success", "Department added successfully!")

            else:
                QMessageBox.warning(self, "Error", "Department already exists!")

    def remove_department(self):
        current_item = self.dept_list.currentItem()
        if current_item:
            department = current_item.text()
            reply = QMessageBox.question(self, "Confirm", f"Remove department:{department}?")
            if reply == QMessageBox.StandardButton.Yes:
                if self. config_manager.remove_department(department):
                    self.load_department()
                    QMessageBox.information(self, "Success","Department removed!")

        else:
            QMessageBox.warning(self,"Error","Please select a department to remove!")

    def add_kpi(self):
        """Open KPI editor to add new KPI"""
        print(f"DEBUG ConfigDialog: self.database = {self.database}")

        dialog = KPIEditorDialog(self,None,self.config_manager, database = self.database)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_kpi = dialog.get_kpi_data()

            # Add to configuration
            if self.config_manager.add_kpi(new_kpi):
                self.load_kpis()
                QMessageBox.information(self,"Success","KPI added successfully!")
            else:
                QMessageBox.warning(self,"Error","Failed to add KPI")

    def edit_kpi(self):
        """Edit selected KPI"""
        current_row = self.kpi_list.currentRow()
        if current_row >= 0:
            kpis = self.config_manager.get_kpis()
            kpi_to_edit = kpis[current_row]

            print(f"=== DEBUG EDIT KPI ===")
            print(f"Editing KPI at index {current_row}")
            print(f"KPI to edit: {kpi_to_edit}")
            print(f"KPI ID: {kpi_to_edit.get('id', 'NO ID')}")
            print(f"KPI Name: {kpi_to_edit.get('name')}")

            dialog = KPIEditorDialog(self,kpi_to_edit, self.config_manager, self.database)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_kpi = dialog.get_kpi_data()
                print(f"Updated KPI data: {updated_kpi}")
                print(f"Updated KPI ID: {updated_kpi.get('id', 'NO ID')}")
                print(f"=== END DEBUG ===")

                # If KPI has an ID (from database), use add_kpi which will update via INSERT OR REPLACE
                if "id" in kpi_to_edit:
                    if self.config_manager.update_kpi(current_row, updated_kpi):
                        self.load_kpis()
                        QMessageBox.information(self, "Success","KPI updated successfully!")
                    else:
                        QMessageBox.warning(self,"Error", "Failed to update KPI")
                else:
                    # For config-only KPIs, use update_kpi
                    if self.config_manager.update_kpi(current_row, updated_kpi):
                        self.load_kpis()
                        QMessageBox.information(self, "Success", "KPI updated successfully!")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to update KPI")


        else:
            QMessageBox.warning(self,"Error","Please select a KPI to edit")

    def remove_kpi(self):
        current_row = self.kpi_list.currentRow()
        if current_row >= 0:
            kpis = self.config_manager.get_kpis()
            kpi_to_remove = kpis[current_row]
            kpi_name = kpi_to_remove["name"]

            reply = QMessageBox.question(self, "Confirm", f"Remove KPI: {kpi_name}?")
            if reply == QMessageBox.StandardButton.Yes:
                # Remove from database if available
                if self.database and "id" in kpi_to_remove:
                    try:
                        self.database.delete_kpi(kpi_to_remove["id"])
                        print(f"DEBUG: KPI {kpi_name} deleted from database")
                    except Exception as e:
                        print(f"Error deleting KPI from database: {e}")
                        QMessageBox.warning(self, "Error", f"Failed to remove KPI from database: {e}")
                        return

                # Remove from config
                kpis.pop(current_row)
                self.config_manager.config["kpis"] = kpis
                if self.config_manager.save_config():
                    self.load_kpis()
                    QMessageBox.information(self, "Success", f"KPI '{kpi_name}' removed successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to save configuration after removal")
        else:
            QMessageBox.warning(self, "Error", "Please select a KPI to remove")

    def test_buttons(self):
        print("Testing KPIs tab buttons...  config_dialog.py  test_buttons line 211")
        print(f"KPI list has {self.kpi_list.count()} items test_buttons line 212")

        # Check if buttons exist
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if widget:
                print(f"Found widget  test_buttons Line 218: {type(widget).__name__}")

    def manage_variables(self):
        """Open custom variables management dialog"""
        print(f"DEBUG manage_variables line 222: Database available: {self.config_manager.database is not None}")

        if self.config_manager.database:
            dialog = VariablesManagerDialog(self, self.config_manager.database)
            dialog.exec()
        else:
            QMessageBox.warning(self,"Error","Database connection not available")


