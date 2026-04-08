# app/services/ai_service.py
from typing import Dict, Any, List
import json
from google import genai
from ..config import GEMINI_API_KEY, GEMINI_MODEL

_client: genai.Client | None = None

def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def _call_gemini(prompt: str) -> str:
    client = _get_client()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return response.text or ""


def generate_seo_suggestions(analysis: Dict[str, Any], my_page: Dict[str, Any]) -> Dict[str, List[str]]:
    keyword = analysis.get("keyword", "the target keyword")

    keyword_comparison = analysis.get("keyword_comparison", {})
    missing_kws = keyword_comparison.get("missing", [])
    underused_kws = keyword_comparison.get("underused", [])

    missing_headings = analysis.get("missing_headings", [])
    common_h2s = analysis.get("common_h2_patterns", [])

    prompt = f"""
    As an SEO expert, convert the following structured insights into actionable recommendations.

    Target Keyword: {keyword}
    Detected Search Intent: {analysis.get("search_intent")}
    Recommended Page Type: {analysis.get("page_type_recommendation")}

    INSIGHTS:
    1. Keyword Gaps:
       - Missing important keywords: {", ".join(missing_kws[:15])}
       - Underused keywords: {", ".join(underused_kws[:15])}
       - Keyword overlap with competitors: {keyword_comparison.get("overlap_pct")}%

    2. Content & Structure Gaps:
       - Competitor word count average: {analysis.get("average_word_count")} (My page: {analysis.get("my_page_word_count")})
       - Common H2 patterns in top pages: {", ".join(common_h2s)}
       - Competitor headings missing from my page: {", ".join(missing_headings)}

    3. Heading Categories detected: {", ".join(analysis.get("heading_patterns", []))}

    TASK:
    Generate a JSON response with specific, data-driven suggestions to improve the SEO of 'My Page'.
    Focus on converting these insights into instructions.

    JSON Keys:
    - missing_keywords: List of keywords to add or use more frequently.
    - content_gaps: Suggestions for new sections or content depth based on missing headings and patterns.
    - title_suggestions: 3 optimized title ideas incorporating the target keyword and intent.
    - quick_wins: 3-5 high-impact, easy changes.
    - recommended_structure: An ideal H1/H2/H3 structure for this page.

    Return ONLY the JSON object, no markdown fences.
    """

    try:
        output = _call_gemini(prompt).strip()
        # Strip any accidental markdown fences
        if output.startswith("```"):
            output = output.split("\n", 1)[1] if "\n" in output else output[3:]
        if output.endswith("```"):
            output = output[:-3]

        suggestions = json.loads(output.strip())

        def ensure_list(data: Any) -> List[str]:
            if isinstance(data, list):
                return [str(item) for item in data]
            elif isinstance(data, dict):
                return [f"{k}: {v}" for k, v in data.items()]
            elif data:
                return [str(data)]
            return []

        return {
            "missing_keywords": ensure_list(suggestions.get("missing_keywords")),
            "content_gaps": ensure_list(suggestions.get("content_gaps")),
            "title_suggestions": ensure_list(suggestions.get("title_suggestions")),
            "quick_wins": ensure_list(suggestions.get("quick_wins")),
            "recommended_structure": ensure_list(suggestions.get("recommended_structure")),
        }

    except Exception as e:
        print(f"AI Service Error: {e}")
        return _fallback_suggestions(analysis, my_page, keyword)


def _fallback_suggestions(
    analysis: Dict[str, Any], my_page: Dict[str, Any], keyword: str
) -> Dict[str, List[str]]:
    keyword_comparison = analysis.get("keyword_comparison", {})
    missing_keywords = keyword_comparison.get("missing", [])
    underused_keywords = keyword_comparison.get("underused", [])

    my_wc = (my_page or {}).get("word_count", 0)
    avg_wc = analysis.get("average_word_count", 0)

    content_gaps: List[str] = []
    if my_wc < avg_wc:
        gap = avg_wc - my_wc
        content_gaps.append(f"Increase content length by ~{gap} words to match competitor average.")

    missing_headings = analysis.get("missing_headings", [])
    if missing_headings:
        content_gaps.append(f"Consider adding sections for: {', '.join(missing_headings[:3])}")

    if not (my_page or {}).get("meta_description"):
        content_gaps.append("Add a compelling meta description (140-160 chars) including the primary keyword.")

    title_suggestions: List[str] = []
    if not (my_page or {}).get("title"):
        title_suggestions.append(f"Add an SEO-friendly title starting with '{keyword.title()}'")

    quick_wins: List[str] = []
    if not (my_page or {}).get("headings", {}).get("h1"):
        quick_wins.append(f"Add an H1 heading containing '{keyword.title()}'.")
    if underused_keywords:
        quick_wins.append(f"Increase usage of key terms: {', '.join(underused_keywords[:3])}")

    recommended_structure = [f"H1: {keyword.title()}"]
    for h2 in analysis.get("common_h2_patterns", []):
        recommended_structure.append(f"H2: {h2.title()}")

    return {
        "missing_keywords": missing_keywords[:15],
        "content_gaps": content_gaps,
        "title_suggestions": title_suggestions,
        "quick_wins": quick_wins,
        "recommended_structure": recommended_structure,
    }
