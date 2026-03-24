from pathlib import Path

from src.crawler import CrawledQuote
from src.indexer import InvertedIndex


def test_tokenize_normalizes_case_and_ignores_surrounding_punctuation():
    tokens = InvertedIndex.tokenize('"Good" friends, GOOD sense!')

    assert tokens == ["good", "friends", "good", "sense"]


def test_build_creates_case_insensitive_postings_with_frequency_and_positions():
    index = InvertedIndex()
    pages = [
        CrawledQuote(
            text='"Good friends, good books."',
            author="Author One",
            tags=["Friendship"],
            page_url="https://quotes.toscrape.com/page/1/",
        ),
        CrawledQuote(
            text='"A good friend is enough."',
            author="Author Two",
            tags=["good"],
            page_url="https://quotes.toscrape.com/page/2/",
        ),
    ]

    built_index = index.build(pages)

    assert built_index["good"] == {
        "https://quotes.toscrape.com/page/1/": {"frequency": 2, "positions": [0, 2]},
        "https://quotes.toscrape.com/page/2/": {"frequency": 2, "positions": [1, 7]},
    }
    assert built_index["friendship"] == {
        "https://quotes.toscrape.com/page/1/": {"frequency": 1, "positions": [6]}
    }
    assert index.page_token_counts == {
        "https://quotes.toscrape.com/page/1/": 7,
        "https://quotes.toscrape.com/page/2/": 8,
    }


def test_postings_for_uses_case_insensitive_lookup_and_handles_missing_words():
    index = InvertedIndex()
    index.build(
        [
            CrawledQuote(
                text='"Good things take time."',
                author="Author",
                tags=[],
                page_url="https://quotes.toscrape.com/page/1/",
            )
        ]
    )

    assert index.postings_for("GOOD") == {
        "https://quotes.toscrape.com/page/1/": {"frequency": 1, "positions": [0]}
    }
    assert index.postings_for("missing") == {}
    assert index.postings_for("   ") == {}


def test_save_and_load_round_trip_index_data(tmp_path: Path):
    index = InvertedIndex()
    index.build(
        [
            CrawledQuote(
                text='"Nonsense improves nonsense."',
                author="Tester",
                tags=["wit"],
                page_url="https://quotes.toscrape.com/page/3/",
            )
        ]
    )

    file_path = tmp_path / "data" / "index.json"
    index.save(file_path)

    loaded_index = InvertedIndex()
    result = loaded_index.load(file_path)

    assert file_path.exists()
    assert result == index.index
    assert loaded_index.page_token_counts == index.page_token_counts
