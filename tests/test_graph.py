"""
Unit tests for ECUQueryAgent module.
"""

import pytest
from unittest.mock import Mock, patch
from me_ecu_agent.graph import ECUQueryAgent, AgentState


class TestECUQueryAgent:
    """Test suite for ECUQueryAgent class."""

    @pytest.fixture
    def agent(self):
        return ECUQueryAgent()

    @pytest.fixture
    def mock_retriever_ecu700(self):
        retriever = Mock()
        retriever.invoke = Mock(return_value=[
            Mock(page_content="ECU-750 has ARM Cortex-A53", metadata={"source": "ECU-700_Manual.md"}),
        ])
        return retriever

    @pytest.fixture
    def mock_retriever_ecu800(self):
        retriever = Mock()
        retriever.invoke = Mock(return_value=[
            Mock(page_content="ECU-850 has ARM Cortex-A72", metadata={"source": "ECU-800_Base.md"}),
        ])
        return retriever

    def test_agent_initialization(self, agent):
        assert agent.config is not None
        assert agent.llm is not None

    def test_register_retriever_ecu700(self, agent, mock_retriever_ecu700):
        agent.register_retriever("ECU-700", mock_retriever_ecu700)
        assert agent.ecu700_retriever == mock_retriever_ecu700

    def test_register_retriever_ecu800(self, agent, mock_retriever_ecu800):
        agent.register_retriever("ECU-800", mock_retriever_ecu800)
        assert agent.ecu800_retriever == mock_retriever_ecu800

    def test_register_retriever_invalid_product_line(self, agent):
        with pytest.raises(ValueError):
            agent.register_retriever("ECU-999", Mock())

    def test_retrieve_ecu700(self, agent, mock_retriever_ecu700):
        agent.register_retriever("ECU-700", mock_retriever_ecu700)
        state = AgentState(
            query="ECU-750 specs",
            detected_product_line="ECU-700",
            retrieved_context="",
            response="",
            messages=[]
        )
        result = agent._retrieve_ecu700(state)
        assert "ECU-700" in result["retrieved_context"]

    def test_retrieve_ecu800(self, agent, mock_retriever_ecu800):
        agent.register_retriever("ECU-800", mock_retriever_ecu800)
        state = AgentState(
            query="ECU-850 specs",
            detected_product_line="ECU-800",
            retrieved_context="",
            response="",
            messages=[]
        )
        result = agent._retrieve_ecu800(state)
        assert "ECU-800" in result["retrieved_context"]

    def test_parallel_retrieval(self, agent, mock_retriever_ecu700, mock_retriever_ecu800):
        agent.register_retriever("ECU-700", mock_retriever_ecu700)
        agent.register_retriever("ECU-800", mock_retriever_ecu800)
        state = AgentState(
            query="Compare specs",
            detected_product_line="both",
            retrieved_context="",
            response="",
            messages=[]
        )
        result = agent._parallel_retrieval(state)
        assert "ECU-700" in result["retrieved_context"]
        assert "ECU-800" in result["retrieved_context"]

    def test_route_to_retriever_ecu700(self, agent):
        state = AgentState(
            query="",
            detected_product_line="ECU-700",
            retrieved_context="",
            response="",
            messages=[]
        )
        assert agent._route_to_retriever(state) == "retrieve_ecu700"

    def test_route_to_retriever_ecu800(self, agent):
        state = AgentState(
            query="",
            detected_product_line="ECU-800",
            retrieved_context="",
            response="",
            messages=[]
        )
        assert agent._route_to_retriever(state) == "retrieve_ecu800"

    def test_route_to_retriever_parallel(self, agent):
        for product_line in ["both", "unknown"]:
            state = AgentState(
                query="",
                detected_product_line=product_line,
                retrieved_context="",
                response="",
                messages=[]
            )
            assert agent._route_to_retriever(state) == "parallel_retrieval"

    def test_invoke_without_retrievers_raises_error(self, agent):
        with pytest.raises(ValueError):
            agent.invoke("Any query")

    def test_create_graph_structure(self, agent):
        graph = agent.create_graph()
        assert graph is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
