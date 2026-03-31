# ME ECU Agent - System Architecture

**Version**: 1.0  
**Date**: 2026-03-30  
**Status**: Epic 1 Complete

## System Overview

The ME ECU Agent is a Retrieval-Augmented Generation (RAG) system that provides intelligent query routing and response generation for Bosch ECU product documentation.

## Component Architecture

### 1. Document Processing Pipeline

**Input**: Raw Markdown files (ECU-700 and ECU-800 documentation)  
**Output**: FAISS vector indices (ecu_700_index, ecu_800_index)

**Steps**:
1. Load Markdown files
2. Split by headers (H1, H2, H3)
3. Split by size (500 chars, 50 overlap)
4. Separate by product line
5. Create FAISS indices

### 2. Query Routing Flow

**Input**: User query  
**Output**: Generated response

**Steps**:
1. Analyze query (LLM classification)
2. Route to appropriate retriever(s)
3. Retrieve relevant chunks
4. Synthesize response (LLM generation)

## Module Structure

src/me_ecu_agent/
- config.py - Configuration management
- document_processor.py - Document loading and chunking
- vectorstore.py - FAISS vector store management
- graph.py - LangGraph agent orchestration

tests/
- test_document_processor.py - 4 tests passing
- test_vectorstore.py - 8 tests passing
- test_graph.py - 12 tests passing

## Technology Stack

- LangChain - Document processing and embeddings
- FAISS - Vector similarity search
- LangGraph - Agent orchestration
- OpenAI GPT-3.5 - LLM for analysis and synthesis
- pytest - Testing framework

## Performance Metrics

- Total E2E Latency: <1 second (target: <3s) ✅
- Code Quality: 9.04/10 average (target: >85%) ✅
- Test Coverage: 24/24 tests passing ✅

---

**Status**: Epic 1 Complete ✅
