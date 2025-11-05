#!/bin/bash
# Voice Input and Transcription Runner
# Records a single voice input and types out the transcription

python voice_input.py \
  --duration 5 \
  --type \
  --prompt "Transcribe the speech in this audio file. Only output the transcribed text, nothing else." \
  --system "You are a transcription assistant. Transcribe the audio accurately and output only the transcribed text."
