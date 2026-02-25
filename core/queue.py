# core/queue.py
import subprocess
import tempfile
import shutil
import time
import os
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal


class Queue(QObject):
    queueChanged = pyqtSignal()
    becameNonEmpty = pyqtSignal()

    def __init__(self, paths, settings):
        super().__init__()
        self.paths = paths
        self.settings = settings
        self.videos = []

    # -----------------------------
    # Queue mutation
    # -----------------------------

    def add(self, video):
        was_empty = not self.videos
        self.videos.append(video)
        self.queueChanged.emit()
        if was_empty:
            self.becameNonEmpty.emit()

    def remove_at(self, index):
        if 0 <= index < len(self.videos):
            del self.videos[index]
            self.queueChanged.emit()

    def move_up(self, index):
        if index > 0:
            self.videos[index - 1], self.videos[index] = (
                self.videos[index],
                self.videos[index - 1],
            )
            self.queueChanged.emit()

    def move_down(self, index):
        if index < len(self.videos) - 1:
            self.videos[index + 1], self.videos[index] = (
                self.videos[index],
                self.videos[index + 1],
            )
            self.queueChanged.emit()

    def clear(self):
        self.videos.clear()
        self.queueChanged.emit()

    # -----------------------------
    # Playlists
    # -----------------------------

    def export(self, playlist_path: Path):
        if not self.videos:
            return

        # Resolve paths
        paths = [
            str(self.paths.resolve_video_path(v.path))
            for v in self.videos
        ]

        playlist_path = playlist_path.with_suffix(".m3u")

        with open(playlist_path, "w", encoding="utf-8") as f:
            for p in paths:
                f.write(p + "\n")

        print(f"[queue] saved playlist: {playlist_path}")

    # -----------------------------
    # Playback
    # -----------------------------

    def play(self):
        if not self.videos:
            return

        # Resolve paths
        paths = [
            str(self.paths.resolve_video_path(v.path))
            for v in self.videos
        ]

        first_ext = Path(paths[0]).suffix.lower()
        player = self.settings.player_for_extension(first_ext)
        if player not in {"mpv", "vlc", "celluloid"}:
            player = self.settings.default_player()

        print(f"[queue] videos: {paths}")
        print(f"[queue] player: {player}")

        if player == "celluloid":
            cmd = ["celluloid", "--enqueue", *paths]

        elif player == "vlc":
            cmd = ["vlc", *paths]

        elif player == "mpv":
            playlist_dir = Path(tempfile.gettempdir()) / "visorum_mpv_queue"
            playlist_dir.mkdir(parents=True, exist_ok=True)

            playlist_path = playlist_dir / "queue.m3u"
            with open(playlist_path, "w", encoding="utf-8") as f:
                for p in paths:
                    f.write(p + "\n")

            cmd = ["mpv", f"--playlist={playlist_path}"]
        else:
            return  # should never happen

        subprocess.Popen(cmd)

        if player == "mpv":
            time.sleep(5)
            os.remove(playlist_path) # Cleanup after ensuring mpv plays, otherwise mpv will play the same queue every time
