from __future__ import annotations

from pathlib import Path

from src.crawler import WebsiteCrawler
from src.indexer import InvertedIndex
from src.search import SearchEngine


class SearchShell:
    def __init__(
        self,
        crawler: WebsiteCrawler | None = None,
        indexer: InvertedIndex | None = None,
        search_engine: SearchEngine | None = None,
        index_path: str | Path = "data/index.json",
    ) -> None:
        self.crawler = crawler or WebsiteCrawler()
        self.indexer = indexer or InvertedIndex()
        self.search_engine = search_engine or SearchEngine()
        self.index_path = Path(index_path)

    def execute(self, command_line: str) -> str:
        if not command_line.strip():
            return "Please enter a command."

        parts = command_line.strip().split()
        command = parts[0].lower()
        args = parts[1:]

        if command == "build":
            return self._build_index()
        if command == "load":
            return self._load_index()
        if command == "print":
            if len(args) != 1:
                return "Usage: print <word>"
            return self._print_word(args[0])
        if command == "find":
            if not args:
                return "Usage: find <query>"
            return self._find_query(" ".join(args))
        if command in {"exit", "quit"}:
            return "Goodbye."
        return f"Unknown command: {command}"

    def _build_index(self) -> str:
        try:
            quotes = self.crawler.crawl()
            index = self.indexer.build(quotes)
            self.indexer.save(self.index_path)
        except Exception as error:
            return f"Build failed: {error}"

        self.search_engine.set_index(index)
        page_count = len({quote.page_url for quote in quotes})
        return f"Built index from {len(quotes)} quotes across {page_count} pages and {len(index)} terms."

    def _load_index(self) -> str:
        try:
            index = self.indexer.load(self.index_path)
        except Exception as error:
            return f"Load failed: {error}"

        self.search_engine.set_index(index)
        return f"Loaded index from {self.index_path}."

    def _print_word(self, word: str) -> str:
        postings = self.indexer.postings_for(word)
        if not postings:
            return f"No postings found for '{word}'."

        lines = [f"Postings for '{word}':"]
        for page_url in sorted(postings):
            posting = postings[page_url]
            frequency = posting.get("frequency", 0)
            positions = posting.get("positions", [])
            lines.append(f"{page_url} -> frequency={frequency}, positions={positions}")
        return "\n".join(lines)

    def _find_query(self, query: str) -> str:
        results = self.search_engine.find(query)
        if not results:
            return f"No results found for query '{query}'."

        lines = [f"Results for '{query}':", *results]
        return "\n".join(lines)

    def repl(self) -> None:

        # Run the interactive shell
        print("COMP3011 Search Engine Tool")
        print("Commands: build, load, print <word>, find <query>, exit")

        while True:
            try:
                command_line = input("> ")
            except KeyboardInterrupt:
                print("\nGoodbye.")
                break
            except EOFError:
                print("\nGoodbye.")
                break

            result = self.execute(command_line)
            print(result)
            if result == "Goodbye.":
                break


def main() -> None:
    SearchShell().repl()


if __name__ == "__main__":
    main()
