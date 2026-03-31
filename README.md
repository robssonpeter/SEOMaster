# SEO Analysis Agent (MVP)

A clean, modular FastAPI service that analyzes the top 10 (mocked) search results for a keyword, crawls those pages, compares them with your target URL, and produces structured SEO insights and AI-style suggestions (simulated; no external API calls).

Current date/time: 2026-03-31 11:35

## Features
- SERP fetching (mock, deterministic per keyword; easy to swap with real provider)
- Web crawler using Requests + BeautifulSoup
- Analyzer: average word counts, common keywords, common headings
- AI suggestions (simulated, structured; ready for future OpenAI integration)
- Single API endpoint: POST /analyze
- Clean architecture and type hints throughout

## Tech Stack
- Python 3.11+
- FastAPI
- Requests
- BeautifulSoup4
- Uvicorn (ASGI server)

## Project Structure
```
seo_agent/
  app/
    main.py                 # FastAPI entry point
    api/
      routes.py             # API endpoints
    services/
      serp_service.py       # Fetch top 10 search results (mock)
      crawler_service.py    # Crawl and extract page data
      analyzer_service.py   # Analyze competitor data
      ai_service.py         # AI prompt + response handling (simulated)
    models/
      schemas.py            # Pydantic models
    utils/
      text_utils.py         # keyword extraction, cleaning
  tests/
requirements.txt
README.md
```

## Getting Started
1. Create and activate a virtual environment (Python 3.11+):
   - macOS/Linux:
     ```bash
     python3.11 -m venv .venv
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     py -3.11 -m venv .venv
     .venv\Scripts\Activate.ps1
     ```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the API (development):
```bash
uvicorn seo_agent.app.main:app --reload
```

4. Test the endpoint:
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"keyword": "nafasi za kazi", "url": "https://example.com"}'
```

## API
- POST /analyze
  - Request body:
    ```json
    {
      "keyword": "nafasi za kazi",
      "url": "https://example.com"
    }
    ```
  - Response body:
    ```json
    {
      "keyword": "...",
      "score": 0,
      "analysis": {
        "average_word_count": 0,
        "common_keywords": [],
        "common_headings": [],
        "competitor_count": 10,
        "my_page_word_count": 0
      },
      "suggestions": {
        "missing_keywords": [],
        "content_gaps": [],
        "title_suggestions": [],
        "quick_wins": []
      }
    }
    ```

## System Overview
- api/routes.py: Defines /analyze endpoint. Delegates all logic to services.
- services/serp_service.py: get_top_results(keyword) returns 10 deterministic mock results with fields: title, url, snippet.
- services/crawler_service.py: extract_page_data(url) pulls title, meta description, h1/h2/h3, visible text, and word count. Handles RequestException and 4xx/5xx by returning None.
- services/analyzer_service.py: analyze_competitors(competitor_pages, my_page) computes:
  - average_word_count across competitors
  - common_keywords via simple stopword-filtered frequency
  - common_headings occurring on at least 2 competitor pages
- services/ai_service.py: generate_seo_suggestions(analysis, my_page) simulates:
  - missing_keywords: common keywords not present on my_page text
  - content_gaps: quick heuristics (word count below average, missing meta description)
  - title_suggestions: recommends adding an SEO title if missing
  - quick_wins: heading tips
- utils/text_utils.py: basic text cleaning and keyword extraction using a small stopword list.
- models/schemas.py: Pydantic models for request/response structures.

## Notes & Extensibility
- SERP: swap mock provider by replacing get_top_results with a real API integration later.
- Crawler: Playwright can be integrated for JS-heavy sites behind a feature flag in the future.
- AI: generate_seo_suggestions is designed to be replaced by an OpenAI or similar LLM call that returns the same structured JSON shape.

## Testing
- Basic placeholder under seo_agent/tests. You can add unit tests for crawler and analyzer later.

## License
MIT
