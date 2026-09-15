# Diagnostic scripts

These are manual diagnostics for the Mexico City flood-risk prototype. They print
predictions and comparisons but contain no assertions or explicit failure exits
for incorrect results. They are not an automated regression-test suite.

| Script | What it exercises |
| --- | --- |
| `test_fix.py` | Calls the actual `realtime.predict_alert_for_coordinates` function and prints whether a known dataset coordinate returns score 39.2 |
| `test_specific_coordinates.py` | Tests the currently configured point `(19.526544451, -99.165879364)` with all four sensor levels and compares dataset/model scores |
| `test_correction.py` | Prints several correction scenarios, including a low-risk point and coordinates outside Mexico City |

The two scripts in this directory implement their own copies of inference/alert
rules. They do not exercise the current dataset-first production inference path.
The coordinate description and machine-specific command inside the first script's
original docstring are stale; the table above describes the executed values.
Consolidating these scripts is separate from the formatting/configuration cleanup.

## Run locally

Install the Python 3.11 dependencies using the [main setup guide](../README.md).
From the repository root, with the virtual environment activated:

```bash
python tests/test_fix.py
python tests/test_specific_coordinates.py
# This script resolves the model relative to the working directory.
cd src
python ../tests/test_correction.py
```

On Windows, set `$env:PYTHONUTF8 = "1"` if your terminal cannot print the scripts'
Unicode output. If GNU Make is available, `make test` runs the same three scripts
from the repository root and sets UTF-8 mode.

## CI and interpretation

GitHub Actions runs Ruff lint/format checks and these scripts as **smoke checks**.
An import error, missing model, or uncaught exception fails the workflow. A printed
success message or zero exit status does not verify the prediction or business
rules. Review the printed results; an assertion-based suite remains future work.

The scripts load the existing model and dataset. They do not require ESP32 hardware,
start the server, or retrain the model.
