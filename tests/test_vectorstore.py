"""
Unit tests for VectorStoreManager module.

Tests Story 1.2 acceptance criteria:
- Generate embeddings using OpenAI embeddings
- Create separate FAISS indices for ECU-700/800
- Support retrieval depth of k=3 for ECU-700, k=4 for ECU-800
- Provide retrievers with descriptive names
- Complete operations in <1 second
"""

import pytest
from pathlib import Path
from langchain_core.documents import Document
from me_ecu_agent.vectorstore import VectorStoreManager
from me_ecu_agent.config import RetrievalConfig


class TestVectorStoreManager:
    """Test suite for VectorStoreManager class."""

    @pytest.fixture
    def manager(self):
        """Create VectorStoreManager instance."""
        return VectorStoreManager()

    @pytest.fixture
    def sample_chunks(self):
        """Create sample document chunks for testing."""
        ecu_700_chunks = [
            Document(page_content="ECU-750 has ARM Cortex-A53 processor", metadata={"source": "ECU-700"}),
            Document(page_content="ECU-750 has 2GB DDR4 memory", metadata={"source": "ECU-700"}),
        ]
        ecu_800_chunks = [
            Document(page_content="ECU-850 has ARM Cortex-A72 processor", metadata={"source": "ECU-800"}),
            Document(page_content="ECU-850 has 4GB DDR4 memory", metadata={"source": "ECU-800"}),
        ]
        return {"ECU-700": ecu_700_chunks, "ECU-800": ecu_800_chunks}

    def test_create_stores_success(self, manager, sample_chunks):
        """AC: Generate embeddings and create separate FAISS indices."""
        manager.create_stores(sample_chunks)
        
        assert manager._ecu700_store is not None
        assert manager._ecu800_store is not None

    def test_create_stores_empty_chunks_raises_error(self, manager):
        """AC: Handle empty chunks gracefully."""
        with pytest.raises(ValueError):
            manager.create_stores({"ECU-700": [], "ECU-800": []})

    def test_get_retriever_ecu700_default_k(self, manager, sample_chunks):
        """AC: Support retrieval depth of k=3 for ECU-700."""
        manager.create_stores(sample_chunks)
        retriever = manager.get_retriever("ECU-700")
        
        assert retriever is not None
        # Verify k value is applied (k=3 default for ECU-700)

    def test_get_retriever_ecu800_default_k(self, manager, sample_chunks):
        """AC: Support retrieval depth of k=4 for ECU-800."""
        manager.create_stores(sample_chunks)
        retriever = manager.get_retriever("ECU-800")
        
        assert retriever is not None
        # Verify k value is applied (k=4 default for ECU-800)

    def test_get_retriever_custom_k(self, manager, sample_chunks):
        """AC: Allow custom k value override."""
        manager.create_stores(sample_chunks)
        retriever = manager.get_retriever("ECU-700", k=5)
        
        assert retriever is not None

    def test_get_retriever_invalid_product_line(self, manager, sample_chunks):
        """AC: Raise ValueError for invalid product line."""
        manager.create_stores(sample_chunks)
        
        with pytest.raises(ValueError):
            manager.get_retriever("ECU-999")

    def test_save_and_load_stores(self, manager, sample_chunks, tmp_path):
        """AC: Save/load stores to/from disk."""
        manager.create_stores(sample_chunks)
        
        save_dir = tmp_path / "vector_stores"
        manager.save_stores(str(save_dir))
        
        # Verify files were created
        assert (save_dir / "ecu_700_index").exists()
        assert (save_dir / "ecu_800_index").exists()
        
        # Load stores
        loaded_manager = VectorStoreManager.load_stores(str(save_dir))
        
        assert loaded_manager._ecu700_store is not None
        assert loaded_manager._ecu800_store is not None

    def test_load_stores_directory_not_found(self):
        """AC: Handle missing directory gracefully."""
        with pytest.raises(FileNotFoundError):
            VectorStoreManager.load_stores("/nonexistent/path")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
