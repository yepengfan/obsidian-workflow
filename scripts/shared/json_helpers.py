"""Shared JSON parsing helpers for LLM pipeline output.

All feed pipelines (ai-digest, github-trending, engineering-blogs, podcast,
cc-plugins) call Claude via subprocess and parse the JSON response.  LLMs
occasionally produce invalid output (markdown fences, wrapper objects, bad
backslash escapes, trailing commas).  This module centralises the repair
logic so fixes are applied consistently.
"""

from __future__ import annotations

import json
import re
from typing import Any


def strip_fences(raw: str) -> str:
    """Remove optional markdown code fences wrapping JSON."""
    raw = raw.strip()
    raw = re.sub(r"^\s*```(?:json)?\s*\n", "", raw)
    raw = re.sub(r"\n\s*```\s*$", "", raw)
    return raw


def fix_json_escapes(s: str) -> str:
    r"""Fix invalid backslash escapes that LLMs sometimes produce.

    JSON only allows: \" \\ \/ \b \f \n \r \t \uXXXX.
    Lone backslashes before other characters (e.g. \: \' \.) cause
    ``json.loads()`` to raise ``Invalid \escape``.  Replace them with
    the character itself (drop the backslash).
    """
    return re.sub(r'\\(?!["\\/bfnrtu])', "", s)


def _remove_trailing_commas(s: str) -> str:
    """Remove trailing commas before ``}`` or ``]``."""
    return re.sub(r",\s*([}\]])", r"\1", s)


def _fix_unescaped_newlines(s: str) -> str:
    """Escape literal newlines inside JSON string values."""
    return re.sub(
        r'(?<=": ")(.*?)(?="[,}\s])',
        lambda m: m.group(0).replace("\n", "\\n"),
        s,
        flags=re.DOTALL,
    )


def safe_json_loads(s: str) -> Any:
    """``json.loads`` with automatic invalid-escape repair."""
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return json.loads(fix_json_escapes(s))


def extract_json_array(raw: str, fallback_keys: tuple[str, ...] = ()) -> list:
    """Extract a JSON array from possibly messy LLM output.

    Tries, in order:
    1. Direct ``[...]`` extraction.
    2. Unwrap ``{key: [...]}`` using *fallback_keys* (first match wins).
    3. Raise ``ValueError`` with a diagnostic snippet.
    """
    raw = strip_fences(raw)
    start = raw.find("[")
    if start != -1:
        end = raw.rfind("]")
        if end != -1:
            return safe_json_loads(raw[start : end + 1])
    # Might be wrapped in an object
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1:
        obj = safe_json_loads(raw[start : end + 1])
        for key in fallback_keys:
            if key in obj and isinstance(obj[key], list):
                return obj[key]
    raise ValueError(f"No JSON array found:\n{raw[:400]}")


def extract_json_object(raw: str) -> dict:
    """Extract a JSON object from possibly messy LLM output.

    Applies a cascade of repairs:
    1. Direct parse after fence stripping.
    2. Invalid backslash escape repair.
    3. Trailing comma removal.
    4. Unescaped newline repair.
    5. Balanced-brace extraction as last resort.
    """
    raw = strip_fences(raw)
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in output:\n{raw[:400]}")
    candidate = raw[start : end + 1]

    # 1. Direct parse
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    # 2. Fix invalid backslash escapes
    repaired = fix_json_escapes(candidate)
    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # 3. Remove trailing commas
    repaired = _remove_trailing_commas(repaired)
    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # 4. Fix unescaped newlines inside string values
    repaired = _fix_unescaped_newlines(repaired)
    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass

    # 5. Last resort: find balanced braces for the first complete object
    depth = 0
    for i in range(start, len(raw)):
        if raw[i] == "{":
            depth += 1
        elif raw[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(
                        _remove_trailing_commas(fix_json_escapes(raw[start : i + 1]))
                    )
                except json.JSONDecodeError:
                    break

    raise ValueError(f"Could not parse JSON from output:\n{candidate[:400]}")
