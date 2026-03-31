"""
Citation Tracking Module

OPTIMIZED (2026-03-30): Tracks which document chunks are used in responses.
Enables verification and improves response quality.
"""

from typing import List, Dict, Tuple
from langchain_core.documents import Document


class CitationTracker:
    """
    Tracks document sources used in agent responses.

    Benefits:
    1. Verifiability - Users can check sources
    2. Debugging - Know which chunks were retrieved
    3. Quality - Ensure answers are grounded
    """

    def __init__(self):
        self.current_citations: List[Dict] = []

    def track_retrieval(self, docs: List[Document], query: str,
                        retriever_type: str) -> None:
        """
        Track retrieved documents for current query.

        Args:
            docs: Retrieved documents
            query: User query
            retriever_type: Type of retriever used
        """
        self.current_citations = []

        for i, doc in enumerate(docs):
            citation = {
                'chunk_id': i,
                'source': doc.metadata.get('source', 'Unknown'),
                'file_path': doc.metadata.get('file_path', ''),
                'content_preview': doc.page_content[:100] + '...',
                'retriever': retriever_type
            }
            self.current_citations.append(citation)

    def get_citations(self) -> List[Dict]:
        """Get current citations."""
        return self.current_citations

    def format_citations(self) -> str:
        """
        Format citations for inclusion in response.

        Returns:
            Formatted citation string
        """
        if not self.current_citations:
            return ""

        formatted = "\n\n--- Sources ---\n"
        for citation in self.current_citations:
            formatted += f"- {citation['source']}\n"

        return formatted

    def verify_response_grounding(self, response: str) -> Dict[str, any]:
        """
        Verify that response is grounded in retrieved documents.

        Args:
            response: Generated response

        Returns:
            Dict with grounding verification results
        """
        if not self.current_citations:
            return {
                'grounded': False,
                'reason': 'No citations available'
            }

        # Check if response contains information from citations
        response_lower = response.lower()
        grounded_chunks = 0

        for citation in self.current_citations:
            # Extract key terms from citation content
            content = citation.get('content_preview', '').lower()
            # Check for overlap
            if any(word in response_lower for word in content.split()[:5]):
                grounded_chunks += 1

        grounding_ratio = grounded_chunks / len(self.current_citations)

        return {
            'grounded': grounding_ratio > 0.3,
            'grounding_ratio': grounding_ratio,
            'chunks_used': grounded_chunks,
            'total_chunks': len(self.current_citations)
        }


def create_citation_tracker() -> CitationTracker:
    """Factory function for citation tracker."""
    return CitationTracker()
