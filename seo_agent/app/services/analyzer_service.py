# app/services/analyzer_service.py
from typing import List, Dict, Any
from collections import Counter
import re
from ..utils.text_utils import extract_keywords, extract_top_keywords


def calculate_confidence_score(
    competitor_pages: List[Dict], keyword: str, common_kws: List[str]
) -> int:
    """Calculate a confidence score (0-100) based on data quality."""
    score = 0
    count = len(competitor_pages)
    if count == 0:
        return 0

    # Competitor count (up to 40 points)
    score += min(40, count * 8)  # 5+ competitors = 40 points

    # Keyword relevance: at least one top keyword contains a token from the search keyword (30 pts)
    kw_tokens = set(keyword.lower().split())
    if any(token in " ".join(common_kws[:10]).lower() for token in kw_tokens):
        score += 30

    # Content depth (up to 30 points)
    avg_wc = sum(p.get("word_count", 0) for p in competitor_pages) / count
    if avg_wc > 300:
        score += 30
    elif avg_wc > 100:
        score += 15

    return score


def is_page_relevant(page: Dict[str, Any], keyword: str) -> bool:
    """Validate if a page has meaningful content related to the keyword."""
    text = page.get("text", "").lower()
    word_count = page.get("word_count", 0)

    if word_count < 100:
        return False

    # Check that at least one keyword token appears in the text
    kw_tokens = [t for t in keyword.lower().split() if len(t) > 2]
    if not kw_tokens:
        return True  # Can't filter without tokens

    return any(token in text for token in kw_tokens)


def detect_search_intent(pages: List[Dict]) -> str:
    transactional_signals = [
        "buy", "price", "order", "shop", "store", "deal", "discount",
        "job", "jobs", "vacancy", "apply", "hire", "hiring", "book", "reserve",
    ]
    informational_signals = [
        "how", "guide", "tips", "learn", "what", "why", "tutorial",
        "advice", "explain", "definition", "history", "overview",
    ]

    transactional_count = 0
    informational_count = 0

    for p in pages:
        text = p.get("text", "").lower()
        for word in transactional_signals:
            transactional_count += text.count(word)
        for word in informational_signals:
            informational_count += text.count(word)

    if transactional_count > informational_count * 1.5:
        return "transactional"
    elif informational_count > transactional_count * 1.5:
        return "informational"
    else:
        return "hybrid"


def extract_heading_patterns(headings: List[str]) -> Dict[str, Any]:
    """Extract patterns from headings without niche-specific hardcoding."""
    h2_patterns: Counter = Counter()

    for h in headings:
        h_norm = re.sub(r"\d+", "", h.lower()).strip()
        words = h_norm.split()
        if len(words) >= 2:
            pattern = " ".join(words[:3])
            h2_patterns[pattern] += 1

    return {
        "common_h2_patterns": [p for p, c in h2_patterns.most_common(10) if c >= 2]
    }


def analyze_competitors(
    competitor_pages: List[Dict[str, Any]], my_page: Dict[str, Any], keyword: str
) -> Dict[str, Any]:
    # Filter pages that have meaningful content related to the keyword
    filtered = [p for p in competitor_pages if is_page_relevant(p, keyword)]
    active_competitors = filtered if len(filtered) >= 3 else competitor_pages

    wc_list = [p.get("word_count", 0) for p in active_competitors if p]
    avg_wc = int(sum(wc_list) / len(wc_list)) if wc_list else 0

    # Keyword importance scoring: frequency × number of pages it appears in
    keyword_page_map: Dict[str, set] = {}
    all_competitor_text = []

    for i, p in enumerate(active_competitors):
        text = p.get("text", "")
        all_competitor_text.append(text)
        for kw in extract_keywords(text, top_n=50):
            keyword_page_map.setdefault(kw, set()).add(i)

    full_text = " ".join(all_competitor_text)
    raw_top_keywords = extract_top_keywords(full_text, limit=100)

    scored_keywords = []
    for item in raw_top_keywords:
        kw = item["keyword"]
        freq = item["frequency"]
        pages_present = len(keyword_page_map.get(kw, []))

        # Require keywords present in at least 2 pages when we have enough competitors
        if len(active_competitors) >= 3 and pages_present < 2:
            continue

        scored_keywords.append({
            "keyword": kw,
            "frequency": freq,
            "pages_present": pages_present,
            "importance_score": freq * pages_present,
        })

    scored_keywords.sort(key=lambda x: x["importance_score"], reverse=True)
    scored_keywords = scored_keywords[:20]
    common_keywords = [kw["keyword"] for kw in scored_keywords]

    confidence_score = calculate_confidence_score(active_competitors, keyword, common_keywords)

    # Heading patterns
    heading_list: List[str] = []
    competitor_h2s: set = set()
    for p in active_competitors:
        for level in ("h1", "h2", "h3"):
            for h in p.get("headings", {}).get(level, []):
                heading_list.append(h)
                if level == "h2":
                    competitor_h2s.add(h.strip().lower())

    heading_data = extract_heading_patterns(heading_list)

    # Headings missing from my page
    my_headings: List[str] = []
    if my_page:
        for level in ("h1", "h2", "h3"):
            my_headings.extend(h.strip().lower() for h in my_page.get("headings", {}).get(level, []))

    heading_counter = Counter(h.strip().lower() for h in heading_list)
    missing_headings = [
        h for h in competitor_h2s
        if h not in my_headings and heading_counter[h] >= 2
    ][:10]

    search_intent = detect_search_intent(active_competitors)
    page_type_map = {
        "transactional": "Product / Service Page",
        "informational": "Blog Post / Guide",
        "hybrid": "Resource Hub / Listing with Content",
    }
    page_type_recommendation = page_type_map.get(search_intent, "Article")

    # Keyword comparison: my page vs competitor keywords
    my_text = (my_page.get("text") or "").lower() if my_page else ""
    missing_keywords: List[str] = []
    underused_keywords: List[str] = []
    overlap_count = 0

    for item in scored_keywords:
        kw = item["keyword"]
        if kw in my_text:
            overlap_count += 1
            my_freq = my_text.count(kw)
            avg_comp_freq = item["frequency"] / len(active_competitors) if active_competitors else 0
            if my_freq < avg_comp_freq * 0.5:
                underused_keywords.append(kw)
        else:
            missing_keywords.append(kw)

    keyword_overlap_pct = (
        int(overlap_count / len(scored_keywords) * 100) if scored_keywords else 0
    )

    return {
        "confidence_score": confidence_score,
        "average_word_count": avg_wc,
        "common_keywords": common_keywords,
        "top_keywords": scored_keywords,
        "heading_patterns": heading_data["common_h2_patterns"],
        "common_h2_patterns": heading_data["common_h2_patterns"],
        "missing_headings": missing_headings,
        "search_intent": search_intent,
        "page_type_recommendation": page_type_recommendation,
        "competitor_count": len(active_competitors),
        "my_page_word_count": my_page.get("word_count", 0) if my_page else 0,
        "keyword_comparison": {
            "missing": missing_keywords,
            "underused": underused_keywords,
            "overlap_pct": keyword_overlap_pct,
        },
    }
