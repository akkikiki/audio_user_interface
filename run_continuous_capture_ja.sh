run_continuous_capture_ja.sh#!/bin/bash
# Continuous Screen Capture and Analysis Runner
# Captures and analyzes screen every 30 seconds

python capture_and_analyze.py \
  --continuous \
  --no-stream \
  --keep-screenshot \
  --interval 30 \
  --speak \
  --voice "Kyoko" \
  --model "mlx-community/gemma-3n-E2B-it-8bit" \
  --prompt "現在の画面のアクティビティを簡潔に説明してください。100語以内でお願いします" \
  --system "あなたは画面監視アシスタントです。"
#  --prompt "Briefly describe the current screen activity. Please keep it under 100 words" \
