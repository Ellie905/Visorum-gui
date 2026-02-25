from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant
from PyQt5.QtGui import QPixmap

class VideoModel(QAbstractListModel):
    """
    Stores all video data for MVD rendering.
    """
    def __init__(self, videos, paths, parent=None):
        super().__init__(parent)
        self.videos = list(videos)
        self.paths = paths
        self.thumb_cache = {}

    def rowCount(self, parent=QModelIndex()):
        return len(self.videos)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        video = self.videos[index.row()]

        if role == Qt.UserRole:  # return full video object
            return video
        elif role == Qt.DecorationRole:  # thumbnail path
            thumb_path = self.paths.resolve_thumbnail_path(video.thumbnail)
            if not thumb_path:
                thumb_path = self.paths.get_thumb_placeholder()
            return thumb_path
        elif role == Qt.DisplayRole:  # text metadata
            meta = (
                f"Uploader: {video.uploader} | "
                f"Date: {video.upload_date}\n"
                f"Duration: {video.duration} | "
                f"Views: {video.views}\n"
                f"Genre: {video.genre}"
            )
            return f"{video.title}\n{meta}"

        return QVariant()

    def get_scaled_thumb(self, thumb_path, width, height):
        key = (thumb_path, width, height)
        if key not in self.thumb_cache:
            pix = QPixmap(str(thumb_path)).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.thumb_cache[key] = pix
        return self.thumb_cache[key]
