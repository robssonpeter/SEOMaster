from typing import Optional, Dict, List
import requests
from bs4 import BeautifulSoup
from ..models.schemas import PageData
from ..utils.text_utils import clean_text, count_words

HEADERS = {"User-Agent": "SEO-Agent/0.1 (+https://example.com/bot)"}
TIMEOUT = 10


def _visible_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    return clean_text(text)


def extract_page_data(url: str) -> Optional[Dict]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if resp.status_code >= 400:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        title_tag = soup.find("title")
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        headings: Dict[str, List[str]] = {
            "h1": [h.get_text(strip=True) for h in soup.find_all("h1")],
            "h2": [h.get_text(strip=True) for h in soup.find_all("h2")],
            "h3": [h.get_text(strip=True) for h in soup.find_all("h3")],
        }
        text = _visible_text(soup)
        data: Dict = {
            "url": url,
            "title": title_tag.get_text(strip=True) if title_tag else None,
            "meta_description": meta_desc_tag.get("content") if meta_desc_tag else None,
            "headings": headings,
            "text": text,
            "word_count": count_words(text),
        }
        return data
    except requests.RequestException:
        return None
