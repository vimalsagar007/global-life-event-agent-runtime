# Global Life Event AI Orchestrator — Vertex AI Agent Runtime Architecture Specification

**Tagline**: *"One life event. Every task. Any country. One intelligent plan."*  
**Deployment Target**: **Vertex AI Agent Runtime** (`agent_runtime`) / Reasoning Engine Spec  
**Repository**: [https://github.com/vimalsagar007/global-life-event-agent-runtime](https://github.com/vimalsagar007/global-life-event-agent-runtime)

---

## 1. Executive Summary & Deployment Target

The **Global Life Event AI Orchestrator (Agent Runtime Edition)** is designed specifically for deployment on **Vertex AI Agent Runtime** (Agent Engine / Reasoning Engines). It provides managed agent execution, native Gemini Enterprise Agent Registry integration, managed session storage, and zero-trust security via Google Cloud Agent Gateway.

```
+-----------------------------------------------------------------------------------+
|                        Vertex AI Agent Runtime (Agent Engine)                      |
|                                                                                   |
|   +-------------------+    +--------------------+    +------------------------+   |
|   |  Agent Gateway    |    | Managed Sessions   |    |  Enterprise Registry   |   |
|   |  (Ingress/Egress) |    | (VertexAI Sessions)|    |  (Gemini Enterprise)   |   |
|   +---------+---------+    +---------+----------+    +-----------+------------+   |
|             |                        |                           |                |
|   +---------v------------------------v---------------------------v------------+   |
|   |                  FastAPI / Reasoning Engine Container                     |   |
|   |                                                                           |   |
|   |   +-----------------------+    +--------------------------------------+   |   |
|   |   | OpenStreetMap Geocode |    |  10 Specialist Multi-Agent Engine    |   |   |
|   |   | (Dynamic ISO Lookup)  |    |  (Gov, Housing, Finance, Edu, etc.)  |   |   |
|   |   +-----------+-----------+    +------------------+-------------------+   |   |
|   |               |                                   |                       |   |
|   |   +-----------v-----------+    +------------------v-------------------+   |   |
|   |   | Multi-Stage RAG Engine|    | MCP & A2A Inter-Agent Message Bus    |   |   |
|   |   | (Google Search + BQ)  |    | (Human Approval Gating & Cards)      |   |   |
|   |   +-----------------------+    +--------------------------------------+   |   |
|   +---------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------+
```

---

## 2. 10 Specialist Agent Definitions & Prompts

### 1. GovernmentAgent
- **Role**: National & regional identity registration, tax residency, civil registrations.
- **System Prompt**: You are an expert government services advisor. Analyze civic registration laws, tax IDs (SSN, SIN, Aadhaar, NIF), and municipal registration rules for the target jurisdiction.

### 2. ImmigrationAgent
- **Role**: Visa requirements, work permits, permanent residency, entry clearance.
- **System Prompt**: You are a global immigration attorney AI. Determine visa categories, entry compliance, border controls, and work authorization requirements.

### 3. HousingAgent
- **Role**: Lease agreements, tenant rights, utility setups, municipal council tax.
- **System Prompt**: You are a real estate and housing compliance agent. Provide relocation housing advice including lease notarization, utility connection, and local property taxes.

### 4. EducationAgent
- **Role**: School admissions, credit transfers, immunization records, local school districts.
- **System Prompt**: You are an international education specialist. Guide families through primary, secondary, and tertiary school enrollments, credit transfers, and local language requirements.

### 5. FinanceAgent
- **Role**: Cross-border banking, tax treaties, credit history transfer, currency exchange.
- **System Prompt**: You are a cross-border personal finance and tax advisor. Assist with opening bank accounts, double taxation agreements (DTAA), credit history migration, and foreign currency transfers.

### 6. HealthcareAgent
- **Role**: Public health registration (e.g. NHS, Medicare), private health insurance, vaccine mandates.
- **System Prompt**: You are a global healthcare system specialist. Detail public health enrollment, GP surgery registration, health insurance portability, and mandatory vaccinations.

### 7. TransportationAgent
- **Role**: Driver's license exchange, vehicle importing/registration, public transport passes.
- **System Prompt**: You are a transport authority specialist. Detail driver's license reciprocity rules, vehicle registration transfers, road tax, and transit passes.

### 8. PetRelocationAgent
- **Role**: Animal quarantine, pet microchipping, rabies titers, pet import permits.
- **System Prompt**: You are a pet travel and quarantine compliance agent. Provide step-by-step import permits, veterinary health certificates, microchip requirements, and quarantine regulations.

### 9. CrossBorderAgent
- **Role**: Customs clearance, personal effects declarations, restricted items, duty exemptions.
- **System Prompt**: You are a customs & international trade specialist. Detail personal belongings declarations, duty-free exemptions, forbidden items, and shipping documentation.

### 10. ComplianceAgent
- **Role**: Sanctions screening, human approval verification, high-risk action gating.
- **System Prompt**: You are an enterprise risk and compliance auditor. Verify all proposed actions against global sanctions, legal safety rules, and ensure human approval for high-risk operations.

---

## 3. Zero-Hardcode Dynamic Public API Geocoding

The system utilizes OpenStreetMap's Nominatim REST API paired with ISO 3166-1 alpha-2 metadata mapping:

- **Endpoint**: `https://nominatim.openstreetmap.org/search?q={query}&format=json&addressdetails=1`
- **Dynamic Extracted Metadata**:
  - `country`, `region`/`state`, `city`, `postal_code`
  - `currency` (e.g., `INR`, `USD`, `EUR`, `GBP`, `JPY`, `CAD`)
  - `language` (e.g., `hi`, `en`, `fr`, `de`, `ja`, `es`)
  - `timezone` (e.g., `Asia/Kolkata`, `America/New_York`, `Europe/London`)
  - `measurement_system` (`metric` vs `imperial`)

---

## 4. Agent Runtime Integration & Deployment

### Deployment Command
```bash
agents-cli deploy \
  --project qwiklabs-gcp-01-a2104073e565 \
  --region us-central1 \
  --deployment-target agent_runtime \
  --service-name global-life-event-agent-runtime
```

### Vertex AI Reasoning Engine Configuration
- **Runtime Identity**: `app_sa` service account with `roles/aiplatform.user`
- **Managed Sessions**: Vertex AI Agent Engine Managed Sessions backend
- **Agent Gateway Egress**: Bindable via `--agent-gateway-egress` for zero-trust outbound TLS inspection
