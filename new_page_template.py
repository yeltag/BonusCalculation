from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QLineEdit, QTableWidgetItem,
                             QComboBox, QTableWidget, QHeaderView,QAbstractScrollArea,QMenu)


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
        #self.create_layout()
        #self.header_labels = []
        #self.context_actions = []


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

        self.central_layout.addStretch()

        return self.central_layout

    def create_buttons_layout(self):
        if self.button_widgets:
            for widg in self.button_widgets:
                self.button_layout.addWidget(widg)

        self.button_layout.addStretch()

        return self.button_layout

    def create_layout(self):
        self.create_header_layout()
        self.create_search_and_filters_layout()
        self.create_central_layout()
        self.create_buttons_layout()
        self.layout.addLayout(self.header_layout)
        self.layout.addWidget(self.filter_group)
        self.layout.addLayout(self.central_layout)
        self.layout.addLayout(self.button_layout)


        self.layout.addStretch()

    def create_search_text_tool(self,list_to_filter,search_fields,filtered_table):
        self.list_to_filter = list_to_filter
        self.filtered_table = filtered_table
        search_widgets_extention = []
        search_widgets_extention.append(QLabel("Search:"))
        #self.search_and_filters_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(f"Search by {', '.join(search_fields)}...")
        self.search_input.setMinimumWidth(200)
        print(type(self.list_to_filter))
        print(self.filtered_table.horizontalHeaderItem(0).text())
        self.search_input.setText(" ")
        print(type(self.search_input.text()))

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
                if combo_box_text and combo_box_text !="All departments":

                    for element in filtered_list:

                        if element[self.column_to_filter] == combo_box_text:
                            self.filtered_elements.append(element)


                elif combo_box_text == "All departments":
                    self.filtered_elements = filtered_list
            else:
                print("There is no Combo_box")

            print("filtered elements: ",self.filtered_elements)
            self.display_elements(self.filtered_elements,self.filtered_table)

    def combo_box_tool(self,combo_box_label,combo_list,filtered_table,column_to_filter,list_to_filter):
        combo_label = QLabel(combo_box_label)
        self.combo_box = QComboBox()
        self.combo_box.addItems(combo_list)
        self.column_to_filter = column_to_filter
        self.filtered_table = filtered_table
        self.list_to_filter = list_to_filter


        self.combo_box.currentTextChanged.connect(lambda text: self.filtering_tool())
        self.filtering_tool()
        search_widgets_extention = [combo_label,self.combo_box]

        return search_widgets_extention


    def display_elements(self,elements,filtered_table):
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
                    element_item = QTableWidgetItem(element[self.filtered_table.horizontalHeaderItem(i).text()])
                    self.filtered_table.setItem(row_ind,i,element_item)
        else:
            self.filtered_table.setRowCount(0)


    def refresh_with_filters(self, new_data, filtered_table):
        """Refrsh the display with new data while appliying current filters"""
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












