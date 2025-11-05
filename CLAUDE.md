# Claude Commands

## Screen Capture and Voice Analysis

Capture a screenshot, analyze it with VL model, and speak the description:

```bash
python scripts/capture_and_analyze.py \
  --no-stream \
  --keep-screenshot \
  --speak \
  --prompt "Briefly describe the current screen activity. Please keep it under 100 words" \
  --system "You are a screen monitoring assistant."
```

This command will:
- Capture a screenshot and save it to the `screenshots/` directory
- Send it to the local VL model endpoint for analysis
- Speak the response using macOS text-to-speech
- Keep the screenshot file (instead of deleting it)
