"""Synthetic counts stay in local tests and are never published as profile data."""
from datetime import date, timedelta
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import generate_commit_city as city


def fixture(counts):
    start = date(2026, 1, 1)
    end = start + timedelta(days=len(counts)-1)
    calendar = {"totalContributions": sum(counts), "weeks": [{"contributionDays": [
        {"date": (start+timedelta(days=i)).isoformat(), "contributionCount": count}
        for i, count in enumerate(counts)]}]}
    return city.normalize_calendar(calendar, "test-user", start, end)


class CityTests(unittest.TestCase):
    def test_thresholds(self):
        self.assertEqual([city.tier(n) for n in [0, 1, 2, 3, 5, 6, 9, 10, 250]],
                         [0, 1, 1, 2, 2, 3, 3, 4, 4])
        self.assertEqual(city.tier(4, [1, 3, 7]), 3)

    def test_zero_has_no_building(self):
        svg = city.render_scene(fixture([0, 1, 3, 6, 10])).svg.tostring()
        root = ET.fromstring(svg)
        buildings = [node for node in root.iter() if node.get("data-contributions")]
        self.assertEqual([node.get("data-contributions") for node in buildings], ["1", "3", "6", "10"])
        self.assertNotIn('id="day-2026-01-01"', svg)

    def test_preserves_chronology(self):
        snapshot = fixture([0, 1, 9])
        snapshot["days"].reverse()
        normalized = city.validate_snapshot(snapshot)
        self.assertEqual([day["date"] for day in normalized["days"]],
                         ["2026-01-01", "2026-01-02", "2026-01-03"])

    def test_rejects_invalid_or_missing_days(self):
        for value in [-1, 1.5, True]:
            with self.assertRaises(ValueError):
                fixture([value])
        snapshot = fixture([1, 2, 3])
        snapshot["days"].pop()
        with self.assertRaises(ValueError):
            city.validate_snapshot(snapshot)

    def test_rejects_total_mismatch(self):
        snapshot = fixture([1, 2])
        snapshot["total"] += 1
        with self.assertRaises(ValueError):
            city.validate_snapshot(snapshot)

    def test_no_token_never_fabricates_data(self):
        with patch.object(city, "urlopen") as request:
            with self.assertRaises(RuntimeError):
                city.fetch_snapshot("test-user", "")
            request.assert_not_called()

    def test_outputs_are_deterministic(self):
        with tempfile.TemporaryDirectory() as folder:
            first = city.generate(fixture([0, 1, 5, 10]), folder, animate=False)
            self.assertEqual(len(first), 3)
            self.assertEqual(city.generate(fixture([0, 1, 5, 10]), folder, animate=False), [])

    def test_placeholder_is_explicit(self):
        with tempfile.TemporaryDirectory() as folder:
            city.placeholder(folder)
            svg = (Path(folder) / "commit-city.svg").read_text(encoding="utf-8")
            self.assertIn("indisponíveis", svg)
            self.assertFalse((Path(folder) / "commit-city-data.json").exists())


if __name__ == "__main__":
    unittest.main()
