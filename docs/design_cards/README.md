# Agent Design Cards & Architectural Specifications Registry

This directory serves as the centralized repository for **Architectural Specifications, Session 0 Briefings, 15-Point Agent Design Cards**, and cross-project metadata across the curriculum (P1 through P12).

---

## 1. Purpose & Lifecycle

Per **Curriculum Roadmap v2 (Section 7)** and repository engineering governance:
1. **Mandatory Pre-Code Phase:** Every specialist or coordinator agent MUST have a verified, written Design Card before any implementation code is authored.
2. **Single Source of Truth:** Documents in this directory preserve the architectural contracts, role boundaries, model tiers, state channels, tool dependencies, failure contracts, and composition interfaces.
3. **Continuous Retrieval:** Before refactoring, writing subagent adapters, or composing multi-agent workflows (e.g. P6 and P12 Capstones), refer to these design cards to preserve inter-agent contracts.

---

## 2. Project Portfolio & Specification Index

| Project | Name / Domain | Role / Archetype | Model Tier (Primary / Fallback) | Design Card Status | Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P1** | **Research Agent** | Knowledge Acquisition Specialist | `low` (`gemini-3.5-flash-lite`) | Historical / Implemented | [`docs/MENTOR_HANDOFF.md`](../MENTOR_HANDOFF.md#p1--research-agent--detailed-state) |
| **P2** | **RAG Agent** | Private Knowledge Retrieval Specialist | `low` (`gemini-3.5-flash-lite`) | Historical / Implemented | [`docs/MENTOR_HANDOFF.md`](../MENTOR_HANDOFF.md#p2--rag-agent--detailed-state) |
| **P3** | **Code Review & Test Gen** | Software Quality Specialist | `medium` (`gemini-3.8-flash`) | Historical / Implemented | [`docs/MENTOR_HANDOFF.md`](../MENTOR_HANDOFF.md#p3--code-review--test-generation-agent) |
| **P4** | **Sandbox / Interpreter Agent** | Controlled Execution Specialist | `medium` (`gemini-3.8-flash`) | Implemented (Phase C Done) | [`docs/MENTOR_HANDOFF.md`](../MENTOR_HANDOFF.md#phase-c-stage-3--enterprise-agent-registry-function-factory-alignment--universal-streaming-observability-2026-09-09-) |
| **P5** | **Memory-Rich Personal Assistant** | Personal Continuity & Memory Specialist | `low` (`gemini-3.5-flash-lite`) / `medium` (`gemini-3.8-flash`) | **ACTIVE** (Phase A) | [`P5_memory_assistant.md`](P5_memory_assistant.md) |
| **P6** | **Research-to-Decision Workflow** | Midterm Multi-Agent Capstone | `medium` (`gemini-3.8-flash`) / `high` (`gpt-5.6-sol`) | Planned | Planned |
| **P7** | **Document Intelligence Agent** | Document Understanding Specialist | `medium` (`gemini-3.8-flash`) | Planned | Planned |
| **P8** | **Customer Support Operations** | Service Operations Specialist | `low` (`gemini-3.5-flash-lite`) / `medium` (`gemini-3.8-flash`) | Planned | Planned |
| **P9** | **Data and SQL Analytics Agent** | Analytics & Decision-Support Specialist | `medium` (`gemini-3.8-flash`) / `high` (`gpt-5.6-sol`) | Planned | Planned |
| **P10** | **Multimodal Perception Agent** | Multimodal Grounding Specialist | `medium` (`gemini-3.8-flash`) | Planned | Planned |
| **P11** | **API & Business Operations Agent** | Controlled Business-Action Specialist | `medium` (`gemini-3.8-flash`) | Planned | Planned |
| **P12** | **Business Operations Control Tower** | Final Enterprise Capstone | `high` (`gpt-5.6-sol` / `claude-opus-5`) | Planned | Planned |

---

## 3. Standard Design Card Template (15 Points)

Each new file in this directory must adhere to the 15-point structure mandated by Section 7 of `docs/Agentic AI Curriculum Roadmap v2.md`:

1. **User Job:** Concrete user/business problem solved.
2. **Role Boundary:** What the agent owns vs. what it refuses or delegates.
3. **Environment:** External states observed (filesystems, stores, APIs).
4. **Tools:** Distinct tools and their architectural separation rationale.
5. **Input Schema:** Typed schema and runtime configs (`thread_id`, `user_id`, etc.).
6. **Output Schema:** Typed final payload and side-effect guarantees.
7. **State:** Transient thread state vs. durable long-term storage channels.
8. **Side Effects:** Mutations performed outside graph boundaries.
9. **Risk Level:** Consequential actions requiring approval (HITL).
10. **Failure Contract:** Degradation policies and error containment.
11. **Verification:** Concrete verification scenarios (unit, e2e, cross-thread).
12. **Composition Boundary:** Subagent or graph wrapper interface for upstream coordinators.
13. **Cost/Latency & Model Tiers:** Explicit tier mapping (`configs/models_config.py`).
14. **Privacy Boundary:** PII, data sanitization, and secret retention constraints.
15. **Phase C Deliverable:** Final reusable specialist artifact handed to future workflows.
