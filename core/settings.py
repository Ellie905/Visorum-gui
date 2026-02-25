import json
from pathlib import Path


DEFAULT_SETTINGS = {
    "default_player": "celluloid",
    "player_map": {
        ".mp4": "celluloid",
        ".mkv": "celluloid",
        ".webm": "celluloid",
    },
    "app_res": "1000,720"
}

VALID_PLAYERS = ["vlc", "mpv", "celluloid"]

APP_RES_PRESETS = {
    "Large (1300×730)": "1300,730",
    "Medium (1000×720)": "1000,720",
    "Small (700×520)": "700,520",
}


"""
    Default App Resolutions:
    Fullscreen
    Large   - 1300,730
    Medium  - 1000,720
    Small   - 700, 520
"""


class Settings:
    """
    Persistent application settings.
    No GUI logic, no subprocess logic.
    """

    def __init__(self, settings_path: Path):
        self.settings_path = settings_path
        self._data = {}
        self._load()

    def _load(self):
        if self.settings_path.exists():
            with open(self.settings_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = DEFAULT_SETTINGS.copy()
            self.save()

    def save(self):
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    # --- Player settings ---

    @property
    def default_player(self) -> str:
        return self._data.get("default_player", DEFAULT_SETTINGS["default_player"])

    @default_player.setter
    def default_player(self, value: str):
        self._data["default_player"] = value
        self.save()

    @property
    def player_map(self) -> dict:
        return self._data.get("player_map", DEFAULT_SETTINGS["player_map"])

    def player_for_extension(self, ext: str) -> str:
        return self.player_map.get(ext, self.default_player)

        # --- Player map mutation ---

    def set_player_for_extension(self, ext: str, player: str):
        if "player_map" not in self._data:
            self._data["player_map"] = {}

        self._data["player_map"][ext] = player
        self.save()


        # --- App resolution ---

    @property
    def app_res(self) -> str:
        return self._data.get("app_res", DEFAULT_SETTINGS["app_res"])

    @app_res.setter
    def app_res(self, value: str):
        # UI guarantees preset values; main.py handles bad manual edits
        self._data["app_res"] = value
        self.save()

