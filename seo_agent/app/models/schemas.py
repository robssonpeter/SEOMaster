from typing import List, Dict, Optional
from pydantic import BaseModel, HttpUrl, Field

class AnalyzeRequest(BaseModel):
    keyword: str = Field(..., min_length=1)
    url: HttpUrl

class PageData(BaseModel):
    url: HttpUrl
    title: Optional[str] = None
    meta_description: Optional[str] = None
    headings: Dict[str, List[str]] = Field(default_factory=dict)
    text: str = ""
    word_count: int = 0

class AnalyzeResponse(BaseModel):
    keyword: str
    score: int
    analysis: Dict[str, object]
    suggestions: Dict[str, List[str]]
