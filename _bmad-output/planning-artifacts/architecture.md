---
stepsCompleted: ['step-01-init', 'step-02-context']
inputDocuments: ['prd.md']
workflowType: 'architecture'
project_name: 'BOSCH_Code_Challenge'
user_name: 'Xiazhichao'
date: '2026-03-30'
---

# Architecture Decision Document - ME Engineering Assistant Agent

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

**Author:** Xiazhichao
**Date:** 2026-03-30
**Status:** Draft
**Version:** 1.0

---

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

The PRD defines 12 functional requirements across 3 tiers:

**Tier 1 - Core AI/ML Engineering (60% - P0 Priority):**
- FR-1: Multi-Source RAG System - Semantic search across ECU-700/800 documentation with header-aware chunking (500 chars, 50 overlap)
- FR-2: Intelligent Query Routing Agent - LangGraph-based agent that routes queries to appropriate retrievers based on intent analysis
- FR-3: MLflow Model Logging - Custom PyFunc wrapper with predict() method, supporting multiple input formats
- FR-4: Architectural Documentation - Comprehensive ADRs explaining chunking, agent graph, retriever design, and technology choices

**Tier 2 - Production MLOps Excellence (30% - P1 Priority):**
- FR-5: Databricks Asset Bundle (DAB) Packaging - Complete IaC deployment with databricks.yml
- FR-6: Automated Deployment Pipeline - Databricks Job for automated document loading, vectorization, and model logging
- FR-7: Comprehensive Testing Strategy - Test cases covering single/cross-document queries, edge cases, error scenarios
- FR-8: REST API Serving & Error Handling - MLflow serving endpoint with graceful error handling

**Tier 3 - Innovation & Leadership (10% - P2 Priority):**
Select 1-2 from: Evaluation Framework, Human-in-the-Loop, Scalability Strategy, Advanced Agent Behaviors

**Non-Functional Requirements:**

| Category | Requirement | Architectural Implication |
|----------|-------------|---------------------------|
| **Performance** | <10s response time, ≥80% accuracy | Optimized RAG pipeline, efficient retrieval |
| **Code Quality** | Pylint >85%, modular design | Component-based architecture, clear separation of concerns |
| **Technology Stack** | LangChain + LangGraph + FAISS + Databricks | Specific framework choices, platform constraints |
| **MLOps Maturity** | Version control, reproducibility, monitoring | MLflow integration, DAB packaging, automated deployment |
| **Scalability** | Plan for thousands of documents | Extensible architecture, growth-enabling design |

**Scale & Complexity:**

- **Primary domain:** AI/ML Engineering + MLOps + Backend API
- **Complexity level:** Medium (not enterprise-scale, but production-grade requirements)
- **Estimated architectural components:** ~8 major components
  1. Document Processor (chunking, indexing)
  2. Vector Store Manager (FAISS, embeddings)
  3. Retriever Tools (ECU-700/800 specific)
  4. LangGraph Agent (routing, orchestration)
  5. MLflow PyFunc Wrapper (model serving)
  6. DAB Deployment Configuration (IaC)
  7. Testing Framework (unit, integration, E2E)
  8. Monitoring & Logging (MLflow Tracking)

### Technical Constraints & Dependencies

**Technology Constraints:**
- **Language:** Python required (no alternatives)
- **Frameworks:** LangChain + LangGraph mandatory for agent implementation
- **Vector Storage:** FAISS in-memory (acceptable for small corpus, fallback to direct context allowed)
- **Deployment:** Must use Databricks Asset Bundles (DABs)
- **Model Management:** MLflow with custom PyFunc wrapper
- **Packaging:** Python package structure (not monolithic notebooks)

**Platform Dependencies:**
- Databricks workspace (compute, storage)
- LLM endpoint (gpt-4.1-mini via Databricks)
- Embedding endpoint (OpenAI via Databricks)
- MLflow Tracking Server
- ME BIOS repository (templates, patterns)

**Data Constraints:**
- Small corpus (85 lines, 3 Markdown files)
- Static documents (no real-time updates expected)
- English language, technical terminology
- Structured format (headers, tables, code blocks)

**Timeline Constraints:**
- 10 days total, 8-10 hours active development
- Tiered development approach (Core → Production → Innovation)

### Cross-Cutting Concerns Identified

**1. Performance Optimization**
- 10-second response time requires optimized RAG pipeline
- Efficient retrieval strategy (top-k selection, chunk overlap)
- LLM call optimization (temperature=0 for consistency)
- Caching opportunities for repeated queries

**2. Error Handling & Resilience**
- Graceful degradation when retrievers fail
- Fallback to direct context injection if vector store unavailable
- Batch processing error isolation (failed queries don't abort batch)
- Clear error messages for common failure modes

**3. Extensibility & Scalability**
- Architecture must support growth from 3 to thousands of documents
- Modular retriever design for easy addition of new product lines
- Vector store abstraction (FAISS → distributed stores)
- Configuration-driven chunking and retrieval parameters

**4. Testing & Validation**
- Comprehensive test coverage (unit, integration, E2E)
- Golden dataset with 10 predefined queries
- Automated performance monitoring (latency, accuracy)
- Domain expertise validation (MLflow evaluation)

**5. Documentation & Knowledge Management**
- Architecture Decision Records (ADRs) for key choices
- API documentation for model interface
- Deployment runbooks for DAB operations
- Clear separation between challenge submission and production code

**6. MLOps & CI/CD**
- Model versioning and artifact management
- Reproducible deployments (IaC via DABs)
- Automated testing and validation pipeline
- Monitoring and observability (MLflow Tracking)

**7. User Experience**
- Intuitive query interface (natural language)
- Fast response times (<10s)
- Accurate answers (≥80%)
- Helpful error messages and guidance

---

## Starter Template Evaluation

### Primary Technology Domain

**AI/ML Engineering + MLOps** - Python-based intelligent agent system with Databricks deployment

**Note:** This project does not use traditional web framework starters (Next.js, React, etc.). Instead, it leverages platform-specific templates and existing codebase.

### Starter Options Considered

**Option 1: ME BIOS Platform Templates (RECOMMENDED) ✨**
- **Source:** Internal ME platform repository
- **Provides:**
  - Databricks Asset Bundle (DAB) structure
  - MLflow PyFunc wrapper templates
  - Deployment job examples
  - pyproject.toml dependency management
- **Advantages:**
  - Optimized for Databricks + MLflow workflow
  - Follows ME platform conventions
  - Production-proven patterns
  - Aligns with challenge requirements

**Option 2: LangChain Official Templates**
- **Source:** LangChain GitHub repository
- **Provides:**
  - Latest LangChain/LangGraph patterns
  - Community best practices
- **Disadvantages:**
  - May not align with ME platform conventions
  - Requires DAB structure adaptation

**Option 3: Extend Existing Codebase**
- **Source:** Current `src/me_ecu_agent/` implementation
- **Provides:**
  - Existing document processor, vector store, tools, graph, model components
  - Established code patterns
- **Gaps:**
  - Missing DAB configuration
  - Incomplete MLflow best practices
  - Needs deployment automation

### Selected Approach: Hybrid Strategy

**Decision:** **ME BIOS Platform Templates + Existing Codebase Enhancement**

**Rationale for Selection:**

1. **Challenge Compliance:** Meets all Databricks + MLflow requirements
2. **Leverage Existing Work:** Builds on proven `src/me_ecu_agent/` implementation
3. **Platform Alignment:** Follows ME platform patterns and conventions
4. **Production Readiness:** Incorporates MLOps best practices from platform templates

**Implementation Strategy:**

1. **Preserve Existing Components:**
   - `document_processor.py` - Header-aware chunking (500 chars, 50 overlap)
   - `vectorstore.py` - FAISS management with separate ECU-700/800 indices
   - `tools.py` - LangChain retriever tools with descriptive names
   - `graph.py` - LangGraph agent with conditional routing
   - `model.py` - MLflow PyFunc wrapper foundation

2. **Add ME Platform Components:**
   - `databricks.yml` - DAB configuration from platform template
   - `pyproject.toml` - Enhanced dependency management
   - `deployment/` - Deployment job automation scripts
   - `tests/` - Testing framework structure from platform examples

3. **Enhance MLOps Practices:**
   - MLflow model signature inference
   - Automated deployment pipeline
   - Comprehensive testing strategy
   - Monitoring and logging integration

**Base Configuration:**

No traditional CLI starter command. Instead:

```bash
# Use existing codebase as foundation
cp -r src/me_ecu_agent/* <package_structure>/

# Augment with ME platform templates
# From: https://github.boschdevcloud.com/bios-eco-mde/ai-platform/
# - databricks.yml template
# - Deployment job examples
# - MLflow logging patterns
```

**Architectural Decisions Provided by This Approach:**

**Language & Runtime:**
- Python 3.10+ (Databricks runtime)
- Type hints for code quality (Pylint >85% target)

**Package Structure:**
```
me_ecu_agent/
├── __init__.py
├── document_processor.py  # Existing: Header-aware chunking
├── vectorstore.py         # Existing: FAISS management
├── tools.py               # Existing: Retriever tools
├── graph.py               # Existing: LangGraph agent
├── model.py               # Existing: MLflow PyFunc (enhance)
└── config.py              # NEW: Configuration management

deployment/
├── build_and_log.py       # NEW: Automated deployment script
└── job_config.yaml        # NEW: Databricks job definition

tests/
├── test_document_processor.py
├── test_vectorstore.py
├── test_graph.py
└── test_model.py

databricks.yml             # NEW: DAB configuration
pyproject.toml             # Enhanced: Dependencies + metadata
README.md                  # Comprehensive documentation
```

**Development Experience:**
- Local development: MLflow with SQLite tracking
- Databricks deployment: Automated via DAB
- Testing: pytest with coverage reporting
- Code quality: Pylint >85% enforcement

**Note:** This hybrid approach leverages your existing implementation while incorporating ME platform best practices for production deployment.

---