# ui/settings_view.py
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QLabel,
    QFrame,
)
from PyQt5.QtCore import Qt

from core.settings import VALID_PLAYERS, APP_RES_PRESETS


class SettingsView(QWidget):
    def __init__(self, settings):
        """
        :param settings: core.settings.Settings instance
        """
        super().__init__()
        self.settings = settings

        root_layout = QVBoxLayout()
        root_layout.setAlignment(Qt.AlignTop)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignTop)

        # --- Default player ---
        #self.default_player_combo = QComboBox()
        #self.default_player_combo.addItems(VALID_PLAYERS)
        #self.default_player_combo.setCurrentText(self.settings.default_player)
        #self.default_player_combo.currentTextChanged.connect(
        #    self.on_default_player_changed
        #)

        #form.addRow("Default player:", self.default_player_combo)

        # --- Player map (per-extension) ---
        for ext, player in sorted(self.settings.player_map.items()):
            combo = QComboBox()
            combo.addItems(VALID_PLAYERS)
            combo.setCurrentText(player)

            combo.currentTextChanged.connect(
                lambda value, e=ext: self.on_extension_player_changed(e, value)
            )

            form.addRow(f"{ext}:", combo)

        # --- App resolution ---
        self.resolution_combo = QComboBox()

        # Populate with labels, store actual value as itemData
        for label, value in APP_RES_PRESETS.items():
            self.resolution_combo.addItem(label, value)

        # Set current selection
        current_res = self.settings.app_res
        for i in range(self.resolution_combo.count()):
            if self.resolution_combo.itemData(i) == current_res:
                self.resolution_combo.setCurrentIndex(i)
                break

        self.resolution_combo.currentIndexChanged.connect(
            self.on_resolution_changed
        )

        form.addRow("App resolution*:", self.resolution_combo)

        # --- Player map notice ---
        player_note = QLabel(
            "Below you can choose which app (of the currently supported local video players) "
            "opens which type of video file. "
            "This app doesn't check if you have the app installed; you should install them "
            "via your system package manager prior to testing."
        )
        player_note.setWordWrap(True)
        player_note.setStyleSheet("color: #fff; font-size: 12px;")
        player_note.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # --- Restart notice ---
        restart_note = QLabel(
            "*Resolution changes take effect after restarting Visorum."
        )
        restart_note.setStyleSheet("color: #888; font-size: 11px;")
        restart_note.setAlignment(Qt.AlignLeft)

        # --- Assemble ---
        root_layout.addWidget(player_note)
        root_layout.addLayout(form)
        root_layout.addSpacing(8)
        root_layout.addWidget(restart_note)

        self.setLayout(root_layout)

    # --- Slots ---

    def on_default_player_changed(self, value: str):
        self.settings.default_player = value

    def on_extension_player_changed(self, ext: str, value: str):
        self.settings.set_player_for_extension(ext, value)

    def on_resolution_changed(self, index: int):
        value = self.resolution_combo.itemData(index)
        self.settings.app_res = value
