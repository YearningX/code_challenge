# ME ECU Agent - Data Flow

## Document Processing Pipeline

1. Load Markdown files from data/
2. Split by headers (H1, H2, H3)
3. Split by size (500 chars, 50 overlap)
4. Separate by product line (ECU-700/800)
5. Create FAISS indices

Output: vector_stores/ecu_700_index and ecu_800_index

## Query Processing Pipeline

1. Analyze query (LLM classification)
2. Route to retriever(s) based on product line
3. Retrieve relevant chunks (k=3 for ECU-700, k=4 for ECU-800)
4. Synthesize response using retrieved context

Total time: <1 second

## Data Structures

- AgentState: query, detected_product_line, retrieved_context, response, messages
- Document: page_content + metadata (source, headers)
- RetrievalConfig: ecu700_k=3, ecu800_k=4

## Performance

- Document processing: ~900ms
- Query processing: ~700-750ms
- All targets met ✅

---
Status: Epic 1 Complete
