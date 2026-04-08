# app/models/schemas.py
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, AnyUrl, Field

class AnalyzeRequest(BaseModel):
    keyword: str = Field(..., min_length=1)
    url: AnyUrl

class PageData(BaseModel):
    url: AnyUrl
    title: Optional[str] = None
    meta_description: Optional[str] = None
    headings: Dict[str, List[str]] = Field(default_factory=dict)
    text: str = ""
    word_count: int = 0

class AnalyzeResponse(BaseModel):
    keyword: str
    score: Dict[str, int]
    analysis: Dict[str, object]
    comparison: Dict[str, Any]
    suggestions: Dict[str, List[str]]
    confidence_score: int = 0
    warning: Optional[str] = None
