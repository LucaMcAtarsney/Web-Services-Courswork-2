from src.crawler import CrawledQuote, WebsiteCrawler


class FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text

    def raise_for_status(self) -> None:
        return None


class FakeSession:
    def __init__(self, pages: dict[str, str]) -> None:
        self.pages = pages
        self.requested_urls: list[str] = []

    def get(self, url: str, timeout: float) -> FakeResponse:
        self.requested_urls.append(url)
        return FakeResponse(self.pages[url])


class FakeSleeper:
    def __init__(self) -> None:
        self.calls: list[float] = []

    def __call__(self, seconds: float) -> None:
        self.calls.append(seconds)


def test_parse_page_extracts_quotes_and_next_page_url():
    crawler = WebsiteCrawler(base_url="https://quotes.toscrape.com")
    html = """
    <html>
      <body>
        <div class="quote">
          <span class="text">"A witty saying proves nothing."</span>
          <small class="author">Voltaire</small>
          <div class="tags">
            <a class="tag">wit</a>
            <a class="tag">truth</a>
          </div>
        </div>
        <li class="next"><a href="/page/2/">Next</a></li>
      </body>
    </html>
    """

    quotes, next_url = crawler._parse_page(html, "https://quotes.toscrape.com/")

    assert quotes == [
        CrawledQuote(
            text='"A witty saying proves nothing."',
            author="Voltaire",
            tags=["wit", "truth"],
            page_url="https://quotes.toscrape.com/",
        )
    ]
    assert next_url == "https://quotes.toscrape.com/page/2/"


def test_crawl_follows_pagination_until_no_next_link():
    session = FakeSession(
        {
            "https://quotes.toscrape.com/": """
            <div class="quote">
              <span class="text">"Quote one."</span>
              <small class="author">Author One</small>
              <div class="tags"><a class="tag">first</a></div>
            </div>
            <li class="next"><a href="/page/2/">Next</a></li>
            """,
            "https://quotes.toscrape.com/page/2/": """
            <div class="quote">
              <span class="text">"Quote two."</span>
              <small class="author">Author Two</small>
              <div class="tags"><a class="tag">second</a></div>
            </div>
            """,
        }
    )
    sleeper = FakeSleeper()
    crawler = WebsiteCrawler(session=session, sleeper=sleeper)

    quotes = crawler.crawl()

    assert quotes == [
        CrawledQuote(
            text='"Quote one."',
            author="Author One",
            tags=["first"],
            page_url="https://quotes.toscrape.com/",
        ),
        CrawledQuote(
            text='"Quote two."',
            author="Author Two",
            tags=["second"],
            page_url="https://quotes.toscrape.com/page/2/",
        ),
    ]
    assert session.requested_urls == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    ]
    assert sleeper.calls == [6.0]


def test_crawl_respects_max_pages_limit():
    session = FakeSession(
        {
            "https://quotes.toscrape.com/": """
            <div class="quote">
              <span class="text">"Quote one."</span>
              <small class="author">Author One</small>
              <div class="tags"><a class="tag">first</a></div>
            </div>
            <li class="next"><a href="/page/2/">Next</a></li>
            """,
            "https://quotes.toscrape.com/page/2/": """
            <div class="quote">
              <span class="text">"Quote two."</span>
              <small class="author">Author Two</small>
              <div class="tags"><a class="tag">second</a></div>
            </div>
            """,
        }
    )
    sleeper = FakeSleeper()
    crawler = WebsiteCrawler(session=session, sleeper=sleeper)

    quotes = crawler.crawl(max_pages=1)

    assert quotes == [
        CrawledQuote(
            text='"Quote one."',
            author="Author One",
            tags=["first"],
            page_url="https://quotes.toscrape.com/",
        )
    ]
    assert session.requested_urls == ["https://quotes.toscrape.com/"]
    assert sleeper.calls == []
