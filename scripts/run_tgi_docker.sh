#!/usr/bin/env bash
set -euo pipefail

MODEL_ID="${MODEL_ID:-openai/gpt-oss-20b}"
HF_TOKEN="${HF_TOKEN:-}"

ARGS=(docker run --rm -p 8080:80)
if [ -n "$HF_TOKEN" ]; then ARGS+=(-e "HF_TOKEN=$HF_TOKEN"); fi
ARGS+=(ghcr.io/huggingface/text-generation-inference:latest \
  --model "$MODEL_ID" \
  --max-input-length 65536 \
  --max-total-tokens 80000)

echo "Starting TGI with model: $MODEL_ID"
"${ARGS[@]}"
