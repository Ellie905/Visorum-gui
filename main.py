#!/usr/bin/env python3
import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
)
from PyQt5.QtCore import Qt

from core.paths import Paths
from core.catalog import Catalog
from core.settings import Settings
from core.player import Player
from core.search import SearchEngine
from ui.main_window import MainWindow
from ui.home import HomeView
from ui.search_view import SearchView


class VisorumApp(QWidget):
    def __init__(self, catalog, paths, settings):
        super().__init__()
        self.paths = paths
        self.catalog = catalog
        self.settings = settings
        self.player = Player(paths, settings)

        self.setWindowTitle("Visorum")
        self.setStyleSheet("background-color: #111; color: #eee;")

        self.x, self.y = self.get_window_size()
        #self.resize(self.x, self.y) # Use this for fullscreen functionality
        self.setFixedSize(self.x, self.y)

        layout = QVBoxLayout()

        search_view = SearchView()

        main_window = MainWindow(
            videos=self.catalog.all_videos(),
            paths=self.paths,
            on_activate=self.player.play,
            search_engine=SearchEngine(self.catalog.all_videos()),
            settings=self.settings,
        )

        search_view.searchRequested.connect(main_window.on_search)

        layout.addWidget(main_window)
        self.setLayout(layout)

    def get_window_size(self):
        x, y = str(self.settings._data.get("app_res", "1000,720")).split(",")
        return int(x), int(y)


def main():
    paths = Paths()

    settings = Settings(paths.settings_path)
    catalog = Catalog(paths.catalog_path)

    app = QApplication(sys.argv)
    window = VisorumApp(catalog, paths, settings)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
