#!/usr/bin/env python3
import argparse, sys, os
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

VERSION = "1.1.0"


# Ver_Log ---------------------------
# - 1.1.0 - Added CLI Flags
# - 1.0.0 - Release
# -----------------------------------


class VisorumApp(QWidget):
    def __init__(self, catalog, paths, settings, path_to_m3u=None):
        super().__init__()
        self.paths = paths
        self.catalog = catalog
        self.settings = settings
        self.player = Player(paths, settings)
        self.path_to_m3u = path_to_m3u

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
            path_to_m3u=self.path_to_m3u
        )

        search_view.searchRequested.connect(main_window.on_search)

        layout.addWidget(main_window)
        self.setLayout(layout)

    def get_window_size(self):
        x, y = str(self.settings._data.get("app_res", "1000,720")).split(",")
        return int(x), int(y)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="Visorum",
        description="Visorum GUI Browser"
    )

    parser.add_argument(
        "-e",
        "--extended",
        action="store_true",
        help="more details for search results (including [VIDEO_ID])"
    )

    parser.add_argument(
        "-s",
        "--search",
        metavar="\"QUERY\"",
        help="print search results and exit"
    )

    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="display all results, negates --limit. ex: Visorum -esa"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="limit number of search results"
    )

    parser.add_argument(
        "--load",
        type=str,
        default=None,
        help="import .m3u playlist to Visorum queue. ex: Visorum --load \"path/to/.m3u\""
    )

    parser.add_argument(
        "--play",
        metavar="VIDEO_ID",
        help="open video in default player. ex: Visorum --play dQw4w9WgXcQ"
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=VERSION
    )

    return parser


def search(query: str):
    # Initialize Required
    paths = Paths()
    catalog = Catalog(paths.catalog_path)

    # Retrieve Videos List
    videos = catalog.all_videos()

    # Initialize Engine
    search_engine = SearchEngine(videos)

    # Return Search
    results = search_engine.search(query)
    return results

def play(video_id: str):
    # Initialize Required
    paths = Paths()
    settings = Settings(paths.settings_path)
    catalog = Catalog(paths.catalog_path)
    player = Player(paths, settings)

    # Find Video
    videos = catalog.all_videos()
    video = None

    for v in videos:
        if v.id == video_id:
            video = v
            break

    if video is not None:
        player.play(video)
    else:
        print(f"[error] could not find a valid video for video id: {video_id}")


def main():
    # Parse CLI Args
    parser = build_parser()
    args = parser.parse_args()
    path_to_m3u = None

    if args.search is not None:
        all = args.all
        extended = args.extended

        if all is True:
            query = "" # Blank query returns all
            limit = None
        else:
            query = args.search
            limit = args.limit

        results = search(query)

        if limit is not None:
            results = results[:limit]

        if extended is True:
            for video in results:
                print(f"{video.title} [{video.id}] - {video.uploader} ({video.duration}) ({video.upload_date})")
        else:
            for video in results:
                print(f"{video.title} - {video.uploader}")

        # Exit Before GUI
        return
    elif args.play is not None:
        video_id = args.play

        play(video_id)

        # Exit Before GUI
        return
    elif args.load is not None:
        path_to_m3u = args.load # Set path to .m3u

        if not os.path.exists(path_to_m3u): # If path not valid, exit
            print(f"path not found: {path_to_m3u}")
            return

        # If valid, open GUI and provide path_to_m3u

    # Initialize GUI
    paths = Paths()
    settings = Settings(paths.settings_path)
    catalog = Catalog(paths.catalog_path)

    # Q App
    app = QApplication(sys.argv)
    window = VisorumApp(catalog, paths, settings, path_to_m3u)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
