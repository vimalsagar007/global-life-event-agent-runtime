# Global Life Event AI Orchestrator (Agent Runtime Edition)

Tagline: **"One life event. Every task. Any country. One intelligent plan."**

Deployable on **Vertex AI Agent Runtime** (Agent Engine / Reasoning Engines).

---

## 🚀 Key Features

1. **Zero-Hardcode Dynamic Geocoding**: Powered by OpenStreetMap Nominatim API + ISO-3166 alpha-2 metadata table (currency, language, timezone, measurement system).
2. **10 Specialist Multi-Agent Engine**: Government, Immigration, Housing, Education, Finance, Healthcare, Transportation, Pet Relocation, Cross-Border, and Compliance.
3. **Vertex AI Agent Runtime Integration**: Managed sessions, Gemini Enterprise Agent Registry support, and Agent Gateway security boundaries.
4. **Model Context Protocol (MCP)**: Tools classified as `READ_ONLY` vs `ACTION` with human approval gating.
5. **A2A Inter-Agent Messaging**: Standard `/api/v1/a2a/agents` card discovery and inter-agent task dispatching.

---

## 🛠️ Quickstart & Local Development

### 1. Run Unit Tests
```bash
python3 scripts/run_tests.py
```

### 2. Run Application Locally
```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### 3. Deploy to Vertex AI Agent Runtime
```bash
agents-cli deploy \
  --project qwiklabs-gcp-01-a2104073e565 \
  --region us-central1 \
  --deployment-target agent_runtime \
  --service-name global-life-event-agent-runtime
```

---

## 🧪 Testing Prompts

Example: Moving from Bangalore to Hyderabad with family:
```json
{
  "raw_input": "Moving from Bangalore to Hyderabad with me, wife and 2 children"
}
```

- **Origin**: `India / Karnataka / Bangalore` (Currency: `INR`)
- **Destination**: `India / Telangana / Hyderabad` (Currency: `INR`)
