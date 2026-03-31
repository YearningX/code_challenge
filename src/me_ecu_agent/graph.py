"""
LangGraph Agent Module - OPTIMIZED VERSION with LangSmith Tracing
"""

import os
from typing import List, Literal, Optional, TypedDict
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from me_ecu_agent.config import LLMConfig
from me_ecu_agent.query_expansion import create_query_expander
from me_ecu_agent.hyde_retriever import create_hyde_retriever
from me_ecu_agent.hybrid_retrieval import create_hybrid_retriever

# Import LangSmith callback for tracing
try:
    from langchain.callbacks import LangChainTracer
    from langchain.smith import run_on_dataset
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    print("Warning: LangSmith not available. Tracing disabled.")


class AgentState(TypedDict):
    query: str
    rewritten_query: str
    detected_product_line: Literal["ECU-700", "ECU-800", "both", "unknown"]
    retrieved_context: str
    retrieved_docs: List[Dict[str, Any]]
    response: str
    messages: List[BaseMessage]


class ECUQueryAgent:
    """Enhanced with HyDE (Hypothetical Document Embeddings)."""

    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()
        self.llm = ChatOpenAI(model=self.config.model_name, temperature=self.config.temperature)
        self.query_expander = create_query_expander()
        self.ecu700_retriever: Optional[VectorStoreRetriever] = None
        self.ecu800_retriever: Optional[VectorStoreRetriever] = None

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

    def _analyze_query(self, state: AgentState) -> AgentState:
        query = state["query"]
        expanded = self.query_expander.expand(query)
        state["rewritten_query"] = expanded
        
        # Use expanded queries for better retrieval
        chain = self.query_analysis_prompt | self.llm
        result = chain.invoke({"query": query})
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
        return state

    def _retrieve_ecu700(self, state: AgentState) -> AgentState:
        if self.ecu700_retriever is None:
            state["retrieved_context"] = "Error: ECU-700 retriever not registered"
            return state
        
        # Support both single string and list of strings
        queries = state["rewritten_query"] if isinstance(state["rewritten_query"], list) else [state["query"]]
        all_docs = []
        seen_content = set()
        
        for q in queries:
            docs = self.ecu700_retriever.invoke(q)
            for doc in docs:
                if doc.page_content not in seen_content:
                    all_docs.append(doc)
                    seen_content.add(doc.page_content)
        
        state["retrieved_docs"] = [{"content": doc.page_content, "metadata": doc.metadata} for doc in all_docs]
        context_parts = [f"[ECU-700: {doc.metadata.get('source', 'U')}]{doc.page_content}" for doc in all_docs]
        state["retrieved_context"] = " ".join(context_parts)
        state["messages"].append(AIMessage(content=f"Retrieved {len(all_docs)} from ECU-700"))
        return state

    def _retrieve_ecu800(self, state: AgentState) -> AgentState:
        if self.ecu800_retriever is None:
            state["retrieved_context"] = "Error: ECU-800 retriever not registered"
            return state
            
        queries = state["rewritten_query"] if isinstance(state["rewritten_query"], list) else [state["query"]]
        all_docs = []
        seen_content = set()
        
        for q in queries:
            docs = self.ecu800_retriever.invoke(q)
            for doc in docs:
                if doc.page_content not in seen_content:
                    all_docs.append(doc)
                    seen_content.add(doc.page_content)
                    
        state["retrieved_docs"] = [{"content": doc.page_content, "metadata": doc.metadata} for doc in all_docs]
        context_parts = [f"[ECU-800: {doc.metadata.get('source', 'U')}]{doc.page_content}" for doc in all_docs]
        state["retrieved_context"] = " ".join(context_parts)
        state["messages"].append(AIMessage(content=f"Retrieved {len(all_docs)} from ECU-800"))
        return state

    def _parallel_retrieval(self, state: AgentState) -> AgentState:
        contexts = []
        final_docs_list = []
        seen_content = set()
        queries = state["rewritten_query"] if isinstance(state["rewritten_query"], list) else [state["query"]]

        if self.ecu700_retriever is not None:
            docs_700 = []
            for q in queries:
                res = self.ecu700_retriever.invoke(q)
                for doc in res:
                    if doc.page_content not in seen_content:
                        docs_700.append(doc)
                        seen_content.add(doc.page_content)
            final_docs_list.extend([{"content": doc.page_content, "metadata": doc.metadata} for doc in docs_700])
            contexts.append(" ".join([f"[ECU-700]{doc.page_content}" for doc in docs_700]))
            
        if self.ecu800_retriever is not None:
            docs_800 = []
            for q in queries:
                res = self.ecu800_retriever.invoke(q)
                for doc in res:
                    if doc.page_content not in seen_content:
                        docs_800.append(doc)
                        seen_content.add(doc.page_content)
            final_docs_list.extend([{"content": doc.page_content, "metadata": doc.metadata} for doc in docs_800])
            contexts.append(" ".join([f"[ECU-800]{doc.page_content}" for doc in docs_800]))
            
        state["retrieved_docs"] = final_docs_list
        state["retrieved_context"] = " ".join(contexts)
        state["messages"].append(AIMessage(content=f"Parallel retrieval complete: {len(final_docs_list)} docs"))
        return state

    def _synthesize_response(self, state: AgentState) -> AgentState:
        chain = self.response_synthesis_prompt | self.llm
        result = chain.invoke({"query": state["query"], "context": state["retrieved_context"]})
        state["response"] = result.content
        state["messages"].append(AIMessage(content=state["response"]))
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

    def invoke(self, query: str) -> dict:
        if self.ecu700_retriever is None and self.ecu800_retriever is None:
            raise ValueError("At least one retriever must be registered")
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
        result = graph.invoke(initial_state)
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
             "Context: {context}."),
            ("human", "{query}")
        ])
        return result
