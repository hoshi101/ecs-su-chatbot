#!/usr/bin/env python3
"""
Frontend Server Startup Script for FSS Hero Chatbot
Starts the Streamlit frontend using the new restructured code.

Usage:
    python scripts/run_frontend.py

Or with custom port:
    python scripts/run_frontend.py --port 8502
"""

import subprocess
import sys
import os
import argparse

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main():
    parser = argparse.ArgumentParser(description="Start FSS Hero Chatbot Frontend")
    parser.add_argument("--port", type=int, default=8501, help="Port to bind to")

    args = parser.parse_args()

    print("🎨 Starting FSS Hero Chatbot Frontend (Restructured)")
    print(f"🔌 Port: {args.port}")
    print(f"📁 App: src/frontend/app.py")
    print()

    # Change to the frontend directory to ensure relative imports work
    frontend_dir = os.path.join(project_root, "src", "frontend")

    cmd = [
        "streamlit", "run", "app.py",
        "--server.port", str(args.port),
        "--server.address", "localhost"
    ]

    try:
        subprocess.run(cmd, cwd=frontend_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start frontend: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install with: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()