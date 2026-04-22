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


def unwrap_claude_envelope(raw: str) -> str:
    """Unwrap the ``{"result": "..."}`` envelope from ``--output-format json``.

    The Claude CLI ``--output-format json`` flag wraps model output in a JSON
    envelope: ``{"result": "<escaped-content>"}``.  When the inner content
    contains literal newlines (common with LLM output), the envelope itself
    becomes invalid JSON because bare ``\\n`` inside a JSON string value is
    illegal.

    Strategy (in order):
    1. Standard ``json.loads`` — works when the envelope is well-formed.
    2. Escape bare newlines inside the envelope string before parsing.
    3. Regex extraction of the ``result`` field value, then unescape.
    4. Fall through and return *raw* unchanged so the caller can still
       attempt ``extract_json_array`` on whatever came back.
    """
    stripped = raw.strip()

    # 1. Direct parse
    try:
        envelope = json.loads(stripped)
        if isinstance(envelope, dict) and "result" in envelope:
            return envelope["result"]
    except (json.JSONDecodeError, ValueError):
        pass

    # 2. Fix bare newlines inside JSON string values.
    #    Replace literal \n (and \r) that are NOT already escaped.
    fixed = stripped.replace("\r\n", "\\n").replace("\r", "\\n")
    fixed = re.sub(r'(?<!\\)\n', r'\\n', fixed)
    try:
        envelope = json.loads(fixed)
        if isinstance(envelope, dict) and "result" in envelope:
            return envelope["result"]
    except (json.JSONDecodeError, ValueError):
        pass

    # 3. Regex: extract everything between "result":" and the last "}
    m = re.search(r'"result"\s*:\s*"(.*)"', stripped, re.DOTALL)
    if m:
        inner = m.group(1)
        # Unescape JSON string escapes (\\n -> \n, \\" -> ", etc.)
        try:
            return json.loads(f'"{inner}"')
        except (json.JSONDecodeError, ValueError):
            # Manual unescape for the most common cases
            inner = inner.replace('\\"', '"').replace("\\n", "\n")
            inner = inner.replace("\\t", "\t").replace("\\\\", "\\")
            return inner

    # 4. Not an envelope — return as-is
    return raw


def _try_parse_array(candidate: str) -> list | None:
    """Attempt to parse *candidate* as a JSON array with cascading repairs."""
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

    return None


def _salvage_truncated_array(raw: str, arr_start: int) -> list | None:
    """Recover complete JSON objects from a truncated array.

    When the LLM output is cut off mid-stream, the closing ``]`` is missing.
    Walk backwards from the end to find the last complete ``}``, append ``]``,
    and try to parse.  This progressively strips trailing incomplete objects
    until a valid array is recovered.
    """
    # Find the last '}' that could close an array element
    pos = len(raw) - 1
    while pos > arr_start:
        pos = raw.rfind("}", arr_start, pos + 1)
        if pos == -1:
            break
        candidate = raw[arr_start : pos + 1] + "]"
        result = _try_parse_array(candidate)
        if result is not None and len(result) > 0:
            return result
        pos -= 1
    return None


def extract_json_array(raw: str, fallback_keys: tuple[str, ...] = ()) -> list:
    """Extract a JSON array from possibly messy LLM output.

    Tries, in order:
    1. Direct ``[...]`` extraction with cascading repairs.
    2. Truncation recovery — salvage complete objects from cut-off output.
    3. Unwrap ``{key: [...]}`` using *fallback_keys* (first match wins).
    4. Raise ``ValueError`` with a diagnostic snippet.
    """
    raw = strip_fences(raw)
    start = raw.find("[")
    if start != -1:
        end = raw.rfind("]")
        if end != -1 and end > start:
            candidate = raw[start : end + 1]
            result = _try_parse_array(candidate)
            if result is not None:
                return result
        # No closing ']' or parsing failed — try truncation recovery
        salvaged = _salvage_truncated_array(raw, start)
        if salvaged is not None:
            return salvaged
    # Might be wrapped in an object
    obj_start = raw.find("{")
    obj_end = raw.rfind("}")
    if obj_start != -1 and obj_end != -1:
        try:
            obj = safe_json_loads(raw[obj_start : obj_end + 1])
        except (json.JSONDecodeError, ValueError):
            obj = {}
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
