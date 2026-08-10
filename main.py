# Author: zhouchanggeng
# Date: 2025-06-08 09:32:13
# LastEditTime: 2025-06-08 22:43:25
# LastEditors: zhouchanggeng
# Description:
# FilePath: \DailyArXiv\main.py
# Copyright (c) 2024 jiaxun.com, Inc. All Rights Reserved
import sys
import time
import logging
from datetime import datetime

from config import (
    keywords, max_result, issues_result,
    readme_file, issue_template_file, column_names,
    API_DELAY,
)
from utils import (
    get_daily_papers_by_keyword_with_retries,
    generate_table,
    get_daily_date,
    _BackupManager,
    beijing_tz,
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

current_date = datetime.now(beijing_tz).strftime("%Y-%m-%d")
logger.info("Current date (Beijing): %s", current_date)

with _BackupManager(readme_file, issue_template_file):
    with open(readme_file, "w") as f_rm, open(issue_template_file, "w") as f_is:
        f_rm.write(
            "# Daily Papers\n"
            "The project automatically fetches the latest papers from arXiv based on keywords.\n\n"
            "The subheadings in the README file represent the search keywords.\n\n"
            "Only the most recent articles for each keyword are retained, "
            "up to a maximum of 100 papers.\n\n"
            "You can click the 'Watch' button to receive daily email notifications.\n\n"
            f"Last update: {current_date}\n\n"
        )
        f_is.write(
            "---\n"
            f"title: Latest {issues_result} Papers - {get_daily_date()}\n"
            "labels: documentation\n"
            "---\n"
            "**Please check the [Github](https://github.com/zezhishao/MTS_Daily_ArXiv) "
            "page for a better reading experience and more papers.**\n\n"
        )

        for keyword in keywords:
            logger.info("Processing keyword: %s", keyword)
            f_rm.write(f"## {keyword}\n")
            f_is.write(f"## {keyword}\n")

            link = "AND" if len(keyword.split()) == 1 else "OR"
            papers = get_daily_papers_by_keyword_with_retries(keyword, column_names, max_result, link)
            if papers is None:
                logger.error("Failed to get papers for keyword '%s'!", keyword)
                sys.exit(1)

            f_rm.write(generate_table(papers))
            f_rm.write("\n\n")
            f_is.write(generate_table(papers[:issues_result], ignore_keys=["Abstract"]))
            f_is.write("\n\n")
            time.sleep(API_DELAY)

logger.info("Daily papers update completed successfully.")
