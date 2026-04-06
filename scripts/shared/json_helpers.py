"""Shared JSON parsing helpers for LLM pipeline output.

All feed pipelines (ai-digest, github-trending, engineering-blogs) call Claude
via subprocess and parse the JSON response.  LLMs occasionally produce invalid
output (markdown fences, wrapper objects, bad backslash escapes).  This module
centralises the repair logic so fixes are applied consistently.
"""

import json
import re


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


def safe_json_loads(s: str):
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
            if key in obj:
                return obj[key]
    raise ValueError(f"No JSON array found:\n{raw[:400]}")


def extract_json_object(raw: str) -> dict:
    """Extract a JSON object from possibly messy LLM output."""
    raw = strip_fences(raw)
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in output:\n{raw[:400]}")
    return safe_json_loads(raw[start : end + 1])
