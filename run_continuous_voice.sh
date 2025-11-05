#!/bin/bash
# Continuous Voice Input Runner
# Records and types out transcriptions continuously

python voice_input.py \
  --continuous \
  --duration 5 \
  --interval 10 \
  --type \
  --keep-recording \
  --prompt "Transcribe what is said this audio file. Only output the transcribed text, nothing else." \
  --system "You are a transcription assistant. Transcribe the audio accurately and output only the transcribed text."
