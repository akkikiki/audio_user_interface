#!/bin/bash
# Continuous Screen Capture and Analysis Runner
# Captures and analyzes screen every 30 seconds

SCRIPT_DIR="$(dirname "$0")"
python "$SCRIPT_DIR/capture_and_analyze.py" \
  --no-stream \
  --keep-screenshot \
  --speak \
  --prompt "Briefly describe the current screen activity. Please keep it under 100 words" \
  --system "You are a screen monitoring assistant."
