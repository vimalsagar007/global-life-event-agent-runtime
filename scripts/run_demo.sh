#!/bin/bash
# Global Life Event AI Orchestrator - Local Launch Script

echo "============================================================"
echo "🌍 Launching Global Life Event AI Orchestrator (Local Mode)"
echo "============================================================"

export USE_MOCK_TOOLS=true
export USE_MOCK_A2A=true
export USE_VERTEX_AI=false
export USE_SEARCH_GROUNDING=false
export PORT=8000

python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
