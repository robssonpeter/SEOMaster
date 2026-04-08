# SEO Analysis Agent (MVP)

A clean, modular FastAPI service that analyzes the top 10 (mocked) search results for a keyword, crawls pages, compares them with your target URL, and produces structured SEO insights and AI-style suggestions.

## Features
- SERP fetching using Gemini AI to discover real, ranking URLs
- Web crawler using Requests + BeautifulSoup for real content extraction
- Analyzer: word counts, common keywords, common headings
- AI suggestions using Gemini AI for high-quality, data-driven insights
- Single API endpoint: POST /analyze
- Clean architecture and type hints

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
    main.py
    api/
      routes.py
    services/
      serp_service.py
      crawler_service.py
      analyzer_service.py
      ai_service.py
    models/
      schemas.py
    utils/
      text_utils.py
  tests/
  requirements.txt
  README.md
```

## Getting Started
1. Create and activate a virtualenv (Python 3.11+):
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

3. Run the API:
```bash
uvicorn seo_agent.app.main:app --reload
```

4. Test the endpoint:
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"keyword": "nafasi za kazi", "url": "https://www.ajiriwa.net/browse-jobs"}'
```

## Response Shape
```
{
  "keyword": "...",
  "score": 0-100,
  "analysis": { ... },
  "suggestions": { ... }
}
```

## Notes
- SERP results are fetched by asking Gemini AI for currently ranking URLs for a given keyword.
- Web crawler visits real URLs to extract text and structure.
- AI suggestions are powered by a Gemini AI integration in `/var/www/node_projects/google-gemini/index.js`.

## Tests
- Placeholder for future tests under `tests/`.

## License
MIT
