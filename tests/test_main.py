from src.main import SearchShell


def test_shell_recognizes_top_level_commands():
    shell = SearchShell()

    assert shell.execute("build") == "build command recognized. Crawling is not implemented yet."
    assert shell.execute("load") == "load command recognized. Index loading is not implemented yet."


def test_shell_validates_print_and_find_arguments():
    shell = SearchShell()

    assert shell.execute("print") == "Usage: print <word>"
    assert shell.execute("print nonsense") == "print command recognized for word 'nonsense'."
    assert shell.execute("find") == "Usage: find <query>"
    assert shell.execute("find good friends") == "find command recognized for query 'good friends'."


def test_shell_handles_empty_unknown_and_exit_commands():
    shell = SearchShell()

    assert shell.execute("") == "Please enter a command."
    assert shell.execute("dance") == "Unknown command: dance"
    assert shell.execute("exit") == "Goodbye."
