#!/bin/sh
set -e

: "${OLLAMA_MODEL:=qwen3}"
: "${OLLAMA_EMBED_MODEL:=qwen3-embedding}"

ollama serve &
OLLAMA_PID=$!

# Wait for the server to be ready
i=0
while [ $i -lt 30 ]; do
  if ollama list >/dev/null 2>&1; then
    break
  fi
  i=$((i + 1))
  sleep 1
done

# Pull required models (no-op if already present)
ollama pull "$OLLAMA_EMBED_MODEL"
ollama pull "$OLLAMA_MODEL"

touch /tmp/ollama.ready

wait $OLLAMA_PID
