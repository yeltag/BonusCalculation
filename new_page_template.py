from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget,QVBoxLayout, QHBoxLayout,QLabel,QGroupBox,QLineEdit,QTableWidgetItem,QComboBox)


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
        self.filtered_elements = []


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

        search_widgets_extention = []
        search_widgets_extention.append(QLabel("Search:"))
        #self.search_and_filters_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(f"Search by {', '.join(search_fields)}...")
        self.search_input.setMinimumWidth(200)
        print(type(list_to_filter))
        print(filtered_table.horizontalHeaderItem(0).text())
        self.search_input.setText(" ")
        print(type(self.search_input.text()))

        self.search_input.textChanged.connect(lambda text: self.filtering_tool())

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
            placeholder_item.setTextAlighnment(Qt.AlignmentFlag.AlignCenter)
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
                        if search_text in value.lower():
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
                print("Combo_box text: ", self.combo_box.currentText())

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

                for i in range (dict_length):
                    element_item = QTableWidgetItem(element_list[i])
                    self.filtered_table.setItem(row_ind,i,element_item)
        else:
            self.filtered_table.setRowCount(0)


    def refresh_with_filters(self, new_data, filtered_table):
        """Refrsh the display with new data while appliying current filters"""
        self.list_to_filter = new_data
        self.filtered_table = filtered_table

        self.filtering_tool()













