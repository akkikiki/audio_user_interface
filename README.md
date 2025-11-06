# audio_user_interface

## Demo

https://github.com/user-attachments/assets/7f51cdb4-adf5-4601-8207-45721efd5ad7

**Note:** Make sure to unmute the video to hear the audio!

## Summary

This project currently uses the default macOS text-to-speech (TTS) system for audio output via the `say` command.

## Setup Instructions

### Prerequisites
- Python 3.13 or later
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment:**

   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

   On Windows:
   ```bash
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   uv pip install -U mlx-vlm
   ```

   Or install from requirements.txt:
   ```bash
   uv pip install -r requirements.txt
   ```

### Running the Server

Before running any scripts, you must start the mlx_vlm server:

```bash
mlx_vlm.server
```

The server must be running for the capture and analysis scripts to work properly.

**Note:** If you need to download models from Hugging Face, you may need to authenticate first:

```bash
huggingface-cli login
```

This is required for downloading gated models or for accessing models that require authentication.

### Dependencies
This project uses MLX VLM (Vision Language Model) which includes:
- mlx (Apple silicon machine learning framework)
- mlx-lm (Language models for MLX)
- mlx-vlm (Vision-language models for MLX)
- transformers, tokenizers, and other supporting libraries

See `requirements.txt` for the complete list of dependencies.

### Voice Options

When using the `--speak` flag with `scripts/capture_and_analyze.py`, remember to use the Ryoko voice for better quality:

```bash
python scripts/capture_and_analyze.py --speak --voice "Ryoko"
```

Note: The `--voice` parameter works with macOS text-to-speech. Use `say -v ?` to list all available voices.
