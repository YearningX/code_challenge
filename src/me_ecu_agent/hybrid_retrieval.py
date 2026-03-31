"""
Hybrid Retrieval Module - Combines Semantic and Keyword Search

OPTIMIZED (2026-03-30): Improves retrieval accuracy by combining
vector similarity with keyword matching for technical specifications.
"""

from typing import List, Dict
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever


class HybridRetriever:
    """
    Enhanced retriever that combines semantic search with keyword matching.

    This improves retrieval for technical specifications where exact numbers
    and model names are critical.
    """

    def __init__(self, vector_retriever: VectorStoreRetriever):
        """
        Initialize hybrid retriever with vector store.

        Args:
            vector_retriever: Base FAISS vector store retriever
        """
        self.vector_retriever = vector_retriever

    def invoke(self, query: str, **kwargs) -> List[Document]:
        """
        Retrieve documents using hybrid approach.

        Strategy:
        1. Use semantic search (vector similarity)
        2. Boost documents with keyword matches
        3. Re-rank by combined score
        """
        # Get semantic search results
        results = self.vector_retriever.invoke(query, **kwargs)

        # Extract keywords from query
        keywords = self._extract_keywords(query)

        # Re-rank results with keyword matching
        reranked = self._rerank_with_keywords(results, keywords, query)

        return reranked

    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract important keywords from query.

        Looks for:
        - Model names (ECU-750, ECU-850, etc.)
        - Numbers (temperatures, capacities, etc.)
        - Technical terms (RAM, NPU, CAN, etc.)
        """
        import re

        keywords = []

        # Model names
        model_patterns = [
            r'ECU-750', r'ECU-850', r'ECU-850b',
            r'750', r'850', r'850b'
        ]
        for pattern in model_patterns:
            if pattern.lower() in query.lower():
                keywords.append(pattern)

        # Numbers with units
        numbers = re.findall(r'\d+\.?\d*\s*(?:GB|MB|°C|C|MHz|GHz|TOPS|mA|A)', query, re.IGNORECASE)
        keywords.extend(numbers)

        # Technical terms
        tech_terms = ['RAM', 'NPU', 'CAN', 'OTA', 'temperature', 'storage', 'processor', 'power', 'consumption']
        for term in tech_terms:
            if term.lower() in query.lower():
                keywords.append(term)

        return keywords

    def _rerank_with_keywords(self, documents: List[Document], keywords: List[str], query: str) -> List[Document]:
        """
        Re-rank documents based on keyword matches.

        Documents with more keyword matches get boosted.
        """
        scored_docs = []

        for doc in documents:
            score = 0
            content_lower = doc.page_content.lower()

            # Count keyword matches
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    score += 1

            # Boost for exact model name matches
            if 'ECU-750' in query and 'ECU-750' in doc.page_content:
                score += 2
            if 'ECU-850' in query and 'ECU-850' in doc.page_content:
                score += 2
            if 'ECU-850b' in query and 'ECU-850b' in doc.page_content:
                score += 2

            scored_docs.append((score, doc))

        # Sort by score (descending)
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        # Return documents in re-ranked order
        return [doc for score, doc in scored_docs]


def create_hybrid_retriever(vector_retriever: VectorStoreRetriever) -> HybridRetriever:
    """
    Factory function to create hybrid retriever.

    Example:
        >>> base_retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        >>> hybrid = create_hybrid_retriever(base_retriever)
        >>> results = hybrid.invoke("ECU-850 RAM specifications")
    """
    return HybridRetriever(vector_retriever)
