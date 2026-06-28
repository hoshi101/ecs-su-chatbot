#!/usr/bin/env python3
"""
Backend server startup script for the ECS chatbot.
Starts the FastAPI backend server.

Usage:
    .venv/bin/python scripts/run_backend.py

Or with custom host/port:
    .venv/bin/python scripts/run_backend.py --host 0.0.0.0 --port 8001
"""

import uvicorn
import sys
import os
import argparse

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main():
    parser = argparse.ArgumentParser(description="Start ECS chatbot backend")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()

    print("Starting ECS chatbot backend")
    print(f"📍 Host: {args.host}")
    print(f"🔌 Port: {args.port}")
    print(f"🔄 Reload: {args.reload}")
    print()

    uvicorn.run(
        "src.backend.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()
