import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

import review


class MigrationInputTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=review.ROOT)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.items = self.root / "Learning/Practice/Review/Items"
        self.items.mkdir(parents=True)
        self.patches = patch.multiple(review, ROOT=self.root, ITEMS=self.items)
        self.patches.start()
        self.addCleanup(self.patches.stop)

    def item(self, item_id="sysd-url-shortener", **fields):
        path = self.items / f"{item_id}.md"
        review.write_note(path, {
            "id": item_id, "domain": "system-design", "title": "Design",
            "prompt": "Design a service.", "status": "active", "stage": 0,
            "review_count": 0, "last_review": None, "next_review": None,
            "attempt_ids": [],
            **({"completed_design_rounds": 0} if fields.get("domain", "system-design") == "system-design" else {}),
            **fields,
        }, "# Existing question\n")
        return path

    def test_migration_populates_only_approved_question_concepts(self):
        path = self.item()
        unrelated = self.item("sysd-other")
        unrelated_bytes = unrelated.read_bytes()
        entry = review.design_profile.APPROVED_BACKFILL[-1]
        progress = self.root / entry["progress"]
        progress.parent.mkdir(parents=True)
        progress.write_text(f"# Bitly\n\n## Progress\n\n{entry['locator']}\n")
        review.migrate([1, 3, 7, 14, 60], 1, True)
        expected = ["scaling.sharding", "consistency.replica-lag", "id.counter", "cache.expiry"]
        metadata, body = review.read_note(path)
        self.assertEqual(metadata["concept_ids"], expected)
        self.assertEqual(body, "# Existing question\n")
        self.assertEqual(unrelated.read_bytes(), unrelated_bytes)
        outline = review.question_outline("sysd-url-shortener")
        self.assertEqual([item["concept_id"] for item in outline["core"]], expected)
        self.assertEqual([item["concept_id"] for item in outline["follow_ups"]], ["cache.expiry"])
        self.assertTrue(outline["follow_ups"][0]["evidence"])
        saved = path.read_bytes()
        review.migrate([1, 3, 7, 14, 60], 1, True)
        self.assertEqual(path.read_bytes(), saved)

    def test_migration_preserves_existing_lists_including_empty(self):
        for concepts in ([], ["cache.expiry"]):
            with self.subTest(concepts=concepts):
                path = self.item(concept_ids=concepts)
                previous = path.read_bytes()
                review.migrate([1, 3, 7, 14, 60], 1, True)
                self.assertEqual(path.read_bytes(), previous)
        path = self.item(domain="algorithm")
        previous = path.read_bytes()
        review.migrate([1, 3, 7, 14, 60], 1, True)
        self.assertEqual(path.read_bytes(), previous)

    def test_present_outcome_aliases_reject_without_recording(self):
        for domain in ("system-design", "algorithm", "behavioral"):
            path = self.item(domain=domain)
            previous = path.read_bytes()
            for outcome in (None, "", "completed"):
                with self.subTest(domain=domain, outcome=outcome):
                    with self.assertRaisesRegex(ValueError, "outcome must be"):
                        review.record("sysd-url-shortener", {
                            "attempt_id": "invalid", "reflection": "Answer", "outcome": outcome,
                        }, date(2026, 11, 26), [1, 3, 7, 14, 60], 1, True)
                    self.assertEqual(path.read_bytes(), previous)


if __name__ == "__main__":
    unittest.main()
