from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListView, QStyleOptionViewItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from ui.video_model import VideoModel
from ui.video_delegate import VideoDelegate

class VideoView(QWidget):
    """
    Replaces HomeView using MVD system (QListView + model + delegate)
    """
    def __init__(self, videos, paths, on_activate, forced_view_mode):
        super().__init__()
        self.videos = videos
        self.paths = paths
        self.on_activate = on_activate
        self.view_mode = forced_view_mode

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Video count
        self.vid_lbl = QLabel(f"Videos loaded: {len(videos)}")
        self.vid_lbl.setStyleSheet("color: #aaa;")
        self.layout.addWidget(self.vid_lbl)

        # QListView
        self.view = QListView()
        self.view.setVerticalScrollMode(QListView.ScrollPerPixel)
        self.view.setSpacing(17)
        self.view.setUniformItemSizes(False)
        self.view.setSelectionMode(QListView.NoSelection)
        self.view.setViewportMargins(21, 0, 0, 0)

        scrollbar = self.view.verticalScrollBar()
        scrollbar.setSingleStep(30)  # pixels per arrow click / wheel tick
        scrollbar.setPageStep(100)   # pixels per page up/down

        self.layout.addWidget(self.view)

        # Model + delegate
        self.model = VideoModel(self.videos, self.paths)
        self.delegate = VideoDelegate()
        self.view.setModel(self.model)
        self.view.setItemDelegate(self.delegate)

        # Configure grid vs list
        self.apply_view_mode()

        # Cursor
        #self.view.setCursor(Qt.PointingHandCursor) # Sets cursor when over listview, not listview items

        # Connect click
        self.view.clicked.connect(self.on_item_clicked)

    def apply_view_mode(self):
        if self.view_mode == "grid":
            self.view.setViewMode(QListView.IconMode)
            self.view.setResizeMode(QListView.Adjust)
        else:
            self.view.setViewMode(QListView.ListMode)
            self.view.setResizeMode(QListView.Adjust)

    def on_item_clicked(self, index):
        # Queue Delegate Logic
        option = self.view.visualRect(index)
        pos = self.view.viewport().mapFromGlobal(QCursor.pos())

        delegate = self.view.itemDelegate()
        if hasattr(delegate, "is_queue_button_click"):
            fake_option = QStyleOptionViewItem()
            fake_option.rect = option

            if delegate.is_queue_button_click(fake_option, pos):
                return  # Only add video to queue | No playback

        # Non-Queue Play Video Logic
        video = index.data(Qt.UserRole)
        if video:
            self.on_activate(video)

    def set_videos(self, videos):
        self.model.beginResetModel()
        self.model.videos = list(videos)
        self.model.endResetModel()
        self.vid_lbl.setText(f"Videos loaded: {len(videos)}")
