"""
HyDE-Enhanced Retriever

OPTIMIZED (2026-03-30): Combines HyDE transformation with hybrid retrieval
for maximum accuracy in technical document searches.
"""

from typing import List
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from me_ecu_agent.hyde_transformer import create_hyde_transformer
from me_ecu_agent.hybrid_retrieval import HybridRetriever


class HyDEEnhancedRetriever:
    """
    Enhanced retriever that uses HyDE for improved accuracy.

    Process:
    1. Transform query to hypothetical answer (HyDE)
    2. Use hypothetical answer for vector search
    3. Combine with original query results
    4. Re-rank by relevance
    """

    def __init__(self, vector_retriever: VectorStoreRetriever):
        """
        Initialize HyDE-enhanced retriever.

        Args:
            vector_retriever: Base vector store retriever
        """
        self.vector_retriever = vector_retriever
        self.hyde_transformer = create_hyde_transformer()
        self.hybrid_retriever = HybridRetriever(vector_retriever)

    def invoke(self, query: str, **kwargs) -> List[Document]:
        """
        Retrieve documents using HyDE-enhanced approach.

        Args:
            query: Original user query
            **kwargs: Additional parameters (k, search_kwargs, etc.)

        Returns:
            List of retrieved and ranked documents
        """
        # Step 1: Generate hypothetical answer
        hypothetical_answer = self.hyde_transformer.transform(query)

        # Step 2: Retrieve using hypothetical answer (primary)
        hypothetical_docs = self._retrieve_with_hypothetical(
            hypothetical_answer, **kwargs
        )

        # Step 3: Retrieve using original query (supplementary)
        original_docs = self.hybrid_retriever.invoke(query, **kwargs)

        # Step 4: Combine and deduplicate
        all_docs = self._combine_and_deduplicate(
            hypothetical_docs, original_docs
        )

        # Step 5: Re-rank by combined score
        final_docs = self._rerank_documents(all_docs, query, hypothetical_answer)

        return final_docs

    def _retrieve_with_hypothetical(self, hypothetical: str, **kwargs) -> List[Document]:
        """
        Retrieve using hypothetical answer.

        Args:
            hypothetical: Hypothetically generated answer
            **kwargs: Retrieval parameters

        Returns:
            Documents retrieved using hypothetical answer
        """
        try:
            # Use hypothetical answer for vector search
            docs = self.vector_retriever.invoke(hypothetical, **kwargs)
            return docs
        except Exception as e:
            print(f"Hypothetical retrieval failed: {e}")
            return []

    def _combine_and_deduplicate(self, docs1: List[Document],
                                 docs2: List[Document]) -> List[Document]:
        """
        Combine two document lists and remove duplicates.

        Args:
            docs1: First document list
            docs2: Second document list

        Returns:
            Combined unique documents
        """
        # Use content as deduplication key
        seen = set()
        unique_docs = []

        for doc in docs1 + docs2:
            content_key = doc.page_content[:100]  # First 100 chars as key
            if content_key not in seen:
                seen.add(content_key)
                unique_docs.append(doc)

        return unique_docs

    def _rerank_documents(self, docs: List[Document],
                          query: str, hypothetical: str) -> List[Document]:
        """
        Re-rank documents by relevance to both query and hypothetical.

        Args:
            docs: Documents to rank
            query: Original query
            hypothetical: Hypothetical answer

        Returns:
            Re-ranked documents (top-k)
        """
        scored_docs = []

        for doc in docs:
            score = 0
            doc_content = doc.page_content.lower()

            # Score 1: Match with original query
            query_words = set(query.lower().split())
            query_match = len(query_words & set(doc_content.split()))
            score += query_match * 2

            # Score 2: Match with hypothetical answer
            hyp_words = set(hypothetical.lower().split())
            hyp_match = len(hyp_words & set(doc_content.split()))
            score += hyp_match * 3  # Higher weight for hypothetical

            # Score 3: Technical spec matching
            import re
            numbers_in_hyp = re.findall(r'\d+\.?\d*\s*[°c°CcFfmggBb]+', hypothetical)
            for num in numbers_in_hyp:
                if num.lower() in doc_content:
                    score += 5  # Bonus for exact spec match

            scored_docs.append((score, doc))

        # Sort by score (descending)
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        # Return top documents (respect original k parameter)
        k = len(docs) if docs else 5
        return [doc for score, doc in scored_docs[:k]]


def create_hyde_retriever(vector_retriever: VectorStoreRetriever) -> HyDEEnhancedRetriever:
    """
    Factory function to create HyDE-enhanced retriever.

    Example:
        >>> base_retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        >>> hyde_retriever = create_hyde_retriever(base_retriever)
        >>> results = hyde_retriever.invoke("ECU-850 RAM specifications")
    """
    return HyDEEnhancedRetriever(vector_retriever)
