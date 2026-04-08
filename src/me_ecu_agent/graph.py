"""
LangGraph Agent Module - OPTIMIZED VERSION with Langfuse Integration
"""

import os
import time
from typing import List, Literal, Optional, TypedDict, Dict, Any
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from me_ecu_agent.config import LLMConfig, LangfuseConfig
from me_ecu_agent.model_config import get_model_config
from me_ecu_agent.query_expansion import create_query_expander
from me_ecu_agent.hybrid_retrieval import create_hybrid_retriever
from me_ecu_agent.langfuse_integration import initialize_langfuse

# Import Langfuse LangChain callback handler and decorators
try:
    from langfuse.callback import CallbackHandler
    from langfuse.decorators import observe, langfuse_context
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    print("Warning: langfuse not available. Install langfuse for detailed tracing.")


class AgentState(TypedDict):
    query: str
    rewritten_query: str
    detected_product_line: Literal["ECU-700", "ECU-800", "both", "unknown"]
    retrieved_context: str
    retrieved_docs: List[Dict[str, Any]]
    response: str
    messages: List[BaseMessage]


class ECUQueryAgent:
    """Enhanced with HyDE (Hypothetical Document Embeddings) and Langfuse Tracing."""

    def __init__(self, config: LLMConfig = None, langfuse_config: LangfuseConfig = None):
        # Initialize configuration from environment via model_config.py
        model_config = get_model_config()
        
        # Merge LLMConfig with environment-based settings
        self.config = config or LLMConfig()
        # Override defaults with environment values if they weren't explicitly provided
        if config is None:
            self.config.model_name = model_config.model_name
            self.config.temperature = model_config.temperature

        self.langfuse_config = langfuse_config or LangfuseConfig()

        # Initialize LLM with full parameters from model_config (API key, base URL, etc.)
        self.llm = ChatOpenAI(
            model=model_config.model_name,
            api_key=model_config.api_key,
            base_url=model_config.base_url,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        # Initialize Langfuse if enabled
        self.langfuse = None
        self.langfuse_enabled = False
        self.langfuse_callback_handler = None

        print(f"\n{'='*60}")
        print(f"ECUQueryAgent - Langfuse Configuration")
        print(f"{'='*60}")
        print(f"Config enabled: {self.langfuse_config.enabled}")
        print(f"Secret Key: {self.langfuse_config.secret_key[:20] if self.langfuse_config.secret_key else None}...")
        print(f"Public Key: {self.langfuse_config.public_key[:20] if self.langfuse_config.public_key else None}...")
        print(f"Base URL: {self.langfuse_config.base_url}")

        if self.langfuse_config.enabled:
            try:
                print("Attempting to initialize Langfuse...")
                self.langfuse = initialize_langfuse(
                    secret_key=self.langfuse_config.secret_key,
                    public_key=self.langfuse_config.public_key,
                    base_url=self.langfuse_config.base_url
                )
                self.langfuse_enabled = self.langfuse.enabled if self.langfuse else False

                # LangChain callback handler will be retrieved dynamically from langfuse_context
                # to ensure correct nesting under nodes decorated with @observe
                if self.langfuse_enabled:
                    print("[OK] Langfuse tracing initialized successfully")
                else:
                    print("[WARN] Langfuse initialized but not enabled")
            except Exception as e:
                print(f"[ERROR] Failed to initialize Langfuse: {e}")
        else:
            print("Langfuse disabled in configuration")
        print(f"Final langfuse_enabled: {self.langfuse_enabled}")
        print(f"LangChain callback available: {self.langfuse_callback_handler is not None}")
        print(f"{'='*60}\n")

        # Initialize query expander and retrievers
        self.query_expander = create_query_expander()
        self.ecu700_retriever: Optional[VectorStoreRetriever] = None
        self.ecu800_retriever: Optional[VectorStoreRetriever] = None

        # Agent observation for current trace (will be set during invoke)
        self.agent_observation = None

        # OPTIMIZED: Enhanced query analysis prompt with strict ECU-800 family detection
        self.query_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Bosch ECU product line classifier. " +
             "CRITICAL RULES: " +
             "1. ECU-800 FAMILY includes: ECU-850, ECU-850b, ECU-850X, ECU-800 series " +
             "2. ECU-700 FAMILY includes: ECU-750, ECU-750X, ECU-700 series " +
             "3. Respond 'both' when: " +
             "   - Explicitly comparing ECU-750 with ECU-850/850b (e.g., 'Compare ECU-750 and ECU-850') " +
             "   - Asking about 'all models', 'each model', 'across all ECUs', 'every ECU' " +
             "   - IMPLICIT comparisons: 'Which ECU has the BEST/WORST/MOST/MAXimum/MINimum...' " +
             "   - Superlatives: 'highest', 'lowest', 'fastest', 'hottest', 'coldest', etc. " +
             "4. If query mentions ONLY ECU-850 and ECU-850b -> respond 'ECU-800' (they're same family!) " +
             "5. ECU-850 vs ECU-850b comparisons are STILL ECU-800 family, NOT 'both' " +
             "Examples: " +
             "'ECU-750 specs'->ECU-700, " +
             "'ECU-850 RAM'->ECU-800, " +
             "'ECU-850b NPU'->ECU-800, " +
             "'differences between ECU-850 and ECU-850b'->ECU-800, " +
             "'Compare ECU-750 and ECU-850'->both, " +
             "'Which ECU has the highest temperature?'->both, " +
             "'storage across all models'->both. " +
             "Respond ONLY: ECU-700, ECU-800, both, or unknown"),
            ("human", "{query}")
        ])

        # OPTIMIZED: Balanced synthesis prompt for quality and speed (2026-04-08)
        self.response_synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Bosch ECU technical assistant. " +
             "CRITICAL RULES: " +
             "1. Always specify exact model names (ECU-750/850/850b). " +
             "2. Carefully extract info from ALL provided context documents. " +
             "3. For comparisons: ensure data completeness for ALL mentioned models. " +
             "4. For specs with multiple states (idle/load, min/max): Include ALL states. " +
             "5. Use exact numbers and units from context. " +
             "6. Be comprehensive but concise - don't include unrelated specs. " +
             "7. DO NOT use any emojis. " +
             "Context: {context}."),
            ("human", "{query}")
        ])
        # Auto-discover and load retrievers if possible
        self._auto_discover_retrievers()

    def _auto_discover_retrievers(self):
        """Finds and loads vector stores from common artifact locations with case-insensitivity."""
        from me_ecu_agent.vectorstore import load_vector_stores
        
        # Priority 1: Container mount point (Production)
        # Priority 2: Local data directory (Development)
        potential_bases = [
            "/models/ecu_agent_model_local/ecu_agent_model",
            os.path.join(os.getcwd(), "models/ecu_agent_model_local/ecu_agent_model"),
            os.path.join(os.getcwd(), "data"),
            "/app/data"
        ]
        
        potential_paths = []
        for base in potential_bases:
            if not os.path.exists(base): continue
            # Add the base itself
            potential_paths.append(base)
            # Find all subdirectories case-insensitively (artifacts, Artifacts, vector_stores_*)
            try:
                for entry in os.listdir(base):
                    full_path = os.path.join(base, entry)
                    if not os.path.isdir(full_path): continue
                    
                    # Target both 'artifacts' folders and direct 'vector_stores' folders
                    if entry.lower() in ["artifacts", "data"] or "vector_stores_" in entry.lower():
                        potential_paths.append(full_path)
                        # Also look inside artifacts/ for vector_stores_
                        if entry.lower() == "artifacts":
                            for sub in os.listdir(full_path):
                                if "vector_stores_" in sub.lower():
                                    potential_paths.append(os.path.join(full_path, sub))
            except Exception: continue

        # De-duplicate and prioritize
        unique_paths = list(dict.fromkeys(potential_paths))
        print(f"Scanning {len(unique_paths)} potential index locations...")

        for path in unique_paths:
            if not os.path.exists(path): continue
            try:
                # Try loading. If it doesn't contain index files, load_vector_stores should raise/return none
                store_700, store_800 = load_vector_stores(path)
                
                if store_700:
                    self.register_retriever("ECU-700", store_700.as_retriever(search_kwargs={"k": 4}))
                if store_800:
                    self.register_retriever("ECU-800", store_800.as_retriever(search_kwargs={"k": 8}))
                
                if self.ecu700_retriever or self.ecu800_retriever:
                    print(f"[OK] Successfully initialized retrievers from: {path}")
                    return # Stop on first success
            except Exception as e:
                continue
        
        print("Warning: No valid vector stores found during auto-discovery.")

    def register_retriever(self, product_line: str, retriever: Any) -> None:
        hybrid = create_hybrid_retriever(retriever)
        if product_line == "ECU-700":
            self.ecu700_retriever = hybrid
        elif product_line == "ECU-800":
            self.ecu800_retriever = hybrid
        else:
            raise ValueError(f"Invalid product_line: {product_line}")

    @observe()
    def _analyze_query(self, state: AgentState) -> AgentState:
        query = state["query"]
        expanded = self.query_expander.expand(query)
        state["rewritten_query"] = expanded

        # Update observation with metadata
        langfuse_context.update_current_observation(
            input={"query": query}
        )

        # Retrieve dynamic callback handler from current context if available
        callbacks = [langfuse_context.get_current_langchain_handler()] if self.langfuse_enabled else []

        # Use expanded queries for better retrieval
        chain = self.query_analysis_prompt | self.llm
        result = chain.invoke({"query": query}, config={"callbacks": callbacks} if callbacks else {})
        detected = result.content.strip().lower()
        if "ecu-700" in detected or "700" in detected:
            state["detected_product_line"] = "ECU-700"
        elif "ecu-800" in detected or "800" in detected:
            state["detected_product_line"] = "ECU-800"
        elif "both" in detected:
            state["detected_product_line"] = "both"
        else:
            state["detected_product_line"] = "unknown"
        state["messages"].append(AIMessage(content=f"Detected: {state['detected_product_line']}"))

        # Update metadata with result
        langfuse_context.update_current_observation(
            output={"detected_product_line": state["detected_product_line"]}
        )

        return state

    @observe()
    def _retrieve_ecu700(self, state: AgentState) -> AgentState:
        if self.ecu700_retriever is None:
            state["retrieved_context"] = "Error: ECU-700 retriever not registered"
            return state
        
        # Update observation with metadata
        langfuse_context.update_current_observation(
            input={"rewritten_query": state.get("rewritten_query", state["query"])}
        )

        # Retrieve dynamic callback handler from current context if available
        callbacks = [langfuse_context.get_current_langchain_handler()] if self.langfuse_enabled else []
        
        # Support both single string and list of strings
        queries = state["rewritten_query"] if isinstance(state["rewritten_query"], list) else [state["query"]]
        all_docs = []
        seen_content = set()
        
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=len(queries)) as executor:
            futures = [executor.submit(self.ecu700_retriever.invoke, q, config={"callbacks": callbacks} if callbacks else {}) for q in queries]
            for future in futures:
                docs = future.result()
                for doc in docs:
                    if doc.page_content not in seen_content:
                        all_docs.append(doc)
                        seen_content.add(doc.page_content)
        
        state["retrieved_docs"] = [{"content": doc.page_content, "metadata": doc.metadata} for doc in all_docs]
        for doc in all_docs:
            doc.metadata["product_line"] = "ECU-700"
        context_parts = [f"[ECU-700: {doc.metadata.get('source', 'U')}]{doc.page_content}" for doc in all_docs]
        state["retrieved_context"] = "\n\n".join(context_parts)
        state["messages"].append(AIMessage(content=f"Retrieved {len(all_docs)} from ECU-700"))

        # Update metadata with result
        langfuse_context.update_current_observation(
            output={
                "retrieved_docs_count": len(all_docs),
                "product_line": "ECU-700"
            }
        )

        return state

    @observe()
    def _retrieve_ecu800(self, state: AgentState) -> AgentState:
        if self.ecu800_retriever is None:
            state["retrieved_context"] = "Error: ECU-800 retriever not registered"
            return state
            
        # Update observation with metadata
        langfuse_context.update_current_observation(
            input={"rewritten_query": state.get("rewritten_query", state["query"])}
        )

        # Retrieve dynamic callback handler from current context if available
        callbacks = [langfuse_context.get_current_langchain_handler()] if self.langfuse_enabled else []

        queries = state["rewritten_query"] if isinstance(state["rewritten_query"], list) else [state["query"]]
        all_docs = []
        seen_content = set()
        
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=len(queries)) as executor:
            futures = [executor.submit(self.ecu800_retriever.invoke, q, config={"callbacks": callbacks} if callbacks else {}) for q in queries]
            for future in futures:
                docs = future.result()
                for doc in docs:
                    if doc.page_content not in seen_content:
                        all_docs.append(doc)
                        seen_content.add(doc.page_content)
                    
        state["retrieved_docs"] = [{"content": doc.page_content, "metadata": doc.metadata} for doc in all_docs]
        for doc in all_docs:
            doc.metadata["product_line"] = "ECU-800"
        context_parts = [f"[ECU-800: {doc.metadata.get('source', 'U')}]{doc.page_content}" for doc in all_docs]
        state["retrieved_context"] = "\n\n".join(context_parts)
        state["messages"].append(AIMessage(content=f"Retrieved {len(all_docs)} from ECU-800"))

        langfuse_context.update_current_observation(
            output={"retrieved_docs_count": len(all_docs), "product_line": "ECU-800"}
        )
        return state

    @observe()
    def _parallel_retrieval(self, state: AgentState) -> AgentState:
        queries = state["rewritten_query"] if isinstance(state["rewritten_query"], list) else [state["query"]]
        final_docs_list = []
        seen_content = set()
        
        # Update observation with metadata
        langfuse_context.update_current_observation(
            input={
                "rewritten_query": state.get("rewritten_query", state["query"]),
                "product_line": state["detected_product_line"]
            }
        )

        print(f"DEBUG: Parallel retrieval started for product_line={state['detected_product_line']}, queries={queries}")

        # OPTIMIZATION: BATCH EMBEDDING
        try:
            embeddings_obj = (self.ecu800_retriever.vector_retriever.vectorstore.embeddings 
                             if self.ecu800_retriever 
                             else self.ecu700_retriever.vector_retriever.vectorstore.embeddings)
            query_vectors = embeddings_obj.embed_documents(queries)
        except Exception as e:
            print(f"ERROR in batch embedding: {e}. Falling back to sequential.")
            query_vectors = None

        if query_vectors:
            from concurrent.futures import ThreadPoolExecutor
            def search_by_vector(retriever, vector, k):
                if retriever is None: return []
                try: return retriever.vector_retriever.vectorstore.similarity_search_by_vector(vector, k=k)
                except Exception as e: return []

            all_futures = []
            with ThreadPoolExecutor(max_workers=len(queries) * 2) as executor:
                for vector in query_vectors:
                    if self.ecu700_retriever:
                        all_futures.append(executor.submit(search_by_vector, self.ecu700_retriever, vector, k=4))
                    if self.ecu800_retriever:
                        all_futures.append(executor.submit(search_by_vector, self.ecu800_retriever, vector, k=8))

                for future in all_futures:
                    for doc in future.result():
                        if doc.page_content not in seen_content:
                            # Robust line detection from source filename if metadata is missing
                            source = doc.metadata.get("source", "")
                            line_tag = "ECU-700" if "700" in source else "ECU-800" if "800" in source else "ECU-GENERIC"
                            doc.metadata["product_line"] = line_tag # Enrich for state
                            final_docs_list.append(doc)
                            seen_content.add(doc.page_content)
        else: pass

        state["retrieved_docs"] = [{"content": doc.page_content, "metadata": doc.metadata} for doc in final_docs_list]
        
        # Build context by prepending tags
        context_parts = []
        for doc in final_docs_list:
            line_tag = doc.metadata.get("product_line", "UNKNOWN")
            source = doc.metadata.get("source", "U")
            context_parts.append(f"[{line_tag}: {source}]{doc.page_content}")
            
        state["retrieved_context"] = "\n\n".join(context_parts)
        state["messages"].append(AIMessage(content=f"Batch-optimized retrieval complete. Found {len(final_docs_list)} docs."))
        
        # Update metadata with result
        langfuse_context.update_current_observation(
            output={"retrieved_docs_count": len(final_docs_list), "product_line": state["detected_product_line"]}
        )
        return state

    @observe()
    def _synthesize_response(self, state: AgentState) -> AgentState:
        # Update observation with metadata
        langfuse_context.update_current_observation(
            input={
                "query": state["query"],
                "retrieved_docs_count": len(state.get("retrieved_docs", []))
            }
        )

        # Retrieve dynamic callback handler from current context if available
        callbacks = [langfuse_context.get_current_langchain_handler()] if self.langfuse_enabled else []

        chain = self.response_synthesis_prompt | self.llm
        result = chain.invoke(
            {"query": state["query"], "context": state["retrieved_context"]},
            config={"callbacks": callbacks} if callbacks else {}
        )
        state["response"] = result.content
        state["messages"].append(AIMessage(content=state["response"]))

        # Update metadata with result
        langfuse_context.update_current_observation(
            output={
                "response": state["response"][:1000],
                "response_length": len(state["response"])
            }
        )

        return state

    def _route_to_retriever(self, state: AgentState) -> str:
        product_line = state["detected_product_line"]
        if product_line == "ECU-700":
            return "retrieve_ecu700"
        if product_line == "ECU-800":
            return "retrieve_ecu800"
        return "parallel_retrieval"

    def create_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        workflow.add_node("analyze_query", self._analyze_query)
        workflow.add_node("retrieve_ecu700", self._retrieve_ecu700)
        workflow.add_node("retrieve_ecu800", self._retrieve_ecu800)
        workflow.add_node("parallel_retrieval", self._parallel_retrieval)
        workflow.add_node("synthesize_response", self._synthesize_response)
        workflow.set_entry_point("analyze_query")
        workflow.add_conditional_edges("analyze_query", self._route_to_retriever, {
            "retrieve_ecu700": "retrieve_ecu700",
            "retrieve_ecu800": "retrieve_ecu800",
            "parallel_retrieval": "parallel_retrieval"
        })
        workflow.add_edge("retrieve_ecu700", "synthesize_response")
        workflow.add_edge("retrieve_ecu800", "synthesize_response")
        workflow.add_edge("parallel_retrieval", "synthesize_response")
        workflow.add_edge("synthesize_response", END)
        return workflow.compile()

    def predict(self, model_input: Any) -> List[Dict[str, Any]]:
        """
        Predict method matching MLflow pyfunc interface for backward compatibility.
        
        Args:
            model_input: Pandas DataFrame or Dict containing 'query'
            
        Returns:
            List containing agent response and metadata
        """
        import pandas as pd
        if isinstance(model_input, pd.DataFrame):
            query = model_input["query"].iloc[0]
        elif isinstance(model_input, dict):
            query = model_input.get("query", "")
        else:
            query = str(model_input)
            
        # Get result from agent
        result = self.invoke(query)
        
        # Format for MLflow-compatible response
        return [{
            "response": result.get("response", ""),
            "detected_product_line": result.get("detected_product_line", "unknown"),
            "retrieved_docs_count": result.get("retrieved_docs_count", 0),
            "trace_id": result.get("trace_id", ""),
            "status": "success"
        }]

    @observe(name="ECU Agent Query")
    def invoke(self, query: str, session_id: str = None, user_id: str = None) -> dict:
        """
        Invoke the ECU agent with Langfuse tracing via @observe decorator.

        Args:
            query: User query string
            session_id: Optional session ID for grouping traces
            user_id: Optional user ID for tracking

        Returns:
            Dictionary containing response and metadata including trace_id
        """
        if self.ecu700_retriever is None and self.ecu800_retriever is None:
            raise ValueError("At least one retriever must be registered")

        # Update trace metadata
        langfuse_context.update_current_trace(
            session_id=session_id or self.langfuse_config.session_id,
            user_id=user_id or self.langfuse_config.user_id,
        )

        start_time = time.time()

        try:
            # Create and invoke graph
            graph = self.create_graph()
            initial_state = AgentState(
                query=query,
                rewritten_query="",
                detected_product_line="unknown",
                retrieved_context="",
                retrieved_docs=[],
                response="",
                messages=[HumanMessage(content=query)]
            )

            # Retrieve dynamic callback handler for graph invocation
            config = {}
            if self.langfuse_enabled:
                config["callbacks"] = [langfuse_context.get_current_langchain_handler()]

            result = graph.invoke(initial_state, config=config)

            # Calculate total duration
            duration = time.time() - start_time

            # Update trace with final results
            langfuse_context.update_current_trace(
                output={
                    "response": result.get("response", "")[:1000],
                    "detected_product_line": result.get("detected_product_line"),
                    "retrieved_docs_count": len(result.get("retrieved_docs", [])),
                    "duration_seconds": round(duration, 2)
                }
            )

            # Add trace details to result
            result["trace_id"] = langfuse_context.get_current_trace_id()
            result["langfuse_enabled"] = self.langfuse_enabled
            result["duration"] = duration

            # Explicitly flush Langfuse traces to ensure they are available in the UI immediately
            if self.langfuse and hasattr(self.langfuse, 'flush'):
                self.langfuse.flush()

            return result

        except Exception as e:
            # Update observation with error details
            langfuse_context.update_current_observation(
                level="ERROR",
                status_message=str(e)
            )
            # Re-raise the exception
            raise
