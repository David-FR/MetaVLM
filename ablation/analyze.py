"""Score predictions from the external VLM runner."""

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

from configurations import ACTIONS, CONFIGURATIONS, RUNS, read_jsonl, sample_key


def accuracy(outcomes, average):
    if average == "frame":
        return 100 * mean(outcomes.values())
    sessions = defaultdict(list)
    for key, correct in outcomes.items():
        sessions[key[:2]].append(correct)
    if average == "session":
        return 100 * mean(mean(values) for values in sessions.values())
    scenarios = defaultdict(list)
    for (scenario, session), values in sessions.items():
        scenarios[scenario].append(mean(values))
    return 100 * mean(mean(values) for values in scenarios.values())


def analyze(labels_path, predictions_path, average="session"):
    if average not in ("frame", "session", "scenario"):
        raise ValueError(f"Unknown averaging method: {average}")
    labels = {}
    for record in read_jsonl(labels_path):
        key = sample_key(record)
        if key in labels:
            raise ValueError(f"Duplicate label: {key}")
        if record.get("action") not in ACTIONS:
            raise ValueError(f"Invalid expert action for {key}")
        labels[key] = record["action"]

    outcomes = {(config, run): {} for config in CONFIGURATIONS for run in RUNS}
    invalid = defaultdict(int)
    for record in read_jsonl(predictions_path):
        key = sample_key(record)
        config, run = record.get("configuration"), record.get("run")
        if not isinstance(config, str) or config not in CONFIGURATIONS:
            raise ValueError(f"Unknown configuration for {key}: {config}")
        if type(run) is not int or run not in RUNS:
            raise ValueError(f"Invalid run for {key}: {run}. Expected 1, 2, or 3.")
        if key not in labels:
            raise ValueError(f"Prediction has no matching label: {key}")
        if key in outcomes[config, run]:
            raise ValueError(f"Duplicate prediction: {key}, {config}, run {run}")
        if "action" not in record:
            raise ValueError(f"Missing action for {key}. Use null for an invalid model response.")
        action = record["action"]
        if action not in ACTIONS:
            invalid[config] += 1
        outcomes[config, run][key] = action == labels[key]

    missing = []
    for (config, run), values in outcomes.items():
        count = len(labels) - len(values)
        if count:
            missing.append(f"{config}, run {run}: {count} missing")
    if missing:
        raise ValueError("Incomplete predictions; no scores produced. " + "; ".join(missing))

    scores = {pair: accuracy(values, average) for pair, values in outcomes.items()}
    rows = []
    for config in CONFIGURATIONS:
        values = [scores[config, run] for run in RUNS]
        differences = [scores["full", run] - scores[config, run] for run in RUNS]
        rows.append({
            "configuration": config,
            "average": average,
            "frames_per_run": len(labels),
            "runs": len(RUNS),
            **{f"accuracy_run_{run}_pct": scores[config, run] for run in RUNS},
            "accuracy_mean_pct": mean(values),
            "accuracy_sd_pp": stdev(values),
            "full_minus_ablated_mean_pp": mean(differences),
            "full_minus_ablated_sd_pp": stdev(differences),
            "invalid_responses": invalid[config],
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("labels", type=Path)
    parser.add_argument("predictions", type=Path)
    parser.add_argument("output", type=Path, help="New CSV file for results")
    parser.add_argument("--average", choices=("frame", "session", "scenario"), default="session")
    args = parser.parse_args()
    try:
        rows = analyze(args.labels, args.predictions, args.average)
        with args.output.open("x", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Error: {error}\n")
    for row in rows:
        print(f"{row['configuration']}: {row['accuracy_mean_pct']:.2f}% accuracy, "
              f"{row['full_minus_ablated_mean_pp']:+.2f} pp Full minus ablated, "
              f"{row['invalid_responses']} invalid responses")
    print(f"Saved results to {args.output} (averaging: {args.average})")


if __name__ == "__main__":
    main()
