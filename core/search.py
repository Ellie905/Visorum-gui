# core/search.py
from typing import Iterable, List, Dict
import unicodedata
import re


_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def normalize(text: str) -> str:
    """
    Normalize unicode text for search:
    - NFKC normalization
    - lowercase
    """
    return unicodedata.normalize("NFKC", text).lower()


def tokenize(text: str) -> List[str]:
    return _TOKEN_RE.findall(text)


class SearchEngine:
    """
    In-memory search engine with:
    - cached tokenization
    - weighted relevance scoring
    - AND-based token matching
    """

    def __init__(self, videos: Iterable):
        self._videos = list(videos)
        print(f"[search] init: {len(self._videos)} videos received")
        self._index: Dict[str, Dict] = {}
        self._build_index()

    def _build_index(self):
        """
        Build a lightweight per-video index.
        This runs once at startup.
        """
        for v in self._videos:
            fields = {
                "title": normalize(v.title),
                "uploader": normalize(v.uploader),
                "description": normalize(v.description),
                "tags": normalize(str(v.tags)),
                "categories": normalize(str(v.categories)),
                "genre": normalize(v.genre),
                "path": normalize(v.path),
            }

            token_sets = {
                name: set(tokenize(text))
                for name, text in fields.items()
            }

            self._index[v.id] = {
                "video": v,
                "fields": fields,
                "tokens": token_sets,
            }
        print(f"[search] index built: {len(self._index)} entries")

    def search(self, query: str) -> List:
        print(f"[search] search called with query={query!r}")

        if not query or not query.strip():
            print("[search] empty query → returning all videos")
            return self._videos

        q_norm = normalize(query)
        q_tokens = set(tokenize(q_norm))
        if not q_tokens:
            return self._videos

        results = []

        for entry in self._index.values():
            tokens = entry["tokens"]

            # AND semantics: all query tokens must appear somewhere
            #if not any(
            #    q_tokens <= field_tokens
            #    for field_tokens in tokens.values()
            #):
            #    continue

            if not self._matches(tokens, q_tokens):
                continue

            score = self._score(entry, q_tokens)
            results.append((score, entry["video"]))

        # higher score first
        results.sort(key=lambda x: x[0], reverse=True)
        print(f"[search] results count: {len(results)}")
        return [v for _, v in results]

    def _score(self, entry: Dict, q_tokens: set) -> int:
        """
        Cheap, predictable relevance scoring.
        """
        score = 0
        tokens = entry["tokens"]

        # weights
        if q_tokens & tokens["title"]:
            score += 100 * len(q_tokens & tokens["title"])

        if q_tokens & tokens["uploader"]:
            score += 40 * len(q_tokens & tokens["uploader"])

        if q_tokens & tokens["description"]:
            score += 30 * len(q_tokens & tokens["description"])

        if q_tokens & tokens["tags"]:
            score += 25 * len(q_tokens & tokens["tags"])

        if q_tokens & tokens["categories"]:
            score += 20 * len(q_tokens & tokens["categories"])

        if q_tokens & tokens["genre"]:
            score += 20 * len(q_tokens & tokens["genre"])

        if q_tokens & tokens["path"]:
            score += 10 * len(q_tokens & tokens["path"])

        return score

    def _matches(self, tokens: Dict[str, set], q_tokens: set) -> bool:
        """
        Return True if all query tokens match at least one field,
        using exact OR prefix matching.
        """
        for q in q_tokens:
            matched = False
            for field_tokens in tokens.values():
                for t in field_tokens:
                    if t == q or t.startswith(q):
                        matched = True
                        break
                if matched:
                    break

            if not matched:
                return False

        return True

