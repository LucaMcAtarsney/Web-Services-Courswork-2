from src.search import SearchEngine


def test_find_returns_empty_list_for_blank_query():
    search = SearchEngine(
        {
            "good": {
                "https://quotes.toscrape.com/page/1/": {"frequency": 1, "positions": [0]},
            }
        }
    )

    assert search.find("   ") == []


def test_find_returns_empty_list_when_any_query_term_is_missing():
    search = SearchEngine(
        {
            "good": {
                "https://quotes.toscrape.com/page/1/": {"frequency": 2, "positions": [0, 2]},
            },
            "friends": {
                "https://quotes.toscrape.com/page/1/": {"frequency": 1, "positions": [1]},
            },
        }
    )

    assert search.find("good missing") == []


def test_find_uses_case_insensitive_and_punctuation_tolerant_query_terms():
    search = SearchEngine(
        {
            "good": {
                "https://quotes.toscrape.com/page/1/": {"frequency": 2, "positions": [0, 2]},
            },
            "friends": {
                "https://quotes.toscrape.com/page/1/": {"frequency": 1, "positions": [1]},
            },
        }
    )

    assert search.find('"GOOD," friends!') == ["https://quotes.toscrape.com/page/1/"]


def test_find_returns_only_pages_that_contain_all_query_terms():
    search = SearchEngine(
        {
            "good": {
                "https://quotes.toscrape.com/page/1/": {"frequency": 2, "positions": [0, 2]},
                "https://quotes.toscrape.com/page/2/": {"frequency": 1, "positions": [3]},
            },
            "friends": {
                "https://quotes.toscrape.com/page/1/": {"frequency": 1, "positions": [1]},
                "https://quotes.toscrape.com/page/3/": {"frequency": 1, "positions": [0]},
            },
        }
    )

    assert search.find("good friends") == ["https://quotes.toscrape.com/page/1/"]


def test_find_ranks_pages_by_total_term_frequency_then_page_url():
    search = SearchEngine(
        {
            "good": {
                "https://quotes.toscrape.com/page/1/": {"frequency": 2, "positions": [0, 2]},
                "https://quotes.toscrape.com/page/2/": {"frequency": 1, "positions": [3]},
                "https://quotes.toscrape.com/page/3/": {"frequency": 1, "positions": [1]},
            },
            "friends": {
                "https://quotes.toscrape.com/page/1/": {"frequency": 1, "positions": [1]},
                "https://quotes.toscrape.com/page/2/": {"frequency": 2, "positions": [0, 4]},
                "https://quotes.toscrape.com/page/3/": {"frequency": 2, "positions": [0, 5]},
            },
        }
    )

    assert search.find("good friends") == [
        "https://quotes.toscrape.com/page/1/",
        "https://quotes.toscrape.com/page/2/",
        "https://quotes.toscrape.com/page/3/",
    ]


def test_set_index_replaces_the_search_index():
    search = SearchEngine()
    new_index = {
        "wisdom": {
            "https://quotes.toscrape.com/page/9/": {"frequency": 1, "positions": [2]},
        }
    }

    search.set_index(new_index)

    assert search.find("wisdom") == ["https://quotes.toscrape.com/page/9/"]


def test_find_ranks_by_tfidf_not_raw_frequency():
    """A page that mentions a term proportionally more often should rank higher
    even when another page has a greater raw count.

    page/1/ mentions 'wisdom' in every token (TF = 1.0).
    page/2/ mentions 'wisdom' in 10 % of its tokens (TF = 0.1).
    Despite page/2/ having a higher raw frequency, TF-IDF should prefer page/1/.
    """
    search = SearchEngine(
        index={
            "wisdom": {
                "https://quotes.toscrape.com/page/1/": {"frequency": 3, "positions": [0, 1, 2]},
                "https://quotes.toscrape.com/page/2/": {"frequency": 10, "positions": list(range(10))},
            }
        },
        page_token_counts={
            "https://quotes.toscrape.com/page/1/": 3,
            "https://quotes.toscrape.com/page/2/": 100,
        },
    )

    results = search.find("wisdom")

    assert results[0] == "https://quotes.toscrape.com/page/1/"
    assert results[1] == "https://quotes.toscrape.com/page/2/"


def test_set_index_accepts_page_token_counts():
    """set_index should update page_token_counts when supplied."""
    search = SearchEngine()
    new_index = {
        "truth": {
            "https://quotes.toscrape.com/page/5/": {"frequency": 2, "positions": [0, 4]},
        }
    }
    token_counts = {"https://quotes.toscrape.com/page/5/": 10}

    search.set_index(new_index, token_counts)

    assert search.page_token_counts == token_counts
