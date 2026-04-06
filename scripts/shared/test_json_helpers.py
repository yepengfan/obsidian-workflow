#!/usr/bin/env python3
"""Tests for shared JSON helpers.

Run: python3 scripts/shared/test_json_helpers.py
"""

import json
import unittest

from json_helpers import (
    extract_json_array,
    extract_json_object,
    fix_json_escapes,
    safe_json_loads,
    strip_fences,
)


class TestStripFences(unittest.TestCase):
    def test_no_fences(self):
        self.assertEqual(strip_fences('[1, 2]'), '[1, 2]')

    def test_json_fences(self):
        self.assertEqual(strip_fences('```json\n[1, 2]\n```'), '[1, 2]')

    def test_plain_fences(self):
        self.assertEqual(strip_fences('```\n{"a": 1}\n```'), '{"a": 1}')

    def test_surrounding_whitespace(self):
        self.assertEqual(strip_fences('  \n```json\n{}\n```\n  '), '{}')


class TestFixJsonEscapes(unittest.TestCase):
    def test_valid_escapes_preserved(self):
        # Only test sequences that are purely valid JSON escapes
        s = r'\"hello\" \n \t \u0041'
        self.assertEqual(fix_json_escapes(s), s)

    def test_escaped_backslash_followed_by_char(self):
        # \\p is two escapes: \\ (valid) then \p (invalid) → \p removed
        self.assertEqual(fix_json_escapes(r'\\path'), r'\path')

    def test_invalid_colon_escape(self):
        self.assertEqual(fix_json_escapes(r'value\:test'), 'value:test')

    def test_invalid_apostrophe_escape(self):
        self.assertEqual(fix_json_escapes(r"it\'s"), "it's")

    def test_no_escapes(self):
        self.assertEqual(fix_json_escapes('plain text'), 'plain text')


class TestSafeJsonLoads(unittest.TestCase):
    def test_valid_json(self):
        self.assertEqual(safe_json_loads('[1, 2, 3]'), [1, 2, 3])

    def test_valid_object(self):
        self.assertEqual(safe_json_loads('{"a": 1}'), {"a": 1})

    def test_repairs_bad_escapes(self):
        # Raw string with invalid \: escape
        raw = '{"key": "value\\:test"}'
        result = safe_json_loads(raw)
        self.assertEqual(result, {"key": "value:test"})

    def test_raises_on_truly_invalid(self):
        with self.assertRaises(json.JSONDecodeError):
            safe_json_loads('not json at all')


class TestExtractJsonArray(unittest.TestCase):
    def test_direct_array(self):
        self.assertEqual(extract_json_array('[{"a": 1}]'), [{"a": 1}])

    def test_array_with_fences(self):
        raw = '```json\n[1, 2, 3]\n```'
        self.assertEqual(extract_json_array(raw), [1, 2, 3])

    def test_wrapped_with_fallback_key(self):
        raw = '{"top_articles": [1, 2]}'
        self.assertEqual(
            extract_json_array(raw, fallback_keys=("top_articles",)),
            [1, 2],
        )

    def test_fallback_key_must_be_list(self):
        raw = '{"top_articles": "not a list"}'
        with self.assertRaises(ValueError):
            extract_json_array(raw, fallback_keys=("top_articles",))

    def test_fallback_skips_non_list_values(self):
        # When fallback key exists but value is not a list, skip it
        raw = '{"count": 5, "items": [1, 2]}'
        self.assertEqual(
            extract_json_array(raw, fallback_keys=("count", "items")),
            [1, 2],
        )

    def test_no_array_raises(self):
        with self.assertRaises(ValueError):
            extract_json_array('just some text')

    def test_preamble_text_before_array(self):
        raw = 'Here are the results:\n[{"id": 1}]'
        self.assertEqual(extract_json_array(raw), [{"id": 1}])

    def test_bad_escapes_in_array(self):
        raw = '[{"key": "path\\:to\\:thing"}]'
        result = extract_json_array(raw)
        self.assertEqual(result, [{"key": "path:to:thing"}])


class TestExtractJsonObject(unittest.TestCase):
    def test_direct_object(self):
        self.assertEqual(
            extract_json_object('{"trend_zh": "hi"}'),
            {"trend_zh": "hi"},
        )

    def test_object_with_fences(self):
        raw = '```json\n{"a": 1}\n```'
        self.assertEqual(extract_json_object(raw), {"a": 1})

    def test_trailing_comma_repair(self):
        raw = '{"a": 1, "b": 2,}'
        self.assertEqual(extract_json_object(raw), {"a": 1, "b": 2})

    def test_bad_escape_repair(self):
        raw = '{"path": "C\\:\\Users"}'
        result = extract_json_object(raw)
        self.assertEqual(result, {"path": "C:Users"})

    def test_nested_trailing_comma(self):
        raw = '{"items": [1, 2,],}'
        self.assertEqual(extract_json_object(raw), {"items": [1, 2]})

    def test_preamble_text(self):
        raw = 'Here is the JSON:\n{"key": "value"}\nDone.'
        self.assertEqual(extract_json_object(raw), {"key": "value"})

    def test_no_object_raises(self):
        with self.assertRaises(ValueError):
            extract_json_object('no json here')

    def test_balanced_brace_fallback(self):
        # Construct a case where only balanced-brace extraction works:
        # valid inner object followed by garbage
        raw = '{"a": 1} some trailing garbage }'
        result = extract_json_object(raw)
        self.assertEqual(result, {"a": 1})


if __name__ == "__main__":
    unittest.main()
