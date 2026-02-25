from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtGui import QPixmap, QFont, QPainter, QColor, QFontMetrics
from PyQt5.QtCore import Qt, QRect, QSize, QPoint, pyqtSignal

class VideoDelegate(QStyledItemDelegate):
    addToQueueRequested = pyqtSignal(object)
    moveUpRequested = pyqtSignal(int)
    removeRequested = pyqtSignal(int)
    moveDownRequested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thumb_width = 260
        self.thumb_height = 150
        self.padding = 4
        self.title_font = QFont("Sans", 11, QFont.Bold)
        self.meta_font = QFont("Sans", 8)
        self.mode = "normal"  # "normal" | "queue"

    def paint(self, painter, option, index):
        painter.save()

        rect = option.rect

        video_text = index.data(Qt.DisplayRole)
        thumb_path = index.data(Qt.DecorationRole)

        # Draw background
        painter.fillRect(rect, QColor("#1c1c1c"))
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.darkGray)

        # Load thumbnail
        thumb_rect = QRect(rect.x() + self.padding, rect.y() + self.padding, self.thumb_width, self.thumb_height)

        thumb_pixmap = index.model().get_scaled_thumb(thumb_path, self.thumb_width, self.thumb_height)
        painter.drawPixmap(thumb_rect, thumb_pixmap)

        # Draw text below thumbnail
        if self.mode == "normal":
            text_rect = QRect(rect.x() + self.padding,
                            rect.y() + self.padding + self.thumb_height + 4,
                            rect.width() - 2*self.padding,
                            rect.height() - self.thumb_height - 2*self.padding)
        elif self.mode == "queue":
            text_rect = QRect(self.thumb_width + 2*self.padding + 10,
                            rect.y() + self.padding,
                            rect.width() - 2*self.padding - 300,
                            self.thumb_height + 2*self.padding)
        painter.setPen(Qt.white)

        # Split title/meta for formatting
        if "\n" in video_text:
            title_text, meta_text = video_text.split("\n", 1)
        else:
            title_text = video_text
            meta_text = ""

        # Title
        painter.setFont(self.title_font)
        painter.drawText(text_rect, Qt.TextWordWrap, title_text)

        title_metrics = QFontMetrics(self.title_font)
        title_height = title_metrics.boundingRect(text_rect, Qt.TextWordWrap, title_text).height()

        # Meta
        meta_rect = text_rect.adjusted(0, title_height, 0, 0)
        painter.setFont(self.meta_font)
        painter.drawText(meta_rect, Qt.TextWordWrap, meta_text)

        if self.mode == "normal":
            # "+" button bottom-right
            btn = QRect(
                rect.right() - 26,
                rect.bottom() - 26,
                18,
                18,
            )
            painter.setBrush(QColor("#3a3a3a"))
            painter.drawRect(btn)
            painter.setPen(Qt.white)
            painter.drawText(btn, Qt.AlignCenter, "+")
        elif self.mode == "queue":
            buttons = self._queue_button_rects(rect)
            painter.setPen(Qt.white)
            painter.setBrush(QColor("#3a3a3a"))

            painter.drawRect(buttons["up"])
            painter.drawText(buttons["up"], Qt.AlignCenter, "↑")

            painter.drawRect(buttons["remove"])
            painter.drawText(buttons["remove"], Qt.AlignCenter, "✕")

            painter.drawRect(buttons["down"])
            painter.drawText(buttons["down"], Qt.AlignCenter, "↓")


        painter.restore()

    def sizeHint(self, option, index):
        # fixed card size
        #return QSize(self.thumb_width + 2*self.padding, self.thumb_height + 90)
        thumb_width = self.thumb_width
        thumb_height = self.thumb_height
        padding = self.padding

        video_text = index.data(Qt.DisplayRole)
        if "\n" in video_text:
            title_text, meta_text = video_text.split("\n", 1)
        else:
            title_text = video_text
            meta_text = ""

        # Calculate dynamic heights
        title_metrics = QFontMetrics(self.title_font)
        title_height = title_metrics.boundingRect(0, 0, thumb_width, 1000, Qt.TextWordWrap, title_text).height()

        meta_metrics = QFontMetrics(self.meta_font)
        meta_height = meta_metrics.boundingRect(0, 0, thumb_width, 1000, Qt.TextWordWrap, meta_text).height()

        total_height = padding*2 + thumb_height + 4 + title_height + 1 + meta_height  # padding + spacing
        total_width = thumb_width + 2*padding

        if self.mode == "queue":
            total_height = total_height - meta_height - title_height - 5

        return QSize(total_width, total_height)

    def _queue_button_rects(self, rect):
        size = 18
        spacing = 6
        right = rect.right() - spacing - size

        top = rect.top() + 20
        mid = rect.center().y() - size // 2
        bot = rect.bottom() - size - 20

        return {
            "up": QRect(right, top, size, size),
            "remove": QRect(right, mid, size, size),
            "down": QRect(right, bot, size, size),
        }

    def editorEvent(self, event, model, option, index):
        if event.type() != event.MouseButtonRelease:
            return False

        pos = event.pos()
        rect = option.rect

        if self.mode == "normal":
            btn = QRect(rect.right() - 26, rect.bottom() - 26, 18, 18)
            if btn.contains(pos):
                video = index.data(Qt.UserRole)
                self.addToQueueRequested.emit(video)
                return True

        elif self.mode == "queue":
            buttons = self._queue_button_rects(rect)
            row = index.row()

            if buttons["up"].contains(pos):
                self.moveUpRequested.emit(row)
                return True
            if buttons["remove"].contains(pos):
                self.removeRequested.emit(row)
                return True
            if buttons["down"].contains(pos):
                self.moveDownRequested.emit(row)
                return True

        return False

    def is_queue_button_click(self, option, pos):
        if self.mode != "normal":
            return False

        btn = QRect(
            option.rect.right() - 26,
            option.rect.bottom() - 26,
            18,
            18,
        )
        return btn.contains(pos)
