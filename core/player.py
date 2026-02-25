import subprocess


class Player:
    """
    Responsible for launching video playback.
    """

    def __init__(self, paths, settings):
        self.paths = paths
        self.settings = settings

    def play(self, video):
        video_path = self.paths.resolve_video_path(video.path)
        ext = video_path.suffix.lower()

        player = self.settings.player_for_extension(ext)

        if player not in {"mpv", "vlc", "celluloid"}:
            player = self.settings.default_player()

        subprocess.Popen([player, str(video_path)])
