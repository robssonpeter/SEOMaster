from typing import List, Dict
import re
from collections import Counter

STOPWORDS = set(
    "a an the and or but if while of in on for to from with by at as is are was were be been being this that those these it its i you we they them he she his her their our your not can could would should will may might etc about into over under out up down more most less least very also just than then so such many much other another each every any some no nor do does did having have has had".split()
)

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^A-Za-z0-9\-\s]", "", text)
    return text.strip().lower()


def extract_keywords(text: str, top_n: int = 20) -> List[str]:
    cleaned = clean_text(text)
    tokens = [t for t in cleaned.split() if t not in STOPWORDS and len(t) > 2]
    counts = Counter(tokens)
    return [w for w, _ in counts.most_common(top_n)]


def count_words(text: str) -> int:
    cleaned = clean_text(text)
    return len(cleaned.split())
