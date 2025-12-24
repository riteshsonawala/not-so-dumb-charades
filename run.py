#!/usr/bin/env python3
"""
Run script for Not So Dumb Charades
Starts both FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import os
import signal
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
os.chdir(PROJECT_DIR)

processes = []


def signal_handler(sig, frame):
    print("\nShutting down...")
    for p in processes:
        p.terminate()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def main():
    print("Starting Not So Dumb Charades...")
    print("=" * 50)

    print("Starting FastAPI backend on http://localhost:8000")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=PROJECT_DIR
    )
    processes.append(api_process)

    time.sleep(2)

    print("Starting Streamlit frontend on http://localhost:8501")
    streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"],
        cwd=PROJECT_DIR
    )
    processes.append(streamlit_process)

    print("=" * 50)
    print("Both services are running!")
    print("API: http://localhost:8000 (Docs: http://localhost:8000/docs)")
    print("UI:  http://localhost:8501")
    print("Press Ctrl+C to stop both services")
    print("=" * 50)

    try:
        while True:
            if api_process.poll() is not None:
                print("API process stopped unexpectedly")
                break
            if streamlit_process.poll() is not None:
                print("Streamlit process stopped unexpectedly")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        signal_handler(None, None)


if __name__ == "__main__":
    main()