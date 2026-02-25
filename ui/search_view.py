# ui/search_view.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt5.QtCore import pyqtSignal


class SearchView(QWidget):
    searchRequested = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.input = QLineEdit()
        self.input.setPlaceholderText("Search videos...")
        self.input.returnPressed.connect(self.emit_search)

        self.button = QPushButton("Search")
        self.button.clicked.connect(self.emit_search)

        layout = QHBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def emit_search(self):
        text = self.input.text()
        print(f"[ui.search] emit_search: {text!r}")
        self.searchRequested.emit(text)
