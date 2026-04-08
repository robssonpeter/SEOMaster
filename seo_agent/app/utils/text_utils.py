# app/utils/text_utils.py
from typing import List, Dict, Any
import re
from collections import Counter

STOPWORDS = set(
    "a an the and or but if while of in on for to from with by at as is are was were be been being this that those these it its i you we they them he she his her their our your not can could would should will may might etc about into over under out up down more most less least very also just than then so such many much other another each every any some no nor do does did having have has had".split()
)
SWAHILI_STOPWORDS = {
    "na", "ya", "wa", "kwa", "ni", "za", "la", "katika", "ni", "si", "yaani", "kama", "hata", "lakini", "pia", "basi", "ila", "au", "ambao", "ambazo", "ambacho", "ambavyo", "ndio", "hapana", "ndiyo", "pia", "baada", "hapo", "huko", "hivyo", "hivyo", "vile", "vilevile", "namna", "tangu", "hadi", "mpaka", "mimi", "sisi", "wewe", "nyinyi", "yeye", "wao", "huyu", "hawa", "yule", "wale", "hiki", "hivi", "kile", "vile", "hilo", "haya", "lile", "yale", "huu", "hii", "ile", "ule", "huo", "hiyo", "leo", "jana", "kesho", "sana", "kabisa", "tu", "zaidi", "kidogo", "tena", "pamoja", "badala", "kwamba", "ikiwa", "ingawa", "ijapokuwa", "ili", "iliyo", "ambaye", "ambao", "ambayo", "ambazo", "ambavyo"
}

UNRELATED_KEYWORDS = {
    "domain", "login", "signup", "copyright", "rights", "reserved", "privacy", "policy", "terms", "cookies", "contact", "about", "navigation", "menu", "search", "footer", "sidebar", "payment", "price", "checkout", "cart", "buy", "purchase", "shilling", "shillings", "usd", "money", "email", "phone", "address", "website", "www", "http", "https", "click", "here", "read", "more", "view", "details"
}

JOB_RELATED_CONTEXT = {
    "job", "kazi", "ajira", "vacancy", "vacancies", "career", "careers", "position", "positions", "hiring", "apply", "application", "cv", "resume", "interview", "recruitment", "employer", "employee", "salary", "qualification", "degree", "experience", "skill", "skills", "jobseekers", "opportunities", "staff", "intern", "internship", "volunteer", "ngo", "mshahara", "nafasi"
}

LOCATION_TERMS = {
    "tanzania", "dar es salaam", "dodoma", "mwanza", "arusha", "mbeya", "morogoro", "tanga", "kahama", "zanzibar", "africa"
}

ALL_STOPWORDS = STOPWORDS.union(SWAHILI_STOPWORDS).union(UNRELATED_KEYWORDS)

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    # Keep Unicode letters/digits, hyphens, and whitespace — preserves non-English content
    text = re.sub(r"[^\w\s\-]", "", text, flags=re.UNICODE)
    # \w includes underscores; strip any that slipped through as standalone tokens
    text = re.sub(r"\b_+\b", " ", text)
    return text.strip().lower()

def normalize_plural(word: str) -> str:
    """Basic plural normalization (e.g., 'jobs' -> 'job', 'vacancies' -> 'vacancy')"""
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("s") and len(word) > 3:
        # Simple heuristic, avoid cutting if it doesn't look like a standard plural
        if not word.endswith(("ss", "us", "is", "as")):
            return word[:-1]
    return word

def extract_top_keywords(text: str, limit: int = 20) -> List[Dict[str, Any]]:
    cleaned = clean_text(text)
    # Filter words: lowercase, remove punctuation (done in clean_text), 
    # remove stopwords, remove words shorter than 3 chars
    tokens = [normalize_plural(t) for t in cleaned.split() if t not in ALL_STOPWORDS and len(t) > 2]
    counts = Counter(tokens)
    return [{"keyword": kw, "frequency": count} for kw, count in counts.most_common(limit)]

def extract_keywords(text: str, top_n: int = 20) -> List[str]:
    """Maintain backward compatibility."""
    top_kws = extract_top_keywords(text, limit=top_n)
    return [item["keyword"] for item in top_kws]


def count_words(text: str) -> int:
    cleaned = clean_text(text)
    return len(cleaned.split())
