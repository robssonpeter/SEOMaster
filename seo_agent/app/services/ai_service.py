from typing import Dict, Any, List


def generate_seo_suggestions(analysis: Dict[str, Any], my_page: Dict[str, Any]) -> Dict[str, List[str]]:
    # Simulated AI suggestions based on analysis heuristics
    my_text = (my_page or {}).get("text", "")
    my_wc = (my_page or {}).get("word_count", 0)
    missing_keywords: List[str] = []
    for kw in analysis.get("common_keywords", []):
        if kw not in my_text:
            missing_keywords.append(kw)

    content_gaps: List[str] = []
    if my_wc < analysis.get("average_word_count", 0):
        content_gaps.append("Increase total word count to meet or exceed competitor average.")
    if not (my_page or {}).get("meta_description"):
        content_gaps.append("Add a compelling meta description (140-160 chars) including the primary keyword.")

    title_suggestions: List[str] = []
    if not (my_page or {}).get("title"):
        title_suggestions.append("Add an SEO-friendly title with the target keyword near the beginning.")

    quick_wins: List[str] = []
    if (my_page or {}).get("headings", {}).get("h1"):
        quick_wins.append("Ensure the H1 includes the target keyword and is unique.")
    else:
        quick_wins.append("Add a clear H1 that includes the primary keyword.")

    return {
        "missing_keywords": missing_keywords[:15],
        "content_gaps": content_gaps,
        "title_suggestions": title_suggestions,
        "quick_wins": quick_wins,
    }
