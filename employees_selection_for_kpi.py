import sys
from PyQt6.QtWidgets import(QWidget, QListWidget, QLabel, QApplication,QTreeWidget,QDateEdit,QPushButton,QAbstractScrollArea,QGroupBox,QCalendarWidget,QVBoxLayout)
from datetime import datetime
import calendar
from database import Database
from config_manager import ConfigManager
from config_dialog import ConfigDialog
from new_page_template import NewPageTemplate


class employee_selection_for_kpi(QWidget):
    def __init__(self):
        super().__init__()
        self.database = Database()
        self.config_manager = ConfigManager(database = self.database)
        self.setup_ui()

    def setup_ui(self):

        self.setWindowTitle("Select departments for KPI")
        self.setGeometry(100,100,800,600)
        self.create_selection_window()


    def create_selection_window (self):

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.select_departments_for_kpi_page = NewPageTemplate("Select departments or employees")

        self.select_departments_for_kpi_page.create_layout()

        departments_dict =  self.config_manager.get_departments()
        employees_list = self.database.get_all_employees()
        list_to_filter = []

        for department in departments_dict.keys():
            list_to_filter.append({"department":department,"employees":[]})
            for employee in employees_list:
                if employee["department"] == department:
                    for dept in range(len(list_to_filter)):
                        if list_to_filter[dept]["department"] == department:
                            list_to_filter[dept]["employees"].append(f"{employee["last_name"]} {employee["first_name"]} {employee["father_name"]}")

        print(list_to_filter)



        main_layout.addWidget(self.select_departments_for_kpi_page)


        #return self.select_departments_for_kpi_page









if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = employee_selection_for_kpi()
    window.show()
    sys.exit(app.exec())