#!/bin/bash
set -e

echo "Setting up Ollama and pulling required models..."

# Check if Ollama is running
if ! curl -s -f http://localhost:11434/api/tags > /dev/null; then
    echo "Error: Ollama is not running. Please start Ollama first."
    exit 1
fi

MODEL_NAME="qwen2.5:7b"

echo "Pulling model $MODEL_NAME (this may take a while)..."
curl -s -X POST http://localhost:11434/api/pull -d "{\"name\": \"$MODEL_NAME\"}"

echo "Verifying model $MODEL_NAME is available..."
if curl -s http://localhost:11434/api/tags | grep -q "$MODEL_NAME"; then
    echo "Success: Model $MODEL_NAME is ready to use!"
else
    echo "Error: Failed to pull model $MODEL_NAME."
    exit 1
fi
