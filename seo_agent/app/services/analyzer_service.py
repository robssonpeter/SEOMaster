from typing import List, Dict, Any
from collections import Counter
from ..utils.text_utils import extract_keywords


def analyze_competitors(competitor_pages: List[Dict[str, Any]], my_page: Dict[str, Any]) -> Dict[str, Any]:
    wc_list = [p.get("word_count", 0) for p in competitor_pages if p]
    avg_wc = int(sum(wc_list) / len(wc_list)) if wc_list else 0

    # common keywords across competitor pages (top 20 each, then frequency over pages)
    all_sets = []
    for p in competitor_pages:
        kws = extract_keywords(p.get("text", ""), top_n=20)
        all_sets.append(set(kws))
    keyword_counter = Counter()
    for s in all_sets:
        for kw in s:
            keyword_counter[kw] += 1
    common_keywords = [kw for kw, c in keyword_counter.most_common(25) if c >= max(2, len(competitor_pages)//3)]

    # common headings
    heading_counter = Counter()
    for p in competitor_pages:
        for level in ("h1", "h2", "h3"):
            for h in p.get("headings", {}).get(level, []):
                heading_counter[h.strip().lower()] += 1
    common_headings = [h for h, c in heading_counter.most_common(25) if c >= 2]

    analysis = {
        "average_word_count": avg_wc,
        "common_keywords": common_keywords,
        "common_headings": common_headings,
        "competitor_count": len(competitor_pages),
        "my_page_word_count": my_page.get("word_count", 0) if my_page else 0,
    }
    return analysis
