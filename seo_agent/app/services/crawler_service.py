# app/services/crawler_service.py
from typing import Optional, Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
from ..utils.text_utils import clean_text, count_words

HEADERS = {"User-Agent": "SEO-Agent/0.1 (+https://example.com/bot)"}
TIMEOUT = 10
MAX_WORKERS = 8


def _visible_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return clean_text(soup.get_text(separator=" "))


def extract_page_data(url: str) -> Optional[Dict]:
    url_str = str(url)
    try:
        resp = requests.get(url_str, headers=HEADERS, timeout=TIMEOUT)
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
        return {
            "url": url_str,
            "title": title_tag.get_text(strip=True) if title_tag else None,
            "meta_description": meta_desc_tag.get("content") if meta_desc_tag else None,
            "headings": headings,
            "text": text,
            "word_count": count_words(text),
        }
    except requests.RequestException:
        return None


def extract_pages_concurrent(urls: List[str]) -> List[Dict]:
    """Fetch multiple pages concurrently, preserving order, skipping failures."""
    results: Dict[str, Optional[Dict]] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(extract_page_data, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception:
                results[url] = None
    # Return in original order, filtering out None
    return [results[url] for url in urls if results.get(url) is not None]
