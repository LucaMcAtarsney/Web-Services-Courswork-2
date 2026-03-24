from __future__ import annotations

from src.indexer import InvertedIndex


class SearchEngine:

    def __init__(
        self,
        index: dict[str, dict[str, dict[str, int | list[int]]]] | None = None,
    ) -> None:
        self.index = index or {}

    def set_index(self, index: dict[str, dict[str, dict[str, int | list[int]]]]) -> None:
        self.index = index

    def find(self, query: str) -> list[str]:
        # Return pages that contain all query terms
        terms = self._normalize_query(query)
        if not terms:
            return []

        postings_by_term = [self.index.get(term, {}) for term in terms]
        if any(not postings for postings in postings_by_term):
            return []

        matching_pages = set(postings_by_term[0])
        for postings in postings_by_term[1:]:
            matching_pages &= set(postings)

        return sorted(
            matching_pages,
            key=lambda page_url: (-self._score_page(page_url, terms), page_url),
        )

    @staticmethod
    def _normalize_query(query: str) -> list[str]:
        return InvertedIndex.tokenize(query)

    def _score_page(self, page_url: str, terms: list[str]) -> int:
        score = 0
        for term in terms:
            page_stats = self.index.get(term, {}).get(page_url, {})
            score += int(page_stats.get("frequency", 0))
        return score
