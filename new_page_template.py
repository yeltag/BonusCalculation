from PyQt6.QtWidgets import (QWidget,QVBoxLayout, QHBoxLayout,QLabel,QGroupBox)

class NewPageTemplate(QWidget):
    def __init__(self,title,search_widgets = [],central_widgets = [],button_widgets = []):
        super(). __init__()
        self.title = title

        self.layout = QVBoxLayout(self)
        self.header_layout = QHBoxLayout()
        self.search_and_filters_layout = QHBoxLayout()
        self.central_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.search_widgets = search_widgets
        self.central_widgets = central_widgets
        self.button_widgets = button_widgets
        self.create_layout()


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





