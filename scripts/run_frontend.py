#!/usr/bin/env python3
"""
Frontend server startup script for the ECS chatbot.
Starts the Streamlit frontend.

Usage:
    .venv/bin/python scripts/run_frontend.py

Or with custom port:
    .venv/bin/python scripts/run_frontend.py --port 8502
"""

import subprocess
import sys
import os
import argparse

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main():
    parser = argparse.ArgumentParser(description="Start ECS chatbot frontend")
    parser.add_argument("--port", type=int, default=8501, help="Port to bind to")

    args = parser.parse_args()

    print("Starting ECS chatbot frontend")
    print(f"🔌 Port: {args.port}")
    print(f"📁 App: src/frontend/app.py")
    print()

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        project_root
        if not existing_pythonpath
        else os.pathsep.join([project_root, existing_pythonpath])
    )

    cmd = [
        sys.executable, "-m", "streamlit", "run", "src/frontend/app.py",
        "--server.port", str(args.port),
        "--server.address", "localhost"
    ]

    try:
        subprocess.run(cmd, cwd=project_root, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install with: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()
