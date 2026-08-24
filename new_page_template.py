from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QLineEdit, QTableWidgetItem,
                             QComboBox, QTableWidget, QHeaderView, QAbstractScrollArea, QMenu, QTreeWidget,
                             QTreeWidgetItem, QCheckBox, QDateEdit, QSizePolicy, QMessageBox)

from PyQt6.QtGui import QColor, QTextCharFormat

from datetime import datetime, date
import calendar


class NewPageTemplate(QWidget):
    def __init__(self,title,search_widgets = [],central_widgets = [],button_widgets = []):
        super(). __init__()
        self.title = title
        self.filtered_table = None
        self.list_to_filter = []
        self.filtered_elements = []
        self.combo_box = None
        self.search_input = None

        self.layout = QVBoxLayout(self)
        self.header_layout = QHBoxLayout()
        self.search_and_filters_layout = QHBoxLayout()
        self.central_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.search_widgets = search_widgets
        self.central_widgets = central_widgets
        self.button_widgets = button_widgets



    def create_header_layout(self):
        title_lable = QLabel(self.title)
        title_lable.setStyleSheet("font-size:16px; font-weight: bold, color: #2c3e50;")
        self.header_layout.addWidget(title_lable)
        self.header_layout.addStretch()
        return self.header_layout

    def create_search_and_filters_layout(self):

        self.filter_group = QGroupBox("Search and filters")
        if self.search_widgets:
            for widg in self.search_widgets:
                self.search_and_filters_layout.addWidget(widg)

        self.search_and_filters_layout.addStretch()
        self.filter_group.setLayout(self.search_and_filters_layout)
        return self.filter_group

    def create_central_layout(self):
        if self.central_widgets:
            for widg in self.central_widgets:
                self.central_layout.addWidget(widg)

                if isinstance(widg, (QTreeWidget, QTableWidget)):
                    widg.setSizePolicy(
                        QSizePolicy.Policy.Expanding,
                        QSizePolicy.Policy.Expanding
                    )
                    widg.setMinimumHeight(600)
                    widg.setMaximumHeight(700)
                    widg.setMaximumWidth(1000)



        return self.central_layout

    def create_buttons_layout(self):
        if self.button_widgets:
            for widg in self.button_widgets:
                self.button_layout.addWidget(widg)

        self.button_layout.addStretch()

        return self.button_layout

    def create_layout(self):
        self.create_header_layout()
        #if hasattr(self,'filter_group'):
        self.create_search_and_filters_layout()
        self.create_central_layout()
        self.create_buttons_layout()
        self.layout.addLayout(self.header_layout)
        #if hasattr(self,'filter_group'):
        self.layout.addWidget(self.filter_group)
        self.layout.addLayout(self.central_layout,stretch = 1)
        self.layout.addLayout(self.button_layout)

    def create_search_text_tool(self,list_to_filter,search_fields,filtered_table):
        self.list_to_filter = list_to_filter
        self.filtered_table = filtered_table
        search_widgets_extention = []
        search_widgets_extention.append(QLabel("Search:"))
        #self.search_and_filters_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(f"Search by {', '.join(search_fields)}...")
        self.search_input.setMinimumWidth(200)

        self.search_input.setText(" ")


        self.search_input.textChanged.connect(lambda text: self.filtering_tool())
        self.filtering_tool()
        search_widgets_extention.append(self.search_input)
        #self.search_and_filters_layout.addWidget(self.search_input)
        #self.layout.activate()
        return search_widgets_extention

    def filtering_tool(self):

        if not self.list_to_filter:
            self.filtered_table.setRowCount(0)
            if self.filtered_table.columnCount()>0:
                header_item = self.filtered_table.horizontalHeaderItem(0)
                header_text = header_item.text() if header_item else "items"
                header_text = header_text.split()[0].lower() if header_text else "items"

            else:
                header_text = "items"

            self.filtered_table.setRowCount(1)
            placeholder_item = QTableWidgetItem(f"No {header_text} found")
            placeholder_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.filtered_table.setSpan(0,0,1,self.filtered_table.columnCount())
            self.filtered_table.setItem(0,0,placeholder_item)
            return

        if self.filtered_table:

            if hasattr(self, "search_input") and self.search_input:

                search_text = self.search_input.text().lower().strip()
                self.filtered_elements = []

                for element in self.list_to_filter:
                    if not search_text:
                        self.filtered_elements.append(element)
                        continue

                    matches = False

                    for value in element.values():
                        if str(search_text) in str(value).lower():
                            matches = True
                            break

                    if matches:
                        self.filtered_elements.append(element)

            if hasattr(self, "combo_box") and self.combo_box and hasattr(self,"column_to_filter"):
                print("Combo_box text: ",self.combo_box.currentText())


                if len(self.filtered_elements) < len(self.list_to_filter):
                    filtered_list = self.filtered_elements.copy()
                else:
                    filtered_list = self.list_to_filter.copy()


                self.filtered_elements = []

                combo_box_text = self.combo_box.currentText()
                if combo_box_text and combo_box_text !=self.combo_list[0]:

                    for element in filtered_list:

                        if element["_".join(self.column_to_filter.lower().split(" "))] == combo_box_text:
                            self.filtered_elements.append(element)


                elif combo_box_text == self.combo_list[0]:
                    self.filtered_elements = filtered_list
            else:
                print("There is no Combo_box")
            if hasattr(self, "date_search_tool"):
                if len(self.filtered_elements) < len(self.list_to_filter):
                    filtered_list = self.filtered_elements.copy()
                else:
                    filtered_list = self.list_to_filter.copy()
                self.filtered_elements = []
                for element in filtered_list:
                    print(element)
                    print(element["_".join(self.date_column.lower().split(" "))])
                    element_date = date.fromisoformat(element["_".join(self.date_column.lower().split(" "))])
                    print(element_date,self.search_date1.date())
                    if element_date >= self.search_date1.date() and element_date <= self.search_date2.date():
                        self.filtered_elements.append(element)


            print("filtered elements: ",self.filtered_elements)
            self.display_elements(self.filtered_elements,self.filtered_table)

    def combo_box_tool(self,combo_box_label,combo_list,filtered_table,column_to_filter,list_to_filter):
        combo_label = QLabel(combo_box_label)
        self.combo_box = QComboBox()
        self.combo_box.addItems(combo_list)
        self.column_to_filter = column_to_filter
        self.filtered_table = filtered_table
        self.list_to_filter = list_to_filter
        self.combo_list = combo_list


        self.combo_box.currentTextChanged.connect(lambda text: self.filtering_tool())
        self.filtering_tool()
        search_widgets_extention = [combo_label,self.combo_box]

        return search_widgets_extention

    def date_range_tool (self, date1, date2, date_column):
        self.date_label1 = date1[0]
        self.search_date1 = date1[1]
        self.date_label2 = date2[0]
        self.search_date2 = date2[1]
        self.date_search_tool = True
        self.date_column = date_column
        self.search_date1.dateChanged.connect(lambda date_val:self.filtering_tool())
        self.search_date2.dateChanged.connect(lambda date_val:self.filtering_tool())
        return (self.date_label1,self.search_date1,self.date_label2,self.search_date2)


    def display_elements(self,elements,filtered_table):
        """Displays elements of qtable widget
        elements - list of dictionaries where keys - names of tables columns and values - values for table rows
        filtered_table - table to be populated"""

        if filtered_table:
            self.filtered_table = filtered_table

        if self.filtered_table:
            print("filtered table = True")
        if elements:
            self.filtered_table.setRowCount(len(elements))
            dict_length = elements[0].__len__()
            for row_ind, element in enumerate(elements):
                element_list = list(element.values())

                for i in range(self.filtered_table.columnCount()):
                    print("_".join(self.filtered_table.horizontalHeaderItem(i).text().lower().split(" ")))
                    print(element["_".join(self.filtered_table.horizontalHeaderItem(i).text().lower().split(" "))])
                    element_item = QTableWidgetItem(str(element["_".join(self.filtered_table.horizontalHeaderItem(i).text().lower().split(" "))]))

                    if "id" in element.keys():
                        element_item.setData(Qt.ItemDataRole.UserRole,element["id"])
                    self.filtered_table.setItem(row_ind,i,element_item)
        else:
            self.filtered_table.setRowCount(0)


    def refresh_with_filters(self, new_data, filtered_table):
        """Refresh the display with new data while appliying current filters"""
        self.list_to_filter = new_data
        self.filtered_table = filtered_table

        self.filtering_tool()

    def create_qtablewidget_tool(self,column_count,header_labels,double_clicked_method,context_actions = []):
        self.context_actions = context_actions
        self.header_labels = header_labels
        new_table = QTableWidget()
        new_table.setColumnCount(column_count)
        new_table.setHorizontalHeaderLabels(self.header_labels)
        header = new_table.horizontalHeader()
        header.setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1,QHeaderView.ResizeMode.ResizeToContents)
        new_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        new_table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        if double_clicked_method:
            new_table.itemDoubleClicked.connect(double_clicked_method)
            new_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            new_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            new_table.customContextMenuRequested.connect(self.show_context_menu)

        return new_table

    def show_context_menu(self,position):
        menu = QMenu()

        copy_action = menu.addAction("Copy")
        edit_action = menu.addAction("Edit")
        remove_action = menu.addAction("Remove")

        table = self.sender()

        if table:

            action = menu.exec(table.viewport().mapToGlobal(position))

            if action == copy_action:
                self.copy_selected_item(table)
            elif action == edit_action:
                self.edit_selected_item(table)
            elif action == remove_action:
                self.remove_selected_item(table)

    def copy_selected_item(self,table,context_actions):

        if len(self.context_actions) >= 1 and self.context_actions[0]:
            self.context_actions[0](table)

    def edit_selected_item(self,table):
        if len(self.context_actions) >=2 and self.context_actions[1]:
            self.context_actions[1](table)

    def remove_selected_item(self,table):
        if len(self.context_actions) >= 3 and self.context_actions[2]:
            self.context_actions[2](table)


    def create_qtreewidget_tool(self,column_count,header_labels,list_for_tree, fields_for_tree,add_widgets=[]):
        #self.list_for_tree = list_for_tree
        #self.fields_for_tree = fields_for_tree
        header_labels = ["/".join(fields_for_tree)]+header_labels

        self.tree = QTreeWidget()
        self.tree.setColumnCount(column_count)
        self.tree.setHeaderLabels(header_labels)

        self.tree._updating_flags = False

        self.tree.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.tree.setMinimumHeight(200)
        self.tree.setMaximumHeight(500)

        self.tree.list_for_tree = list_for_tree
        self.tree.fields_for_tree = fields_for_tree
        self.tree.column_widgets = add_widgets


        #self.tree.count_dict = 1
        self.tree.count_dict = 0
        #self.populate_tree(self.tree,self.create_dict_for_tree())

        self.populate_tree_new(self.tree, self.create_dict_for_tree_new())

        return self.tree

    def populate_tree_new(self,tree_widget,data,parent = None, current_level = 0):

        # if type(data) is list:
        #     for element in data:
        #         item = QTreeWidgetItem(parent)
        #         item.setText(0,element["field"])
        #         user_role_data = [element["id"],element["field"]]
        #         item.setData(0,Qt.ItemDataRole.UserRole,user_role_data)
        #         item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        #         item.setCheckState(0, Qt.CheckState.Unchecked)
        # else:

        def populate_tree_inner(tree_widget,data,parent = None):
            for i in data:
                for key,value in i.items():
                    if parent == None:
                        item = QTreeWidgetItem(tree_widget)
                    else:
                        item = QTreeWidgetItem (parent)

                    item.setText(0, value[0]["field"])
                    user_role_data = [key, value[0]["field"]]
                    item.setData(0,Qt.ItemDataRole.UserRole,user_role_data)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsAutoTristate)
                    item.setCheckState(0, Qt.CheckState.Unchecked)
                    item.setExpanded(True)
                    if  value[1] != []:

                        populate_tree_inner(tree_widget,value[1],item)


        populate_tree_inner(tree_widget,data)
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(False)
        self.tree.resizeColumnToContents(2)

    def populate_tree(self,tree_widget,data, parent = None):



        for value in list(data.values())[self.tree.count_dict-1]:
            self.tree.count_dict -= 1

            if parent is None:
                item = QTreeWidgetItem(tree_widget)
                if self.tree.fields_for_tree[self.tree.count_dict] != 'employee':
                    item.setText(0, str(value[self.tree.fields_for_tree[self.tree.count_dict].lower()]))
                    if "id" in value.keys():
                        item.setData(0,Qt.ItemDataRole.UserRole,value["id"])
                else:

                    item.setText(0, f'{value["last_name"]} {value["first_name"]} {value["father_name"]}')
                    user_role_data = {"id":value["id"],"first_name":value["first_name"],"last_name":value["last_name"]}
                    item.setData(0,Qt.ItemDataRole.UserRole,user_role_data)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsAutoTristate)
                item.setCheckState(0, Qt.CheckState.Unchecked)
            else:
                #item = QTreeWidgetItem(parent)

                #print(value[self.tree.fields_for_tree[self.tree.count_dict-1]])
                #if value[self.tree.fields_for_tree[self.tree.count_dict-1]] == parent:
                if value[0] == parent.text(0):

                    for element in value[1]:

                        item = QTreeWidgetItem(parent)
                        if self.tree.fields_for_tree[self.tree.count_dict] != 'employee':
                            item.setText(0,str(value[self.tree.fields_for_tree[self.tree.count_dict].lower()]))
                        else:
                            print("Value = ",value)
                            item.setText(0,f'{element["last_name"]} {element["first_name"]} {element["father_name"]}')
                            user_role_data = {"id":element["id"],"first_name":element["first_name"],"last_name":element["last_name"],"father_name":element["father_name"]}
                            item.setData(0, Qt.ItemDataRole.UserRole, user_role_data)
                        item.setFlags(item.flags()|Qt.ItemFlag.ItemIsUserCheckable|Qt.ItemFlag.ItemIsAutoTristate)
                        item.setCheckState(0,Qt.CheckState.Unchecked)

            self.tree.count_dict +=1

            if self.tree.count_dict < self.tree.lenth - 1:
            #if self.tree.count_dict < self.tree.lenth-1:
                self.tree.count_dict +=1
                self.populate_tree(tree_widget,data,item)
            else:
                print(list(data.values())[self.tree.count_dict])
                for value in list(data.values())[self.tree.count_dict]:
                    if value[0] == item.text(0):
                        for element in value[1]:
                            print("value =",value)
                            print("element =",element)

                            child = QTreeWidgetItem(item)
                            if self.tree.fields_for_tree[self.tree.count_dict] != 'employee':
                                child.setText(0, str(element[self.tree.fields_for_tree[self.tree.count_dict].lower()]))
                            else:
                                child.setText(0, f'{element["last_name"]} {element["first_name"]} {element["father_name"]}')
                                user_role_data = {"id":element["id"],"last_name":element["last_name"],"first_name":element["first_name"],"father_name":element["father_name"]}
                                child.setData(0,Qt.ItemDataRole.UserRole,user_role_data)
                            child.setFlags(child.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsAutoTristate)
                            child.setCheckState(0, Qt.CheckState.Unchecked)

        header = self.tree.header()
        header.setSectionResizeMode(0,QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1,QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(False)
        self.tree.resizeColumnToContents(2)



            #self.tree.itemChanged.connect(self.on_item_changed)

        #self.tree.expandAll()

    def on_date_check_changed(self,tree,state,item_one,column):
        print(f"DEBUG on_date_check_changed: state={state}, item={item_one.text(0)}")
        if state == 2:
            # Store the "apply to all" state IMMEDIATELY, before any other operations
            #item_one.setData(0, Qt.ItemDataRole.UserRole + 1, True)
            #print(f"DEBUG: Set apply_to_all=True for {item_one.text(0)}")
            #print(f"DEBUG: Verify data stored: {item_one.data(0, Qt.ItemDataRole.UserRole + 1)}")  # Verify immediately

            if item_one.checkState(0) == Qt.CheckState.Unchecked:
                item_one.setCheckState(0,Qt.CheckState.Checked)
                item_one.setExpanded(True)

            item_one_date_widget = self.tree.itemWidget(item_one,column-1)
            if item_one_date_widget:
                item_one_date = item_one_date_widget.date()

            for i in range(item_one.childCount()):
                child = item_one.child(i)
                child_date_widget = self.tree.itemWidget(child,column-1)
                if child_date_widget:
                    child_date_widget.setDate(item_one_date)
                    child_date_widget.setReadOnly(True)
                    child_date_widget.setStyleSheet("""
                    QDateEdit {
                    color: #707070;
                    }
                    QDateEdit QAbstractItemView {
                    color: #707070;  /* Color for dates in the calendar popup */
                    background-color: #FFFFFF;
                    }
                    """)


                    child_flags = child.flags()
                    child.setFlags(child_flags & ~Qt.ItemFlag.ItemIsUserCheckable)
                    #child.setDisabled(True)
            current_flags = item_one.flags()
            item_one.setFlags(current_flags & ~Qt.ItemFlag.ItemIsUserCheckable)
            #item_one.setDisabled(True)

            # Store apply_to_al  as an attribute of the tree widget
            if not hasattr(self.tree, 'apply_to_all_dict'):
                self.tree.apply_to_all_dict = {}
            self.tree.apply_to_all_dict[id(item_one)] = True



        else:

            #item_one.setData(0, Qt.ItemDataRole.UserRole + 1, False)
            #print(f"DEBUG: Set apply_to_all=False for {item_one.text(0)}")

            for i in range(item_one.childCount()):
                child = item_one.child(i)
                child_date_widget = self.tree.itemWidget(child,column-1)
                if child_date_widget:

                    child_date_widget.setReadOnly(False)
                    child_date_widget.setStyleSheet("""
                            QDateEdit {
                            color: #222222;
                        }
                        QDateEdit QAbstractItemView {
                            color: #222222;  /* Color for dates in the calendar popup */
                            background-color: #FFFFFF;
                        }
                        """)
                    child_flags = child.flags()
                    child.setFlags(child_flags | Qt.ItemFlag.ItemIsUserCheckable)
                #child.setDisabled(False)

            current_flags = item_one.flags()
            item_one.setFlags(current_flags | Qt.ItemFlag.ItemIsUserCheckable)
            #item_one.setDisabled(False)

            # Store apply_to_all as False
            if not hasattr(self.tree, 'apply_to_all_dict'):
                self.tree.apply_to_all_dict = {}
            self.tree.apply_to_all_dict[id(item_one)] = False


    def on_date_changed(self, item, tree,column):
        """Removes 'Apply to all' checkbox if the item date is changed """


        checkbox = tree.itemWidget(item,column+1)

        if checkbox:
            checkbox.setCheckState(Qt.CheckState.Unchecked)

    def create_dict_for_tree_new(self):

        self.tree.lenth = len(self.tree.list_for_tree)
        dict_for_tree = {}

        if self.tree.lenth > 1:
            minus_step = -1
            second_dict = []
            for step in range(self.tree.lenth - 1):

                interim_dict = []
                if minus_step == -1:
                    for i in self.tree.list_for_tree[-1]:
                        second_dict_key = i["id"]
                        second_dict.append ({second_dict_key: [i,[]]})


                for element in self.tree.list_for_tree[minus_step-1]:

                    interim_list = []
                    element_dict = {}
                    for j in second_dict:

                        for key, value in j.items():
                            if element["id"].lower() == value[0][self.tree.fields_for_tree[minus_step-1]].lower():

                                interim_list.append(j)
                    for key in element.keys():
                        if key != "id":
                            element_dict[key] = element[key]
                    interim_dict.append({element["id"]:[element_dict,interim_list]})
                minus_step -=1
                second_dict = interim_dict.copy()

        else:
            interim_dict = {}
            for element in self.tree.list_for_tree[-1]:
                element_dict = {}
                for key in element.keys():
                    if key != "id":
                        element_dict[key] = element[key]
            interim_dict[element["id"]] = [element_dict]
        dict_for_tree = interim_dict





        return dict_for_tree



    def create_dict_for_tree(self):

        self.tree.lenth = len(self.tree.list_for_tree)
        dict_for_tree = {}
        dict_for_tree_plus = {}

        first_list = []
        for element in self.tree.list_for_tree[0]:
            first_list.append(element)

        dict_for_tree_plus[0] = first_list

        if self.tree.lenth > 1:

            for j in self.tree.list_for_tree[-2]:

                dict_for_tree[j[self.tree.fields_for_tree[-2]]] = []
                for i in self.tree.list_for_tree[-1]:

                    if i[self.tree.fields_for_tree[-2]].lower() == j[self.tree.fields_for_tree[-2]].lower():
                        dict_for_tree[j[self.tree.fields_for_tree[-2]]].append(i)


        print(dict_for_tree)
        #new_list_for_tree = list(dict_for_tree.items())
        #print(new_list_for_tree)
        dict_for_tree_plus[self.tree.lenth-1]=list(dict_for_tree.items())
        print(dict_for_tree_plus)

        if self.tree.lenth < 3:
            return dict_for_tree_plus
        else:
            repeat = -3
            for step in range(self.tree.lenth-2):
                for j in self.tree.list_for_tree[repeat]:
                    dict_for_tree[j[self.tree.fields_for_tree[repeat]]] = []
                    for i in self.tree.list_for_tree[repeat+1]:
                        if i[self.tree.fields_for_tree[repeat]] == j[self.tree.fields_for_tree[repeat]]:
                            key = i[self.tree.fields_for_tree[repeat+1]]
                            value = dict_for_tree[key]
                            dict_for_tree[j[self.tree.fields_for_tree[repeat]]].append(i)
                            #dict_for_tree[j[self.tree.fields_for_tree[repeat]]].append({key:value})
                            dict_for_tree.pop(key)
                        dict_for_tree_plus[repeat+self.tree.lenth+1] = list(dict_for_tree.items())
                repeat -=1

        print(dict_for_tree_plus.items())
        # for key, value in dict_for_tree_plus.items():
        #     print(key,value)
        #     if key < self.tree.lenth - 1:
        #         new_value = []
        #         for element in value:
        #             values_list = []
        #             for dict_elem in element[1]:
        #                 values_list.append(list(dict_elem.keys())[0])
        #             element = element(element[0],values_list)
        #             new_value.append(element)
        #         dict_for_tree_plus[key] = new_value

        # first_list = []
        # for element in self.tree.list_for_tree[0]:
        #     first_list.append(element)
        #
        # dict_for_tree_plus[0]=first_list


        dict_for_tree_plus = dict(sorted(dict_for_tree_plus.items()))

        print(dict_for_tree)
        print(dict_for_tree_plus)
        return dict_for_tree_plus


    def create_widget_for_tree(self,widget_type,tree_widget,column=None,items_depth=None,changed_method=None,text = None):
        """Universal method for creation widgets for qTreeWidget
        widget_type - dict ex. {"date":[changed_method]},{"check_box":[changed_method]} for single widgets and  {"container":[{"combobox":[changed_method,[value1,value2,...]},{"date":changed_method}] for container with multiple widgets
        changed_method - the method called when the value of the widget is changed
        tree_widget - current tree
        column - number of column where the widget should be placed
        items_depth - levels of tree to which the widget should be placed, 0 for top level items, 1 for 1st level children, etc.
        text - widget text
        """

        def process_date_widget(item,item_depth,current_level):

            for level in item_depth:

                if current_level == level:

                    if item.childCount() > 0:
                        if "date" in widget_type.keys():

                            self.date_widget(tree_widget,item,widget_type["date"][0],column)
                        elif "check_box" in widget_type.keys():

                            self.check_box_widget(tree_widget,text,item,widget_type["check_box"][0],column)
                        elif "container" in widget_type.keys():

                            self.create_container_with_multiple_widgets(tree_widget, item, column,
                                                                        widget_type['container'])


                        for j in range(item.childCount()):
                            process_date_widget(item.child(j),item_depth,current_level+1)
                    else:
                        if "date" in widget_type.keys():

                            self.date_widget(tree_widget, item, widget_type["date"][0], column)
                        elif "check_box" in widget_type.keys():

                            self.check_box_widget(tree_widget, text, item, widget_type["check_box"][0], column)
                        elif type(widget_type) == dict and "container" in widget_type.keys():

                            self.create_container_with_multiple_widgets(tree_widget, item, column,
                                                                        widget_type['container'])


        for i in range(tree_widget.topLevelItemCount()):
            item = tree_widget.topLevelItem(i)

            if 0 in items_depth:

                if "date" in widget_type.keys():

                    self.date_widget(tree_widget,item,widget_type["date"][0],column)
                elif "check_box" in widget_type.keys():

                    self.check_box_widget(tree_widget,text,item,widget_type["check_box"][0],column)
                elif "container" in widget_type.keys():

                    self.create_container_with_multiple_widgets(tree_widget,item,column,widget_type['container'])
            if (not 0) in items_depth:
                if items_depth[0] == 0:
                    new_items_depth = items_depth[1:]
                else:
                    new_items_depth = items_depth.copy()
                for j in range(item.childCount()):

                    process_date_widget(item.child(j),new_items_depth,1)

        tree_widget.resizeColumnToContents(column)

    def date_widget(self,tree=None,item=None,change_method = None,column=1):
        """Calls creation of QDateEdit widget and places it to the passed column for the passed item
        tree - current tree
        item - current item
        change_method - the method called when the date value of the widget is changed
        column - the column where the widget should be placed
        """

        date = self.date_widget_inner(tree= tree, item = item, change_method = change_method, column = column)
        tree.setItemWidget(item, column, date)

    def date_widget_inner(self, tree= None, item = None, change_method = None,column = 1):
        """Creates and returns QDateEdit widget for the passed tree
        """
        date = QDateEdit()
        date.setCalendarPopup(True)
        date.setDate(datetime.now().date())
        if change_method:

            date.dateChanged.connect(lambda date_val, i=item, t=tree, c=column: change_method(i, t, c))  #date_val - the new date value of the widget

        return date

    def enforce_first_of_the_month(self,selected_date):
        """ Makes the first of each month the only valid selection for date_widget"""

        forced_date = None
        if selected_date.day() !=1:
            if selected_date.month() == 12:
                month = 1
            else:
                month = selected_date.month()+1

            if month == 1:
                year = selected_date.year()+1
            else:
                year = selected_date.year()

            forced_date = QDate(year, month,1)
        else:
            forced_date = selected_date

        return forced_date

    def create_inactive_calendar_style(self, date_widget=None):
        today = date.today().day
        print(type(today)," ",today)

        start_date = QDate(date.today().year,date.today().month,1)

        end_date = start_date.addYears(5)
        print("start_date: ",start_date)
        print("end_date: ",end_date)

        date_widget.setMinimumDate(start_date)
        #date_widget.setDate(start_date)
        self.calendar = date_widget.calendarWidget()


        self.calendar.setStyleSheet("""
             /* Remove grey hover background for disabled calendar dates */
             QCalendarWidget QAbstractItemView::item[day=1] {
                color: #000000 !important;
                }
                
             QCalendarWidget QAbstractItemView::item: inactive {
                color: #bebebe !important;
                }   
             
             QCalendarWidget QAbstractItemView {
                
                background-color: #f8f8f8; 
                selection-background-color: transparent;
                selection_color: #000000}
                
             QCalendarWidget QAbstractItemView::item:hover {
                background-color: #f8f8f8;
                }
        """)


        try:
            self.calendar.currentPageChanged.disconnect(self.on_month_changed)
        except TypeError:
            pass
        self.calendar.currentPageChanged.connect(self.on_month_changed)
        self.on_month_changed(date.today().year, date.today().month)
        #self.enforce_first_of_the_month(date_widget.date())
        return date_widget

    def on_month_changed(self, year: int, month: int):

        fmt = QTextCharFormat()
        #fmt.setBackground(QColor("#f8f8f8"))
        fmt.setForeground(QColor("#bebebe"))
        fmt_first = QTextCharFormat()
        #fmt_first.setBackground(QColor("transparent"))
        fmt_first.setForeground(QColor("#000000"))
        visible_dates = self.get_visible_dates_on_page(self.calendar)
        print(visible_dates)

        for day in visible_dates:
            if day.day() == 1:
                print(f"Found 1st: {day} - Month: {day.month()}")

        empty_fmt = QTextCharFormat()
        for day in visible_dates:
            self.calendar.setDateTextFormat(day, empty_fmt)



        for day in visible_dates:
            if day.day() == 1:
                print(f"Setting BLACK for: {day}")
                self.calendar.setDateTextFormat(day, fmt_first)
            else:
                print(f"Setting GRAY for: {day}")
                self.calendar.setDateTextFormat(day, fmt)

        self.calendar.update()

        # while curr <= end_date:
        #     if curr.day() != 1:
        #         calendar.setDateTextFormat(curr, fmt)


            #curr = curr.addDays(1)

    def get_visible_dates_on_page(self, calendar):
        year = calendar.yearShown()
        month = calendar.monthShown()
        first_of_month = QDate(year, month, 1)
        print(first_of_month.dayOfWeek())
        first_day_of_week = calendar.firstDayOfWeek().value
        print(first_day_of_week)
        day_offset = (first_of_month.dayOfWeek() - first_day_of_week)%7
        grid_start_date = first_of_month.addDays(-day_offset)
        visible_dates = []
        for i in range(42):
            current_date = grid_start_date.addDays(i)
            visible_dates.append(current_date)

        return visible_dates

    def check_box_widget (self, tree= None, text = None, item=None, changed_status = None,column=2):
        """ Creates checkbox widget for the passed tree:
        tree - current tree
        text - widget text
        item - current item
        changed status - the method called when the checkbox status is changed
        column - the column where the checkbox is placed
        """

        self.date_check = QCheckBox(text)
        self.date_check.setChecked(False)
        self.date_check.stateChanged.connect(lambda state, t = tree, d=item, c = column: changed_status(t, state, d, c))  # check_box state
        self.tree.setItemWidget(item, column, self.date_check)

    def on_end_date_check_changed(self,tree,state,item_one, column):

        if state == 2:
            item_widget = self.tree.itemWidget(item_one,column - 1)
            if item_widget.layout():
                container_info = {'children':[]}
                for i in range(item_widget.layout().count()):
                    child = item_widget.layout().itemAt(i).widget()
                    if child:
                        child_info = {
                            'type':type(child).__name__,
                            'widget':child,
                            'object_name': child.objectName(),
                            'is_enabled':child.isEnabled(),
                            'is_visible':child.isVisible()
                        }

                        container_info['children'].append(child_info)


                if container_info['children'][0]['type'] == "QComboBox":
                    if container_info['children'][1]['type'] == "QDateEdit":
                        combobox_widget = container_info['children'][0]['widget']
                        date_widget = container_info['children'][1]['widget']
                        for j in range(item_one.childCount()):
                            item_child = item_one.child(j)
                            item_child_widget = self.tree.itemWidget(item_child,column-1)
                            child_combo = item_child_widget.layout().itemAt(0).widget()
                            child_date = item_child_widget.layout().itemAt(1).widget()
                            child_combo.setCurrentText(item_widget.layout().itemAt(0).widget().currentText())
                            child_combo.setEnabled(False)

                            if child_combo.currentText() != "Open date":
                                child_date.setDate(item_widget.layout().itemAt(1).widget().date())
                                child_date.setReadOnly(True)
                                child_date.setStyleSheet("""
                                QDateEdit {
                                color: #707070;
                                }
                                QDateEdit QAbstractItemView {
                                color: #707070;  /* Color for dates in the calendar popup */
                                background-color: #FFFFFF;
                                }
                                """)



            elif type(item_widget).__name__ == "QDateEdit":
                for j in range(item_widget.childCount()):
                    item_child = item_one.child(j)
                    item_child.setDate(item_widget.date())
                    item_widget.setReadOnly(True)
        else:
            item_widget = self.tree.itemWidget(item_one, column - 1)
            if item_widget.layout():
                container_info = {'children': []}
                for i in range(item_widget.layout().count()):
                    child = item_widget.layout().itemAt(i).widget()
                    if child:
                        child_info = {
                            'type': type(child).__name__,
                            'widget': child,
                            'object_name': child.objectName(),
                            'is_enabled': child.isEnabled(),
                            'is_visible': child.isVisible()
                        }

                        container_info['children'].append(child_info)


                if container_info['children'][0]['type'] == "QComboBox":
                    if container_info['children'][1]['type'] == "QDateEdit":
                        combobox_widget = container_info['children'][0]['widget']
                        date_widget = container_info['children'][1]['widget']
                        for j in range(item_one.childCount()):
                            item_child = item_one.child(j)
                            item_child_widget = self.tree.itemWidget(item_child, column - 1)
                            child_combo = item_child_widget.layout().itemAt(0).widget()
                            child_combo.setEnabled(True)
                            child_date = item_child_widget.layout().itemAt(1).widget()
                            child_date.setReadOnly(False)
                            child_date.setStyleSheet("""
                            QDateEdit {
                            color: #222222;
                        }
                        QDateEdit QAbstractItemView {
                            color: #222222;  /* Color for dates in the calendar popup */
                            background-color: #FFFFFF;
                        }
                        """)

    def date_widget_with_open_end_combobox(self, tree= None, item = None, change_method = None, column = 1):
        """Create a date widget with an Open End option using a combobox"""

        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0,0,0,0)
        container_layout.setSpacing(5)

        # Create date edit
        date = QDateEdit()
        date.setCalendarPopup(True)
        date.setDate(datetime.now().date())

        if change_method:
            date.dateChanged.connect(lambda _, item = item, tree=tree,column = column: change_method(item,tree,column))

        container_layout.addWidget(date)

        #Add combobox for date type selection

        if column == 3: #End date column
            date_type_combo = QComboBox()
            date_type_combo.addItems(["Specific Date", "Open End"])
            date_type_combo.setProperty("item",item)
            date_type_combo.setProperty("date_widget",date)

            date_type_combo.currentTextChanged.connect(lambda text,item=item,date_widget = date,combo = date_type_combo:self.on_date_type_changed(text,item,date_widget,combo))

            container_layout.addWidget(date_type_combo)

        tree.setItemWidget(item, column, container)
        return date

    def on_date_type_changed(self,text,item,date_widget,combo):
        if text == "Open End":
            date_widget.setEnabled(False)
            date_widget.setStyleSheet("QDateEdit{background_color:#fofofo; color: #888888;}")
            date_widget.setSpecialValueText("Open End")
            date_widget.setDate(datetime(2099,12,31).date())
        else:
            date_widget.setEnabled(True)
            date_widget.setStyleSheet("")
            date_widget.setSpecialValueText("")
            date_widget.setDate(datetime.now().date())

    def create_container_with_multiple_widgets(self,tree,item,column,content,changed_method = None):
        """Add multiple widgets to a single column
        tree -current tree
        item - current item
        column - column where the container should be placed
        content - list od dictionaries, where keys - widget names, values[0] - changed_method for relevant widget

        """
        # Create a container widget
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(5)

        content_keys = []
        content_widgets = []
        widget_refs = {}
        for i in range(len(content)):
            content_keys.append(list(content[i].keys())[0])
            if "date" in content[i].keys():

                date_edit = self.date_widget_inner(tree, item, content[i]['date'][0], column)
                #date_edit = self.date_widget_inner(tree,item,content[i]['date'],column)
                date_edit.setObjectName(f"date_{id(item)}_{column}")
                layout.addWidget(date_edit)
                content_widgets.append(date_edit)
                widget_refs["date"] = date_edit
            elif "combobox" in content[i].keys():

                combobox_widget = self.combobox_widget_inner(tree,item,content[i]["combobox"],column)
                combobox_widget.setObjectName(f"combobox_{id(item)}_{column}")
                layout.addWidget(combobox_widget)
                content_widgets.append(combobox_widget)
                widget_refs['combobox'] = combobox_widget

            item.widget_refs = widget_refs

            if not hasattr(item,"container_widgets"):
                self.container_widgets = {}
            self.container_widgets[id(item)] = {
                "container": container,
                "widgets": widget_refs
            }

        self.container_items_relationship(content_keys,content_widgets)

        tree.setItemWidget(item,column,container)

    def container_items_relationship(self,content_keys,content_widgets,widget_date=None):
        """Set relationship between container widgets
         content_keys - keys of dictionaries for widgets included in container
         content_widgets - list of widgets included in container
         """
        if content_keys == ["combobox","date"]:
            if content_widgets[0].currentText() == "Open date":
                content_widgets[1].setDate(datetime(1900,1,1).date())
                content_widgets[1].setReadOnly(True)
                content_widgets[1].setStyleSheet("""
            QDateEdit {
            color: #707070;
        }
        QDateEdit QAbstractItemView {
            color: #707070;  /* Color for dates in the calendar popup */
            background-color: #FFFFFF;
        }
        """)
            else:
                if widget_date:
                    content_widgets[1].setDate(widget_date)
                else:
                    content_widgets[1].setDate(datetime.now().date())
                content_widgets[1].setReadOnly(False)
                content_widgets[1].setStyleSheet("""
                                    QDateEdit {
                                    color: #222222;
                                }
                                QDateEdit QAbstractItemView {
                                    color: #222222;  /* Color for dates in the calendar popup */
                                    background-color: #FFFFFF;
                                }
                                """)

    def get_widget_from_container(self,item,column,widget_type):
        """Get a specific widget from a container using object name
        widget_type - ex. "combobox","date"
        """
        container = self.tree.itemWidget(item,column)
        if container:
            #Find by object name pattern
            widget = container.findChild(QWidget,f"{widget_type}_{id(item)}_{column}")
            return widget
        return None

    def create_comobobox_widget(self,tree,item,content,column):
        """ Calls creation of combobox widget and adds it the tree item
        tree - current tree
        item - current item
        content - list where [0] - chenged_method, [1] - combobox values
        column - the column where combobox should be placed
        """
        combobox_widget = self.combobox_widget_inner(tree,item,content,column)
        tree.setItemWidget(item,column,combobox_widget)

    def combobox_widget_inner(self,tree,item,content,column):
        """Creates and returns combobox widget for the passed tree item"""
        item = item
        column = column
        combo = QComboBox()
        combo.addItems(content[1])
        combo.currentTextChanged.connect(lambda text, t = tree, d=item, c = column: content[0](text,t,d,c))
        return combo

    def combobox_text_changed(self,text,tree,item,column):
        combobox_widget = self.get_widget_from_container(item,column,"combobox")
        date_widget = self.get_widget_from_container(item,column,"date")
        self.container_items_relationship(["combobox","date"],[combobox_widget,date_widget])
        self.on_date_changed(item,self.tree,column)























