from typing import List, Dict
import hashlib

# Mock SERP provider. Deterministic per keyword and limited to 10 results.
def get_top_results(keyword: str) -> List[Dict[str, str]]:
    seed = int(hashlib.sha256(keyword.encode("utf-8")).hexdigest(), 16)
    domains = [
        "example.com", "example.org", "example.net", "sample.com",
        "demo.org", "testsite.com", "mysite.io", "coolblog.dev",
        "newsportal.com", "docs.io", "help.site", "guidebook.dev",
    ]
    results: List[Dict[str, str]] = []
    for i in range(10):
        d = domains[(seed + i) % len(domains)]
        url = f"https://{d}/post-{(seed >> (i % 8)) % 1000}"
        results.append({
            "title": f"{keyword.title()} - Resource {(i+1)}",
            "url": url,
            "snippet": f"Learn about {keyword} with tips and best practices #{i+1}.",
        })
    return results
