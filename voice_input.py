#!/usr/bin/env python3
"""
Voice Input and Transcription Script
Records voice input and sends it to a local audio model endpoint for transcription.
"""

import requests
import json
import sys
import os
import time
import subprocess
import platform
from datetime import datetime
import argparse
import sounddevice as sd
import soundfile as sf
import numpy as np
import pyautogui


def record_audio(duration=5, sample_rate=16000, output_path=None):
    """
    Record audio from the microphone.

    Args:
        duration: Recording duration in seconds
        sample_rate: Sample rate for recording (default: 16000 Hz)
        output_path: Path to save the audio. If None, generates a timestamped filename.

    Returns:
        str: Path to the saved audio file
    """
    if output_path is None:
        # Create audio directory if it doesn't exist
        audio_dir = "audio_recordings"
        os.makedirs(audio_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(audio_dir, f"recording_{timestamp}.wav")

    print(f"Recording for {duration} seconds...")
    print("Speak now!")

    try:
        # Record audio
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()  # Wait until recording is finished

        # Save as WAV file
        sf.write(output_path, audio_data, sample_rate)
        print(f"Recording saved to: {output_path}")

        return output_path

    except Exception as e:
        print(f"Error recording audio: {e}", file=sys.stderr)
        sys.exit(1)


def text_to_speech(text):
    """
    Convert text to speech using macOS 'say' command.

    Args:
        text: Text to speak
    """
    if not text or not text.strip():
        return

    print("\nSpeaking response...")
    try:
        # Use macOS say command
        subprocess.run(['say', text], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error with text-to-speech: {e}", file=sys.stderr)
    except FileNotFoundError:
        print("Error: 'say' command not found. Text-to-speech is only available on macOS.", file=sys.stderr)


def type_text(text, delay=3):
    """
    Type out text using keyboard simulation.

    Args:
        text: Text to type
        delay: Delay in seconds before typing starts (to allow switching windows)
    """
    if not text or not text.strip():
        return

    print(f"\nTyping text in {delay} seconds... Switch to your target window!")
    time.sleep(delay)

    try:
        # Type the text with a small interval between keypresses for more natural typing
        pyautogui.write(text, interval=0.05)
        print("Done typing!")
    except Exception as e:
        print(f"Error typing text: {e}", file=sys.stderr)


def send_to_endpoint(audio_path, prompt, model="mlx-community/gemma-3n-E2B-it-4bit",
                    endpoint="http://localhost:8000/generate", system_prompt=None,
                    stream=True, max_tokens=500):
    """
    Send the audio to the local endpoint for analysis.

    Args:
        audio_path: Path to the audio file
        prompt: The prompt to send with the audio
        model: Model name to use
        endpoint: API endpoint URL
        system_prompt: System prompt for the model
        stream: Whether to stream the response
        max_tokens: Maximum tokens in response

    Returns:
        tuple: (response, response_text) - Response object and extracted text
    """
    # Get absolute path
    abs_audio_path = os.path.abspath(audio_path)

    payload = {
        "model": model,
        "audio": [abs_audio_path],
        "prompt": prompt,
        "stream": stream,
        "max_tokens": max_tokens
    }

    if system_prompt:
        payload["system"] = system_prompt

    headers = {
        "Content-Type": "application/json"
    }

    print(f"\nSending request to {endpoint}...")
    print(f"Prompt: {prompt}\n")

    try:
        response = requests.post(endpoint, headers=headers, json=payload, stream=stream)
        response.raise_for_status()

        response_text = ""

        if stream:
            print("Response (streaming):")
            print("-" * 80)
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    # Parse SSE format (data: {...})
                    if decoded_line.startswith('data: '):
                        try:
                            json_data = json.loads(decoded_line[6:])  # Skip 'data: ' prefix
                            print(json_data)
                            chunk = json_data.get('chunk', '')
                            if chunk:
                                print(chunk, end='', flush=True)
                                response_text += chunk
                        except json.JSONDecodeError:
                            # If not valid JSON, just print the line
                            print(decoded_line)
                            response_text += decoded_line + " "
                    else:
                        print(decoded_line)
                        response_text += decoded_line + " "
            print("\n" + "-" * 80)
        else:
            print("Response:")
            print("-" * 80)
            response_json = response.json()
            print(json.dumps(response_json, indent=2))
            print("-" * 80)
            # Extract text from JSON response
            if isinstance(response_json, dict):
                response_text = response_json.get('text', response_json.get('response', str(response_json)))
            else:
                response_text = str(response_json)

        return response, response_text.strip()

    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to connect to endpoint: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Record voice input and send to audio model endpoint for transcription"
    )
    parser.add_argument(
        "--prompt", "-p",
        default="Transcribe the speech in this audio file. Only output the transcribed text, nothing else.",
        help="Prompt to send with the audio"
    )
    parser.add_argument(
        "--system", "-s",
        default="You are a transcription assistant. Transcribe the audio accurately and output only the transcribed text.",
        help="System prompt for the model"
    )
    parser.add_argument(
        "--model", "-m",
        default="mlx-community/gemma-3n-E2B-it-4bit",
        help="Model name to use"
    )
    parser.add_argument(
        "--endpoint", "-e",
        default="http://localhost:8000/generate",
        help="API endpoint URL"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output path for audio recording (default: recording_TIMESTAMP.wav)"
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=5,
        help="Recording duration in seconds (default: 5)"
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=16000,
        help="Sample rate for recording in Hz (default: 16000)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=500,
        help="Maximum tokens in response"
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming response"
    )
    parser.add_argument(
        "--keep-recording",
        action="store_true",
        help="Keep the audio file after sending (default: delete)"
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run continuously, recording and analyzing"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Interval in seconds between recordings in continuous mode (default: 10)"
    )
    parser.add_argument(
        "--speak",
        action="store_true",
        help="Read the response aloud using text-to-speech (macOS only)"
    )
    parser.add_argument(
        "--type",
        action="store_true",
        help="Type out the transcribed text using keyboard simulation"
    )
    parser.add_argument(
        "--type-delay",
        type=int,
        default=3,
        help="Delay in seconds before typing starts (default: 3)"
    )
    parser.add_argument(
        "--audio-file",
        help="Use an existing audio file instead of recording (skips recording)"
    )

    args = parser.parse_args()

    if args.continuous:
        print(f"Starting continuous mode - recording every {args.interval} seconds")
        print("Press Ctrl+C to stop\n")

        iteration = 0
        try:
            while True:
                iteration += 1
                print(f"\n{'='*80}")
                print(f"Recording #{iteration} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*80}\n")

                audio_path = record_audio(
                    duration=args.duration,
                    sample_rate=args.sample_rate,
                    output_path=args.output
                )

                try:
                    response, response_text = send_to_endpoint(
                        audio_path=audio_path,
                        prompt=args.prompt,
                        model=args.model,
                        endpoint=args.endpoint,
                        system_prompt=args.system,
                        stream=not args.no_stream,
                        max_tokens=args.max_tokens
                    )

                    # Type or speak the response if requested
                    if args.type and response_text:
                        type_text(response_text, delay=args.type_delay)
                    elif args.speak and response_text:
                        text_to_speech(response_text)
                finally:
                    # Clean up audio unless user wants to keep it
                    if not args.keep_recording and not args.output:
                        if os.path.exists(audio_path):
                            os.remove(audio_path)

                print(f"\nWaiting {args.interval} seconds until next recording...")
                time.sleep(args.interval)

        except KeyboardInterrupt:
            print("\n\nStopping continuous recording. Goodbye!")
            sys.exit(0)
    else:
        # Single recording mode
        if args.audio_file:
            # Use existing audio file
            if not os.path.exists(args.audio_file):
                print(f"Error: Audio file not found: {args.audio_file}", file=sys.stderr)
                sys.exit(1)
            audio_path = args.audio_file
            print(f"Using existing audio file: {audio_path}")
        else:
            # Record new audio
            audio_path = record_audio(
                duration=args.duration,
                sample_rate=args.sample_rate,
                output_path=args.output
            )

        try:
            response, response_text = send_to_endpoint(
                audio_path=audio_path,
                prompt=args.prompt,
                model=args.model,
                endpoint=args.endpoint,
                system_prompt=args.system,
                stream=not args.no_stream,
                max_tokens=args.max_tokens
            )

            # Type or speak the response if requested
            if args.type and response_text:
                type_text(response_text, delay=args.type_delay)
            elif args.speak and response_text:
                text_to_speech(response_text)
        finally:
            # Clean up audio unless user wants to keep it or used existing file
            if not args.audio_file and not args.keep_recording and not args.output:
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    print(f"\nCleaned up recording: {audio_path}")


if __name__ == "__main__":
    main()
