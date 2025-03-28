#!/bin/bash
set -e

echo "==== STARTING DEBUG AND SETUP PROCESS ===="

# Run debug script to diagnose and fix issues
python debug_setup.py

# Check if ANTHROPIC_API_KEY is set
if [ -z "${ANTHROPIC_API_KEY}" ]; then
    echo "WARNING: ANTHROPIC_API_KEY environment variable is not set."
    echo "The review generation features will not work without a valid API key."
    echo "Please set this in your Huggingface Space settings."
fi

# Start the API server
echo "==== STARTING API SERVER ===="
exec uvicorn app:app --host 0.0.0.0 --port 7860