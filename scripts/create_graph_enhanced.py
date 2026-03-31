import os

content = '''"""
LangGraph Agent Module for ME ECU Query System.
[Full implementation here - abbreviated for this operation]
"""

from typing import TypedDict, Optional, List, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.vectorstores import VectorStoreRetriever
from me_ecu_agent.config import LLMConfig

class AgentState(TypedDict):
    query: str
    detected_product_line: Literal["ECU-700", "ECU-800", "both", "unknown"]
    retrieved_context: str
    response: str
    messages: List[BaseMessage]

class ECUQueryAgent:
    """Intelligent query routing agent for ECU documentation system."""

    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()
        self.llm = ChatOpenAI(model=self.config.model_name, temperature=self.config.temperature)
        self.ecu700_retriever: Optional[VectorStoreRetriever] = None
        self.ecu800_retriever: Optional[VectorStoreRetriever] = None
        self.query_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a product line classification expert for Bosch ECU documentation. Analyze the user query and determine which ECU product line(s) it relates to. Rules: - If query mentions ECU-700, ECU-750, 750, or 700 series → respond with ECU-700 - If query mentions ECU-800, ECU-850, 850, 850b, or 800 series → respond with ECU-800 - If query mentions both product lines → respond with both - If query mentions neither or is unclear → respond with unknown. Respond with ONLY one word: ECU-700, ECU-800, both, or unknown"),
            ("human", "{query}")
        ])
        self.response_synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a technical support assistant for Bosch ECU products. Use the retrieved context to answer the user query accurately and concisely. Context: {context}. If the context doesn't contain enough information to answer the query, state this clearly. Do not make up information beyond what's provided in the context."),
            ("human", "{query}")
        ])

    def register_retriever(self, product_line: str, retriever: VectorStoreRetriever) -> None:
        if product_line == "ECU-700":
            self.ecu700_retriever = retriever
        elif product_line == "ECU-800":
            self.ecu800_retriever = retriever
        else:
            raise ValueError(f"Invalid product_line: {product_line}. Must be ECU-700 or ECU-800")

    def _analyze_query(self, state: AgentState) -> AgentState:
        query = state["query"]
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
        state["messages"].append(AIMessage(content=f"Detected product line: {state['detected_product_line']}"))
        return state

    def _retrieve_ecu700(self, state: AgentState) -> AgentState:
        if self.ecu700_retriever is None:
            state["retrieved_context"] = "Error: ECU-700 retriever not registered"
            return state
        docs = self.ecu700_retriever.invoke(state["query"])
        context_parts = [f"[ECU-700 Source: {doc.metadata.get('source', 'Unknown')}]{doc.page_content}" for doc in docs]
        state["retrieved_context"] = " ".join(context_parts)
        state["messages"].append(AIMessage(content=f"Retrieved {len(docs)} chunks from ECU-700 store"))
        return state

    def _retrieve_ecu800(self, state: AgentState) -> AgentState:
        if self.ecu800_retriever is None:
            state["retrieved_context"] = "Error: ECU-800 retriever not registered"
            return state
        docs = self.ecu800_retriever.invoke(state["query"])
        context_parts = [f"[ECU-800 Source: {doc.metadata.get('source', 'Unknown')}]{doc.page_content}" for doc in docs]
        state["retrieved_context"] = " ".join(context_parts)
        state["messages"].append(AIMessage(content=f"Retrieved {len(docs)} chunks from ECU-800 store"))
        return state

    def _parallel_retrieval(self, state: AgentState) -> AgentState:
        contexts = []
        if self.ecu700_retriever is not None:
            docs_700 = self.ecu700_retriever.invoke(state["query"])
            context_700 = " ".join([f"[ECU-700: {doc.metadata.get('source', 'Unknown')}]{doc.page_content}" for doc in docs_700])
            contexts.append(context_700)
        if self.ecu800_retriever is not None:
            docs_800 = self.ecu800_retriever.invoke(state["query"])
            context_800 = " ".join([f"[ECU-800: {doc.metadata.get('source', 'Unknown')}]{doc.page_content}" for doc in docs_800])
            contexts.append(context_800)
        state["retrieved_context"] = " ".join(contexts)
        state["messages"].append(AIMessage(content="Retrieved chunks from both ECU-700 and ECU-800 stores"))
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
        elif product_line == "ECU-800":
            return "retrieve_ecu800"
        else:
            return "parallel_retrieval"

    def create_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        workflow.add_node("analyze_query", self._analyze_query)
        workflow.add_node("retrieve_ecu700", self._retrieve_ecu700)
        workflow.add_node("retrieve_ecu800", self._retrieve_ecu800)
        workflow.add_node("parallel_retrieval", self._parallel_retrieval)
        workflow.add_node("synthesize_response", self._synthesize_response)
        workflow.set_entry_point("analyze_query")
        workflow.add_conditional_edges("analyze_query", self._route_to_retriever, {"retrieve_ecu700": "retrieve_ecu700", "retrieve_ecu800": "retrieve_ecu800", "parallel_retrieval": "parallel_retrieval"})
        workflow.add_edge("retrieve_ecu700", "synthesize_response")
        workflow.add_edge("retrieve_ecu800", "synthesize_response")
        workflow.add_edge("parallel_retrieval", "synthesize_response")
        workflow.add_edge("synthesize_response", END)
        return workflow.compile()

    def invoke(self, query: str) -> dict:
        if self.ecu700_retriever is None and self.ecu800_retriever is None:
            raise ValueError("At least one retriever must be registered. Use register_retriever() first.")
        graph = self.create_graph()
        initial_state = AgentState(query=query, detected_product_line="unknown", retrieved_context="", response="", messages=[HumanMessage(content=query)])
        result = graph.invoke(initial_state)
        return result
'''

with open('src/me_ecu_agent/graph.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Enhanced graph.py created successfully!")
