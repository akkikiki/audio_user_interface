#!/usr/bin/env python3
"""
Screenshot Capture and Analysis Script
Captures a screenshot and sends it to a local VL model endpoint for analysis.
"""

import requests
import json
import sys
import os
import time
import subprocess
import platform
from datetime import datetime
from PIL import ImageGrab
import argparse


def capture_screenshot(output_path=None):
    """
    Capture a screenshot of the entire screen.

    Args:
        output_path: Path to save the screenshot. If None, generates a timestamped filename.

    Returns:
        str: Path to the saved screenshot
    """
    if output_path is None:
        # Create screenshots directory if it doesn't exist
        screenshots_dir = "screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(screenshots_dir, f"screenshot_{timestamp}.png")

    print(f"Capturing screenshot...")

    # Use native screenshot tool based on platform
    if platform.system() == "Darwin":  # macOS
        # Use macOS native screencapture command for better compatibility
        try:
            subprocess.run(['screencapture', '-x', output_path], check=True)
            print(f"Screenshot saved to: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error capturing screenshot with screencapture: {e}", file=sys.stderr)
            print("Falling back to PIL ImageGrab...", file=sys.stderr)
            screenshot = ImageGrab.grab()
            screenshot.save(output_path)
            print(f"Screenshot saved to: {output_path}")
    else:
        # Use PIL for other platforms (Windows, Linux)
        screenshot = ImageGrab.grab()
        screenshot.save(output_path)
        print(f"Screenshot saved to: {output_path}")

    return output_path


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


def send_to_endpoint(image_path, prompt, model="mlx-community/gemma-3n-E2B-it-4bit",
                    endpoint="http://localhost:8000/generate", system_prompt=None,
                    stream=True, max_tokens=1000):
    """
    Send the image to the local endpoint for analysis.

    Args:
        image_path: Path to the image file
        prompt: The prompt to send with the image
        model: Model name to use
        endpoint: API endpoint URL
        system_prompt: System prompt for the model
        stream: Whether to stream the response
        max_tokens: Maximum tokens in response

    Returns:
        tuple: (response, response_text) - Response object and extracted text
    """
    # Get absolute path
    abs_image_path = os.path.abspath(image_path)

    payload = {
        "model": model,
        "image": [abs_image_path],
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
                    print(decoded_line)
                    # Collect the text for TTS
                    response_text += decoded_line + " "
            print("-" * 80)
        else:
            print("Response:")
            print("-" * 80)
            response_json = response.json()
            print(json.dumps(response_json, indent=2))
            print("-" * 80)
            # Extract text from JSON response (adjust key based on your API's response format)
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
        description="Capture screenshot and send to VL model endpoint for analysis"
    )
    parser.add_argument(
        "--prompt", "-p",
        default="Please analyze this screenshot and describe what you see.",
        help="Prompt to send with the image"
    )
    parser.add_argument(
        "--system", "-s",
        default="You are a helpful assistant.",
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
        help="Output path for screenshot (default: screenshot_TIMESTAMP.png)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=1000,
        help="Maximum tokens in response"
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming response"
    )
    parser.add_argument(
        "--keep-screenshot",
        action="store_true",
        help="Keep the screenshot file after sending (default: delete)"
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run continuously, capturing every 30 seconds"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Interval in seconds between captures in continuous mode (default: 30)"
    )
    parser.add_argument(
        "--speak",
        action="store_true",
        help="Read the response aloud using text-to-speech (macOS only)"
    )

    args = parser.parse_args()

    if args.continuous:
        print(f"Starting continuous mode - capturing every {args.interval} seconds")
        print("Press Ctrl+C to stop\n")

        iteration = 0
        try:
            while True:
                iteration += 1
                print(f"\n{'='*80}")
                print(f"Capture #{iteration} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*80}\n")

                screenshot_path = capture_screenshot(args.output)

                try:
                    response, response_text = send_to_endpoint(
                        image_path=screenshot_path,
                        prompt=args.prompt,
                        model=args.model,
                        endpoint=args.endpoint,
                        system_prompt=args.system,
                        stream=not args.no_stream,
                        max_tokens=args.max_tokens
                    )

                    # Speak the response if requested
                    if args.speak and response_text:
                        text_to_speech(response_text)
                finally:
                    # Clean up screenshot unless user wants to keep it
                    if not args.keep_screenshot and not args.output:
                        if os.path.exists(screenshot_path):
                            os.remove(screenshot_path)

                print(f"\nWaiting {args.interval} seconds until next capture...")
                time.sleep(args.interval)

        except KeyboardInterrupt:
            print("\n\nStopping continuous capture. Goodbye!")
            sys.exit(0)
    else:
        # Single capture mode
        screenshot_path = capture_screenshot(args.output)

        try:
            response, response_text = send_to_endpoint(
                image_path=screenshot_path,
                prompt=args.prompt,
                model=args.model,
                endpoint=args.endpoint,
                system_prompt=args.system,
                stream=not args.no_stream,
                max_tokens=args.max_tokens
            )

            # Speak the response if requested
            if args.speak and response_text:
                text_to_speech(response_text)
        finally:
            # Clean up screenshot unless user wants to keep it
            if not args.keep_screenshot and not args.output:
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
                    print(f"\nCleaned up screenshot: {screenshot_path}")


if __name__ == "__main__":
    main()
