"""Search engine module providing TF-IDF ranked retrieval over an inverted index."""

from __future__ import annotations

import math

from src.indexer import InvertedIndex


class SearchEngine:
    """Ranked search over an in-memory inverted index using TF-IDF scoring.

    Boolean AND semantics are used: every query term must appear in a page for
    that page to be returned.  Matching pages are ranked by their combined
    TF-IDF score (descending), with URL as a deterministic tiebreaker.

    TF-IDF formula
    --------------
    TF(term, page)  = term frequency in page / total tokens in page
    IDF(term)       = log((N + 1) / (df + 1)) + 1   (Laplace-smoothed)
    Score(page)     = Σ  TF(t, page) × IDF(t)  for each query term t

    where N is the total number of distinct pages in the index and df is the
    number of pages that contain the term.  The +1 smoothing prevents zero
    division and moderates the influence of very rare terms.
    """

    def __init__(
        self,
        index: dict[str, dict[str, dict[str, int | list[int]]]] | None = None,
        page_token_counts: dict[str, int] | None = None,
    ) -> None:
        self.index: dict[str, dict[str, dict[str, int | list[int]]]] = index or {}
        self.page_token_counts: dict[str, int] = page_token_counts or {}

    def set_index(
        self,
        index: dict[str, dict[str, dict[str, int | list[int]]]],
        page_token_counts: dict[str, int] | None = None,
    ) -> None:
        """Replace the active index and optionally update page token counts."""
        self.index = index
        if page_token_counts is not None:
            self.page_token_counts = page_token_counts

    def find(self, query: str) -> list[str]:
        """Return all pages containing every query term, ranked by TF-IDF score.

        Pages missing any single term are excluded (Boolean AND).  Results
        with identical scores are ordered lexicographically by URL so that
        output is fully deterministic.

        Time complexity: O(t × p) where t = number of query terms and
        p = number of pages in the matching set.
        """
        terms = self._normalize_query(query)
        if not terms:
            return []

        postings_by_term = [self.index.get(term, {}) for term in terms]
        if any(not postings for postings in postings_by_term):
            return []

        matching_pages: set[str] = set(postings_by_term[0])
        for postings in postings_by_term[1:]:
            matching_pages &= set(postings)

        total_pages = len({url for postings in self.index.values() for url in postings})

        return sorted(
            matching_pages,
            key=lambda page_url: (-self._score_page(page_url, terms, total_pages), page_url),
        )

    @staticmethod
    def _normalize_query(query: str) -> list[str]:
        """Tokenize and normalise a raw query string using the indexer's rules."""
        return InvertedIndex.tokenize(query)

    def _score_page(self, page_url: str, terms: list[str], total_pages: int) -> float:
        """Compute the summed TF-IDF score for *page_url* over all query *terms*.

        Falls back to 0.0 when the index is empty.
        """
        if total_pages == 0:
            return 0.0

        score = 0.0
        for term in terms:
            postings = self.index.get(term, {})
            page_stats = postings.get(page_url, {})
            freq = int(page_stats.get("frequency", 0))
            total_tokens = self.page_token_counts.get(page_url, 1) or 1

            tf = freq / total_tokens
            df = len(postings)
            idf = math.log((total_pages + 1) / (df + 1)) + 1

            score += tf * idf

        return score
