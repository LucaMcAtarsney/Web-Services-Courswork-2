"""Inverted index builder, serialiser, and query helper."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from src.crawler import CrawledQuote


# Matches runs of alphanumeric characters and apostrophes (preserves contractions).
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9']+")


class InvertedIndex:
    """Builds and stores a word-level inverted index over crawled quote pages.

    Index structure
    ---------------
    The top-level mapping is::

        {
            "<word>": {
                "<page_url>": {
                    "frequency": <int>,
                    "positions": [<int>, ...]
                }
            }
        }

    Each word maps to a *postings list*: one entry per page that contains the
    word, recording how many times it appears (``frequency``) and the zero-based
    token offsets within the page's combined token stream (``positions``).

    Token positions are global across all content on a page (quote text +
    author name + tags concatenated), so they can be used to compute proximity
    between terms if needed.

    Persistence
    -----------
    The index and per-page token counts are serialised to JSON via
    :meth:`save` and restored via :meth:`load`.
    """

    def __init__(self) -> None:
        self.index: dict[str, dict[str, dict[str, int | list[int]]]] = {}
        self.page_token_counts: dict[str, int] = {}

    def build(self, pages: Iterable[CrawledQuote]) -> dict[str, dict[str, dict[str, int | list[int]]]]:
        """Build the inverted index from an iterable of crawled quotes.

        Each page's content (text, author, and tags) is concatenated into a
        single token stream.  Position numbers are monotonically increasing
        within a page across all content segments.

        Returns the populated index dict (also stored in ``self.index``).
        """
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
        """Serialise the index and page token counts to a JSON file.

        Parent directories are created automatically if they do not exist.
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "index": self.index,
            "page_token_counts": self.page_token_counts,
        }

        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)

    def load(self, file_path: str | Path) -> dict[str, dict[str, dict[str, int | list[int]]]]:
        """Load a previously saved index from *file_path*.

        Raises :exc:`FileNotFoundError` if the file does not exist, or
        :exc:`json.JSONDecodeError` if the file is not valid JSON.
        Returns the loaded index dict (also stored in ``self.index``).
        """
        path = Path(file_path)

        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        self.index = payload.get("index", {})
        self.page_token_counts = payload.get("page_token_counts", {})
        return self.index

    def postings_for(self, word: str) -> dict[str, dict[str, int | list[int]]]:
        """Return the postings dict for *word*, or an empty dict if not found.

        The lookup is case-insensitive: ``postings_for("GOOD")`` returns the
        same result as ``postings_for("good")``.
        """
        normalized = self.normalize_word(word)
        if not normalized:
            return {}
        return self.index.get(normalized, {})

    @staticmethod
    def normalize_word(word: str) -> str:
        """Strip surrounding whitespace and convert *word* to lower-case."""
        return word.strip().lower()

    @classmethod
    def tokenize(cls, text: str) -> list[str]:
        """Extract normalised tokens from *text*.

        Tokens are sequences of letters, digits, and apostrophes.  Leading
        and trailing apostrophes are stripped from each token so that
        quotation artefacts (e.g. ``'twas``) are indexed without the
        surrounding punctuation.  Empty strings after stripping are discarded.
        """
        tokens = []
        for raw in TOKEN_PATTERN.findall(text):
            token = cls.normalize_word(raw).strip("'")
            if token:
                tokens.append(token)
        return tokens

    @classmethod
    def _tokens_for_page_content(cls, page: CrawledQuote) -> list[str]:
        """Return the ordered token stream for all content on *page*."""
        segments = [page.text, page.author, *page.tags]
        combined_text = " ".join(segment for segment in segments if segment)
        return cls.tokenize(combined_text)
