from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QScrollArea,
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt


class VideoCard(QWidget):
    def __init__(self, video, thumb_path, on_activate):
        super().__init__()
        self.video = video

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        thumb = QLabel()
        pixmap = QPixmap(str(thumb_path)).scaled(
            260, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        thumb.setPixmap(pixmap)
        thumb.setCursor(Qt.PointingHandCursor)
        thumb.mousePressEvent = lambda e: on_activate(video)
        layout.addWidget(thumb)

        title = QLabel(video.title)
        title.setFont(QFont("Sans", 10, QFont.Bold))
        title.setStyleSheet("color: #eee;")
        title.setWordWrap(True)
        title.setCursor(Qt.PointingHandCursor)
        title.mousePressEvent = lambda e: on_activate(video)
        layout.addWidget(title)

        meta = (
            f"Uploader: {video.uploader} | "
            f"Date: {video.upload_date} | "
            f"Duration: {video.duration} | "
            f"Views: {video.views} | "
            f"Genre: {video.genre}"
        )
        meta_label = QLabel(meta)
        meta_label.setFont(QFont("Sans", 8))
        meta_label.setStyleSheet("color: #aaa;")
        meta_label.setWordWrap(True)
        layout.addWidget(meta_label)

        self.setLayout(layout)
        self.setStyleSheet(
            "background-color: #1c1c1c; border-radius: 8px; padding: 4px;"
        )


class HomeView(QWidget):
    def __init__(self, videos, paths, on_activate, forced_view_mode: str, resolution):
        super().__init__()

        self.paths = paths
        self.on_activate = on_activate
        self.videos = list(videos)
        self.view_mode = forced_view_mode  # "grid" or "list"
        self.resolution = resolution

        self.card_cache = {}

        print(f"[home] init | mode={self.view_mode} | videos={len(self.videos)}")

        # Scroll container
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.content = QWidget()
        self.scroll.setWidget(self.content)

        # Persistent container
        self.container_layout = QVBoxLayout()
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.content.setLayout(self.container_layout)

        # Layouts
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(12)

        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(8)

        self.active_layout = None

        # Video count label (preserved)
        self.vid_lbl = QLabel(f"Videos loaded: {len(self.videos)}")
        self.vid_lbl.setStyleSheet("color: #aaa;")

        outer = QVBoxLayout()
        outer.addWidget(self.vid_lbl)
        outer.addWidget(self.scroll)
        self.setLayout(outer)

        self.render()

    # --------------------------------------------------

    def set_videos(self, videos):
        self.videos = list(videos)
        self.vid_lbl.setText(f"Videos loaded: {len(self.videos)}")
        print(f"[home] set_videos: {len(self.videos)}")
        print(f"[home] view_mode: {self.view_mode}")
        self.render()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setVisible(False)

    def render(self):
        print(f"[home] render | mode={self.view_mode} | videos={len(self.videos)}")

        new_layout = self.grid_layout if self.view_mode == "grid" else self.list_layout

        if self.active_layout is not new_layout:
            if self.active_layout:
                self.clear_layout(self.active_layout)
                self.container_layout.removeItem(self.active_layout)

            self.active_layout = new_layout
            self.container_layout.addLayout(self.active_layout)

        self.clear_layout(self.active_layout)

        if self.view_mode == "grid":
            row = col = 0
            for video in self.videos:
                key = video.thumbnail
                card = self.card_cache.get(key)

                if not card:
                    thumb_path = self.paths.resolve_thumbnail_path(video.thumbnail)

                    if not thumb_path:
                        thumb_path = self.paths.get_thumb_placeholder()
                    card = VideoCard(video, thumb_path, self.on_activate)
                    self.card_cache[key] = card

                card.setVisible(True)
                self.active_layout.addWidget(card, row, col)

                # No horizontal scroll
                x, y = str(self.resolution).split(",")
                c = 4 # default num of columns

                if int(x) >= 1300: # large
                    c = 4
                elif int(x) >= 1000: # medium
                    c = 3
                elif int(x) >= 700: # small
                    c = 2
                else:
                    c = 1

                col += 1
                if col >= c:
                    col = 0
                    row += 1
        else:
            for video in self.videos:
                key = video.thumbnail
                card = self.card_cache.get(key)

                if not card:
                    thumb_path = self.paths.resolve_thumbnail_path(video.thumbnail)
                    card = VideoCard(video, thumb_path, self.on_activate)
                    self.card_cache[key] = card

                card.setVisible(True)
                self.active_layout.addWidget(card)

            self.active_layout.addStretch()
