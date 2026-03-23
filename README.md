# COMP3011 Search Engine Tool

Skeleton project structure for `COMP3011 Coursework 2`.

## Project Overview

This repository will contain a Python command-line search engine tool for `https://quotes.toscrape.com/`.

## Repository Structure

```text
repository-name/
├── src/
│   ├── crawler.py
│   ├── indexer.py
│   ├── search.py
│   └── main.py
├── tests/
│   ├── test_crawler.py
│   ├── test_indexer.py
│   └── test_search.py
├── data/
│   └── index.json
├── requirements.txt
└── README.md
```

## Current State

The first increment is now in place:

- a working interactive shell
- recognition of `build`, `load`, `print`, `find`, and `exit`
- placeholder responses for commands whose full functionality is not implemented yet

## Planned Commands

- `build`
- `load`
- `print <word>`
- `find <query>`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Running

```bash
python3 -m src.main
```

Example:

```text
> build
build command recognized. Crawling is not implemented yet.
> print nonsense
print command recognized for word 'nonsense'.
> find good friends
find command recognized for query 'good friends'.
> exit
Goodbye.
```
