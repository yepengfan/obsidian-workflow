"""Tests for title deduplication."""

from datetime import datetime, timezone

from digest.sources.rss import Article
from digest.dedup import deduplicate, _tokenize, _jaccard


def _article(title: str, source: str = "test") -> Article:
    return Article(
        title=title,
        link=f"https://example.com/{title.replace(' ', '-')}",
        pub_date=datetime.now(timezone.utc),
        description="test description",
        source_name=source,
    )


class TestTokenize:
    def test_basic(self):
        assert _tokenize("Hello World") == {"hello", "world"}

    def test_strips_hn_prefix(self):
        assert "show" not in _tokenize("Show HN: My Cool Project")
        assert "cool" in _tokenize("Show HN: My Cool Project")

    def test_strips_punctuation(self):
        tokens = _tokenize("Rust's new async/await features!")
        assert "rust" in tokens
        assert "async" in tokens


class TestJaccard:
    def test_identical(self):
        s = {"a", "b", "c"}
        assert _jaccard(s, s) == 1.0

    def test_disjoint(self):
        assert _jaccard({"a", "b"}, {"c", "d"}) == 0.0

    def test_partial(self):
        assert _jaccard({"a", "b", "c"}, {"b", "c", "d"}) == 0.5

    def test_empty(self):
        assert _jaccard(set(), {"a"}) == 0.0


class TestDeduplicate:
    def test_no_duplicates(self):
        articles = [
            _article("Rust async features"),
            _article("Python type hints guide"),
            _article("Go generics tutorial"),
        ]
        result = deduplicate(articles)
        assert len(result) == 3

    def test_removes_near_duplicate(self):
        articles = [
            _article("GPT-5 Released with Major Improvements"),
            _article("GPT-5 Released with Major New Features"),
        ]
        result = deduplicate(articles, threshold=0.5)
        assert len(result) == 1

    def test_keeps_different_articles(self):
        articles = [
            _article("Rust memory safety"),
            _article("Python web frameworks comparison"),
        ]
        result = deduplicate(articles, threshold=0.6)
        assert len(result) == 2

    def test_empty_list(self):
        assert deduplicate([]) == []
