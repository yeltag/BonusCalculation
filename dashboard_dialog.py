import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt
from datetime import datetime


class DashboardDialog(QDialog):
    def __init__(self, parent=None, database=None, config_manager=None):
        super().__init__(parent)
        self.database = database
        self.config_manager = config_manager
        self.setWindowTitle("Dashboard - Reports and Analytics")
        self.setFixedSize(1000, 700)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Summary statistics
        summary_group = QGroupBox("Summary Statistics")
        summary_layout = QHBoxLayout()

        employees = self.database.get_all_employees()
        active_employees = len([emp for emp in employees if emp["status"] == "Active"])
        departments = len(self.config_manager.get_departments())
        kpis = len(self.config_manager.get_kpis())

        stats = [
            ("Total Employees", len(employees)),
            ("Active Employees", active_employees),
            ("Departments", departments),
            ("Active KPIs", kpis)
        ]

        for label, value in stats:
            stat_label = QLabel(f"{label}: {value}")
            stat_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
            summary_layout.addWidget(stat_label)

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        # Department distribution
        dept_group = QGroupBox("Department Distribution")
        dept_layout = QVBoxLayout()

        dept_table = QTableWidget()
        dept_table.setColumnCount(2)
        dept_table.setHorizontalHeaderLabels(["Department", "Employee Count"])

        dept_counts = {}
        for emp in employees:
            dept = emp["department"]
            dept_counts[dept] = dept_counts.get(dept, 0) + 1

        dept_table.setRowCount(len(dept_counts))
        for row, (dept, count) in enumerate(dept_counts.items()):
            dept_table.setItem(row, 0, QTableWidgetItem(dept))
            dept_table.setItem(row, 1, QTableWidgetItem(str(count)))

        dept_layout.addWidget(dept_table)
        dept_group.setLayout(dept_layout)
        layout.addWidget(dept_group)

        # Recent activity placeholder
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout()
        activity_layout.addWidget(QLabel("Recent bonus calculations and system activity will be shown here."))
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)

        self.setLayout(layout)