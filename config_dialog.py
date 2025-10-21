import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QMessageBox, QTabWidget,
    QWidget, QInputDialog, QComboBox, QTextEdit)

class ConfigDialog(QDialog):
    def __init__(self, parent = None, config_manager = None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("System Configuration")
        self.setFixedSize(600, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Create tabs
        tabs = QTabWidget()

        #Departments tab

        dept_tab = QWidget()
        dept_layout = QVBoxLayout()

        dept_layout.addWidget(QLabel("Manage Departments"))
        self.dept_list = QListWidget()
        self.load_departments()
        dept_layout.addWidget(self.dept_list)

        dept_buttons = QHBoxLayout()
        add_dept_btn = QPushButton("Add Department")
        add_dept_btn.clicked.connect(self.add_department)
        remove_dept_btn = QPushButton("Remove Selected")
        remove_dept_btn.clicked.connect(self.remove_department)

        dept_buttons.addWidget(add_dept_btn)
        dept_buttons.addWidget(remove_dept_btn)
        dept_layout.addlayout(dept_buttons)

        dept_tab.setLayout(dept_layout)
        tabs.addTab(dept_tab, "Departments")

        # KPIs Tab
        kpi_tab = QWidget()
        kpi_layout = QVBoxLayout()

        kpi_layout.addWidget(QLabel("Manage KPIs"))
        self.kpi_list = QListWidget()
        self.load_kpis()
        kpi_layout.addWidget(self.kpi_list)

        kpi_buttons = QHBoxLayout()
        add_kpi_btn = QPushButton("Add KPI")
        add_kpi_btn.clicked.connect(self.add_kpi)
        edit_kpi_btn = QPushButton("Edit Selected")
        edit_kpi_btn.clicked.connect(self.edit_kpi)
        remove_kpi_btn = QPushButton("Remove Selected")
        remove_kpi_btn.clicked.connect(self.remove_kpi)

        kpi_tab.setLayout(kpi_layout)
        tabs.addTab(kpi_tab, "KPIs")

        layout.addWidget(tabs)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.setLayout(layout)

    def load_department(self):
        self.dept_list.clear()
        departments = self.config_manager.get_departments()
        self.dept_list.addItems(departments)

    def load_kips(self):
        self.kpi_list.clear()
        kips = self.config_manager.get_kips()
        for kpi in kips:
            self.kpi_list.addOtem(f"{kpi["name]} ({kpi["calculation_method]})")

    def add_department(self):
        department, ok = QInputDialog.getText(self, "Add Department", "Department name:")
        if ok and department:
            if self.config_manager.add_department(department.strip()):
                self.load_departments()
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
                    self.load_departmnets()
                    QMessageBox.information(self, "Success","Department removed!")

        else:
            QMessageBox.warning(self,"Error","Please select a department to remove!")

    def add_kpi(self):
        #Simplified for now - we'll create a detailed KPI dialog later
        name, ok = QInputDialog.getText(self, "Add KPI", "KPI name:")
        if ok and name:
            kpi_data = {
                "name": name,
                "departments":[],
                "calculation_method": "percentage",
                "formula": "base_salary * 0.1",
                "weight": 0.3
            }
            if self.config_manager.add_kpi(kpi_data):
                self.load_kpis()
                QMessageBox.information(self, "Success","KPI added!")

    def edit_kpi(self):
        # We'll implement detailed KPI editing later
        QMessageBox.information(self,"Info", "Detailed KPI editor coming soon!")

    def remove_kpi(self):
        current_row = self.kpi_list.currentRow()
        if current_row >=0:
            kpis = self.config_manager.get_kpis()
            kpi_name = kpis[current_row]["name"]
            reply = QMessageBox.question(self, "Confirm", f"Remove KPI: {kpi_name}?")
            if reply == QMessageBox.StandardButton.Yes:
                kpis.pop(current_row)
                self.config_manager.config["kpis"] = kpis
                self.config_manager.save_config()
                self.load_kpis()






