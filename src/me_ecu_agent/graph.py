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
from me_ecu_agent.hyde_retriever import create_hyde_retriever
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

        # OPTIMIZED: Enhanced query analysis prompt
        self.query_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Bosch ECU product line classifier. " +
             "CRITICAL RULES: " +
             "1. If query asks about 'all models', 'across all', 'each model', or similar -> respond 'both' " +
             "2. If query compares ECU-750 with ECU-850/850b -> respond 'both' " +
             "3. Distinguish ECU-850 (base) from ECU-850b (enhanced). " +
             "Examples: " +
             "'ECU-750 specs'->ECU-700, " +
             "'ECU-850 RAM'->ECU-800, " +
             "'ECU-850b NPU'->ECU-800, " +
             "'Compare ECU-750 and ECU-850'->both, " +
             "'storage across all models'->both, " +
             "'compare all ECUs'->both. " +
             "Classification Rules: " +
             "ECU-700=ECU-750 ONLY. " +
             "ECU-800=ECU-850 OR ECU-850b. " +
             "both=Any comparison or 'all models' query. " +
             "Respond ONLY: ECU-700, ECU-800, both, or unknown"),
            ("human", "{query}")
        ])

        # OPTIMIZED: Balanced synthesis prompt - relevant but complete
        self.response_synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Bosch ECU technical assistant. " +
             "CRITICAL INSTRUCTIONS: " +
             "1. Always specify exact model names (ECU-750/850/850b). " +
             "2. Answer using RELEVANT information from context (don't include unrelated specs). " +
             "3. COMPREHENSIVENESS for the asked question: " +
             "   - For 'which models support X': List both supported AND unsupported models. " +
             "   - For 'compare all': Provide info for each relevant model. " +
             "   - For specs with multiple states (idle/load, min/max): Include ALL states. " +
             "4. Use exact numbers and units from context. " +
             "5. Only use provided information - do not hallucinate. " +
             "6. STRICT REQUIREMENT: DO NOT use any emojis (like ✅, ➡️, etc.). Use standard professional text only. " +
             "Context: {context}."),
            ("human", "{query}")
        ])

    def register_retriever(self, product_line: str, retriever: VectorStoreRetriever) -> None:
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
        context_parts = [f"[ECU-700: {doc.metadata.get('source', 'U')}]{doc.page_content}" for doc in all_docs]
        state["retrieved_context"] = " ".join(context_parts)
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
        context_parts = [f"[ECU-800: {doc.metadata.get('source', 'U')}]{doc.page_content}" for doc in all_docs]
        state["retrieved_context"] = " ".join(context_parts)
        state["messages"].append(AIMessage(content=f"Retrieved {len(all_docs)} from ECU-800"))

        # Update metadata with result
        langfuse_context.update_current_observation(
            output={
                "retrieved_docs_count": len(all_docs),
                "product_line": "ECU-800"
            }
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

        # Retrieve dynamic callback handler from current context if available
        callbacks = [langfuse_context.get_current_langchain_handler()] if self.langfuse_enabled else []

        print(f"DEBUG: Parallel retrieval started for product_line={state['detected_product_line']}, queries={queries}")

        from concurrent.futures import ThreadPoolExecutor

        def retrieve_from_store(retriever, query):
            if retriever is None:
                return []
            try:
                return retriever.invoke(query, config={"callbacks": callbacks} if callbacks else {})
            except Exception as e:
                print(f"ERROR in parallel retrieval: {e}")
                return []

        # Execute retrievals in parallel
        all_futures = []
        with ThreadPoolExecutor(max_workers=len(queries) * 2) as executor:
            # Add ECU700 retrievals
            if self.ecu700_retriever:
                for q in queries:
                    all_futures.append(executor.submit(retrieve_from_store, self.ecu700_retriever, q))
            
            # Add ECU800 retrievals
            if self.ecu800_retriever:
                for q in queries:
                    all_futures.append(executor.submit(retrieve_from_store, self.ecu800_retriever, q))

            # Wait for all and collect results
            for future in all_futures:
                res = future.result()
                for doc in res:
                    if doc.page_content not in seen_content:
                        final_docs_list.append(doc)
                        seen_content.add(doc.page_content)

        state["retrieved_docs"] = [{"content": doc.page_content, "metadata": doc.metadata} for doc in final_docs_list]
        
        # Group contexts by product line for synthesis
        contexts_700 = [f"[ECU-700: {doc.metadata.get('source', 'U')}]{doc.page_content}" 
                        for doc in final_docs_list if doc.metadata.get("product_line") == "ECU-700"]
        contexts_800 = [f"[ECU-800: {doc.metadata.get('source', 'U')}]{doc.page_content}" 
                        for doc in final_docs_list if doc.metadata.get("product_line") == "ECU-800"]
        
        state["retrieved_context"] = " ".join(contexts_700 + contexts_800)
        state["messages"].append(AIMessage(content=f"Parallel retrieval complete. Found {len(final_docs_list)} documents."))
        
        print(f"DEBUG: Parallel retrieval complete. Total unique docs: {len(final_docs_list)}")
        
        # Update metadata with result
        langfuse_context.update_current_observation(
            output={
                "retrieved_docs_count": len(final_docs_list),
                "product_line": state["detected_product_line"]
            }
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
