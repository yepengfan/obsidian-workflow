import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

import review


class CloseoutRetryTests(unittest.TestCase):
    def test_round_five_retry_after_archive_has_no_closing_summary(self):
        with tempfile.TemporaryDirectory(dir=review.ROOT) as temporary:
            root = Path(temporary)
            review_root = root / "Learning/Practice/Review"
            items = review_root / "Items"
            items.mkdir(parents=True)
            (review_root / "Content").mkdir()
            (review_root / "Content/system-design.md").touch()
            (root / "flow.md").touch()
            topic = {
                "id": "bitly", "title": "Bitly", "domain": "system-design",
                "prompt": "Design Bitly.",
            }
            config = ([1, 3, 7, 14, 60], 1, {"system-design": "flow.md"}, True)
            with patch.multiple(review, ROOT=root, REVIEW=review_root, ITEMS=items):
                review.add(topic, config[2])
                for number in range(1, 5):
                    review.record("bitly", {
                        "attempt_id": f"r{number}", "reflection": "Completed.",
                    }, date(2026, 11, number), config[0], config[1], True)

                def session(number):
                    path = root / review.design_profile.SOLUTIONS / f"Bitly-r{number}" / "progress.md"
                    path.parent.mkdir(parents=True)
                    review.write_note(path, {"topic": "Bitly", "tags": ["system-design/wip"]}, "# Bitly\n")
                    return path

                fifth, sixth = session(5), session(6)
                attempt5 = {"attempt_id": "r5", "reflection": "Fifth round."}
                attempt6 = {"attempt_id": "r6", "reflection": "Final mock."}
                with patch.object(review.design_profile, "rebuild", side_effect=OSError("profile unavailable")):
                    with self.assertRaisesRegex(OSError, "profile unavailable"):
                        review.finish(topic, attempt5, fifth, date(2026, 11, 5), config)
                receipt6 = review.finish(topic, attempt6, sixth, date(2026, 11, 6), config)
                self.assertEqual(receipt6["status"], "archived")
                self.assertEqual(sixth.read_text().count("## Round summary"), 1)
                receipt5 = review.finish(topic, attempt5, fifth, date(2026, 11, 5), config)
                self.assertEqual(receipt5["attempt_completed_round"], 5)
                self.assertNotIn("## Round summary", fifth.read_text())
                self.assertEqual(review.read_note(fifth)[0]["tags"], ["system-design/done"])
                review.finish(topic, attempt6, sixth, date(2026, 11, 6), config)
                self.assertEqual(sixth.read_text().count("## Round summary"), 1)
                metadata, _ = review.read_note(items / "bitly.md")
                self.assertEqual(metadata["review_count"], 6)
                self.assertEqual(metadata["completed_design_rounds"], 6)


if __name__ == "__main__":
    unittest.main()
