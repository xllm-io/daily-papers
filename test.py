import keyword
import json
import urllib, urllib.request

from typing import List, Dict
# from DailyArXiv.config import max_result
import feedparser
from easydict import EasyDict

def request_paper_with_arXiv_api(keyword: str, max_results: int, link: str = "OR") -> List[Dict[str, str]]:
    # keyword = keyword.replace(" ", "+")
    assert link in ["OR", "AND"], "link should be 'OR' or 'AND'"
    keyword = "\"" + keyword + "\""
    url = "http://export.arxiv.org/api/query?search_query=ti:{0}+{2}+abs:{0}&max_results={1}&sortBy=lastUpdatedDate".format(keyword, max_results, link)
    url = urllib.parse.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
    print("[###] keyword: {0}, url: {1}".format(keyword, url))
    response = urllib.request.urlopen(url).read().decode('utf-8')
    feed = feedparser.parse(response)
    # print(json.dumps(feed))
    with open("res.json", "w") as fd:
        fd.write(json.dumps(feed))


if __name__ == "__main__":
    keyword = "Sparse Attention"
    max_results = 30
    request_paper_with_arXiv_api(keyword=keyword, max_results=max_results)