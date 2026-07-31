import sys
from PyQt6.QtWidgets import (QDialog, QWidget, QListWidget, QLabel, QApplication, QTreeWidget, QDateEdit, QPushButton,
                             QAbstractScrollArea, QGroupBox, QCalendarWidget, QVBoxLayout, QDialogButtonBox, QComboBox)
from datetime import datetime
import calendar
from PyQt6.QtCore import Qt, pyqtSignal, QDate
#from PyQt6.QtWidgets.QMainWindow import childEvent

from database import Database
from config_manager import ConfigManager
#from config_dialog import ConfigDialog
from new_page_template import NewPageTemplate
#from main_window import MainWindow


class EmployeeSelectionForKPI(QDialog):
    data_saved = pyqtSignal(dict,bool,list,list)

    def __init__(self, existing_departments = None,existing_employees = None,exclusion = False):
        super().__init__()
        self.database = Database()
        self.config_manager = ConfigManager(database = self.database)
        self.selected_data = {"departments":[],"employees":[]}
        self.existing_departments = existing_departments
        self.existing_employees = existing_employees
        self.exclusion = exclusion
        self.setup_ui()


        #self.main_window = MainWindow()

    def setup_ui(self):

        self.setWindowTitle("Select departments for KPI")
        self.setGeometry(100,100,900,800)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint
        )
        self.create_selection_window()


    def create_selection_window (self):
        #self.main_window = MainWindow()
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        if self.exclusion == False:

            window_title = "Select employees"
            column_count = 5
            header_labels = ["Start Date","Apply start date to all","End date", "Apply end date to all"]
            tree_data = self.create_lists_and_fields_for_tree()
            lists_for_tree = tree_data[0]
            fields_for_tree = tree_data[1]

        else:
            window_title = self.exclusion[1]
            column_count = self.exclusion[2]
            header_labels = []
            if self.exclusion[0] and self.exclusion[0] == 'kpi_selection':
                lists_for_tree = self.exclusion[3]
                fields_for_tree = self.exclusion[4]
            else:
                tree_data = self.create_lists_and_fields_for_tree()
                lists_for_tree = tree_data[0]
                fields_for_tree = tree_data[1]

        self.select_departments_for_kpi_page = NewPageTemplate(window_title)

        dept_empl_qtree = self.select_departments_for_kpi_page.create_qtreewidget_tool(column_count,header_labels,lists_for_tree,fields_for_tree)

        if not self.exclusion:

            changed_method = self.select_departments_for_kpi_page.on_date_changed

            self.select_departments_for_kpi_page.create_widget_for_tree({"date":[changed_method]},dept_empl_qtree,1, [0,1],changed_method,False)

            changed_method = self.select_departments_for_kpi_page.on_date_check_changed

            widget_text = ""

            self.select_departments_for_kpi_page.create_widget_for_tree({"check_box":[changed_method]}, dept_empl_qtree, 2, [0], changed_method,widget_text)

            changed_method = self.select_departments_for_kpi_page.combobox_text_changed
            combobox = {"combobox":[changed_method,["Open date","Set the date"]]}
            changed_method = self.select_departments_for_kpi_page.on_date_changed
            date = {"date":[changed_method]}
            container = {"container":[combobox,date]}


            self.select_departments_for_kpi_page.create_widget_for_tree(container,dept_empl_qtree,3,[0,1],changed_method)

            changed_method = self.select_departments_for_kpi_page.on_end_date_check_changed

            self.select_departments_for_kpi_page.create_widget_for_tree({"check_box":[changed_method]}, dept_empl_qtree, 4, [0],changed_method)



        central_widgets = [dept_empl_qtree]

        self.select_departments_for_kpi_page.central_widgets = central_widgets

        self.tree_widget = dept_empl_qtree

        # Apply any preselected data after tree is populated

        #if not self.exclusion:
        self.apply_preselected_data()

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)

        button_box.accepted.connect(self.accept_and_save)
        button_box.rejected.connect(self.reject)

        button_widgets =[button_box]
        self.select_departments_for_kpi_page.button_widgets = button_widgets

        self.select_departments_for_kpi_page.create_layout()

        main_layout.addWidget(self.select_departments_for_kpi_page)

        #return self.select_departments_for_kpi_page

    def create_lists_and_fields_for_tree(self):
        self.all_departments = self.config_manager.get_departments()
        self.departments_list = []
        for key, value in self.all_departments.items():
            self.departments_list.append({"id": key, "department": key, "status": value, "field":key})
        self.all_employess = self.database.get_all_employees()
        self.employees_list = []
        for employee in self.all_employess:
            employee["field"] = f'{employee["last_name"]} {employee["first_name"]} {employee["father_name"]}'
            self.employees_list.append(employee)

        lists_for_tree = [self.departments_list, self.employees_list]
        fields_for_tree = ['department', 'employee']

        return [lists_for_tree,fields_for_tree]

    def apply_preselected_data(self):
        """Apply existing selections to the tree widget (for edit mode)"""

        if not hasattr(self,"tree_widget") or not self.tree_widget:
            print("No tree widget available for pre-population")
            return

        if self.existing_departments and self.existing_employees:

            print(f"Applying preselected departments: {self.existing_departments}")
            print(f"Applying preselected employees: {self.existing_employees}")
            

        if self.existing_departments:
            # Apply department selections
            for dept in self.existing_departments:
                dept_name = dept.get('department_name')
                start_date = dept.get('start_date')
                apply_to_all = dept.get('apply_to_all',False)
                check_state = dept.get('check_state')
                enddate_combobox = dept.get('enddate_combobox')
                end_date = dept.get('end_date')
                enddate_check = dept.get('enddate_check')
                created_by = dept.get('created_by')
                version = dept.get('version')

                #check_state = Qt.CheckState.Checked
                if apply_to_all:
                    check_box_state = Qt.CheckState.Checked
                else:
                    check_box_state = Qt.CheckState.Unchecked



                if not dept_name:
                    continue

                # Find the department item in the tree
                for i in range(self.tree_widget.topLevelItemCount()):
                    item = self.tree_widget.topLevelItem(i)
                    if item.text(0) == dept_name:
                        # Check the department
                        if check_state and int(check_state) == 2:
                            item.setCheckState(0,Qt.CheckState.Checked)
                        elif check_state and int(check_state) == 1:
                            item.setCheckState(0,Qt.CheckState.PartiallyChecked)
                        else:
                            item.setCheckState(0,Qt.CheckState.Unchecked)

                        # Set the date widget if start_date exists
                        if start_date:
                            date_widget = self.tree_widget.itemWidget(item, 1)
                            if date_widget:
                                try:
                                    # Parse the date string
                                    if isinstance(start_date, str):
                                        qdate = QDate.fromString(start_date,"yyyy-MM-dd")
                                        if qdate.isValid():
                                            date_widget.setDate(qdate)
                                except Exception as e:
                                    print(f"Error setting date for department {dept_name}: {e}")

                        enddate_container_widget = self.tree_widget.itemWidget(item, 3)

                        if enddate_combobox:

                            enddate_combo_widget = enddate_container_widget.findChildren(QComboBox)[0]
                            enddate_combo_widget.setCurrentText(enddate_combobox)

                        if end_date:
                            end_date_widget = enddate_container_widget.findChildren(QDateEdit)[0]
                            enddate = QDate.fromString(end_date,"yyyy-MM-dd")
                            end_date_widget.setDate(enddate)

                        endcheck_widget = self.tree_widget.itemWidget(item, 4)
                        print(type(endcheck_widget))
                        if enddate_check == 0:
                            endcheck_widget.setChecked(False)
                        else:
                            endcheck_widget.setChecked(True)

                        #if apply_to_all:
                            #print(f"Setting Apply to all for {dept_name}")
                        checkbox_widget = self.tree_widget.itemWidget(item,2)
                        #    item.setCheckState(2,Qt.CheckState.Checked)
                        #else:
                        checkbox_widget.setCheckState(check_box_state)

                        # Expand to show employees
                        item.setExpanded(True)

                        break

        if self.existing_employees:
            # Apply employee selections
            emp_id_list = []
            for emp in self.existing_employees:
                emp_id_list.append(emp.get('employee_id'))


            for emp in self.existing_employees:
                emp_id = emp.get('employee_id')
                start_date = emp.get('start_date')
                check_state = emp.get('check_state')

                if not emp_id:
                    continue

                # Find and check the employee
                for i in range(self.tree_widget.topLevelItemCount()):
                    department_item = self.tree_widget.topLevelItem(i)
                    for j in range(department_item.childCount()):
                        employee_item = department_item.child(j)
                        # Get the employee ID stored in UserRole
                        item_emp_id = employee_item.data(0, Qt.ItemDataRole.UserRole)[0]

                        if item_emp_id == emp_id:

                            employee_item.setCheckState(0,Qt.CheckState.Checked)


                            # Set the date widget if start_date exists
                            if start_date:
                                date_widget = self.tree_widget.itemWidget(employee_item,1)
                                if date_widget:
                                    try:
                                        if isinstance(start_date, str):
                                            qdate = QDate.fromString(start_date,"yyyy-MM-dd")
                                            if qdate.isValid():
                                                date_widget.setDate(qdate)
                                    except Exception as e:
                                        print(f"Error setting date for employee {emp_id}: {e}")


                            break
                        elif item_emp_id not in emp_id_list:
                            employee_item.setCheckState(0,Qt.CheckState.Unchecked)


    def accept_and_save(self):
        self.save_emp_list_for_kpi(self.tree_widget)

        self.data_saved.emit(self.selected_data,self.order_required,self.dpt_changes,self.emp_changes)

        self.accept()

    def save_emp_list_for_kpi(self,tree_widget):
        kpi_application_dict = {"departments":[],"employees":[]}

        def process_departments(item):
            # Get the date widget
            date_widget = tree_widget.itemWidget(item, 1)
            start_date = None
            #print("item.columnCount: ",item.columnCount())
            #print("Item,checkstate: ",item.checkState(2))
            if date_widget:
                try:
                    start_date = date_widget.date().toString("yyyy-MM-dd")

                except:
                    start_date = datetime.now().strftime("%Y-%m-%d")

            apply_to_all = 0

            #if hasattr(tree_widget,'apply_to_all_dict'):

                #apply_to_all = tree_widget.apply_to_all_dict.get(id(item),False)



            checkbox_widget = tree_widget.itemWidget(item,2)

            # Also check the checkbox widget directly
            if checkbox_widget:


                if apply_to_all == 0 and checkbox_widget.isChecked():
                    apply_to_all = 1

            if apply_to_all == 1:
                checkbox_state = Qt.CheckState.Checked
            else:
                try:

                    checkbox_state = Qt.CheckState.Checked if checkbox_widget.isChecked() else Qt.CheckState.Unchecked
                except:
                    checkbox_state = Qt.CheckState.Unchecked


            check_state = item.checkState(0).value

            container = tree_widget.itemWidget(item,3)
            if container:
                combobox_widget = self.select_departments_for_kpi_page.get_widget_from_container(item,3,"combobox")
                date_widget = self.select_departments_for_kpi_page.get_widget_from_container(item,3,"date")
                if combobox_widget:
                    combobox_text = combobox_widget.currentText()
                else:
                    combobox_text = None

                if date_widget:
                    date_widget_date = date_widget.date().toString("yyyy-MM-dd")
                else:
                    date_widget_date = None

            else:
                combobox_text = None
                date_widget_date = None


            end_checkbox_widget = tree_widget.itemWidget(item,4)
            if end_checkbox_widget:
                end_check_state = 1 if end_checkbox_widget.isChecked() else 0
            else:
                end_check_state = None

            if self.existing_departments:
                dept_version = self.existing_departments[0]['version']
            else:
                dept_version = None

            department_data = {
            "department": item.text(0),
            "check_state": check_state, #if item.flags() & Qt.ItemFlag.ItemIsUserCheckable or checkbox_state == Qt.CheckState.Checked else None,
            #"date_data": tree_widget.itemWidget(item,1).date() if tree_widget.itemWidget(item,1) else None,
            "start_date": start_date,
            "check_box_state": checkbox_state,
            "apply_to_all":apply_to_all,
            "id":item.text(0),
            "field":item.text(0),
            "enddate_combobox": combobox_text,
            "end_date": date_widget_date,
            "enddate_check": end_check_state,
            "employees": process_employees(tree_widget.topLevelItem(i), apply_to_all),
            "version": dept_version

            }



            return department_data

        def process_employees(item, apply_to_all = False):
            employees = []
            for i in range(item.childCount()):
                child = item.child(i)
                # Get the date widget for employee
                date_widget = tree_widget.itemWidget(child, 1)
                start_date = None
                if date_widget:
                    try:
                        start_date = date_widget.date().toString("yyyy-MM-dd")

                    except:
                        start_date = datetime.now().strftime("%Y-%m-%d")

                #if apply_to_all:
                    #check_state = Qt.CheckState.Checked
                #else:
                check_state = child.checkState(0).value # if child.flags() & Qt.ItemFlag.ItemIsUserCheckable else Qt.CheckState.Checked

                user_role_data = child.data(0,Qt.ItemDataRole.UserRole)

                emp_container = tree_widget.itemWidget(child, 3)
                if emp_container:
                    emp_combobox = self.select_departments_for_kpi_page.get_widget_from_container(child,3,"combobox")
                    emp_date = self.select_departments_for_kpi_page.get_widget_from_container(child,3,"date")
                    if emp_combobox:
                        emp_combo_text = emp_combobox.currentText()
                    else:
                        emp_combo_text = None

                    if emp_date:
                        emp_date_text = emp_date.date().toString("yyyy-MM-dd")
                    else:
                        emp_date_text = None
                else:
                    emp_combo_text = None
                    emp_date_text = None

                kpi_list = []
                if child.childCount() > 0:
                    kpi_list = process_kpis(child)

                if self.existing_employees:
                    emp_version = self.existing_employees[0]['version']
                else:
                    emp_version = None

                employee_data = {
                    "id": user_role_data[0],
                    "field": user_role_data[1],
                    "start_date":start_date,
                    "check_state": check_state,
                    "department":item.text(0),
                    "name":child.text(0),
                    "combo_text":emp_combo_text,
                    "end_date":emp_date_text,
                    "kpis":kpi_list,
                    'version':emp_version
                }
                employees.append(employee_data)

            return employees

        def process_kpis(item):
            kpis = []
            for i in range(item.childCount()):
                child = item.child(i)
                check_state = child.checkState(0).value
                user_role_data = child.data(0,Qt.ItemDataRole.UserRole)
                print(user_role_data)
                kpi_data = {
                    "id": user_role_data[0],
                    "field": user_role_data[1],
                    "check_state": check_state,
                    "employee": item.data(0, Qt.ItemDataRole.UserRole)[0] if item.data(0, Qt.ItemDataRole.UserRole) else None
                }


                kpis.append(kpi_data)

            return kpis

        for i in range(tree_widget.topLevelItemCount()):
            kpi_application_dict["departments"].append(process_departments(tree_widget.topLevelItem(i)))
            #kpi_application_dict["employees"].append(process_employees(tree_widget.topLevelItem(i)))

        self.selected_data = kpi_application_dict
        print("kpi_application_dict")
        for i in kpi_application_dict["departments"]:
            print(i)

        self.tree_widget.changes_in_emp_list = False
        print("self.existing_departments: ")
        for i in self.existing_departments:
            print(i)
        preselected_departments = [dept['department_name'] for dept in self.existing_departments]
        print("self.existing_employees: ")
        for i in self.existing_employees:
            print (i)
        selected_departments = [{"department_name":dep['department'],"check_state":dep['check_state'],"start_date":dep['start_date'],"end_date":dep['end_date'],"apply_to_all":dep['apply_to_all'],"enddate_combobox":dep['enddate_combobox'],"enddate_check":dep['enddate_check']} for dep in kpi_application_dict["departments"] if dep['check_state'] != 0]
        for dep in selected_departments:
            print(dep)
        preselected_employees = [emp["employee_id"] for emp in self.existing_employees]
        selected_employees = []
        for dpt in kpi_application_dict["departments"]:
            for empl in dpt["employees"]:
                if empl["check_state"] != 0:
                    selected_employees.append({"employee_id":empl["id"],"employee_name":empl["field"],"start_date":empl['start_date'],"check_state":empl['check_state'],"combo_text":empl['combo_text'],"end_date":empl['end_date']})
        for emp in selected_employees:
            print(emp)
        dept_changes_list = []
        dep_ind = ['check_state','start_date','apply_to_all','enddate_combobox','end_date','enddate_check']
        dep_ind_dict={'check_state':'Department checkbox','start_date':'Start date','apply_to_all':'Apply to all: start date','enddate_combobox':'End date type','end_date':'End date','enddate_check':'Apply to all: end date'}

        emp_changes_list = []
        emp_ind = ['check_state', 'start_date', 'end_date', 'combo_text']
        emp_ind_dict = {'check_state': 'Employee checkbox', 'start_date': 'Start date', 'end_date': 'End date',
                        'combo_text': 'End date type'}
        print("self.existing_employees", self.existing_employees)

        def checkbox_text(deptoremp,tablecolumn,temp_changes):
            checkbox_value = ''
            if str(temp_changes[tablecolumn]) == '0':
                checkbox_value = "Unchecked"
            elif str(temp_changes[tablecolumn]) == '2':
                checkbox_value = "Checked"
            elif str(temp_changes[tablecolumn]) == '1':
                if temp_changes[1] == 'apply_to_all' or "enddate_check":
                    checkbox_value = "Checked"
                else:
                    checkbox_value = "Partially checked"

            else:
                checkbox_value = temp_changes[tablecolumn]
            return checkbox_value

        def create_changes_list(exist,new,diff,ind_list,ind_dict):
            changes_list = []
            if False in diff:
                self.tree_widget.changes_in_emp_list = True
                change_ind = -1
                for i in range(diff.count(False)):
                    change_ind = diff.index(False,change_ind+1)
                    if 'department_name' in exist.keys():
                        changes_temp = [exist['department_name'],ind_list[change_ind],exist[ind_list[change_ind]],new[ind_list[change_ind]]]
                        print('changes_temp: ',changes_temp)
                        changes_list.append((new['department_name'],ind_dict[ind_list[change_ind]],checkbox_text('department',2,changes_temp),checkbox_text('department',3,changes_temp)))
                        print('changes_list: ',changes_list)
                    else:
                        changes_temp = [exist['employee_id'],new['employee_name'],ind_list[change_ind],exist[ind_list[change_ind]],new[ind_list[change_ind]]]
                        print('changes_temp: ', changes_temp)
                        changes_list.append((new['employee_name'],ind_dict[ind_list[change_ind]],checkbox_text('employee',3,changes_temp),checkbox_text('employee',4,changes_temp),empl['employee_id']))
                        print('changes_list: ', changes_list)
            return changes_list

        listed_deps = []
        for dep in self.existing_departments:
            listed_deps.append(dep['department_name'])
        for dep in self.existing_departments:
            for dept in selected_departments:
                if dep['department_name']==dept["department_name"]:

                    dep_diff = [str(dep[dep_ind[0]])==str(dept[dep_ind[0]]),dep[dep_ind[1]]==dept[dep_ind[1]],dep[dep_ind[2]]==dept[dep_ind[2]],dep[dep_ind[3]]==dept[dep_ind[3]],dep[dep_ind[4]]==dept[dep_ind[4]],dep[dep_ind[5]]==dept[dep_ind[5]]]
                    print("dep_diff: ",dep_diff)
                    dept_changes = create_changes_list(dep, dept, dep_diff,dep_ind,dep_ind_dict)
                    dept_changes_list += dept_changes
                elif dept['department_name'] not in listed_deps:

                    dep_diff = [str(dep[dep_ind[0]]) == str(0), dep[dep_ind[1]] == '1900-01-01',dep[dep_ind[2]] == 0, dep[dep_ind[3]] == '',dep[dep_ind[4]] == '1900-01-01', dep[dep_ind[5]] == 0]
                    print("dep_diff: ", dep_diff)
                    dept_changes = create_changes_list(dep,dept,dep_diff,dep_ind,dep_ind_dict)

                    dept_changes_list +=dept_changes
        print("dept_changes_list: ",dept_changes_list)

        listed_emps=[]
        for emp in self.existing_employees:
            listed_emps.append(emp['employee_id'])
        for emp in self.existing_employees:
            for empl in selected_employees:
                if emp['employee_id']==empl['employee_id']:
                    emp_diff = [str(emp[emp_ind[0]])==str(empl[emp_ind[0]]),emp[emp_ind[1]]==empl[emp_ind[1]],emp[emp_ind[2]]==empl[emp_ind[2]],emp[emp_ind[3]]==empl[emp_ind[3]]]
                    print("emp_diff: ",emp_diff)
                    emp_changes = create_changes_list(emp, empl,emp_diff,emp_ind,emp_ind_dict)
                    emp_changes_list += emp_changes
                elif emp['employee_id'] not in listed_emps:
                    emp_diff = [str(emp[emp_ind[0]])==str(0),emp[emp_ind[1]]=='1900-01-01',emp[emp_ind[2]]=='1900-01-01',emp[emp_ind[3]]=='']
                    print("emp_diff: ", emp_diff)
                    emp_changes = create_changes_list(emp, empl, emp_diff,emp_ind,emp_ind_dict)
                    emp_changes_list += emp_changes

        print("emp_changes_list: ",emp_changes_list)


        self.order_required = self.tree_widget.changes_in_emp_list
        self.dpt_changes = dept_changes_list
        self.emp_changes = emp_changes_list
        return kpi_application_dict, self.tree_widget.changes_in_emp_list, dept_changes_list, emp_changes_list

    def get_selected_data(self):

        return self.selected_data

    def preload_existing_selection(self,selected_departments, selected_employees):
        """Pre-populate the tree existing selections.
        Args:
            selected_departments: List of dics with department_name, start_date, end_date
            selected_employees: List of dicts with employee_id, start_date, end_date"""

        if not hasattr(self, 'tree_widget'):
            return

        # Pre-check departments
        for dept in selected_departments:
            dept_name = dept.get("department_name")
            start_date = dept.get("start_date")

            # Find the department item in the tree
            for i in range(self.tree_widget.topLevelItemCount()):
                item = self.tree_widget.topLevelItem(i)
                if item.text(0) == dept_name:
                    # Check the department
                    item.setCheckState(0, Qt.CheckState.Checked)

                    # Set the date widget
                    date_widget = self.tree_widget.itemWidget(item,1)
                    if date_widget and start_date:
                        date_widget.setDate(QDate.fromString(start_date,"yyyy-MM-dd"))

                    # Expand to show employees
                    item.setExpanded(True)
                    break

            # Pre-check employees
            for emp in selected_employees:
                emp_id = emp.get("employee_id")
                start_date = emp.get("start_date")

                # Find and check the employee
                for i in range(self.tree_widget.topLevelItemCount()):
                    department_item = self.tree_widget.topLevelItem(i)
                    for j in range(department_item.childCount()):
                        employee_item = department_item.child(j)
                        if employee_item.data(0,Qt.ItemDataRole.UserRole) == emp_id:
                            employee_item.setCheckState(0, Qt.CheckState.Checked)

                            # Set the date widget
                            date_widget = self.tree_widget.itemWidget(employee_item,1)
                            if date_widget and start_date:
                                date_widget.setDate(QDate.fromString(start_date,"yyyy-MM-dd"))

                            break






if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmployeeSelectionForKPI()
    window.show()
    sys.exit(app.exec())