# ui/main_window.py
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QPushButton,
)
from PyQt5.QtCore import Qt

from ui.video_view import VideoView  # the new MVD-based replacement
from ui.search_view import SearchView
from ui.settings_view import SettingsView
from ui.queue_view import QueueView
from core.queue import Queue


class MainWindow(QWidget):
    def __init__(self, videos, paths, on_activate, search_engine, settings):
        super().__init__()

        self.videos = list(videos)
        self.paths = paths
        self.on_activate = on_activate
        self.search_engine = search_engine
        self.settings = settings
        self.queue = Queue(self.paths, self.settings)

        # --- Search bar ---
        self.search_view = SearchView()
        self.search_view.searchRequested.connect(self.on_search)

        # --- Tabs (replace Grid/List buttons) ---
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)

        # --- Home tab (grid, full catalog) ---
        self.home_view = VideoView(
            videos=self.videos,
            paths=self.paths,
            on_activate=self.on_activate,
            forced_view_mode="grid",
        )
        self.tabs.addTab(self.home_view, "Home")

        # --- Search tab (list, filtered) ---
        self.search_results_view = VideoView(
            videos=[],
            paths=self.paths,
            on_activate=self.on_activate,
            forced_view_mode="grid",
        )
        self.tabs.addTab(self.search_results_view, "Search")

        # Search tab hidden until first search
        self.tabs.setTabVisible(1, False)

        # --- Queue tab ---
        self.queue_view = QueueView(self.queue, self.paths)
        self.tabs.addTab(self.queue_view, "Queue")
        self.tabs.setTabVisible(2, False)

        for view in (self.home_view, self.search_results_view):
            view.delegate.addToQueueRequested.connect(self.queue.add)

        self.queue.becameNonEmpty.connect(
            lambda: self.tabs.setTabVisible(2, True)
        )

        # --- Settings tab ---
        self.settings_view = SettingsView(self.settings)
        self.tabs.addTab(self.settings_view, "Settings")

        # --- Layout ---
        layout = QVBoxLayout()
        layout.addWidget(self.search_view)
        layout.addWidget(self.tabs)

        self.setLayout(layout)

    # --------------------------------------------------
    # Search handling
    # --------------------------------------------------

    def on_search(self, query: str):
        query = query.strip()

        if not query:
            # Empty search → Home tab + grid
            self.home_view.set_videos(self.videos)
            self.tabs.setTabVisible(1, False)
            self.tabs.setCurrentIndex(0)
            return

        # Non-empty → Search tab + list
        results = self.search_engine.search(query)
        self.search_results_view.set_videos(results)
        self.tabs.setTabVisible(1, True)
        self.tabs.setCurrentIndex(1)

