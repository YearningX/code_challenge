---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics']
inputDocuments: ['prd.md', 'architecture-decisions-complete.md']
---

# ME Engineering Assistant Agent - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for ME Engineering Assistant Agent, decomposing the requirements from the PRD and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

**FR1:** Multi-Source RAG System - Implement Retrieval Augmented Generation architecture that retrieves and synthesizes information from ECU-700 and ECU-800 documentation sources with semantic search, header-aware chunking (500 chars, 50 overlap), OpenAI embeddings via Databricks, FAISS in-memory storage, and top-k retrieval strategy (k=3 for ECU-700, k=4 for ECU-800).

**FR2:** Intelligent Query Routing Agent - Implement LangGraph-based agent that analyzes user queries to determine relevant product line(s), routes ECU-700 queries to ECU-700 retriever tool, routes ECU-800 queries to ECU-800 retriever tool, handles comparative queries requiring both sources, synthesizes information from multiple sources into coherent response, and falls back to general knowledge when tools unavailable, using gpt-4.1-mini with temperature=0 for consistency.

**FR3:** MLflow Model Logging - Package LangGraph agent as custom MLflow PyFunc model with predict() method that accepts multiple input formats (DataFrame, list, string, dict), returns structured agent responses, logs model to MLflow Tracking Server, includes vector stores as model artifacts, supports model versioning and metadata with auto-inferred signature, and supports batch processing with error isolation.

**FR4:** Architectural Documentation - Include comprehensive architectural documentation explaining chunking strategy (why 500 chars, why overlap), agent graph structure (nodes, edges, routing logic), retriever tool design (separate vs. unified), technology choice justifications (LangGraph, FAISS, etc.), system architecture diagram, and data flow from query to response.

**FR5:** Databricks Asset Bundle (DAB) Packaging - Package system as complete Databricks Asset Bundle with valid databricks.yml configuration file, proper resource definitions (jobs, models, notebooks), dependency management via pyproject.toml, bundle structure following DAB best practices, deployable via `databricks bundle deploy` command, and environment-specific configuration support, following ME platform conventions.

**FR6:** Automated Deployment Pipeline - Include automated Databricks Job that builds resources and logs MLflow model with job definition in databricks.yml, automated document loading and vectorization, automated MLflow model logging, job success/failure notifications, idempotent deployment (re-run safe), and deployment status logging, using MLflow Tracking Server (SQLite for local, backend for prod).

**FR7:** Comprehensive Testing Strategy - Include documented testing and validation framework with test cases covering single-product fact queries, cross-product comparisons, edge cases (unknown products, ambiguous queries), error scenarios (missing docs, retrieval failures), performance monitoring metrics (latency, accuracy, throughput), error handling validation (common failure modes), test data set with expected answers, and automated test execution capability, using unit tests, integration tests, evaluation metrics, and golden dataset of 10 predefined queries.

**FR8:** REST API Serving & Error Handling - Make MLflow model servable via REST API with comprehensive error handling, including MLflow model serving endpoint responding to HTTP requests, returning JSON-formatted responses, handling malformed input gracefully, providing meaningful error messages, implementing retry logic for transient failures, and logging errors for debugging with structured logs for monitoring.

**FR9 (Option A - Tier 3):** Evaluation Framework - Implement comprehensive evaluation framework with MLflow integration, including automated testing with predefined engineering questions, domain expertise validation using MLflow evaluation, custom evaluation metrics (accuracy, relevance, completeness), performance metrics logging integrated into Databricks Job, and evaluation results visualization.

**FR10 (Option B - Tier 3):** Human-in-the-Loop Integration - Incorporate human oversight for low-confidence scenarios, including confidence scoring for agent responses, threshold-based routing to human review, feedback collection mechanism, and continuous improvement loop (feedback → fine-tuning).

**FR11 (Option C - Tier 3):** Scalability Strategy - Document detailed strategy for scaling to thousands of documents, including scalability analysis (bottlenecks, growth projections), incremental update strategy (document additions, modifications), performance optimization roadmap, and architecture evolution plan (in-memory → distributed vector store).

**FR12 (Option D - Tier 3):** Advanced Agent Behaviors - Demonstrate advanced agentic capabilities, including multi-step reasoning (break down complex queries), tool composition (chain multiple retrievals), query decomposition (split complex questions), and context retention across conversation turns.

### NonFunctional Requirements

**NFR1:** Performance - Query Response Time <10 seconds (end-to-end timing from query input to response), Accuracy Rate ≥80% (8/10 predefined test queries correct), Throughput not specified (single user focus).

**NFR2:** Code Quality - Pylint Score >85% (`pylint src/me_ecu_agent/`), Modularity High (component-based architecture), Maintainability High (clear separation of concerns, documented decisions).

**NFR3:** Architecture - Framework: LangChain + LangGraph, Vector Storage: FAISS (in-memory), LLM: gpt-4.1-mini via Databricks, Embeddings: OpenAI embeddings via Databricks, Deployment: Databricks Asset Bundles (DABs), Model Management: MLflow with custom PyFunc, Packaging: Python package (not notebooks).

**NFR4:** MLOps Maturity - Version Control: Git-based, MLflow model versioning, Reproducibility: DAB packaging, dependency management, Monitoring: MLflow Tracking, performance metrics, Automation: Automated deployment pipeline, Documentation: Comprehensive README and architecture doc.

**NFR5:** Scalability Considerations - Document Corpus: Small (85 lines, 3 docs) → Plan for thousands of documents, Vector Store: In-memory FAISS → Distributed vector store (e.g., Pinecone, Milvus), Retrieval Strategy: Full-document search → Hierarchical retrieval, hybrid search, Deployment: Single Databricks workspace → Multi-environment (dev, staging, prod).

### Additional Requirements (from Architecture)

**Starter Template Strategy:** Use ME BIOS Platform Templates + Existing Codebase Enhancement (hybrid approach), preserving existing components (document_processor.py, vectorstore.py, tools.py, graph.py, model.py) and adding ME platform components (databricks.yml, pyproject.toml, deployment/ scripts, tests/ framework), enhancing MLOps practices with MLflow model signature inference, automated deployment pipeline, comprehensive testing strategy, and monitoring and logging integration.

**Package Structure:** me_ecu_agent/ package with __init__.py, document_processor.py (existing), vectorstore.py (existing), tools.py (existing), graph.py (existing), model.py (existing to enhance), config.py (NEW), deployment/ directory with build_and_log.py (NEW) and job_config.yaml (NEW), tests/ directory with test files, databricks.yml (NEW), pyproject.toml (enhanced), README.md (comprehensive).

**Configuration Management:** Python 3.10+ with type hints for code quality (Pylint >85% target), chunking parameters (CHUNK_SIZE=500, CHUNK_OVERLAP=50), retrieval parameters (ECU700_RETRIEVAL_K=3, ECU800_RETRIEVAL_K=4), LLM parameters (MODEL_NAME="gpt-4.1-mini", TEMPERATURE=0), performance parameters (MAX_QUERY_LENGTH=1000 characters, RESPONSE_TIMEOUT=10 seconds), MLflow parameters (EXPERIMENT_NAME="me-ecu-agent", MODEL_NAME="ME-ECU-Assistant").

**Component Interfaces:** DocumentProcessor with load_markdown_files(), split_by_headers(), split_by_size(), separate_by_product_line() methods, VectorStoreManager with create_stores(), get_retriever(), save_stores(), load_stores() methods, Retriever Tools with descriptive naming for intelligent routing, LangGraph Agent with AgentState (query, product_line, retrieved_context, response), graph nodes (analyze_query, retrieve_ecu700, retrieve_ecu800, synthesize_response), MLflow PyFunc Wrapper with load_context(), predict(), _normalize_input() methods, Deployment Pipeline with build_and_log.py main() function.

**Deployment Architecture:** Local Development Environment with Python 3.10+, MLflow Tracking SQLite (mlflow.db), Vector Stores as In-memory FAISS, Documents in local data/ directory, testing with pytest and coverage, Pylint >85%, local MLflow UI for experimentation. Databricks Production Environment with Databricks Runtime Latest ML runtime, MLflow Tracking Databricks-managed backend, Compute as Single-node cluster (sufficient for small corpus), Storage as DBFS for model artifacts, Deployment via Databricks Asset Bundle (databricks.yml), Automated job as deployment/build_and_log.py, Model serving as MLflow REST API endpoint.

**Data Flow:** Query Processing Flow from User → MLflow REST API → PythonModel.predict() → LangGraph Agent → Query Analysis → Product Line Routing → Retriever (ECU-700/800/Both) → FAISS Vector Stores → LLM Synthesis → Response → MLflow → User. Comparative Query Flow with parallel retrieval from both ECU-700 and ECU-800 retrievers, then synthesis.

**Security & Compliance:** Data Security with internal ECU documentation (no sensitive customer data), no PII, public technical specifications, API Security with MLflow serving endpoints using Databricks authentication, no external API exposure (internal use only), rate limiting via Databricks workspace settings, Model Safety with input validation (query length limits, input sanitization), output filtering (no harmful content generation, technical queries only - domain-scoped), Compliance with ISO 26262 considerations (ECU documentation mentions safety certifications, agent provides information doesn't make safety decisions, human-in-the-loop for critical engineering decisions).

**Performance & Scalability:** Current Performance for 85-line corpus with Query Response Time Target <10s Expected ~3-5s, Accuracy Target ≥80% Expected ~85-90%, Throughput Not specified Expected ~20 queries/min (single-threaded), Performance Breakdown: Query analysis ~0.5s (LLM call), Retrieval ~0.1s (FAISS in-memory), Response synthesis ~2-3s (LLM call with context), Total ~3-5s per query. Scalability Strategy when corpus grows to thousands of documents: Vector Store from FAISS in-memory to Pinecone/Weaviate (distributed), Retrieval from Top-k (3-4) to Hierarchical retrieval, hybrid search, Deployment from Single-node to Multi-cluster, load balancing, Caching from None to Redis cache for common queries, Monitoring from MLflow basic to Prometheus + Grafana. Performance Optimizations: Query Caching for identical queries, Batch Processing for multiple queries in parallel, Streaming Responses for long answers, Model Quantization using smaller LLM models for faster inference.

**Monitoring & Observability:** Metrics to Track including Performance Metrics (Query latency p50/p95/p99, Retrieval time, LLM inference time, End-to-end response time), Quality Metrics (Accuracy rate vs. golden dataset, Retrieval relevance mean average precision, User feedback thumbs up/down), System Metrics (Model version deployed, API error rate, Vector store size, Query volume). MLflow Integration with Automatic Logging of parameters (chunk_size, chunk_overlap, ecu700_k, ecu800_k), metrics (accuracy, avg_latency, retrieval_time), model logging with artifacts, Evaluation Framework with evaluate_model() function for automated testing and metric logging.

### UX Design Requirements

**None identified** - This is an AI backend system with no UI requirements specified.

### FR Coverage Map

FR1: Epic 1 - Multi-Source RAG System with semantic search and document retrieval
FR2: Epic 1 - LangGraph intelligent query routing and response synthesis
FR3: Epic 2 - MLflow PyFunc model packaging with flexible input handling
FR4: Epic 1 - Comprehensive architectural documentation with ADRs
FR5: Epic 3 - Databricks Asset Bundle configuration and packaging
FR6: Epic 3 - Automated deployment pipeline with Databricks Job
FR7: Epic 4 - Comprehensive testing strategy with golden dataset
FR8: Epic 2 - REST API serving with error handling
FR9: Epic 5 (Option) - Evaluation framework with MLflow integration
FR10: Epic 5 (Option) - Human-in-the-loop low-confidence handling
FR11: Epic 5 (Option) - Scalability strategy for thousands of documents
FR12: Epic 5 (Option) - Advanced agent behaviors (multi-step reasoning)

## Epic List

### Epic 1: Core RAG Query System

**User Value:** Engineers can query ECU documentation using natural language and receive accurate, contextual answers about both legacy (ECU-700) and modern (ECU-800) product specifications.

**Goal:** Build a complete Retrieval Augmented Generation system with intelligent query routing that processes ECU-700 and ECU-800 documentation, enabling single-product fact queries and cross-product comparisons.

**FRs covered:** FR1, FR2, FR4

---

### Epic 2: Production Model Serving

**User Value:** Engineers can access the query system through a standardized REST API with reliable error handling, supporting multiple input formats and production-grade serving infrastructure.

**Goal:** Package the RAG agent as an MLflow PyFunc model with flexible input handling, deployable via MLflow REST API with comprehensive error handling and monitoring.

**FRs covered:** FR3, FR8

---

### Epic 3: Enterprise Deployment Automation

**User Value:** The system can be reliably deployed and updated in the Databricks production environment using Infrastructure-as-Code principles with automated pipelines.

**Goal:** Implement complete Databricks Asset Bundle packaging with automated deployment pipeline for reproducible, version-controlled deployments.

**FRs covered:** FR5, FR6

---

### Epic 4: Testing & Quality Assurance

**User Value:** System quality and accuracy are continuously validated through comprehensive testing, ensuring reliable performance and correct answers.

**Goal:** Establish a complete testing and validation framework with automated tests, performance monitoring, and quality metrics tracking.

**FRs covered:** FR7

---

### Epic 5: Advanced AI Capabilities (Tier 3 Innovation)

**User Value:** The system demonstrates advanced AI engineering capabilities and technical leadership through innovative features.

**Goal:** Implement 1-2 advanced capabilities (select from Evaluation Framework, Human-in-the-Loop, Scalability Strategy, or Advanced Agent Behaviors) to showcase technical excellence.

**FRs covered:** FR9 or FR10 or FR11 or FR12 (select 1-2 options)



