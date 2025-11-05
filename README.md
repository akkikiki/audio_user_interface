# audio_user_interface

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

### Dependencies
This project uses MLX VLM (Vision Language Model) which includes:
- mlx (Apple silicon machine learning framework)
- mlx-lm (Language models for MLX)
- mlx-vlm (Vision-language models for MLX)
- transformers, tokenizers, and other supporting libraries

See `requirements.txt` for the complete list of dependencies.