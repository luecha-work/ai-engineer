#!/bin/sh
set -e

ollama serve &
OLLAMA_PID=$!

# Wait briefly for the server to start
sleep 2

# Pull required models (no-op if already present)
ollama pull nomic-embed-text
ollama pull llama3:8b

wait $OLLAMA_PID
