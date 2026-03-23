from __future__ import annotations


class SearchShell:

    def execute(self, command_line: str) -> str:
        if not command_line.strip():
            return "Please enter a command."

        parts = command_line.strip().split()
        command = parts[0].lower()
        args = parts[1:]

        if command == "build":
            return "build command recognized. Crawling is not implemented yet."
        if command == "load":
            return "load command recognized. Index loading is not implemented yet."
        if command == "print":
            if len(args) != 1:
                return "Usage: print <word>"
            return f"print command recognized for word '{args[0]}'."
        if command == "find":
            if not args:
                return "Usage: find <query>"
            return f"find command recognized for query '{' '.join(args)}'."
        if command in {"exit", "quit"}:
            return "Goodbye."
        return f"Unknown command: {command}"

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
