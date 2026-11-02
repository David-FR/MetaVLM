# Leave-one-out metadata ablation

These scripts prepare inputs and score VLM predictions for the leave-one-out
metadata experiment. They do not load models or run inference. They use
Python 3.9 or later and only the standard library.

All 20 scenario scripts save the same metadata structure. The tools read their
existing `metadata.jsonl` files and RGB images without changing them.

Starting with expert action labels, the workflow is:

1. Generate RGB frames and metadata with the CARLA scenario scripts, or use existing recordings.
2. Match the expert labels to the selected frames.
3. Prepare the five metadata configurations.
4. Run the VLM model(s) externally for three runs per configuration.
5. Analyze the saved predictions.

## 1. Generate or locate recordings

Run the desired scenario script using the CARLA setup described in the
[repository README](../README.md#simulation-scripts). Each recording produces a
session folder containing RGB frames and `metadata.jsonl`, for example:

```text
sessions/recording_01/
├── frames/
│   ├── 00000481.png
│   └── ...
└── metadata.jsonl
```

Use the metadata file to identify the recorded frames. Match each selected
frame to its expert action label before adding it to `samples.jsonl`. For new
recordings, verify label alignment using the scenario timing or annotated
event; CARLA frame IDs may differ between recordings.

## 2. List the evaluated frames

Create `samples.jsonl` with one line per evaluated frame. For the paper's
evaluation, use the original selected frames and expert labels. For a new
evaluation, use the newly recorded frames and their matched expert labels.
In either case, all five configurations must use exactly the same samples.
For example, one line could be:

```json
{"scenario_id":"01_VID_FTSA","session_id":"clear_noon","metadata_path":"sessions/recording_01/metadata.jsonl","frame_id":481,"action":"Brake"}
```

This is a format example, not an actual annotation. Replace the path, frame ID,
session ID, and action with your data.

- `scenario_id` identifies the base scenario.
- `session_id` identifies a recording within that scenario. Different weather
  or lighting recordings must have different session IDs.
- `metadata_path` is absolute or relative to `samples.jsonl`.
- `frame_id` is the CARLA frame ID stored in the metadata, not a line number.
- `action` is the expert label: `Brake`, `Maintain Speed`, `Accelerate`,
  `Turn Left`, or `Turn Right`.

The scenario, session, and frame ID together identify a sample. Each session
must map to one metadata file, and each metadata file to one session.
There is no automatic frame selection or label generation.

## 3. Prepare the inputs

Run from the repository root:

```bash
python3 ablation/prepare.py /path/to/samples.jsonl /path/to/prepared
```

Use a new output directory. The script checks the selected frames, image paths,
metadata groups, and labels before writing:

- `inputs.jsonl`: five configurations and three run IDs for each frame.
- `labels.jsonl`: expert labels, stored separately for scoring.

| Configuration | Metadata groups |
|---|---|
| `full` | ego, lane, weather, actors, risk |
| `without_ego` | lane, weather, actors, risk |
| `without_lane` | ego, weather, actors, risk |
| `without_weather` | ego, lane, actors, risk |
| `without_actors_risk` | ego, lane, weather |

Each input contains `scenario_id`, `session_id`, `frame_id`, `configuration`,
`run`, `image_path`, and `metadata`. Image paths are absolute. Prepare the inputs
on the inference machine, or update image paths when transferring recordings.

The same image and retained metadata values are used in every configuration.
Removed groups are omitted, not replaced with zeros or missing-value text.
Missing values already present inside retained groups remain unchanged.
Segmentation, depth, and expert labels are not included in the inputs.

## 4. Run the VLM model(s) externally

Your inference code should read `inputs.jsonl`, use `image_path` to load the RGB
image, and pass only `metadata` to your metadata formatter. For each model,
keep the prompt instructions, field formatting, retained field order, model
checkpoint, and generation settings fixed across configurations. To reproduce
the paper's evaluation, use the original formatter and settings. Omit removed
groups from the context line; do not let the formatter fill them back in.

The configuration, run, and sample IDs are tracking fields. Do not include them
in the model prompt. Do not pass `labels.jsonl` to the model.

Run IDs 1, 2, and 3 request separate generations. They do not set a random seed
or execute inference. Record the settings and seeds in your external runner;
use the original three-run settings when reproducing the paper's evaluation.
Do not copy one prediction into all three runs.

Write one line per input to `predictions.jsonl`:

```json
{"scenario_id":"01_VID_FTSA","session_id":"clear_noon","frame_id":481,"configuration":"without_weather","run":1,"action":"Brake"}
```

Use the five action names listed above. If a model response cannot be parsed,
write `"action": null`. You can also save extra fields such as `raw_response`;
the analysis script ignores them. Failed inference calls should be retried,
not recorded as model decisions.

For multiple models, use the same prepared samples and save a separate
predictions file for each model. Do not combine predictions from different
models in one file.

## 5. Score the predictions

```bash
python3 ablation/analyze.py /path/to/prepared/labels.jsonl /path/to/predictions.jsonl /path/to/results.csv
```

Run this command separately for each model, using that model's predictions file
and a different output CSV file.

The script rejects duplicate, unexpected, or missing predictions. Every
configuration and run must cover exactly the same labeled frames. Invalid
actions count as incorrect and are also counted separately; they are not
dropped from the denominator.

By default, accuracy is calculated within each session and then averaged equally
across sessions. Use the same averaging rule for Full and all ablations:

- `--average session`: each recording has equal weight (default).
- `--average frame`: each evaluated frame has equal weight.
- `--average scenario`: average frames within sessions, sessions within base
  scenarios, then give each base scenario equal weight.

The CSV includes each run's accuracy, mean accuracy, sample standard deviation
across the three runs, and the mean and standard deviation of paired
`Full − ablated` differences. Differences are in percentage points. A positive
difference means removing the group hurts accuracy. Invalid-response counts
cover all three runs. Existing result files are not overwritten.

Run-to-run standard deviation does not measure uncertainty across base
scenarios. These scripts do not yet perform the separate weather comparison or
calculate confidence intervals across scenarios.

## Interpretation

Each result measures the effect of removing a metadata group while retaining
the others. Groups share information: for example, removing ego fields leaves
headway and relative speed available. These are conditional group effects,
not independent effects of every underlying signal.

## Checks

```bash
python3 -m unittest discover -s ablation -p 'test_*.py'
```

The checks run without CARLA, a VLM, or the original evaluation data.
