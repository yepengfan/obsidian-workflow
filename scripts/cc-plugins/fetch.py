"""Claude Code Plugins discovery via GitHub Search + npm Registry.

Runs multiple GitHub search queries to find Claude Code plugin repos,
resolves npm package info, merges with state.json to classify each as
new / updated / unchanged, and outputs JSON to stdout.

Usage:
    python3 fetch.py [--vault-path /path/to/vault]

Exit codes:
    0 — success, JSON written to stdout
    1 — error (API failure, network error)
    2 — this week's report already exists (idempotency skip)
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path


GITHUB_API_BASE = "https://api.github.com"
GITHUB_SEARCH = f"{GITHUB_API_BASE}/search/repositories"
NPM_REGISTRY = "https://registry.npmjs.org"

SCRIPT_DIR = Path(__file__).parent
STATE_PATH = SCRIPT_DIR / "state.json"

# Search queries to cast a wide net for Claude Code plugins
SEARCH_QUERIES = [
    'topic:claude-code-plugin',
    'topic:claude-code topic:plugin',
    '"claude-code" in:name,description',
    '"claude/plugins" OR ".claude/plugins" in:readme',
    '"claude-code" plugin in:readme',
    '"claude-code" skill OR hook in:readme',
    'topic:mcp-server claude in:readme',
]

# Minimum stars threshold (repos below this AND older than 30 days are skipped)
MIN_STARS = 2
NEW_REPO_WINDOW_DAYS = 30


# ── State management ───────────────────────────────────────────────

def load_state() -> dict:
    """Load state.json or return empty structure."""
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            print("[fetch] Warning: state.json corrupted, starting fresh.", file=sys.stderr)
    return {"last_run": None, "plugins": {}}


def get_iso_week(d: date) -> str:
    """Return ISO week string like '2026-W14'."""
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


# ── CLI / API helpers ──────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Claude Code plugins → JSON")
    parser.add_argument("--vault-path", default=".", help="Obsidian vault path")
    return parser.parse_args()


def build_headers() -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"token {token}"
        print("[fetch] Using GITHUB_TOKEN for authenticated requests.", file=sys.stderr)
    else:
        print(
            "[fetch] Warning: GITHUB_TOKEN not set. Unauthenticated rate limit "
            "is 10 req/min. With 7 queries x up to 4 pages each, set GITHUB_TOKEN "
            "(30 req/min) to avoid rate-limit errors.",
            file=sys.stderr,
        )
    return headers


def api_get(url: str, headers: dict, timeout: int = 30) -> dict:
    """Generic GET request returning parsed JSON."""
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"[fetch] HTTP {e.code}: {error_body[:300]}", file=sys.stderr)
        raise
    except urllib.error.URLError as e:
        print(f"[fetch] Network error: {e.reason}", file=sys.stderr)
        raise


MAX_PLUGINS = 100  # limit output to top N by stars (keeps Haiku call manageable)


def search_github(query: str, headers: dict) -> list[dict]:
    """Run a single GitHub search query, returning all items (up to 60)."""
    items = []
    for page in range(1, 5):  # max 4 pages (120 results) to cast a wider net
        params = (
            f"q={urllib.request.quote(query)}"
            f"&sort=stars&order=desc&per_page=30&page={page}"
        )
        url = f"{GITHUB_SEARCH}?{params}"
        print(f"[fetch] GET {url}", file=sys.stderr)

        try:
            data = api_get(url, headers)
        except Exception:
            print(f"[fetch] Search query failed: {query}", file=sys.stderr)
            break

        page_items = data.get("items", [])
        items.extend(page_items)
        print(f"[fetch]   Page {page}: {len(page_items)} results", file=sys.stderr)

        if len(page_items) < 30:
            break
        time.sleep(6)  # rate limit: 10 req/min unauthenticated → ≥6s between pages

    return items


# ── npm resolution ─────────────────────────────────────────────────

def fetch_package_json(full_name: str, headers: dict) -> str | None:
    """Try to read package.json 'name' field from the repo's default branch."""
    url = f"https://raw.githubusercontent.com/{full_name}/HEAD/package.json"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            pkg = json.loads(resp.read().decode("utf-8"))
            return pkg.get("name")
    except Exception:
        return None


def fetch_npm_info(package_name: str) -> dict | None:
    """Fetch npm registry info for a package."""
    url = f"{NPM_REGISTRY}/{urllib.request.quote(package_name, safe='@/')}"
    try:
        data = api_get(url, {"Accept": "application/json"})
        dist_tags = data.get("dist-tags", {})
        latest = dist_tags.get("latest", "")

        # Weekly downloads from a separate API
        downloads = 0
        try:
            dl_url = f"https://api.npmjs.org/downloads/point/last-week/{urllib.request.quote(package_name, safe='@/')}"
            dl_data = api_get(dl_url, {"Accept": "application/json"})
            downloads = dl_data.get("downloads", 0)
        except Exception:
            pass

        # Find publish date for latest version
        time_map = data.get("time", {})
        publish_date = time_map.get(latest, "")

        return {
            "npm_package": package_name,
            "latest_version": latest,
            "publish_date": publish_date,
            "weekly_downloads": downloads,
        }
    except Exception:
        return None


# ── README fetching ────────────────────────────────────────────────

def fetch_readme_raw(full_name: str, max_chars: int = 2000) -> str:
    """Fetch raw README content via raw.githubusercontent.com."""
    for readme_name in ["README.md", "readme.md", "README.rst", "README"]:
        url = f"https://raw.githubusercontent.com/{full_name}/HEAD/{readme_name}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.read().decode("utf-8", errors="replace")[:max_chars]
        except Exception:
            continue
    return ""


# ── Repo normalization ─────────────────────────────────────────────

def normalize_repo(item: dict, today: date) -> dict:
    """Extract relevant fields from a GitHub API repo item."""
    full_name = item.get("full_name", "")
    stars = item.get("stargazers_count", 0)
    created_str = item.get("created_at", "")
    pushed_str = item.get("pushed_at", "")

    # Calculate age
    age_days = 999
    if created_str:
        try:
            created_date = datetime.fromisoformat(
                created_str.replace("Z", "+00:00")
            ).date()
            age_days = max((today - created_date).days, 1)
        except (ValueError, TypeError):
            pass

    return {
        "repo_url": item.get("html_url", ""),
        "full_name": full_name,
        "name": full_name.split("/")[-1] if "/" in full_name else full_name,
        "description": item.get("description") or "",
        "stars": stars,
        "forks": item.get("forks_count", 0),
        "language": item.get("language") or "",
        "topics": item.get("topics") or [],
        "created_at": created_str,
        "pushed_at": pushed_str,
        "age_days": age_days,
        "readme_excerpt": "",  # populated later
        "npm_info": None,  # populated later
    }


# ── Main ───────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()
    today = date.today()
    week = get_iso_week(today)
    vault = Path(args.vault_path).expanduser()

    # Idempotency: check if this week's report exists
    feed_dir = vault / "Feeds" / "CC-Plugins"
    report_file = feed_dir / f"{week}.md"
    if report_file.exists():
        print(f"[fetch] This week's report already exists: {report_file}", file=sys.stderr)
        sys.exit(2)

    # Load state
    state = load_state()
    known_plugins = state.get("plugins", {})
    print(f"[fetch] State loaded: {len(known_plugins)} known plugins.", file=sys.stderr)

    headers = build_headers()

    # ── Run search queries ──────────────────────────────────────
    all_items: list[dict] = []
    for i, query in enumerate(SEARCH_QUERIES, 1):
        print(f"[fetch] Query {i}/{len(SEARCH_QUERIES)}: {query}", file=sys.stderr)
        items = search_github(query, headers)
        all_items.extend(items)
        print(f"[fetch] Query {i} returned {len(items)} results.", file=sys.stderr)
        if i < len(SEARCH_QUERIES):
            time.sleep(2)  # rate limit between queries

    print(f"[fetch] Total raw results: {len(all_items)}", file=sys.stderr)

    # ── Deduplicate by repo URL ─────────────────────────────────
    seen: dict[str, dict] = {}
    for item in all_items:
        repo = normalize_repo(item, today)
        url = repo["repo_url"]
        if not url or url in seen:
            continue

        # Filter: skip repos with < MIN_STARS AND older than NEW_REPO_WINDOW_DAYS
        if repo["stars"] < MIN_STARS and repo["age_days"] > NEW_REPO_WINDOW_DAYS:
            continue

        seen[url] = repo

    print(f"[fetch] After dedup + filter: {len(seen)} repos.", file=sys.stderr)

    if not seen:
        print("[fetch] No plugin repos found. Exiting.", file=sys.stderr)
        sys.exit(1)

    # ── Rank by stars and take top N ────────────────────────────
    # Sort by stars descending, limit to MAX_PLUGINS to keep Haiku call manageable
    ranked = sorted(seen.values(), key=lambda r: r["stars"], reverse=True)[:MAX_PLUGINS]
    seen = {r["repo_url"]: r for r in ranked}
    print(f"[fetch] Top {len(seen)} repos selected by stars.", file=sys.stderr)

    # ── Resolve npm packages + fetch READMEs ────────────────────
    print(f"[fetch] Resolving npm packages and fetching READMEs...", file=sys.stderr)
    for i, (url, repo) in enumerate(seen.items()):
        # Fetch README
        readme = fetch_readme_raw(repo["full_name"])
        repo["readme_excerpt"] = readme

        # Try to resolve npm package
        pkg_name = fetch_package_json(repo["full_name"], headers)
        if pkg_name:
            npm_info = fetch_npm_info(pkg_name)
            if npm_info:
                repo["npm_info"] = npm_info

        if (i + 1) % 5 == 0:
            print(f"[fetch]   Resolved {i + 1}/{len(seen)} repos...", file=sys.stderr)
            time.sleep(1)

    npm_count = sum(1 for r in seen.values() if r["npm_info"])
    print(f"[fetch] npm packages resolved: {npm_count}/{len(seen)}", file=sys.stderr)

    # ── Classify as new / updated / unchanged ───────────────────
    for url, repo in seen.items():
        known = known_plugins.get(url)
        if known is None:
            repo["change_type"] = "new"
        elif (
            repo["npm_info"]
            and known.get("last_version")
            and repo["npm_info"]["latest_version"] != known["last_version"]
        ):
            repo["change_type"] = "updated"
            repo["previous_version"] = known["last_version"]
        else:
            repo["change_type"] = "unchanged"

    new_count = sum(1 for r in seen.values() if r["change_type"] == "new")
    updated_count = sum(1 for r in seen.values() if r["change_type"] == "updated")
    unchanged_count = sum(1 for r in seen.values() if r["change_type"] == "unchanged")
    print(
        f"[fetch] Classification: {new_count} new, {updated_count} updated, "
        f"{unchanged_count} unchanged.",
        file=sys.stderr,
    )

    # ── Build output payload ────────────────────────────────────
    plugins = list(seen.values())
    payload = {
        "week": week,
        "date": today.isoformat(),
        "plugins": plugins,
        "stats": {
            "total_fetched": len(all_items),
            "after_dedup": len(seen),
            "new": new_count,
            "updated": updated_count,
            "unchanged": unchanged_count,
            "npm_resolved": npm_count,
        },
    }

    json.dump(payload, sys.stdout, ensure_ascii=False)
    print(file=sys.stdout)


if __name__ == "__main__":
    main()
