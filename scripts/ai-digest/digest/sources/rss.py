"""Async RSS/Atom feed fetcher."""

import asyncio
import re
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from xml.etree import ElementTree as ET

import aiohttp

from digest.feeds import RSS_FEEDS

CONCURRENCY = 10
TIMEOUT_S = 15

DATE_FORMATS = [
    "%a, %d %b %Y %H:%M:%S %z",      # RSS 2.0
    "%a, %d %b %Y %H:%M:%S %Z",      # RSS 2.0 with TZ name
    "%Y-%m-%dT%H:%M:%S%z",            # Atom / ISO 8601
    "%Y-%m-%dT%H:%M:%SZ",             # Atom UTC
    "%Y-%m-%d %H:%M:%S%z",
    "%Y-%m-%d",
]

ATOM_NS = "{http://www.w3.org/2005/Atom}"
HTML_TAG_RE = re.compile(r"<[^>]+>")


@dataclass
class Article:
    title: str
    link: str
    pub_date: datetime
    description: str
    source_name: str
    source_type: str = "rss"


def _parse_date(text: str | None) -> datetime | None:
    if not text:
        return None
    text = text.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def _strip_html(text: str | None) -> str:
    if not text:
        return ""
    return HTML_TAG_RE.sub("", text).strip()


def _parse_rss(xml_bytes: bytes, source_name: str) -> list[Article]:
    """Parse RSS 2.0 or Atom feed XML into Article list."""
    articles = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []

    # Atom feed
    if root.tag == f"{ATOM_NS}feed" or root.tag == "feed":
        ns = ATOM_NS if root.tag.startswith("{") else ""
        for entry in root.findall(f"{ns}entry"):
            title = (entry.findtext(f"{ns}title") or "").strip()
            link_el = entry.find(f"{ns}link[@rel='alternate']") or entry.find(f"{ns}link")
            link = (link_el.get("href", "") if link_el is not None else "").strip()
            date_text = entry.findtext(f"{ns}published") or entry.findtext(f"{ns}updated")
            pub_date = _parse_date(date_text)
            desc = _strip_html(
                entry.findtext(f"{ns}summary") or entry.findtext(f"{ns}content") or ""
            )
            if title and pub_date:
                articles.append(Article(
                    title=title, link=link, pub_date=pub_date,
                    description=desc[:500], source_name=source_name,
                ))
        return articles

    # RSS 2.0
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = _parse_date(item.findtext("pubDate") or item.findtext("dc:date"))
        desc = _strip_html(item.findtext("description") or "")
        if title and pub_date:
            articles.append(Article(
                title=title, link=link, pub_date=pub_date,
                description=desc[:500], source_name=source_name,
            ))

    return articles


async def _fetch_one(
    session: aiohttp.ClientSession,
    feed: dict,
    semaphore: asyncio.Semaphore,
) -> list[Article]:
    """Fetch and parse a single feed."""
    async with semaphore:
        try:
            async with session.get(feed["xmlUrl"], timeout=aiohttp.ClientTimeout(total=TIMEOUT_S)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.read()
                return _parse_rss(data, feed["name"])
        except Exception:
            return []


async def fetch_all_feeds(hours: int = 48) -> tuple[list[Article], int]:
    """Fetch all RSS feeds concurrently, filter by time window.

    Returns (articles, feeds_ok_count).
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    semaphore = asyncio.Semaphore(CONCURRENCY)

    async with aiohttp.ClientSession() as session:
        tasks = [_fetch_one(session, feed, semaphore) for feed in RSS_FEEDS]
        results = await asyncio.gather(*tasks)

    feeds_ok = sum(1 for r in results if r)
    all_articles = [a for batch in results for a in batch if a.pub_date >= cutoff]
    all_articles.sort(key=lambda a: a.pub_date, reverse=True)

    return all_articles, feeds_ok
