# ui/queue_view.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListView, QFileDialog
from PyQt5.QtCore import Qt
from pathlib import Path
from ui.video_model import VideoModel
from ui.video_delegate import VideoDelegate


class QueueView(QWidget):
    def __init__(self, queue, paths):
        super().__init__()
        self.queue = queue
        self.paths = paths

        layout = QVBoxLayout(self)

        self.play_btn = QPushButton("Play Queue")
        layout.addWidget(self.play_btn)

        self.export_btn = QPushButton("Export Playlist to .m3u")
        layout.addWidget(self.export_btn)

        self.view = QListView()
        self.view.setVerticalScrollMode(QListView.ScrollPerPixel)
        self.view.setViewMode(QListView.ListMode)
        self.view.setSpacing(10)
        self.view.setSelectionMode(QListView.NoSelection)

        scrollbar = self.view.verticalScrollBar()
        scrollbar.setSingleStep(30)  # pixels per arrow click / wheel tick
        scrollbar.setPageStep(100)   # pixels per page up/down

        layout.addWidget(self.view)

        self.model = VideoModel(self.queue.videos, self.paths)
        self.delegate = VideoDelegate()
        self.delegate.mode = "queue"

        self.view.setModel(self.model)
        self.view.setItemDelegate(self.delegate)

        # Wiring
        self.play_btn.clicked.connect(self.queue.play)
        self.export_btn.clicked.connect(self.export_playlist)
        self.queue.queueChanged.connect(self.refresh)

        self.delegate.moveUpRequested.connect(self.queue.move_up)
        self.delegate.removeRequested.connect(self.queue.remove_at)
        self.delegate.moveDownRequested.connect(self.queue.move_down)

    def refresh(self):
        self.model.beginResetModel()
        self.model.videos = self.queue.videos
        self.model.endResetModel()

    def export_playlist(self):
        if not self.queue.videos:
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Playlist",
            "playlist.m3u",
            "M3U Playlist (*.m3u)"
        )

        if not filename:
            return  # user cancelled

        self.queue.export(Path(filename))

