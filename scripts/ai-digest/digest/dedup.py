"""Title-based deduplication using Jaccard similarity."""

import re
from digest.sources.rss import Article

_WORD_RE = re.compile(r"[a-z0-9]+")
_STRIP_PREFIXES = ["show hn:", "ask hn:", "tell hn:", "launch hn:"]


def _tokenize(title: str) -> set[str]:
    """Lowercase, strip prefixes, extract word tokens."""
    t = title.lower().strip()
    for prefix in _STRIP_PREFIXES:
        if t.startswith(prefix):
            t = t[len(prefix):].strip()
    return set(_WORD_RE.findall(t))


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def deduplicate(articles: list[Article], threshold: float = 0.6) -> list[Article]:
    """Remove near-duplicate articles based on title Jaccard similarity.

    Greedy: iterate articles (already sorted by pub_date desc), skip any
    that are too similar to an already-kept article.
    """
    kept: list[tuple[set[str], Article]] = []

    for article in articles:
        tokens = _tokenize(article.title)
        is_dup = False
        for kept_tokens, _ in kept:
            if _jaccard(tokens, kept_tokens) > threshold:
                is_dup = True
                break
        if not is_dup:
            kept.append((tokens, article))

    return [article for _, article in kept]
