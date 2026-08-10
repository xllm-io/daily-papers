import os
import time
import logging
import pytz
import shutil
import datetime
from typing import List, Dict, Optional

import feedparser
from easydict import EasyDict
import urllib.request, urllib.error, urllib.parse

from config import (
    MAX_COMMENT_LENGTH, COMMENT_SUMMARY_LENGTH,
    API_DELAY, MAX_RETRIES, RETRY_DELAY,
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

beijing_tz = pytz.timezone('Asia/Shanghai')


def remove_duplicated_spaces(text: str) -> str:
    return " ".join(text.split())


def request_paper_with_arXiv_api(keyword: str, max_results: int, link: str = "OR") -> List[Dict[str, str]]:
    assert link in ("OR", "AND"), "link should be 'OR' or 'AND'"
    keyword = f'"{keyword}"'
    url = (
        f"http://export.arxiv.org/api/query"
        f"?search_query=ti:{keyword}+{link}+abs:{keyword}"
        f"&max_results={max_results}&sortBy=lastUpdatedDate"
    )
    url = urllib.parse.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    logger.info("[###] keyword: %s, url: %s", keyword, url)
    response = urllib.request.urlopen(url, timeout=30).read().decode('utf-8')
    feed = feedparser.parse(response)
    return [EasyDict(entry) for entry in feed.entries]


def filter_tags(
    papers: List[Dict[str, str]],
    target_fileds: List[str] = ("cs", "stat"),
) -> List[Dict[str, str]]:
    results = []
    for paper in papers:
        if any(tag.split(".")[0] in target_fileds for tag in paper.Tags):
            results.append(paper)
    return results


def get_daily_papers_by_keyword(
    keyword: str,
    column_names: List[str],
    max_results: int,
    link: str = "OR",
) -> List[Dict[str, str]]:
    papers = request_paper_with_arXiv_api(keyword, max_results, link)
    papers = filter_tags(papers)
    return [
        {col: paper[col] for col in column_names}
        for paper in papers
    ]


def get_daily_papers_by_keyword_with_retries(
    keyword: str,
    column_names: List[str],
    max_results: int,
    link: str = "OR",
    retries: int = MAX_RETRIES,
) -> Optional[List[Dict[str, str]]]:
    for attempt in range(retries):
        try:
            papers = get_daily_papers_by_keyword(keyword, column_names, max_results, link)
            if papers:
                return papers
            logger.warning("Keyword '%s': empty result (attempt %d/%d)", keyword, attempt + 1, retries)
        except urllib.error.URLError as e:
            logger.warning("Keyword '%s': network error (%s), attempt %d/%d",
                           keyword, e.reason, attempt + 1, retries)
        except Exception as e:
            logger.error("Keyword '%s': unexpected error: %s", keyword, e)
        if attempt < retries - 1:
            time.sleep(RETRY_DELAY)
    logger.error("Keyword '%s': failed after %d retries", keyword, retries)
    return None


def generate_table(papers: List[Dict[str, str]], ignore_keys: List[str] = None) -> str:
    if ignore_keys is None:
        ignore_keys = []
    formatted = []
    for paper in papers:
        row: Dict[str, str] = {}
        row["Title"] = f"**[{paper['Title']}]( {paper['Link']})**"
        row["Date"] = paper["Date"].split("T")[0]
        for key in paper:
            if key in ("Title", "Link", "Date") or key in ignore_keys:
                continue
            if key == "Abstract":
                row[key] = f"<details><summary>Show</summary><p>{paper[key]}</p></details>"
            elif key == "Authors":
                row[key] = f"{paper[key][0]} et al."
            elif key == "Tags":
                tags = ", ".join(paper[key])
                row[key] = (
                    f"<details><summary>{tags[:5]}...</summary><p>{tags}</p></details>"
                    if len(tags) > 10
                    else tags
                )
            elif key == "Comment":
                if paper[key]:
                    raw = paper[key]
                    comment = (raw[:MAX_COMMENT_LENGTH].rstrip() + " [truncated]"
                               if len(raw) > MAX_COMMENT_LENGTH
                               else raw)
                    if len(comment) > 20:
                        row[key] = (
                            f"<details><summary>{comment[:COMMENT_SUMMARY_LENGTH]}...</summary>"
                            f"<p>{comment}</p></details>"
                        )
                    else:
                        row[key] = comment
                else:
                    row[key] = ""
        formatted.append(row)

    columns = list(formatted[0].keys())
    header = "| " + " | ".join(f"**{c}**" for c in columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = "\n".join("| " + " | ".join(row.values()) + " |" for row in formatted)
    return header + "\n" + sep + "\n" + body


class _BackupManager:
    """Safely backs up, restores, or removes files with .bk suffix."""

    def __init__(self, *files: str):
        self.files = files
        self.bks = [f + ".bk" for f in files]

    def _restore(self) -> None:
        for bk, orig in zip(self.bks, self.files):
            if os.path.exists(bk):
                shutil.move(bk, orig)

    def backup(self) -> None:
        for f, bk in zip(self.files, self.bks):
            if os.path.exists(f):
                shutil.move(f, bk)

    def remove(self) -> None:
        for bk in self.bks:
            if os.path.exists(bk):
                os.remove(bk)

    def __enter__(self) -> "_BackupManager":
        self.backup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is not None:
            self._restore()
        else:
            self.remove()
        return False  # do not suppress exceptions


def get_daily_date() -> str:
    today = datetime.datetime.now(beijing_tz)
    return today.strftime("%B %d, %Y")
