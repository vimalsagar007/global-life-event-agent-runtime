# Global Life Event AI Orchestrator - Technical Architecture

## Overview
The **Global Life Event AI Orchestrator** is an enterprise-grade AI system built to solve complex multi-domain life events (e.g. international relocations, business moves, home purchases) across any global jurisdiction without country assumptions.

## Core Pillars

### 1. Dynamic Jurisdiction Engine
- **Hierarchical Representation**: `WORLD -> COUNTRY -> REGION/STATE/PROVINCE -> CITY -> POSTAL CODE`
- **Zero Hardcoded Assumptions**: Automatically extracts origin and destination jurisdictions, detects cross-border events, and adapts locale, currency, date formatting, and regulatory compliance.

### 2. Multi-Agent & Agent-to-Agent (A2A) Architecture
- **Orchestrator**: `LifeEventOrchestrator` central graph engine.
- **Agent Cards**: Standardized A2A contracts specifying capabilities, skills, endpoints, and input/output schemas.
- **Specialist Suite**: 20 specialized agents including `GovernmentAgent`, `EducationAgent`, `ImmigrationAgent`, `HousingAgent`, `FinanceAgent`, `HealthcareAgent`, `TransportationAgent`, `PetRelocationAgent`, `CrossBorderAgent`, `ComplianceAgent`, etc.

### 3. Model Context Protocol (MCP) & Safety Controls
- Tool categorization: `READ_ONLY` vs `ACTION`.
- Human-in-the-Loop Gating: All consequential actions (sending notifications, scheduling calendar events, submitting applications) require explicit human sign-off.
- Security Guardrails: Prompt injection defenses, PII anonymization, non-advisory legal/tax disclaimers.

### 4. Advanced Multilingual & Temporal RAG
- Metadata filtering (`country`, `jurisdiction`, `authority_level`, `effective_date`).
- Authority Level Scoring (`OFFICIAL_GOVERNMENT`, `REGULATORY`, `TRUSTED_SECONDARY`).
- Freshness reranking and citation validation.
- Live Google Search grounding integration.

### 5. Event-Driven Re-planning Bus (Pub/Sub)
- Listens to `SOURCE_CHANGED` and `JURISDICTION_CHANGED` notifications.
- Dynamically updates execution graphs and highlights OLD PLAN vs NEW PLAN visual diffs.
