"""Metadata groups used in the leave-one-out experiment."""

import json
from pathlib import Path


CONFIGURATIONS = {
    "full": ("ego", "lane", "weather", "actors", "risk"),
    "without_ego": ("lane", "weather", "actors", "risk"),
    "without_lane": ("ego", "weather", "actors", "risk"),
    "without_weather": ("ego", "lane", "actors", "risk"),
    "without_actors_risk": ("ego", "lane", "weather"),
}
RUNS = (1, 2, 3)
ACTIONS = ("Brake", "Maintain Speed", "Accelerate", "Turn Left", "Turn Right")


def read_jsonl(path):
    records = []
    with Path(path).open() as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except ValueError as error:
                raise ValueError(f"{path}, line {line_number}: {error}") from error
            if not isinstance(record, dict):
                raise ValueError(f"{path}, line {line_number}: expected a JSON object")
            records.append(record)
    if not records:
        raise ValueError(f"No records found in {path}")
    return records


def sample_key(record):
    for field in ("scenario_id", "session_id"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError(f"Each record needs a nonempty {field}")
    if type(record.get("frame_id")) is not int or record["frame_id"] < 0:
        raise ValueError("Each record needs a nonnegative integer frame_id")
    return record["scenario_id"], record["session_id"], record["frame_id"]


def select_metadata(record, configuration):
    # Check the full record so every configuration uses the same valid samples.
    for group in CONFIGURATIONS["full"]:
        expected_type = list if group == "actors" else dict
        if not isinstance(record.get(group), expected_type):
            raise ValueError(f"Missing or invalid metadata group: {group}")
    return {group: record[group] for group in CONFIGURATIONS[configuration]}
