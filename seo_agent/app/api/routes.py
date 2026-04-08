# app/api/routes.py
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from ..config import API_KEY
from ..models.schemas import AnalyzeRequest, AnalyzeResponse
from ..services.serp_service import get_top_results
from ..services.crawler_service import extract_page_data, extract_pages_concurrent
from ..services.analyzer_service import analyze_competitors
from ..services.ai_service import generate_seo_suggestions

router = APIRouter()

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def _require_api_key(key: str = Security(_api_key_header)) -> None:
    if not API_KEY:
        return  # Auth disabled when API_KEY is not configured
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@router.post("/analyze", response_model=AnalyzeResponse, dependencies=[Security(_require_api_key)])
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        serp_results = get_top_results(request.keyword)
        competitor_urls = [r["url"] for r in serp_results]

        # Fetch competitor pages and user page concurrently
        all_urls = competitor_urls + [str(request.url)]
        all_pages = extract_pages_concurrent(all_urls)

        # Split user page from competitor pages
        user_url = str(request.url)
        competitor_pages = [p for p in all_pages if p["url"] != user_url]
        my_page_matches = [p for p in all_pages if p["url"] == user_url]
        my_page_data = my_page_matches[0] if my_page_matches else None

        analysis = analyze_competitors(competitor_pages, my_page_data, request.keyword)
        analysis["keyword"] = request.keyword

        confidence_score = analysis.get("confidence_score", 0)
        warning = None
        if confidence_score < 50:
            warning = "Low confidence analysis due to insufficient or inconsistent data"

        suggestions = generate_seo_suggestions(analysis, my_page_data)

        # Comparison block
        my_wc = analysis.get("my_page_word_count", 0)
        avg_wc = analysis.get("average_word_count", 0)
        keyword_comparison = analysis.get("keyword_comparison", {})
        keyword_overlap = keyword_comparison.get("overlap_pct", 0)

        comparison = {
            "your_word_count": my_wc,
            "avg_word_count": avg_wc,
            "word_count_gap": my_wc - avg_wc,
            "keyword_overlap": keyword_overlap,
            "page_type_recommendation": analysis.get("page_type_recommendation"),
        }

        # Scoring (100 pts total, 4 distinct signals, 25 pts each)
        # 1. Content length vs competitor average
        score_content = min(25, int(my_wc / avg_wc * 25)) if avg_wc > 0 else 25

        # 2. Keyword coverage (missing vs present)
        score_keywords = min(25, int(keyword_overlap / 100 * 25))

        # 3. Heading structure depth
        my_h_count = sum(
            len((my_page_data or {}).get("headings", {}).get(lvl, []))
            for lvl in ("h1", "h2", "h3")
        )
        score_structure = min(25, my_h_count * 5)  # 5 headings = full score

        # 4. Search intent alignment: measure how many top competitor keywords appear
        #    in my page vs total (independent from raw keyword_overlap)
        top_kws = [k["keyword"] for k in analysis.get("top_keywords", [])]
        my_text = (my_page_data or {}).get("text", "").lower()
        intent_hits = sum(1 for kw in top_kws if kw in my_text)
        score_intent = min(25, int(intent_hits / len(top_kws) * 25)) if top_kws else 0

        score = {
            "overall": score_content + score_keywords + score_structure + score_intent,
            "content_length": score_content,
            "keyword_usage": score_keywords,
            "structure": score_structure,
            "intent_match": score_intent,
        }

        return AnalyzeResponse(
            keyword=request.keyword,
            score=score,
            analysis=analysis,
            comparison=comparison,
            suggestions=suggestions,
            confidence_score=confidence_score,
            warning=warning,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
