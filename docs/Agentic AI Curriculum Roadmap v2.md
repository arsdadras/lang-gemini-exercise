**“12 projects in Term P, with P6 and P12 serving as two milestone capstones, followed by the start of Term E for hardening, workflow architecture, platformization, and scale**.”

In this environment, the ability to generate downloadable files was not enabled, so I am providing the full text of the file below so you can copy it directly into a file such as `AGENTIC_AI_ROADMAP_V2.md`. Its design is structured around the distinction between workflow and agent, the necessity of selecting the simplest suitable architecture, and the patterns of sequential execution, routing, parallelization, orchestrator-worker, and evaluator-optimizer. Additionally, tools are treated as primary agent boundaries rather than mere auxiliary functions.\[[anthropic](https://www.anthropic.com/engineering/building-effective-agents)\]\[[resources.anthropic](https://resources.anthropic.com/hubfs/Building%20Effective%20AI%20Agents-%20Architecture%20Patterns%20and%20Implementation%20Frameworks.pdf)\]\[[anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)\]

---

# **Agentic AI Curriculum Roadmap v2**

## **Mentor Handoff Document**

**Purpose:** This document defines the next curriculum generation after P1-P4 and turns the project into a deliberate, multi-stage path from specialist agent construction to multi-agent workflows, agentic application development, system design, and scaling.

**Important:** This is a planning and teaching document. It does not authorize implementation by itself. Each project remains a separate mentor session with a new mentor instance. The mentor must follow the repository's existing delivery rules, verify current library APIs, work one meaningful item at a time, and wait for explicit approval before advancing a stage.

---

## **1\. Strategic Decision**

The curriculum will contain exactly **12 projects: P1 through P12**. Each project keeps the same three-phase model:

* **Phase A — Basic:** build a complete, useful vertical slice of the domain.  
* **Phase B — Growth:** add statefulness, reliability, governance, recovery, and meaningful complexity.  
* **Phase C — Advanced:** make the specialist reusable, composable, policy-aware, and suitable for later workflows.

The curriculum deliberately has two simultaneous progression axes.

### **Vertical progression inside each project**

Every P moves from a basic domain capability to a mature and reusable implementation:

A: domain core  
B: robust operation  
C: composable specialist

### **Horizontal progression across projects**

Later projects must not merely introduce new domain names. They must also increase:

* architectural depth;  
* state and context complexity;  
* tool and integration diversity;  
* reliability expectations;  
* security and permission boundaries;  
* cross-agent contracts;  
* system-design maturity;  
* production-grade thinking.

The learner will therefore revisit earlier capabilities in harder settings. Retrieval, HITL, persistence, sandboxing, streaming, memory, structured output, delegation, and verification should reappear across later projects with better boundaries and stronger operational behavior.

---

## **2\. Why Twelve Projects Before Term E**

The purpose of P1-P12 is not to collect twelve unrelated demos. It is to build a broad but coherent **agent capability portfolio** before entering the dedicated scaling term.

This stage is justified because the learner is still expanding:

* agentic vocabulary;  
* domain intuition;  
* tool-design skill;  
* state-modeling skill;  
* understanding of failure modes;  
* judgment about when to use a workflow versus an autonomous agent;  
* familiarity with specialist role boundaries;  
* practical knowledge of what later orchestration actually needs.

A specialist portfolio gives the later coordinator real components with distinct contracts, risks, tools, and failure modes. A coordinator designed before those boundaries are understood tends to become a vague “god agent” rather than a reliable system.

The curriculum must still avoid a common trap: building twelve agents and postponing all composition until the end. Small supervised or multi-agent workflow exercises will appear throughout the curriculum. They are not separate full projects unless explicitly named; they are milestone implementations that prove the current specialists can cooperate.

Anthropic distinguishes workflows, where the application owns a predefined control path, from agents, where the model dynamically directs its process. The curriculum will use both deliberately and will not force every problem into an autonomous agent architecture. The simplest design that solves the problem and passes evaluation is preferred.\[[anthropic](https://www.anthropic.com/engineering/building-effective-agents)\]

---

## **3\. Fixed Phase Contract**

### **Phase A — Basic / Domain Core**

**Goal:** Make the domain useful end-to-end.

Typical contents:

* one clear user job;  
* minimum viable tools;  
* basic state or context;  
* typed output where downstream consumption requires it;  
* one runnable application entry point;  
* a clear success condition;  
* a small set of representative live explorations.

**In scope:** domain behavior, core agent loop or workflow, essential tools, basic schemas, basic safety boundaries.

**Out of scope:** broad platform abstractions, premature generic registries, full deployment, comprehensive evaluation infrastructure, and unrelated integrations.

### **Phase B — Growth / Robust Operation**

**Goal:** Make the domain behavior resilient and operationally meaningful.

Typical contents:

* persistent or resumable state where required;  
* retry and recovery boundaries;  
* streaming or progress visibility;  
* validation and correction;  
* HITL for consequential ambiguity or side effects;  
* domain-specific error handling;  
* richer tool use;  
* moderate internal composition;  
* edge-case exploration.

**In scope:** behavior that directly improves correctness, safety, recoverability, or user experience.

**Out of scope:** extracting every reusable primitive into a platform before a second consumer exists, and full-scale deployment concerns unless the domain itself requires them.

### **Phase C — Advanced / Composable Specialist**

**Goal:** Turn the domain implementation into a bounded specialist that can be safely reused by future workflows.

Typical contents:

* explicit input and output contracts;  
* stable invocation boundary;  
* clear side-effect declaration;  
* permission and risk boundary;  
* failure contract;  
* subagent or graph wrapper where appropriate;  
* reusable prompt/tool configuration;  
* selective delegation;  
* domain-specific verification;  
* one small composition exercise with earlier or current specialists.

**In scope:** composability, architecture, specialist quality, and domain-specific professional patterns.

**Out of scope:** automatically declaring the entire system production-ready. Full observability, evaluation, service deployment, multi-tenancy, and scale belong to Term E unless explicitly pulled forward for a justified learning reason.

---

## **4\. Project Status and Curriculum Boundary**

### **Completed or currently established**

* **P1 — Research Agent:** completed for the current scope, including research delegation, structured reporting, middleware, HITL, registry-related work, and streaming foundations.  
* **P2 — RAG Agent:** completed for the current scope, including corrective retrieval, checkpointing, streaming, replay, web fallback, groundedness validation, skills/subagent composition, and related retrieval architecture.  
* **P3 — Code Review and Test Generation Agent:** completed through the current advanced scope with subgraphs, HITL, sandbox verification, persistence, time-travel, and compiled subagent composition.  
* **P4 — Sandbox / Interpreter Agent:** completed through the current advanced scope with governed execution, artifacts, persistence, standardized subagents, registry work, and a coordinator-level integration exercise.

The P4 Phase C ending integration already demonstrated a small synthesis of Research, Code Review, and Interpreter capabilities. This is an important precedent: future P projects must continue to include small, bounded composition exercises rather than treating composition as something that begins only after P12.

### **Next project**

* **P5 — Memory-Rich Personal Assistant:** next project and the first project whose central new capability is persistent user continuity, memory governance, skills, and user-scoped context.

### **Term P boundary**

* **P6 — Midterm/Final for the first half of Term P.** P6 is not a new isolated specialist. It is the first formal multi-agent capstone. It must combine selected P1-P5 capabilities to solve one coherent workflow with a clear business or user outcome.  
* **P12 — Final for Term P.** P12 is the second and more advanced formal capstone. It must combine a broader specialist portfolio and demonstrate a richer supervised or multi-agent workflow, stronger contracts, more deliberate routing, verification, and cross-domain synthesis.

P6 and P12 are therefore milestone projects, not merely consecutive domain agents.

---

## **5\. Project Portfolio: P1-P12**

## **P1 — Research Agent**

**Domain problem:** Given a topic or question, research external sources and return a structured, cited report.

**Primary role:** Knowledge acquisition specialist.

**Core capability:** Web search, source synthesis, structured reporting, citation-aware generation.

### **Existing progression**

* **A:** Tavily search, basic DeepAgents orchestration, streaming.  
* **B:** structured report, retry/fallback middleware, HITL before search, checkpointing.  
* **C:** per-subquestion researcher subagent, groundedness direction, registry/manifest and reusable streaming foundations.

### **New lessons introduced**

* tool-enabled research;  
* structured final output;  
* first middleware and fallback boundaries;  
* first specialist delegation.

### **Composition seed**

A research worker contributes findings to a larger synthesis workflow.

### **Expected reusable output**

A bounded research subagent with a stable findings/report contract.

---

## **P2 — RAG and Knowledge Grounding Agent**

**Domain problem:** Answer questions over private documents, notes, code, or a saved corpus with grounded retrieval.

**Primary role:** Private knowledge specialist.

**Core capability:** Retrieval, relevance grading, corrective retrieval, fallback, source-grounded generation.

### **Progression**

* **A:** ingest, retrieve, grade, generate.  
* **B:** query rewriting, checkpointing, streaming, time travel, replay.  
* **C:** hybrid local/web retrieval, response validation, skills, compiled subagent composition.

### **New lessons introduced**

* explicit raw graph state;  
* deterministic node/edge separation;  
* retrieval feedback loops;  
* durable graph execution;  
* time-travel debugging;  
* groundedness as a reusable concern.

### **Composition seed**

The RAG specialist supplies private context to P1, P3, P6, and later document/support workflows.

### **Expected reusable output**

A retrieval specialist that can be invoked as a bounded subagent without exposing internal graph wiring.

---

## **P3 — Code Review and Test Generation Agent**

**Domain problem:** Analyze code or a diff, identify defects, suggest changes, generate tests, and verify them.

**Primary role:** Software quality specialist.

**Core capability:** Review, refactor reasoning, test generation, sandbox verification, human approval.

### **Progression**

* **A:** review and test output with typed schemas.  
* **B:** HITL before modifications, sandbox execution, self-correction, persistence.  
* **C:** reviewer/test-writer/refactor-gate subgraphs, compiled subagent, time travel, model routing.

### **New lessons introduced**

* risk-sensitive approval;  
* file-changing side effects;  
* execution-backed verification;  
* subgraph boundaries;  
* correction based on external test results.

### **Composition seed**

P3 consumes repository context from P2 and external technical research from P1.

### **Expected reusable output**

A code-quality worker with explicit review, mutation, and verification boundaries.

---

## **P4 — Sandbox / Interpreter and Coding Operations Agent**

**Domain problem:** Plan and execute code or shell work in an isolated workspace, produce artifacts, and recover from execution failures.

**Primary role:** Controlled execution specialist.

**Core capability:** File operations, shell execution, Python computation, artifacts, permissions, persistence, delegation.

### **Progression**

* **A:** native workspace and execution loop.  
* **B:** permission policies, HITL for high-risk commands, artifacts, cross-session persistence.  
* **C:** streaming execution, standardized subagents, registry integration, coordinator-level composition.

### **New lessons introduced**

* environment as an agent interface;  
* physical workspace versus graph state;  
* permission boundaries;  
* artifact lifecycle;  
* execution failure and recovery;  
* multi-agent coding coordination.

### **Composition seed**

Existing P4 Phase C integration combines P1 research, P3 review, and P4 execution. This pattern becomes a model for future end-of-project mini-workflows.

### **Expected reusable output**

A governed execution worker that can be called by coding, analytics, document, and operations workflows.

---

## **P5 — Memory-Rich Personal Assistant**

**Domain problem:** Support an ongoing user relationship while remembering approved facts, preferences, constraints, and prior tasks across sessions.

**Primary role:** Personal continuity and memory specialist.

**Core capability:** Short-term state, long-term store, skills, memory consolidation, user context, controlled personal tools.

### **Progression**

* **A:** CompositeBackend with conversation state and long-term memory, basic personal tools.  
* **B:** reusable skills, consolidation subagent, HITL for sensitive writes, PII protection.  
* **C:** per-user namespaces, durable store, MCP integrations, memory quality and drift handling.

### **New lessons introduced**

* distinction between thread state and long-term memory;  
* memory write policy;  
* memory conflict and staleness;  
* personal data boundaries;  
* behavior/skill loading;  
* user-scoped context.

### **Composition seed**

P5 provides user preferences, project context, and approved constraints to later workflows without becoming the workflow coordinator.

### **Expected reusable output**

A memory and personalization subsystem with explicit read/write policies.

---

## **P6 — Midterm/Final I: Research-to-Decision Workflow**

**Type:** First formal multi-agent capstone.

**Domain problem:** Turn an open-ended question into a grounded decision brief using external research, private knowledge, analysis, and verification.

### **Suggested workflow**

User objective  
    \-\> scope and clarification  
    \-\> P1 external research  
    \-\> P2 private knowledge retrieval  
    \-\> optional P4 structured analysis/artifact  
    \-\> lightweight verification  
    \-\> human approval or final delivery

### **Phase A — Basic composition**

* coordinator invokes P1 and P2;  
* shared task state is explicit;  
* outputs are passed through typed contracts;  
* final synthesis is produced;  
* one simple approval gate exists before delivery.

### **Phase B — Growth**

* parallel research branches;  
* source conflict handling;  
* corrective retrieval;  
* state checkpointing;  
* partial failure recovery;  
* synthesis validation;  
* optional artifact generation through P4.

### **Phase C — Advanced**

* hierarchical or orchestrator-worker pattern;  
* specialist capability registry;  
* evaluator/optimizer loop;  
* reusable workflow interface;  
* a second use case that reuses the same workers.

### **Architectural pattern**

The main teaching target is orchestration with explicit contracts, not a giant autonomous supervisor. Use deterministic routing where the path is known, and model-driven delegation only where task decomposition is genuinely open-ended. This follows the principle that workflows should own predictable control flow while agents are reserved for flexible decision-making.\[[anthropic](https://www.anthropic.com/engineering/building-effective-agents)\]

### **P6 milestone outcome**

The learner proves that P1-P5 are not isolated demos. They can cooperate in a bounded workflow with state, synthesis, approval, and failure boundaries.

---

## **P7 — Document Intelligence Agent**

**Domain problem:** Ingest heterogeneous documents and extract, classify, validate, compare, and explain their contents.

**Primary role:** Document understanding specialist.

**Core capability:** Multiformat input, extraction, schema mapping, validation, exception routing.

### **Progression**

* **A:** one document family, extraction into typed schemas, basic confidence reporting.  
* **B:** multiple formats, table/layout handling, validation loops, human review for ambiguity, document comparison.  
* **C:** document lineage, multi-document reasoning, reusable extraction skills, audit-ready outputs, composition with P2 and P4.

### **New lessons introduced**

* document as a structured artifact;  
* extraction versus interpretation;  
* confidence and ambiguity;  
* schema evolution;  
* provenance and lineage;  
* human review of uncertain fields.

### **Mini-workflow at the end of P7**

Document intake  
    \-\> P7 extraction  
    \-\> P2 private knowledge lookup  
    \-\> validation gate  
    \-\> P4 report/artifact generation

This is the first focused document workflow and introduces the pattern of an agent producing an intermediate structured artifact for another agent.

---

## **P8 — Customer Support and Service Operations Agent**

**Domain problem:** Triage support requests, retrieve relevant knowledge, draft or execute responses, and escalate according to risk, priority, and confidence.

**Primary role:** Service operations specialist.

**Core capability:** Intent classification, routing, knowledge retrieval, response drafting, escalation, controlled actions.

### **Progression**

* **A:** classify ticket, retrieve answer, draft response.  
* **B:** multi-intent tickets, customer context, SLA/priority routing, HITL for sensitive actions, escalation states, memory-aware continuity.  
* **C:** action permissions, ticket-system integration, audit trail, evaluator/critic, reusable support workflow component.

### **New lessons introduced**

* routing among distinct specialists;  
* confidence-based escalation;  
* policy-aware side effects;  
* operational priority and SLA state;  
* customer context without uncontrolled memory;  
* response versus action separation.

### **Mini-workflow at the end of P8: Support Resolution Cell**

This is the second formal mini-integration and must be implemented as a small supervised workflow, not merely described.

Incoming ticket  
    \-\> P8 intent and risk triage  
    \-\> P2 retrieval over support knowledge  
    \-\> P1 research fallback for missing external information  
    \-\> lightweight verification/critic check  
    \-\> human approval for consequential action  
    \-\> response draft or controlled ticket update

### **Why this pattern matters**

It combines routing, retrieval, fallback, verification, and approval in a bounded business workflow. It also forces a distinction between generating a response and performing a side effect. That distinction is essential before scaling.

### **P8 milestone outcome**

The curriculum reaches a second meaningful workflow checkpoint with a business-facing domain, not just a developer-facing one.

---

## **P9 — Data and SQL Analytics Agent**

**Domain problem:** Translate a natural-language business question into safe data access, analysis, visualizations, and an evidence-backed report.

**Primary role:** Analytics and decision-support specialist.

**Core capability:** Schema discovery, SQL generation, validation, Python analysis, chart/artifact production.

### **Progression**

* **A:** question-to-query-to-result flow with basic chart or table output.  
* **B:** query validation, SQL repair, sandboxed analysis, multi-step metrics, artifact management, HITL before risky queries.  
* **C:** semantic metric layer, provenance, reusable analysis plans, anomaly explanation, evaluator checks, composition with P1/P4 and verification.

### **New lessons introduced**

* data as an external stateful environment;  
* query safety and read/write separation;  
* metric definitions and semantic consistency;  
* reproducible artifact generation;  
* evidence-backed narrative synthesis.

### **Mini-workflow option**

Business question  
    \-\> P9 data analysis  
    \-\> P4 artifact generation  
    \-\> P1 research for external benchmark/context  
    \-\> verification  
    \-\> decision report  
---

## **P10 — Multimodal Perception and Document/Media Agent**

**Domain problem:** Understand and act on mixed text, image, audio, scanned documents, screenshots, charts, or short video inputs.

**Primary role:** Multimodal perception and grounding specialist.

**Core capability:** Modality-aware ingestion, OCR/vision/audio interpretation, cross-modal retrieval, grounded synthesis, artifact references.

### **Progression**

* **A:** one non-text modality plus text context, such as image or audio understanding.  
* **B:** multiple modalities, modality-specific preprocessing, confidence and uncertainty, cross-modal evidence linking, HITL for ambiguous perception.  
* **C:** multimodal workflow composition, temporal media handling, cross-modal memory boundaries, provenance, reusable perception subagents.

### **New lessons introduced**

* content versus representation;  
* modality-specific preprocessing;  
* cross-modal state;  
* references to regions, timestamps, pages, or frames;  
* uncertainty in perception;  
* multimodal tool and model routing.

### **Mini-workflow option**

Mixed input  
    \-\> P10 perception and extraction  
    \-\> P7 document/schema interpretation  
    \-\> P2 grounded context retrieval  
    \-\> verification  
    \-\> P4 artifact/report generation

### **Design caution**

Multimodality is not merely adding images to a text agent. It changes input contracts, evidence representation, context budgeting, evaluation, and error handling. It should therefore be treated as a real domain project, not a feature checkbox.

---

## **P11 — API and Business Operations Agent**

**Domain problem:** Safely interact with external SaaS or business APIs to read state, prepare actions, request approval, and execute idempotent changes.

**Primary role:** Controlled business-action specialist.

**Core capability:** API tools, authentication boundaries, schema translation, side-effect control, idempotency, auditability.

### **Progression**

* **A:** read-only API integration and structured response.  
* **B:** action proposals, approval gates, retries, rate limits, error mapping, idempotency keys.  
* **C:** transactional workflow boundaries, compensation strategies, tenant isolation, connector registry, reusable operations interface.

### **New lessons introduced**

* external side effects;  
* action proposal versus action execution;  
* idempotency;  
* compensation;  
* integration contracts;  
* connector capability discovery.

### **Mini-workflow option**

User request  
    \-\> planning  
    \-\> context gathering  
    \-\> P11 action proposal  
    \-\> HITL approval  
    \-\> idempotent API execution  
    \-\> verification and audit record  
---

## **P12 — Final: Business Operations Control Tower**

**Type:** Final capstone for Term P.

**Domain problem:** Coordinate a realistic business request across research, private knowledge, documents, data, planning, verification, and controlled external actions.

**This is not a generic super-agent.** It is a bounded control-tower workflow with explicit routing and approval boundaries.

### **Suggested scenario**

A business request arrives that requires understanding documents, checking internal knowledge, researching external context, producing an analysis, and optionally updating an external system.

### **Suggested architecture**

Request intake  
    \-\> P5 user/project context  
    \-\> planning and classification  
    \-\> P7 document understanding when needed  
    \-\> P2 private knowledge retrieval  
    \-\> P1 external research when needed  
    \-\> P9 data analysis when needed  
    \-\> P10 multimodal perception when needed  
    \-\> verification and policy checks  
    \-\> P11 controlled action when approved  
    \-\> P4 artifact/report production  
    \-\> final synthesis and audit record

### **P12 Phase A — Controlled composition**

* coordinator and explicit routing;  
* selected specialists only;  
* typed inter-agent contracts;  
* sequential and at least one parallel branch;  
* final synthesis;  
* human approval before side effects.

### **P12 Phase B — Supervised operational workflow**

* planner/executor separation;  
* task dependencies;  
* partial failure recovery;  
* retries and compensation;  
* evaluation at intermediate gates;  
* persistent workflow state;  
* progress streaming;  
* per-specialist permissions;  
* context budget and summary boundaries.

### **P12 Phase C — Advanced term final**

* hierarchical orchestration;  
* reusable agent registry and capability discovery;  
* evaluator-optimizer loop;  
* workflow replay and audit;  
* multiple workflow variants using the same specialists;  
* multi-user or multi-project isolation at the architectural level;  
* documented decision of where deterministic graph control ends and model-directed agency begins.

### **P12 milestone outcome**

The learner demonstrates not just many agents, but judgment about composing them. The final result must show that each specialist has a bounded purpose and that the coordinator does not duplicate their internal logic.

---

## **6\. Mini-Workflow Cadence**

Composition is introduced progressively and must not be postponed until P12.

### **Existing precedent**

The final P4 integration already combined P1 research, P3 code review, and P4 interpreter/execution behavior. This should be treated as the first composition seed, not as an isolated demo.

### **Formal checkpoints**

* **P4 Phase C end:** Research \+ Code Review \+ Interpreter coding workflow.  
* **P6:** Research-to-Decision Workflow.  
* **P7 end:** Document Intake and Validation Cell.  
* **P8 end:** Support Resolution Cell.  
* **P9 end:** Analytics-to-Report Cell.  
* **P10 end:** Multimodal Evidence Cell.  
* **P11 end:** Plan-to-Action Cell.  
* **P12:** Business Operations Control Tower.

### **Rules for mini-workflows**

Each mini-workflow must:

* have one user-facing objective;  
* use only the minimum required specialists;  
* declare its control pattern;  
* define input/output contracts;  
* include one verification or approval boundary;  
* record what failed or remained ambiguous;  
* avoid introducing a generic platform abstraction unless a second consumer justifies it;  
* be small enough to understand completely.

The main patterns to practice are:

* sequential workflow;  
* routing;  
* parallelization and synthesis;  
* orchestrator-workers;  
* evaluator-optimizer;  
* supervised action workflow;  
* hierarchical composition.

These patterns are intentionally introduced as needed rather than all at once. Workflows have predefined control paths, while agents dynamically choose actions; the curriculum must teach the learner to make that architectural decision explicitly.\[[anthropic](https://www.anthropic.com/engineering/building-effective-agents)\]

---

## **7\. Agent Design Contract**

Every new specialist must have a written design card before implementation begins.

### **Required design card**

1. **User job:** What concrete problem does it solve?  
2. **Role boundary:** What does it own and what does it refuse or delegate?  
3. **Environment:** What external state can it observe?  
4. **Tools:** What tools are essential, and why are they not merged into one broad tool?  
5. **Input schema:** What typed input does it accept?  
6. **Output schema:** What typed output does it return?  
7. **State:** What is transient, durable, or shared?  
8. **Side effects:** What can it change outside the graph?  
9. **Risk level:** What actions require approval?  
10. **Failure contract:** What errors can occur and how are they surfaced?  
11. **Verification:** How can success be checked?  
12. **Composition boundary:** How can another workflow call it?  
13. **Cost/latency expectation:** What model or execution tier is appropriate?  
14. **Privacy boundary:** What data may it read, store, or transmit?  
15. **Phase C output:** What reusable artifact will be handed to later projects?

Tool design deserves special attention. Tools should have distinct purposes, clear names, meaningful context-rich outputs, and interfaces that reduce invalid actions. Tool quality and testing often matter more than adding clever prompt complexity.\[[anthropic](https://www.anthropic.com/engineering/writing-tools-for-agents)\]

---

## **8\. Composition Patterns and When to Use Them**

### **Sequential workflow**

Use when steps are known and ordered.

extract \-\> validate \-\> summarize \-\> approve

Best for repeatability, auditability, and predictable business processes.

### **Routing**

Use when one request belongs to one of several specialist paths.

classify \-\> document | support | analytics | research

Best for distinct request classes and bounded capabilities.

### **Parallelization**

Use when independent specialists can work concurrently.

research \+ private retrieval \+ data lookup \-\> synthesis

Best for reducing latency or obtaining independent perspectives.

### **Orchestrator-workers**

Use when the coordinator must decompose an open-ended task at runtime.

plan \-\> dynamic subtasks \-\> workers \-\> merge

Use cautiously; the coordinator needs clear worker contracts and a stopping condition.

### **Evaluator-optimizer**

Use when a generated result can be checked against a meaningful rubric.

generate \-\> evaluate \-\> revise \-\> accept or escalate

Useful for reports, code, extraction, and support drafts.

### **Hierarchical workflow**

Use when the system has multiple domains or business units.

top-level control tower \-\> domain supervisor \-\> specialists

This should be introduced at P12 or later, after lower-level boundaries are understood.

### **Full autonomous agent loop**

Use only when the path cannot be reliably hardcoded and progress can still be verified through tools, tests, environment state, or explicit human checkpoints.

The curriculum should prefer the simplest pattern that meets the requirement. More agents do not automatically mean a better system.\[[anthropic](https://www.anthropic.com/engineering/building-effective-agents)\]

---

## **9\. Progression of Architecture Across P1-P12**

| Capability | First introduced | Revisited later as |
| ----- | ----- | ----- |
| Tool use | P1 | bounded connectors, API actions, multimodal tools |
| Structured output | P1 | inter-agent contracts and workflow schemas |
| Retry and fallback | P1 | typed failure classes, compensation, provider routing |
| Streaming | P1/P2 | nested graph and multi-agent progress events |
| Retrieval | P2 | support, documents, multimodal evidence, decision workflows |
| Checkpointing | P2 | durable long-running workflows and recovery |
| Time travel/replay | P2/P3 | audit and workflow debugging |
| HITL | P3 | risk-aware approvals, edits, actions, escalations |
| Sandbox | P3/P4 | analytics, document processing, controlled execution |
| Subgraphs/compiled subagents | P2/P3 | specialist registry and hierarchical composition |
| Memory | P5 | personal, project, team, and workflow context |
| Skills | P5 | dynamic behavior selection and reusable domain methods |
| MCP/integrations | P5/P11 | connector ecosystems and external actions |
| Multimodality | P10 | cross-modal workflows and evidence grounding |
| Verification | P3/P7/P8/P9 | evaluator-optimizer and policy gates |
| Routing | P6/P8 | capability discovery and hierarchical orchestration |
| Planning | P6/P11/P12 | task dependencies and long-running workflows |
| Business side effects | P11 | idempotent distributed operations in Term E |

The progression must be cumulative. A later P should often revisit an older capability under harder constraints instead of merely moving to an unrelated feature.

---

## **10\. Term E: Post-P12 Scaling and Productization**

P1-P12 belong to the specialist and composition term. **Term E begins only after P12.** Term E is not another collection of disconnected agents. It is the transition from learning through projects to building reusable systems and products.

### **E1 — Production Hardening**

**Goal:** Make the P12 control tower measurable, reliable, auditable, and operationally defensible.

Focus:

* LangSmith traces and trace taxonomy;  
* evaluation datasets and regression runs;  
* quality, cost, latency, and reliability metrics;  
* failure classification;  
* idempotency and duplicate prevention;  
* durable persistence;  
* timeout and cancellation;  
* audit records;  
* authorization and tenant boundaries;  
* secrets and configuration;  
* sandbox/session isolation;  
* health checks and operational logging.

This is where deferred hardening commitments from the earlier curriculum are intentionally collected rather than repeatedly scattered across individual P projects.

### **E2 — Workflow Portfolio**

Build two or three distinct business workflows using the same specialists and primitives.

Candidate workflows:

* Research-to-decision.  
* Document-to-approval.  
* Ticket-to-resolution.  
* Question-to-analysis.  
* Issue-to-verified-change.  
* Request-to-controlled-API-action.

The goal is to test reuse. If every workflow requires rewriting the same routing, memory, approval, persistence, or event code, the platform boundary is not ready.

### **E3 — Agent Platform and Runtime**

Extract only abstractions justified by multiple consumers:

* agent registry and manifest;  
* versioned capability catalog;  
* input/output contract registry;  
* model routing;  
* tool registry;  
* permission policy;  
* workflow runtime;  
* event and streaming layer;  
* checkpoint and store abstraction;  
* artifact service;  
* evaluation runner;  
* cost and usage attribution;  
* connector lifecycle.

The platform must support composition without hiding important behavior. Generic abstraction is not an achievement by itself; it must reduce duplication while preserving inspectability.

### **E4 — Vertical Productization**

Select one business vertical and develop domain depth rather than adding more generic agents.

Strong candidates based on the portfolio:

* developer delivery operations;  
* document-heavy business operations;  
* support and service operations;  
* analytics and decision intelligence;  
* research and competitive intelligence.

A vertical product should add domain-specific data models, workflows, permissions, integrations, evaluation cases, and user experience. It should not be only a renamed generic assistant.

### **E5 — Scale and Distributed Execution**

Move from local composition to service architecture.

Focus:

* FastAPI API boundary;  
* asynchronous job submission;  
* queue and worker model;  
* long-running workflow execution;  
* durable event log;  
* streaming subscriptions;  
* per-tenant namespaces;  
* artifact/object storage;  
* database and vector-index lifecycle;  
* rate limits and backpressure;  
* provider failover;  
* idempotency keys;  
* cancellation and resume;  
* cost attribution and quotas.

A request-response HTTP endpoint should not hold the connection open for every long-running agent workflow. The service should submit a job, persist its identity, execute through workers, and expose progress and results through a durable state/event boundary.

### **E6 — Advanced and Adaptive Systems**

Only after real traces, evaluations, and workflows exist should the curriculum explore:

* adaptive workflow selection;  
* automatic model/agent routing based on cost and quality;  
* workflow optimization;  
* trace-driven improvement;  
* synthetic users and environment simulation;  
* failure injection and replay;  
* long-lived organizational memory;  
* candidate workflow generation with offline evaluation;  
* controlled self-improvement and version promotion.

No self-modification should be promoted directly to production. Candidate changes must pass evaluation and explicit promotion gates.

---

## **11\. Term P to Term E Transition Gate**

Do not begin Term E solely because P12's happy path works. The transition requires evidence that the learner can reason about the system.

Recommended gate:

* at least 10 specialist roles have been built or deliberately waived with rationale;  
* P6 and P12 have been completed as distinct capstone workflows;  
* at least three mini-workflows have been implemented during P7-P11;  
* every retained specialist has a design card and composition contract;  
* at least two workflow patterns have been used correctly;  
* at least one deterministic workflow and one model-directed workflow have been compared;  
* at least one approval and one side-effect boundary have been exercised;  
* at least one failure has been replayed and analyzed;  
* shared abstractions are justified by multiple consumers;  
* the learner can explain why a given node is a workflow step, tool, agent, or human gate.

This is a learning gate, not a claim that the system is already production-ready.

---

## **12\. Mentor Operating Rules for This Roadmap**

The existing repository governance remains authoritative. This document adds curriculum strategy; it does not replace `AGENTS.md` or `MENTOR_HANDOFF.md`.

For every new P:

1. Begin with a Session 0 orientation.  
2. State the domain problem and the reason this specialist exists.  
3. Explain what A, B, and C will add.  
4. State explicit in-scope and out-of-scope boundaries.  
5. Identify what earlier specialists or capabilities will be reused.  
6. Define the expected composition seed or mini-workflow.  
7. Write the agent design card before implementation.  
8. Work one meaningful concept or component at a time.  
9. Explain architecture before delivering code.  
10. Deliver implementation code only after concept alignment.  
11. Wait for mentee confirmation before the next component.  
12. Keep code, docstrings, comments, strings, and blocks in English.  
13. Verify current ecosystem APIs using official documentation or the repository's documentation MCP.  
14. Verify implementation before presenting it.  
15. End each phase with a short summary and each project with a retrospective.  
16. At the end of each project, update the backlog with unfinished official items and newly discovered extensions.  
17. Never silently expand scope because a capability seems interesting.  
18. Never advance a stage without explicit learner approval.

For P6 and P12 specifically:

* treat them as milestone capstones;  
* define the workflow before defining the coordinator;  
* choose the smallest set of specialists that solves the problem;  
* preserve specialist boundaries;  
* include explicit verification and approval;  
* document why each agent is present;  
* avoid a generic supervisor with unrestricted access to every tool.

---

## **13\. Final Curriculum Map**

TERM P — SPECIALISTS AND COMPOSITION

P1  Research Agent  
P2  RAG / Knowledge Grounding Agent  
P3  Code Review and Test Generation Agent  
P4  Sandbox / Interpreter Agent  
P5  Memory-Rich Personal Assistant  
P6  MIDTERM/FINAL I — Research-to-Decision Workflow  
P7  Document Intelligence Agent  
P8  Customer Support and Service Operations Agent  
P9  Data and SQL Analytics Agent  
P10 Multimodal Perception and Document/Media Agent  
P11 API and Business Operations Agent  
P12 FINAL — Business Operations Control Tower

TERM E — ENGINEERING, PRODUCTIZATION, AND SCALE

E1  Production Hardening and Evaluation  
E2  Workflow Portfolio  
E3  Agent Platform and Runtime  
E4  Vertical Productization  
E5  Distributed Execution and Scale  
E6  Adaptive and Self-Improving Systems

The central educational principle is:

Learn specialists deeply.  
Compose them early in small controlled workflows.  
Use P6 and P12 as formal milestones.  
Only after real composition evidence, extract platforms and scale.

This version fully aligns with the new strategic decisions: exactly 12 projects, strict adherence to the three-phase structure, designation of P6 and P12 as midterm and final milestones, progressive implementation of mini-workflows, integration of multimodal capabilities, and transitioning to Term E only after completing the portfolio and demonstrating real composition mechanics.

