from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class CrawledQuote:

    text: str
    author: str
    tags: list[str]
    page_url: str


class WebsiteCrawler:
    # Crawl quote pages from quotes.toscrape.com

    def __init__(
        self,
        base_url: str = "https://quotes.toscrape.com",
        session: requests.Session | Any | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.timeout = timeout

    def crawl(self, max_pages: int | None = None) -> list[CrawledQuote]:
        # Crawl quote pages until pagination ends or max_pages is reached
        quotes: list[CrawledQuote] = []
        next_url = f"{self.base_url}/"
        visited_urls: set[str] = set()
        pages_crawled = 0

        while next_url and next_url not in visited_urls:
            if max_pages is not None and pages_crawled >= max_pages:
                break

            visited_urls.add(next_url)
            html = self._fetch_page(next_url)
            page_quotes, next_url = self._parse_page(html, next_url)
            quotes.extend(page_quotes)
            pages_crawled += 1

        return quotes

    def _fetch_page(self, url: str) -> str:
        # Fetch a single page and return its HTML
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def _parse_page(self, html: str, page_url: str) -> tuple[list[CrawledQuote], str | None]:
        # Extract quote records and the next page URL from page HTML
        soup = BeautifulSoup(html, "html.parser")
        quotes = [self._parse_quote(block, page_url) for block in soup.select("div.quote")]

        next_link = soup.select_one("li.next > a")
        next_href = next_link.get("href") if next_link is not None else None
        next_url = urljoin(page_url, next_href) if next_href else None
        return quotes, next_url

    @staticmethod
    def _parse_quote(quote_block: Any, page_url: str) -> CrawledQuote:
        # Convert a quote block into a structured record
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
