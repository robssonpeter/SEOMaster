from fastapi import APIRouter, HTTPException
from ..models.schemas import AnalyzeRequest, AnalyzeResponse
from ..services.serp_service import get_top_results
from ..services.crawler_service import extract_page_data
from ..services.analyzer_service import analyze_competitors
from ..services.ai_service import generate_seo_suggestions

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        serp_results = get_top_results(request.keyword)
        competitor_urls = [r["url"] for r in serp_results]
        competitor_pages = []
        for url in competitor_urls:
            data = extract_page_data(url)
            if data:
                competitor_pages.append(data)
        my_page_data = extract_page_data(request.url)
        analysis = analyze_competitors(competitor_pages, my_page_data)
        suggestions = generate_seo_suggestions(analysis, my_page_data)
        score = int(min(100, max(0, 50 + (len(analysis.get("common_keywords", [])) - 5) * 5)))
        return AnalyzeResponse(
            keyword=request.keyword,
            score=score,
            analysis=analysis,
            suggestions=suggestions,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
