import sys
from pathlib import Path

class Paths:
    """
    Resolves all filesystem paths relative to the executable/script.
    This works for:
    - symlink testing
    - running from source
    - PyInstaller one-file or one-dir builds
    """

    def __init__(self):
        self.debug = False
        self.app_dir = self._detect_app_dir()
        self.work_dir = self.app_dir / "1_New_Downloads"
        self.settings_path = self.work_dir / "settings.json"
        self.catalog_path = self.work_dir / "catalog.json"
        self.thumb_placeholder = "ui/placeholder.jpg"

    def _detect_app_dir(self) -> Path:
        # Detect current directory

        if getattr(sys, 'frozen', False):
            adir = Path(sys.executable).parent.resolve()
            #print(f"debug: executable's parent's path: {adir}")
        else:
            adir = Path(__file__).parent.parent.resolve()

        if self.debug == True:
            print(f"debug: Current app_dir: {adir}")

        # If a symlink exists, point to the real root
        data_root = adir / "yt-dlp" # works for testing with symlink

        if self.debug:
            print(f"debug: Symlink app_dir: {data_root}")

        # fallback for production where app lives inside data
        if not data_root.exists():
            data_root = adir.parent  # parent of '1 New Downloads'
            if self.debug:
                print(f"debug: Symlink not used: Current app_dir: {data_root}")

        return data_root

    def resolve_video_path(self, relative_path: str) -> Path:
        path = (self.app_dir / relative_path).resolve()

        if self.debug:
            print(f"debug: Resolved video path: {path}")

        return path

    def resolve_thumbnail_path(self, relative_path: str | None) -> Path:
        if not relative_path:
            return self.thumb_placeholder

        p = self.app_dir / relative_path
        if p.exists():
            return p

        return self.thumb_placeholder

    def get_thumb_placeholder(self):
        return self.thumb_placeholder
