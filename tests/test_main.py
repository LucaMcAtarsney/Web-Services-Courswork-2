from pathlib import Path

from src.crawler import CrawledQuote
from src.main import SearchShell


class FakeCrawler:
    def __init__(self, quotes: list[CrawledQuote]) -> None:
        self.quotes = quotes
        self.called = False

    def crawl(self) -> list[CrawledQuote]:
        self.called = True
        return self.quotes


class FakeIndexer:
    def __init__(
        self,
        built_index: dict[str, dict[str, dict[str, int | list[int]]]] | None = None,
        loaded_index: dict[str, dict[str, dict[str, int | list[int]]]] | None = None,
        postings: dict[str, dict[str, int | list[int]]] | None = None,
    ) -> None:
        self.built_index = built_index or {}
        self.loaded_index = loaded_index or {}
        self.postings = postings or {}
        self.saved_path: Path | None = None
        self.loaded_path: Path | None = None

    def build(
        self,
        quotes: list[CrawledQuote],
    ) -> dict[str, dict[str, dict[str, int | list[int]]]]:
        return self.built_index

    def save(self, file_path: str | Path) -> None:
        self.saved_path = Path(file_path)

    def load(self, file_path: str | Path) -> dict[str, dict[str, dict[str, int | list[int]]]]:
        self.loaded_path = Path(file_path)
        return self.loaded_index

    def postings_for(self, word: str) -> dict[str, dict[str, int | list[int]]]:
        return self.postings


class FakeSearchEngine:
    def __init__(self, results: list[str] | None = None) -> None:
        self.results = results or []
        self.index: dict[str, dict[str, dict[str, int | list[int]]]] | None = None

    def set_index(self, index: dict[str, dict[str, dict[str, int | list[int]]]]) -> None:
        self.index = index

    def find(self, query: str) -> list[str]:
        return self.results


def test_shell_build_and_load_commands_use_real_integration_flow():
    quotes = [
        CrawledQuote(
            text='"Good friends, good books."',
            author="Author One",
            tags=["friendship"],
            page_url="https://quotes.toscrape.com/page/1/",
        )
    ]
    built_index = {
        "good": {
            "https://quotes.toscrape.com/page/1/": {"frequency": 2, "positions": [0, 2]},
        }
    }
    loaded_index = {
        "friends": {
            "https://quotes.toscrape.com/page/1/": {"frequency": 1, "positions": [1]},
        }
    }
    crawler = FakeCrawler(quotes)
    indexer = FakeIndexer(built_index=built_index, loaded_index=loaded_index)
    search_engine = FakeSearchEngine()
    shell = SearchShell(
        crawler=crawler,
        indexer=indexer,
        search_engine=search_engine,
        index_path="data/index.json",
    )

    assert shell.execute("build") == "Built index from 1 quotes across 1 pages and 1 terms."
    assert crawler.called is True
    assert indexer.saved_path == Path("data/index.json")
    assert search_engine.index == built_index

    assert shell.execute("load") == "Loaded index from data/index.json."
    assert indexer.loaded_path == Path("data/index.json")
    assert search_engine.index == loaded_index


def test_shell_print_and_find_commands_format_results():
    postings = {
        "https://quotes.toscrape.com/page/1/": {"frequency": 2, "positions": [0, 2]},
    }
    results = ["https://quotes.toscrape.com/page/1/"]
    shell = SearchShell(
        crawler=FakeCrawler([]),
        indexer=FakeIndexer(postings=postings),
        search_engine=FakeSearchEngine(results=results),
    )

    assert shell.execute("print good") == (
        "Postings for 'good':\n"
        "https://quotes.toscrape.com/page/1/ -> frequency=2, positions=[0, 2]"
    )
    assert shell.execute("find good friends") == (
        "Results for 'good friends':\n"
        "https://quotes.toscrape.com/page/1/"
    )


def test_shell_validates_arguments_and_handles_missing_results():
    shell = SearchShell(
        crawler=FakeCrawler([]),
        indexer=FakeIndexer(postings={}),
        search_engine=FakeSearchEngine(results=[]),
    )

    assert shell.execute("") == "Please enter a command."
    assert shell.execute("print") == "Usage: print <word>"
    assert shell.execute("print nonsense") == "No postings found for 'nonsense'."
    assert shell.execute("find") == "Usage: find <query>"
    assert shell.execute("find missing query") == "No results found for query 'missing query'."
    assert shell.execute("dance") == "Unknown command: dance"
    assert shell.execute("exit") == "Goodbye."
