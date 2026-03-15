"""Tests for Obsidian report generation."""

import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

from digest.summarizer import SummarizedArticle
from digest.report import (
    generate_reports,
    update_dashboard,
    archive_old_reports,
    format_zh_report,
    format_en_report,
)


def _article(title: str = "Test Article", category: str = "ai-ml") -> SummarizedArticle:
    return SummarizedArticle(
        title=title,
        link="https://example.com/test",
        pub_date=datetime.now(timezone.utc),
        description="test",
        source_name="test.com",
        source_type="rss",
        relevance=8, quality=7, timeliness=9,
        category=category, keywords=["test", "ai"],
        total_score=27,
        title_zh="测试文章",
        summary_zh="中文摘要",
        reason_zh="中文理由",
        summary_en="English summary",
        reason_en="English reason",
    )


STATS = {
    "sources_total": 92,
    "feeds_ok": 80,
    "articles_fetched": 100,
    "articles_after_dedup": 90,
    "articles_selected": 15,
    "bedrock_cost": 0.05,
    "bedrock_calls": 10,
}


class TestFormatReport:
    def test_zh_has_frontmatter(self):
        content = format_zh_report([_article()], "趋势总结", STATS, date(2026, 3, 15))
        assert "---" in content
        assert "lang: zh" in content
        assert "date: 2026-03-15" in content

    def test_zh_has_wikilink(self):
        content = format_zh_report([_article()], "趋势", STATS, date(2026, 3, 15))
        assert "[[2026-03-15-en]]" in content

    def test_en_has_wikilink(self):
        content = format_en_report([_article()], "trends", STATS, date(2026, 3, 15))
        assert "[[2026-03-15]]" in content

    def test_zh_has_article_content(self):
        content = format_zh_report([_article()], "趋势", STATS, date(2026, 3, 15))
        assert "测试文章" in content
        assert "中文摘要" in content

    def test_en_has_article_content(self):
        content = format_en_report([_article()], "trends", STATS, date(2026, 3, 15))
        assert "English summary" in content
        assert "English reason" in content


class TestGenerateReports:
    def test_creates_both_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            zh, en = generate_reports(
                [_article()], "趋势", "trends", STATS,
                vault_path=tmpdir, today=date(2026, 3, 15),
            )
            assert zh.exists()
            assert en.exists()
            assert zh.name == "2026-03-15.md"
            assert en.name == "2026-03-15-en.md"


class TestDashboard:
    def test_creates_dashboard(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a fake daily report
            feed_dir = Path(tmpdir) / "Feeds" / "AI-Daily"
            feed_dir.mkdir(parents=True)
            (feed_dir / "2026-03-15.md").write_text("test")

            dash = update_dashboard(vault_path=tmpdir, today=date(2026, 3, 15))
            assert dash.exists()
            content = dash.read_text()
            assert "[[2026-03-15]]" in content

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dash = update_dashboard(vault_path=tmpdir, today=date(2026, 3, 15))
            assert "No digests yet" in dash.read_text()


class TestArchive:
    def test_moves_old_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            feed_dir = Path(tmpdir) / "Feeds" / "AI-Daily"
            feed_dir.mkdir(parents=True)
            (feed_dir / "2026-01-01.md").write_text("old zh")
            (feed_dir / "2026-01-01-en.md").write_text("old en")
            (feed_dir / "2026-03-15.md").write_text("new")

            moved = archive_old_reports(vault_path=tmpdir, keep_days=14)
            assert moved == 2
            assert (feed_dir / "archive" / "2026-01-01.md").exists()
            assert (feed_dir / "archive" / "2026-01-01-en.md").exists()
            assert (feed_dir / "2026-03-15.md").exists()

    def test_nothing_to_archive(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            assert archive_old_reports(vault_path=tmpdir) == 0
