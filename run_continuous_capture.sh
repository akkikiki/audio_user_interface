#!/bin/bash
# Continuous Screen Capture and Analysis Runner
# Captures and analyzes screen every 30 seconds

python capture_and_analyze.py \
  --continuous \
  --interval 30 \
  --prompt "Briefly describe the current screen activity" \
  --system "You are a screen monitoring assistant."
