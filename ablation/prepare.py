"""Prepare metadata variants for an external VLM runner."""

import argparse
import json
from pathlib import Path

from configurations import ACTIONS, CONFIGURATIONS, RUNS, read_jsonl, sample_key, select_metadata


def prepare(samples_path, output_dir):
    samples_path = Path(samples_path).resolve()
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise ValueError(f"Output directory already exists: {output_dir}. Use a new directory.")

    sources = {}
    source_sessions = {}
    session_sources = {}
    seen = set()
    samples = []
    for sample in read_jsonl(samples_path):
        key = sample_key(sample)
        if key in seen:
            raise ValueError(f"Duplicate sample: {key}")
        seen.add(key)
        if sample.get("action") not in ACTIONS:
            raise ValueError(f"Invalid expert action for {key}. Expected one of {ACTIONS}")
        if not isinstance(sample.get("metadata_path"), str) or not sample["metadata_path"]:
            raise ValueError(f"Missing metadata_path for {key}")

        metadata_path = (samples_path.parent / sample["metadata_path"]).resolve()
        session = key[:2]
        if session in session_sources and session_sources[session] != metadata_path:
            raise ValueError(f"Session {session} points to more than one metadata file")
        if metadata_path in source_sessions and source_sessions[metadata_path] != session:
            raise ValueError(f"Metadata file assigned to more than one session: {metadata_path}")
        session_sources[session] = metadata_path
        source_sessions[metadata_path] = session

        if metadata_path not in sources:
            frames = {}
            for record in read_jsonl(metadata_path):
                frame_id = record.get("frame_id")
                if type(frame_id) is not int or frame_id < 0:
                    raise ValueError(f"Invalid frame_id in {metadata_path}")
                if frame_id in frames:
                    raise ValueError(f"Duplicate frame {frame_id} in {metadata_path}")
                frames[frame_id] = record
            sources[metadata_path] = frames
        if key[2] not in sources[metadata_path]:
            raise ValueError(f"Frame {key[2]} not found in {metadata_path}")

        record = sources[metadata_path][key[2]]
        metadata = select_metadata(record, "full")
        json.dumps(metadata, allow_nan=False)
        if not isinstance(record.get("rgb_path"), str) or not record["rgb_path"]:
            raise ValueError(f"Missing rgb_path for {key}")
        image_path = (metadata_path.parent / record["rgb_path"]).resolve()
        if not image_path.is_file():
            raise ValueError(f"Missing RGB image for {key}: {image_path}")
        identity = dict(zip(("scenario_id", "session_id", "frame_id"), key))
        samples.append((identity, str(image_path), metadata, sample["action"]))

    # Keep labels separate from the inputs sent to the model.
    output_dir.mkdir(parents=True)
    with (output_dir / "inputs.jsonl").open("w") as inputs, (output_dir / "labels.jsonl").open("w") as labels:
        for identity, image_path, metadata, action in samples:
            labels.write(json.dumps({**identity, "action": action}) + "\n")
            for configuration in CONFIGURATIONS:
                selected = select_metadata(metadata, configuration)
                for run in RUNS:
                    task = {
                        **identity,
                        "configuration": configuration,
                        "run": run,
                        "image_path": image_path,
                        "metadata": selected,
                    }
                    inputs.write(json.dumps(task, allow_nan=False) + "\n")
    return len(samples)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("samples", type=Path, help="JSONL file listing the evaluated frames and expert actions")
    parser.add_argument("output", type=Path, help="New directory for inputs.jsonl and labels.jsonl")
    args = parser.parse_args()
    try:
        count = prepare(args.samples, args.output)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Error: {error}\n")
    print(f"Prepared {count} frames, {count * len(CONFIGURATIONS) * len(RUNS)} model inputs.")
    print(f"Saved inputs and separate labels to {args.output}")


if __name__ == "__main__":
    main()
