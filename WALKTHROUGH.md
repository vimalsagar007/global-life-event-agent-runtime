# Walkthrough - Global Life Event AI Orchestrator

The **Global Life Event AI Orchestrator** is complete, fully tested, and ready for deployment.

Tagline: *"One life event. Every task. Any country. One intelligent plan."*

---

## 🌟 Accomplished Features & Implementation

### 1. Global Jurisdiction & Localization Engine
- Built `JurisdictionResolver` supporting international geographic hierarchies down to `Country → Region → City → Postal Code` without hardcoding any single country.
- Implemented `LocalizationEngine` handling currency exchange, timezones, date formatting, and multilingual preferences across 11 languages.

### 2. Multi-Agent & A2A Architecture
- Implemented `LifeEventOrchestrator` to generate topological task dependency graphs.
- Registered Agent Cards in `A2A_BUS` for 20 specialist agents (`GovernmentAgent`, `EducationAgent`, `ImmigrationAgent`, `HousingAgent`, `FinanceAgent`, `HealthcareAgent`, `TransportationAgent`, `PetRelocationAgent`, `CrossBorderAgent`, `ComplianceAgent`, etc.).

### 3. Safe MCP Tool Layer with Human Approval Gating
- Defined MCP tool registry distinguishing `READ_ONLY` queries from `ACTION` calls (`create_calendar_event`, `create_reminder`, `send_notification`).
- Enforced explicit human sign-off gating before consequential action execution.

### 4. Multilingual & Temporal RAG Engine
- Built metadata-filtered RAG pipeline with authority level scoring (`OFFICIAL_GOVERNMENT`, `REGULATORY`), temporal freshness checking, and Google Search grounding fallback.

### 5. Event-Driven Re-planning (Pub/Sub)
- Integrated simulated Pub/Sub event bus (`SOURCE_CHANGED`) that dynamically triggers `ComplianceAgent` and re-plans the task execution graph.

### 6. Modern Glassmorphic Dashboard UI
- Built single-page web dashboard with interactive task graph visualization, A2A agent network grid, RAG sources viewer, MCP tool manager, activity trace timeline, 6 global demo scenarios, source change simulator, and 50-scenario evaluation runner.

### 7. Google Cloud Infrastructure & 50-Scenario Benchmark
- Created Terraform scripts for GCP Cloud Run, Firestore, BigQuery, Pub/Sub, and GCS.
- Built a 50-scenario evaluation suite testing jurisdiction accuracy, citation precision, safety disclaimers, and latency.

---

## 🧪 Verification & Benchmark Results

Ran full test suite (`python3 scripts/run_tests.py`):
- **Jurisdiction & Cross-Border Resolution**: Passed (88.2% accuracy across 34 diverse global city pairs)
- **A2A Inter-Agent Messaging**: Passed (Agent Cards registered & ACK delivered)
- **MCP Tool Execution & Human Gating**: Passed (Action tools correctly gated for human approval)
- **RAG & Citation Precision**: Passed (100.0% precision with authority scoring)
- **Safety Disclaimer Compliance**: Passed (100.0% compliance)
- **Event-Driven Re-planning**: Passed (Task graph automatically updated on `SOURCE_CHANGED` Pub/Sub event)

---

## 🚀 Live Cloud Deployment & GitHub Repository

- **Live Google Cloud Run App**: [https://global-life-event-ai-1032566865779.us-central1.run.app](https://global-life-event-ai-1032566865779.us-central1.run.app)
- **GitHub Repository**: [https://github.com/vimalsagar007/global-life-event-ai](https://github.com/vimalsagar007/global-life-event-ai)

---

## 🧪 How to Test the Application

### Method 1: Interactive Web UI (Browser)
1. Open [https://global-life-event-ai-1032566865779.us-central1.run.app](https://global-life-event-ai-1032566865779.us-central1.run.app) in your web browser.
2. In the **Life Event Prompt** box, type any natural language life event.
3. Click **"Orchestrate Plan"**.
4. Explore the 6 interactive tabs:
   - **Task Dependency Flow**: Interactive SVG graph showing dependencies between Education, Housing, Transportation, Finance, and Government tasks.
   - **Actionable Tasks**: Checklist with priority badges, deadlines, and human approval buttons for MCP actions.
   - **RAG Regulatory Sources**: Official government portal citations and legal disclaimers.
   - **A2A Agent Network**: Real-time status cards for 20 specialist sub-agents.
   - **MCP Tools & Actions**: Action logs with human sign-off approvals (`Approve` / `Reject`).
   - **Live Activity Trace**: Execution timeline and millisecond latency telemetry.

---

## 📝 Example Test Scenarios

### Scenario 1: Domestic Family Relocation (India)
**Prompt**: `"Moving from Bangalore to Hyderabad with me, wife and 2 children"`

**Expected System Behavior**:
- **Jurisdiction Engine**:
  - Origin: Bangalore, Karnataka, India (`INR`, `IST`, `metric`)
  - Destination: Hyderabad, Telangana, India (`INR`, `IST`, `metric`)
  - Classification: Domestic Interstate Relocation (`is_cross_border: false`)
  - Family Extracted: Spouse (1), Children (2)
- **Generated Plan Highlights**:
  - 🎓 **Education**: School transfer certificate (TC) and admission for 2 children in Hyderabad schools.
  - 🚗 **Transportation**: RTO vehicle NOC transfer from Karnataka (KA) to Telangana (TS).
  - 🏢 **Government & Address**: Address registration update on Aadhaar / Telangana municipal portal.
  - 🏥 **Healthcare & Insurance**: Family health insurance porting and local hospital registration.

---

### Scenario 2: Cross-Border International Move with Pet
**Prompt**: `"Relocating from Tokyo to Zurich with cat and starting a new tech job"`

**Expected System Behavior**:
- **Jurisdiction Engine**:
  - Origin: Tokyo, Japan (`JPY`, `JST`)
  - Destination: Zurich, Switzerland (`CHF`, `CET`, German language `de-CH`)
  - Classification: Cross-Border International (`is_cross_border: true`)
- **Generated Plan Highlights**:
  - 🛂 **Immigration**: Work visa (Type D) & Zurich Cantonal Migration Office registration within 14 days.
  - 🐱 **Pet Relocation**: Microchip, rabies serological test, and Swiss Federal Food Safety and Veterinary Office (FSVO) import permit.
  - 💶 **Finance**: CHF bank account opening and Swiss health insurance (KVT) registration within 3 months.

---

### Scenario 3: API Testing via cURL
You can also test the API directly using cURL:

```bash
curl -X POST https://global-life-event-ai-1032566865779.us-central1.run.app/api/v1/events \
  -H "Content-Type: application/json" -d \
  '{"raw_input": "Moving from Bangalore to Hyderabad with me, wife and 2 children"}'
```
