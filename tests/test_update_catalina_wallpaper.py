import argparse
import datetime as dt
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

import update_catalina_wallpaper as updater


class DurationLogicTests(unittest.TestCase):
    def test_build_durations_returns_nine_segments(self) -> None:
        boundaries = [0.0, 18063.0, 19619.0, 22448.0, 43947.0, 65446.0, 66718.0, 68274.0, 69831.0, 86400.0]

        static_durations, transition_durations = updater.build_durations(boundaries)

        self.assertEqual(len(static_durations), 9)
        self.assertEqual(len(transition_durations), 9)
        self.assertTrue(all(value > 0 for value in static_durations))
        self.assertTrue(all(value > 0 for value in transition_durations))
        self.assertAlmostEqual(
            sum(static_durations) + sum(transition_durations),
            updater.SECONDS_PER_DAY,
            places=1,
        )

    def test_transition_duration_never_consumes_whole_segment(self) -> None:
        for segment in (120.0, 300.0, 900.0, 2400.0, 7200.0):
            with self.subTest(segment=segment):
                transition = updater.choose_transition_duration(segment)
                self.assertGreaterEqual(transition, 60.0)
                self.assertLess(transition, segment)


class RenderXmlTests(unittest.TestCase):
    def test_render_xml_creates_expected_blocks(self) -> None:
        start_of_day = dt.datetime(2026, 3, 30, tzinfo=dt.timezone.utc)
        images = [f"/tmp/Catalina-{index}.jpg" for index in range(1, 10)]
        static = [900.0] * 9
        transitions = [180.0] * 9

        rendered = updater.render_xml(start_of_day, images, static, transitions)
        root = ET.fromstring(rendered)

        self.assertEqual(root.find("starttime/year").text, "2026")
        self.assertEqual(root.find("starttime/month").text, "3")
        self.assertEqual(root.find("starttime/day").text, "30")
        self.assertEqual(len(root.findall("static")), 9)
        self.assertEqual(len(root.findall("transition")), 9)


class PathAndArgsTests(unittest.TestCase):
    def test_compact_home_path_replaces_home_prefix(self) -> None:
        sample_path = Path.home() / "folder" / "file.txt"
        self.assertEqual(updater.compact_home_path(sample_path), "~/folder/file.txt")

    def test_resolve_coordinates_prefers_manual_values(self) -> None:
        args = argparse.Namespace(lat=-22.25, lon=-47.0098, tz="America/Sao_Paulo")
        latitude, longitude, timezone = updater.resolve_coordinates(args)

        self.assertEqual(latitude, -22.25)
        self.assertEqual(longitude, -47.0098)
        self.assertEqual(timezone, "America/Sao_Paulo")


if __name__ == "__main__":
    unittest.main()
