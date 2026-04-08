# app/services/serp_service.py
from typing import List, Dict, Any, Optional
import json
import re
import os
from google import genai
from google.genai import types
from ..config import GEMINI_API_KEY, GEMINI_MODEL, SERP_API_KEY

_client: genai.Client | None = None

def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


class SerpProvider:
    def fetch(self, keyword: str) -> List[Dict[str, Any]]:
        raise NotImplementedError


class GeminiSearchSerpProvider(SerpProvider):
    """Uses Gemini with Google Search grounding to return real, current search results."""

    def fetch(self, keyword: str) -> List[Dict[str, Any]]:
        client = _get_client()
        try:
            google_search_tool = types.Tool(google_search=types.GoogleSearch())
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=f"Search Google for: {keyword}. List the top results.",
                config=types.GenerateContentConfig(
                    tools=[google_search_tool],
                    response_modalities=["TEXT"],
                ),
            )

            results: List[Dict[str, Any]] = []

            # Extract real URLs from grounding metadata
            for candidate in response.candidates or []:
                metadata = getattr(candidate, "grounding_metadata", None)
                if not metadata:
                    continue
                for chunk in getattr(metadata, "grounding_chunks", []):
                    web = getattr(chunk, "web", None)
                    if web and getattr(web, "uri", None):
                        results.append({
                            "title": getattr(web, "title", "") or "",
                            "url": web.uri,
                            "snippet": "",
                        })

            return results[:10] if results else []

        except Exception as e:
            print(f"GeminiSearchSerpProvider Error: {e}")
            return []


class SerpApiProvider(SerpProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or SERP_API_KEY

    def fetch(self, keyword: str) -> List[Dict[str, Any]]:
        if not self.api_key:
            print("SerpApi API Key not found, skipping...")
            return []
        try:
            import requests
            params = {
                "q": keyword,
                "api_key": self.api_key,
                "num": 10,
                "engine": "google",
            }
            response = requests.get("https://serpapi.com/search", params=params, timeout=10)
            response.raise_for_status()
            organic = response.json().get("organic_results", [])
            return [
                {"title": r.get("title", ""), "url": r.get("link", ""), "snippet": r.get("snippet", "")}
                for r in organic
                if r.get("link")
            ]
        except Exception as e:
            print(f"SerpApi Error: {e}")
            return []


def _get_serp_provider() -> SerpProvider:
    if SERP_API_KEY:
        return SerpApiProvider()
    return GeminiSearchSerpProvider()


def calculate_relevance_score(item: Dict[str, Any], keyword: str) -> float:
    """Score a SERP result purely on keyword token overlap — no niche-specific signals."""
    score = 0.0
    kw_norm = keyword.lower()
    title = item.get("title", "").lower()
    snippet = item.get("snippet", "").lower()
    content = title + " " + snippet

    # Exact full-keyword matches are the strongest signal
    if kw_norm in title:
        score += 5.0
    if kw_norm in snippet:
        score += 3.0

    # Partial token matches (handles multi-word keywords)
    for token in kw_norm.split():
        if len(token) > 2 and token in content:
            score += 0.5

    return score


def get_top_results(keyword: str) -> List[Dict[str, Any]]:
    provider = _get_serp_provider()
    results = provider.fetch(keyword)

    if not results:
        raise RuntimeError(
            "No SERP results could be retrieved for the given keyword. "
            "Check your GEMINI_API_KEY or add a SERP_API_KEY for more reliable results."
        )

    # Score and sort by keyword relevance
    for res in results:
        res["relevance_score"] = calculate_relevance_score(res, keyword)

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:10]
