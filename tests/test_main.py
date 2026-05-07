from pathlib import Path

from src.crawler import CrawledQuote
from src.indexer import InvertedIndex
from src.main import SearchShell
from src.search import SearchEngine


class FakeCrawler:
    def crawl(self) -> list[CrawledQuote]:
        return [
            CrawledQuote(
                text='"Good friends, good books."',
                author="Author One",
                tags=["friendship"],
                page_url="https://quotes.toscrape.com/page/1/",
            ),
            CrawledQuote(
                text='"A good friend is enough."',
                author="Author Two",
                tags=["wisdom"],
                page_url="https://quotes.toscrape.com/page/2/",
            ),
        ]


class FailingCrawler:
    """Crawler that always raises to simulate a network failure."""

    def crawl(self) -> list[CrawledQuote]:
        raise RuntimeError("Simulated network failure")


def make_shell(index_path: Path) -> SearchShell:
    indexer = InvertedIndex()
    search_engine = SearchEngine()
    return SearchShell(
        crawler=FakeCrawler(),
        indexer=indexer,
        search_engine=search_engine,
        index_path=index_path,
    )


def test_shell_build_creates_saves_and_uses_index(tmp_path: Path):
    shell = make_shell(tmp_path / "index.json")

    assert shell.execute("build") == "Built index from 2 quotes across 2 pages and 12 terms."
    assert (tmp_path / "index.json").exists()
    assert shell.execute("find good friends") == "\n".join(
        [
            "Results for 'good friends':",
            "https://quotes.toscrape.com/page/1/",
        ]
    )


def test_shell_load_restores_index_for_print_and_find(tmp_path: Path):
    first_shell = make_shell(tmp_path / "index.json")
    first_shell.execute("build")

    loaded_shell = SearchShell(index_path=tmp_path / "index.json")

    assert loaded_shell.execute("load") == f"Loaded index from {tmp_path / 'index.json'}."
    assert loaded_shell.execute("print GOOD") == "\n".join(
        [
            "Postings for 'GOOD':",
            "https://quotes.toscrape.com/page/1/ -> frequency=2, positions=[0, 2]",
            "https://quotes.toscrape.com/page/2/ -> frequency=1, positions=[1]",
        ]
    )
    assert loaded_shell.execute("find wisdom") == "\n".join(
        [
            "Results for 'wisdom':",
            "https://quotes.toscrape.com/page/2/",
        ]
    )


def test_shell_validates_print_and_find_arguments(tmp_path: Path):
    shell = make_shell(tmp_path / "index.json")

    assert shell.execute("print") == "Usage: print <word>"
    assert shell.execute("print nonsense") == "No postings found for 'nonsense'."
    assert shell.execute("find") == "Usage: find <query>"
    assert shell.execute("find good friends") == "No results found for query 'good friends'."


def test_shell_handles_empty_unknown_and_exit_commands(tmp_path: Path):
    shell = make_shell(tmp_path / "index.json")

    assert shell.execute("") == "Please enter a command."
    assert shell.execute("dance") == "Unknown command: dance"
    assert shell.execute("exit") == "Goodbye."


def test_shell_load_returns_error_message_for_missing_index_file(tmp_path: Path):
    """Loading an index before build has run should produce a helpful message."""
    shell = SearchShell(index_path=tmp_path / "does_not_exist.json")

    result = shell.execute("load")

    assert "not found" in result.lower()
    assert "build" in result.lower()


def test_shell_build_returns_error_message_on_crawl_failure(tmp_path: Path):
    """If the crawler raises, build should return an error string, not propagate."""
    shell = SearchShell(
        crawler=FailingCrawler(),
        index_path=tmp_path / "index.json",
    )

    result = shell.execute("build")

    assert "failed" in result.lower()
    assert not (tmp_path / "index.json").exists()
