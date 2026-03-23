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

This is only the skeleton scaffold. The implementation will be added incrementally.

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
