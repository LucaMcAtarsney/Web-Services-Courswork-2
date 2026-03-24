from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from src.crawler import CrawledQuote


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9']+")


class InvertedIndex:

    def __init__(self) -> None:
        self.index: dict[str, dict[str, dict[str, int | list[int]]]] = {}
        self.page_token_counts: dict[str, int] = {}

    def build(self, pages: Iterable[CrawledQuote]) -> dict[str, dict[str, dict[str, int | list[int]]]]:
        self.index = {}
        self.page_token_counts = {}

        page_positions: dict[str, int] = {}

        for page in pages:
            for token in self._tokens_for_page_content(page):
                page_url = page.page_url
                page_positions.setdefault(page_url, 0)
                position = page_positions[page_url]

                word_entry = self.index.setdefault(token, {})
                posting = word_entry.setdefault(page_url, {"frequency": 0, "positions": []})
                posting["frequency"] += 1
                posting["positions"].append(position)

                page_positions[page_url] += 1

        self.page_token_counts = dict(page_positions)
        return self.index

    def save(self, file_path: str | Path) -> None:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "index": self.index,
            "page_token_counts": self.page_token_counts,
        }

        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)

    def load(self, file_path: str | Path) -> dict[str, dict[str, dict[str, int | list[int]]]]:
        path = Path(file_path)

        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        self.index = payload.get("index", {})
        self.page_token_counts = payload.get("page_token_counts", {})
        return self.index

    def postings_for(self, word: str) -> dict[str, dict[str, int | list[int]]]:
        normalized = self.normalize_word(word)
        if not normalized:
            return {}
        return self.index.get(normalized, {})

    @staticmethod
    def normalize_word(word: str) -> str:
        return word.strip().lower()

    @classmethod
    def tokenize(cls, text: str) -> list[str]:
        return [cls.normalize_word(token) for token in TOKEN_PATTERN.findall(text)]

    @classmethod
    def _tokens_for_page_content(cls, page: CrawledQuote) -> list[str]:
        segments = [page.text, page.author, *page.tags]
        combined_text = " ".join(segment for segment in segments if segment)
        return cls.tokenize(combined_text)
