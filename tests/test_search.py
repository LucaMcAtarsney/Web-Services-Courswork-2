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
