"""Web crawler for https://quotes.toscrape.com/ with configurable politeness delay."""

from __future__ import annotations

from dataclasses import dataclass
from time import sleep
from typing import Any, Callable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class CrawledQuote:
    """Immutable record for a single quote extracted from a crawled page."""

    text: str
    author: str
    tags: list[str]
    page_url: str


class WebsiteCrawler:
    """Crawls all quote pages on the target site and returns structured records.

    A configurable politeness delay (default 6 s) is enforced between every
    successive HTTP request.  The crawler follows pagination links until no
    "next" link is found, a ``max_pages`` limit is reached, or a network error
    occurs, at which point it stops and returns whatever it has collected.
    """

    def __init__(
        self,
        base_url: str = "https://quotes.toscrape.com",
        session: requests.Session | Any | None = None,
        timeout: float = 10.0,
        politeness_delay: float = 6.0,
        sleeper: Callable[[float], None] = sleep,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.timeout = timeout
        self.politeness_delay = politeness_delay
        self.sleeper = sleeper

    def crawl(self, max_pages: int | None = None) -> list[CrawledQuote]:
        """Crawl all quote pages and return a flat list of extracted quotes.

        Pagination is followed automatically.  The first page is fetched
        immediately; each subsequent page waits ``politeness_delay`` seconds.
        On an unrecoverable network or HTTP error the crawl stops early and
        returns whatever quotes have been collected so far.
        """
        quotes: list[CrawledQuote] = []
        next_url = f"{self.base_url}/"
        visited_urls: set[str] = set()
        pages_crawled = 0

        while next_url and next_url not in visited_urls:
            if max_pages is not None and pages_crawled >= max_pages:
                break

            if pages_crawled > 0:
                self.sleeper(self.politeness_delay)

            visited_urls.add(next_url)
            try:
                html = self._fetch_page(next_url)
                page_quotes, next_url = self._parse_page(html, next_url)
                quotes.extend(page_quotes)
            except requests.RequestException:
                break

            pages_crawled += 1

        return quotes

    def _fetch_page(self, url: str) -> str:
        """Fetch *url* and return its HTML body, raising on HTTP errors."""
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def _parse_page(self, html: str, page_url: str) -> tuple[list[CrawledQuote], str | None]:
        """Parse an HTML page into a list of quotes and the next-page URL."""
        soup = BeautifulSoup(html, "html.parser")
        quotes = [self._parse_quote(block, page_url) for block in soup.select("div.quote")]

        next_link = soup.select_one("li.next > a")
        next_href = next_link.get("href") if next_link is not None else None
        next_url = urljoin(page_url, next_href) if next_href else None
        return quotes, next_url

    @staticmethod
    def _parse_quote(quote_block: Any, page_url: str) -> CrawledQuote:
        """Extract a single :class:`CrawledQuote` from a ``div.quote`` block."""
        text_element = quote_block.select_one("span.text")
        author_element = quote_block.select_one("small.author")
        tags = [tag.get_text(strip=True) for tag in quote_block.select(".tags a.tag")]

        if text_element is None or author_element is None:
            raise ValueError("Quote block is missing required text or author fields.")

        return CrawledQuote(
            text=text_element.get_text(strip=True),
            author=author_element.get_text(strip=True),
            tags=tags,
            page_url=page_url,
        )
