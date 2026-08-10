# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Daily Papers is a Python script that automatically fetches the latest papers from arXiv based on configurable keywords and writes them into `README.md` (display table) and `.github/ISSUE_TEMPLATE.md` (issue body). A GitHub Actions workflow runs daily to update both files and commit the changes.

## Commands

```bash
# Run the full pipeline (regenerates README.md and .github/ISSUE_TEMPLATE.md)
python main.py

# Install dependencies
pip install -r requirements.txt

# Smoke test (queries arXiv for "Sparse Attention", writes res.json — no assertions)
python test.py
```

The GitHub Actions workflow in `.github/workflows/update.yaml` runs `main.py` automatically on a cron schedule (00:30 Beijing time, Mon–Fri), commits the generated files to `main`, and creates a GitHub issue via `JasonEtco/create-an-issue@v2`. It also supports manual dispatch (`workflow_dispatch`) and a `label.created` trigger.

## Architecture

- **`config.py`** — All tunable parameters: keyword list, `max_result` (50 papers per keyword), `issues_result` (20 papers for the issue body — must stay under GitHub's 65,536-char issue body limit), output file paths, and the column set displayed (`Title`, `Link`, `Abstract`, `Date`, `Comment`).
- **`main.py`** — Orchestration. Reads the current `Last update:` line from `README.md` (currently unused — the no-op skip is commented out at lines 32–33). Backs up both output files, iterates over keywords, calls the retrying API layer, generates tables, writes the files, and removes backups. Exits with code 1 on any API failure.
- **`utils.py`** — Core logic:
  - `request_paper_with_arXiv_api()` — builds the arXiv query URL, calls the API, parses the feed with `feedparser`, and returns a list of `EasyDict` paper objects with fields: Title, Abstract, Authors, Link, Tags, Comment, Date.
  - `filter_tags()` — keeps only papers whose tags match the default `["cs", "stat"]` prefix.
  - `get_daily_papers_by_keyword_with_retries()` — wraps the above with up to 6 retries and 60 s back-off on empty results.
  - `generate_table()` — renders a Markdown table. Abstract and long Tags/Comments are collapsed into `<details>` blocks; Comments are truncated at 500 chars.
  - `back_up_files()` / `restore_files()` / `remove_backups()` — safe round-trip for the two output files.
  - `get_daily_date()` — returns today's date in Beijing time as `"Month D, YYYY"`.
- **`.github/workflows/update.yaml`** — GitHub Action scheduled at 00:30 Beijing time (16:30 UTC) Mon–Fri. Runs `main.py`, commits updated `README.md` and `.github/ISSUE_TEMPLATE.md` to `main` (author: zhangjun / ewalker@live.cn), and creates a GitHub issue via `JasonEtco/create-an-issue@v2` to notify watchers. Also supports manual dispatch (`workflow_dispatch`) and a `label.created` trigger (for testing).
- **`README.md`** — The generated output; subheadings are the keywords. Each entry is a Markdown table row. Currently ~1MB.
- **`.github/ISSUE_TEMPLATE.md`** — A smaller copy of the README table (max `issues_result` papers per keyword, Abstract omitted), used as the body of the daily issue created by the workflow. Must stay under GitHub's 65,536-char limit for issue bodies.

## Key Behaviors

- **Link strategy**: keywords with a single word use `AND` (must appear in both title and abstract); multi-word keywords use `OR`.
- **Author display**: only the first author is shown, formatted as `"Name et al."`.
- **Date handling**: the raw arXiv `updated` field (`2021-08-01T00:00:00Z`) is stripped to `YYYY-MM-DD` in the table.
- **Safety on failure**: `_BackupManager` context manager ensures original files are restored if any keyword fails — the commit is rolled back automatically.
- **Retry logic**: up to 6 retries per keyword with 60s delay. Network errors (`URLError`) and empty results are handled separately in logs.
- **Timeout**: arXiv API calls have a 30-second timeout to prevent hanging.

## Common Tasks

- **Add a new keyword**: edit `config.py` and append to the `keywords` list.
- **Change result counts**: adjust `max_result` (README, default 50) or `issues_result` (issue body, default 20) in `config.py`. Keep `issues_result` low enough that `13 × issues_result × ~205 chars/row < 65,536`.
- **Change displayed columns**: modify `column_names` in `config.py`.
- **Adjust retry behavior**: modify `MAX_RETRIES` and `RETRY_DELAY` in `config.py`.
- **Adjust API delay**: modify `API_DELAY` in `config.py` (default 5s between keywords).
- **Run tests**: `python test.py` runs a connectivity smoke test against the arXiv API.
