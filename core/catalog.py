import json
from helpers.normal import format_date, format_number, format_time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class Video:
    id: str
    title: str
    uploader: str
    upload_date: str
    duration: str
    views: str
    description: str
    tags: list()
    categories: list()
    genre: str
    path: str
    thumbnail: str | None


class Catalog:
    """
    Authoritative, read-only view of catalog.json
    """

    def __init__(self, catalog_path: Path):
        self._videos: Dict[str, Video] = {}
        #print(f"debug: catalog_path: {catalog_path}")
        self._load(catalog_path)

    def _load(self, path: Path):
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        for vid, data in raw.get("videos", {}).items():
            self._videos[vid] = Video(
                id=vid,
                title=data.get("title", ""),
                uploader=data.get("uploader", ""),
                upload_date=format_date(data.get("upload_date", "")), # 2026-01-04
                duration=format_time(int(data.get("duration", 0))), # 1h23m33s
                views=format_number(int(data.get("view_count", 0))),
                description=data.get("description", ""),
                tags=data.get("tags", []),
                categories=data.get("categories", []),
                genre=data.get("genre", ""),
                path=data.get("path", ""),
                thumbnail=data.get("thumbnail"),
            )

    def all_videos(self) -> List[Video]:
        return list(self._videos.values())
