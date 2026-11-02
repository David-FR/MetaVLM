"""Check sample matching, metadata removal, and scoring with small examples."""

import ast
import base64
import json
import tempfile
import unittest
from pathlib import Path

from analyze import analyze
from configurations import CONFIGURATIONS, RUNS, read_jsonl, select_metadata
from prepare import prepare


ONE_PIXEL_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgYGAAAAAEAAH2FzhVAAAAAElFTkSuQmCC"
)


class AblationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.metadata = {
            "ego": {"speed_mps": 12.0},
            "lane": {"is_junction": False},
            "weather": {"fog": 0.0},
            "actors": [{"distance_m": 20.0}],
            "risk": {"ttc_s": None, "headway_s": 1.67},
        }
        self.samples = []
        for session in ("clear_noon", "fog_night"):
            folder = self.root / session
            folder.mkdir()
            (folder / "image.png").write_bytes(ONE_PIXEL_PNG)
            self.write(folder / "metadata.jsonl", [{
                "frame_id": 5, "rgb_path": "image.png", **self.metadata,
            }])
            self.samples.append({
                "scenario_id": "01_VID_FTSA", "session_id": session,
                "frame_id": 5, "metadata_path": f"{session}/metadata.jsonl",
                "action": "Brake",
            })
        self.manifest = self.root / "samples.jsonl"
        self.write(self.manifest, self.samples)

    def write(self, path, records):
        path.write_text("".join(json.dumps(record) + "\n" for record in records))

    def prepared_predictions(self):
        output = self.root / "prepared"
        prepare(self.manifest, output)
        tasks = read_jsonl(output / "inputs.jsonl")
        predictions = [{
            **{field: task[field] for field in
               ("scenario_id", "session_id", "frame_id", "configuration", "run")},
            "action": "Brake",
        } for task in tasks]
        return output / "labels.jsonl", predictions

    def test_preparation_keeps_frames_and_labels_separate(self):
        output = self.root / "prepared"
        self.assertEqual(prepare(self.manifest, output), 2)
        tasks = read_jsonl(output / "inputs.jsonl")
        self.assertEqual(len(tasks), 30)
        self.assertEqual(len(read_jsonl(output / "labels.jsonl")), 2)
        for task in tasks:
            self.assertNotIn("action", task)
            self.assertNotIn("metadata_path", task)
            self.assertTrue(Path(task["image_path"]).is_file())
            self.assertEqual(task["metadata"], {
                group: self.metadata[group]
                for group in CONFIGURATIONS[task["configuration"]]
            })
        with self.assertRaisesRegex(ValueError, "already exists"):
            prepare(self.manifest, output)

    def test_bad_input_does_not_create_output(self):
        for change, message in (
            ({"frame_id": 99}, "not found"),
            ({"action": "Stop"}, "Invalid expert action"),
            ({"metadata_path": "missing.jsonl"}, None),
        ):
            with self.subTest(change=change):
                self.write(self.manifest, [{**self.samples[0], **change}])
                output = self.root / "bad"
                with self.assertRaises((ValueError, OSError)):
                    prepare(self.manifest, output)
                self.assertFalse(output.exists())
        self.write(self.manifest, self.samples)
        (self.root / "clear_noon" / "image.png").unlink()
        with self.assertRaisesRegex(ValueError, "Missing RGB"):
            prepare(self.manifest, self.root / "bad")

    def test_missing_group_rejected_even_when_removed(self):
        record = dict(self.metadata)
        del record["weather"]
        with self.assertRaisesRegex(ValueError, "weather"):
            select_metadata(record, "without_weather")

    def test_duplicate_samples_and_metadata_frames_rejected(self):
        self.write(self.manifest, [self.samples[0], self.samples[0]])
        with self.assertRaisesRegex(ValueError, "Duplicate sample"):
            prepare(self.manifest, self.root / "bad")
        self.write(self.manifest, self.samples)
        path = self.root / "clear_noon" / "metadata.jsonl"
        self.write(path, read_jsonl(path) * 2)
        with self.assertRaisesRegex(ValueError, "Duplicate frame"):
            prepare(self.manifest, self.root / "bad")

    def test_scores_invalid_actions_and_paired_differences(self):
        labels, predictions = self.prepared_predictions()
        for record in predictions:
            if record["configuration"] == "without_weather":
                if record["run"] == 2 or (record["run"] == 1 and record["session_id"] == "fog_night"):
                    record["action"] = None
        path = self.root / "predictions.jsonl"
        self.write(path, predictions)
        rows = {row["configuration"]: row for row in analyze(labels, path)}
        self.assertEqual(rows["full"]["accuracy_mean_pct"], 100)
        weather = rows["without_weather"]
        self.assertEqual(weather["accuracy_mean_pct"], 50)
        self.assertEqual(weather["accuracy_sd_pp"], 50)
        self.assertEqual(weather["full_minus_ablated_mean_pp"], 50)
        self.assertEqual(weather["full_minus_ablated_sd_pp"], 50)
        self.assertEqual(weather["invalid_responses"], 3)

    def test_incomplete_duplicate_and_unexpected_predictions_rejected(self):
        labels, predictions = self.prepared_predictions()
        path = self.root / "predictions.jsonl"
        for records, message in (
            (predictions[:-1], "Incomplete predictions"),
            (predictions + [predictions[0]], "Duplicate prediction"),
            ([{**predictions[0], "frame_id": 999}] + predictions[1:], "no matching label"),
            ([{**predictions[0], "run": True}] + predictions[1:], "Invalid run"),
        ):
            with self.subTest(message=message):
                self.write(path, records)
                with self.assertRaisesRegex(ValueError, message):
                    analyze(labels, path)

    def test_averaging_with_unequal_session_sizes(self):
        from analyze import accuracy
        outcomes = {("A", "clear", 1): True, ("A", "clear", 2): True,
                    ("A", "fog", 1): False, ("B", "clear", 1): False}
        self.assertEqual(accuracy(outcomes, "frame"), 50)
        self.assertAlmostEqual(accuracy(outcomes, "session"), 100 / 3)
        self.assertEqual(accuracy(outcomes, "scenario"), 25)

    def test_all_scenario_scripts_have_matching_metadata_schemas(self):
        scripts = sorted((Path(__file__).resolve().parents[1] / "scripts").glob("*_scenario.py"))
        self.assertEqual(len(scripts), 20)
        schemas = []
        for script in scripts:
            tree = ast.parse(script.read_text())
            schema = {}
            for node in tree.body:
                if isinstance(node, ast.ClassDef) and node.name in (
                    "EgoState", "LaneContext", "WeatherSummary", "ActorSummary", "RiskSummary", "FrameRecord"
                ):
                    schema[node.name] = [field.target.id for field in node.body
                                         if isinstance(field, ast.AnnAssign)]
            self.assertTrue(set(CONFIGURATIONS["full"]).issubset(schema["FrameRecord"]))
            schemas.append(schema)
        self.assertTrue(all(schema == schemas[0] for schema in schemas))


if __name__ == "__main__":
    unittest.main()
