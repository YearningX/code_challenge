"""
Vector Store Management Module for ME ECU Agent.

Architecture Decision Record (ADR-002): Separate Vector Stores
- Separate FAISS indices for query routing efficiency
- Different retrieval depth (k=3 for ECU-700, k=4 for ECU-800)
"""

from pathlib import Path
from typing import Dict, Optional, List
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from me_ecu_agent.config import RetrievalConfig
from me_ecu_agent.model_config import get_embeddings_config


class VectorStoreManager:
    """Manages FAISS vector stores for ECU-700 and ECU-800 product lines."""

    def __init__(self, config: RetrievalConfig = None):
        """Initialize VectorStoreManager with configuration."""
        self.config = config or RetrievalConfig()
        
        # Get dynamic embeddings configuration
        embed_config = get_embeddings_config()
        self.embeddings = OpenAIEmbeddings(
            model=embed_config.model_name,
            api_key=embed_config.api_key,
            base_url=embed_config.base_url
        )
        self._ecu700_store: Optional[FAISS] = None
        self._ecu800_store: Optional[FAISS] = None

    def create_stores(self, chunks: Dict[str, List[Document]]) -> None:
        """Create FAISS vector stores from document chunks."""
        ecu_700_chunks = chunks.get("ECU-700", [])
        ecu_800_chunks = chunks.get("ECU-800", [])

        if not ecu_700_chunks and not ecu_800_chunks:
            raise ValueError("At least one product line must have chunks")

        if ecu_700_chunks:
            self._ecu700_store = FAISS.from_documents(ecu_700_chunks, self.embeddings)
            print(f"Created ECU-700 store with {len(ecu_700_chunks)} chunks")

        if ecu_800_chunks:
            self._ecu800_store = FAISS.from_documents(ecu_800_chunks, self.embeddings)
            print(f"Created ECU-800 store with {len(ecu_800_chunks)} chunks")

    def get_retriever(self, product_line: str, k: int = None) -> Optional[VectorStoreRetriever]:
        """Get retriever for specified product line."""
        if product_line not in ["ECU-700", "ECU-800"]:
            raise ValueError(f"Invalid product_line: {product_line}")

        if k is None:
            k = self.config.ecu700_k if product_line == "ECU-700" else self.config.ecu800_k

        store = self._ecu700_store if product_line == "ECU-700" else self._ecu800_store

        if store is None:
            return None
        return store.as_retriever(search_kwargs={"k": k})

    def save_stores(self, directory: str) -> None:
        """Save FAISS vector stores to disk."""
        save_path = Path(directory)
        save_path.mkdir(parents=True, exist_ok=True)

        if self._ecu700_store:
            self._ecu700_store.save_local(str(save_path / "ecu_700_index"))
            print(f"Saved ECU-700 store")

        if self._ecu800_store:
            self._ecu800_store.save_local(str(save_path / "ecu_800_index"))
            print(f"Saved ECU-800 store")

    @classmethod
    def load_stores(cls, directory: str, config: RetrievalConfig = None):
        """Load FAISS vector stores from disk."""
        save_path = Path(directory)
        if not save_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        manager = cls(config=config)
        ecu700_path = save_path / "ecu_700_index"
        ecu800_path = save_path / "ecu_800_index"

        if ecu700_path.exists():
            manager._ecu700_store = FAISS.load_local(
                str(ecu700_path), manager.embeddings,
                allow_dangerous_deserialization=True
            )
            print(f"Loaded ECU-700 store")

        if ecu800_path.exists():
            manager._ecu800_store = FAISS.load_local(
                str(ecu800_path), manager.embeddings,
                allow_dangerous_deserialization=True
            )
            print(f"Loaded ECU-800 store")

        return manager


# Backward compatibility functions
def create_vector_stores(ecu_700_docs, ecu_800_docs):
    """Create vector stores from document chunks (backward compatibility)."""
    manager = VectorStoreManager()
    manager.create_stores({"ECU-700": ecu_700_docs, "ECU-800": ecu_800_docs})
    return manager._ecu700_store, manager._ecu800_store


def save_vector_stores(store_700, store_800, directory: str) -> None:
    """Save vector stores to directory (backward compatibility)."""
    save_path = Path(directory)
    save_path.mkdir(parents=True, exist_ok=True)

    if store_700:
        store_700.save_local(str(save_path / "ecu_700_index"))
        print(f"Saved ECU-700 store to {save_path / 'ecu_700_index'}")

    if store_800:
        store_800.save_local(str(save_path / "ecu_800_index"))
        print(f"Saved ECU-800 store to {save_path / 'ecu_800_index'}")


def load_vector_stores(directory: str):
    """Load vector stores from directory (backward compatibility)."""
    from langchain_openai import OpenAIEmbeddings

    save_path = Path(directory)
    if not save_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    # Use centralized config for backward compatibility functions
    from me_ecu_agent.model_config import get_embeddings_config
    embed_config = get_embeddings_config()
    embeddings = OpenAIEmbeddings(
        model=embed_config.model_name,
        api_key=embed_config.api_key,
        base_url=embed_config.base_url
    )
    store_700 = None
    store_800 = None

    ecu700_path = save_path / "ecu_700_index"
    ecu800_path = save_path / "ecu_800_index"

    if ecu700_path.exists():
        store_700 = FAISS.load_local(
            str(ecu700_path), embeddings,
            allow_dangerous_deserialization=True
        )
        print(f"Loaded ECU-700 store from {ecu700_path}")

    if ecu800_path.exists():
        store_800 = FAISS.load_local(
            str(ecu800_path), embeddings,
            allow_dangerous_deserialization=True
        )
        print(f"Loaded ECU-800 store from {ecu800_path}")

    return store_700, store_800
