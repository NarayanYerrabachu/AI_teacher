#!/bin/bash

echo "🚀 Starting AI Teacher Backend..."
echo ""
echo "Backend will run on: http://localhost:8000"
echo "API Docs available at: http://localhost:8000/docs"
echo ""

cd /home/evocenta/PycharmProjects/AI_teacher

# Load environment variables from .env file
if [ -f .env ]; then
    set -a
    source <(grep -v '^#' .env | grep -v '^$' | sed 's/#.*//')
    set +a
fi

# Ensure OPENAI_API_BASE is unset (in case it was set elsewhere)
unset OPENAI_API_BASE

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY not found in .env file"
    exit 1
fi

pipenv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
