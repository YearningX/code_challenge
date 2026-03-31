"""
Relevance Scoring Module (RAGAS-inspired)

OPTIMIZED (2026-03-30): Evaluates and improves response relevance.
Implements faithfulness and relevance scoring.
"""

from typing import List, Dict, Tuple
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class RelevanceScorer:
    """
    Scores relevance of retrieved documents and response quality.
    
    Metrics:
    1. Retrieval Relevance: How relevant are retrieved chunks?
    2. Response Faithfulness: Is response grounded in context?
    3. Answer Relevance: Does response address the query?
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
        
        # Faithfulness check prompt
        self.faithfulness_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a response evaluator. Check if the response is "
            "grounded in the context. Answer: 'yes' or 'no' with brief reason."),
            ("human", "Context: {context}\n\nResponse: {response}\n\n"
            "Is the response faithful to the context?")
        ])
        
        # Relevance check prompt
        self.relevance_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a relevance evaluator. Rate how relevant the "
            "retrieved context is to the query. Score 0-10 with brief reason."),
            ("human", "Query: {query}\n\nContext: {context}\n\nRelevance score:")
        ])
    
    def score_retrieval(self, query: str, docs: List[Document]) -> float:
        """
        Score relevance of retrieved documents.
        
        Args:
            query: User query
            docs: Retrieved documents
            
        Returns:
            Relevance score (0-1)
        """
        if not docs:
            return 0.0
        
        # Combine document contents
        context = "\n".join([doc.page_content for doc in docs[:3]])
        
        # Score relevance
        chain = self.relevance_prompt | self.llm
        result = chain.invoke({"query": query, "context": context})
        
        # Parse score from response
        try:
            score_line = result.content.strip().split('\n')[0]
            score = float(''.join(filter(str.isdigit, score_line)))
            return min(score / 10.0, 1.0)
        except:
            return 0.5  # Default if parsing fails
    
    def score_faithfulness(self, response: str, context: str) -> float:
        """
        Score faithfulness of response to context.
        
        Args:
            response: Generated response
            context: Retrieved context
            
        Returns:
            Faithfulness score (0-1)
        """
        chain = self.faithfulness_prompt | self.llm
        result = chain.invoke({"context": context, "response": response})
        
        # Check if response is faithful
        return 1.0 if 'yes' in result.content.lower() else 0.0
    
    def select_best_chunks(self, query: str, docs: List[Document], 
                          top_k: int = 5) -> List[Document]:
        """
        Select most relevant chunks using relevance scoring.
        
        Args:
            query: User query
            docs: Retrieved documents
            top_k: Number of top chunks to return
            
        Returns:
            Top-k most relevant documents
        """
        if len(docs) <= top_k:
            return docs
        
        # Score each document
        scored_docs = []
        for doc in docs:
            # Simple keyword matching score
            query_words = set(query.lower().split())
            doc_words = set(doc.page_content.lower().split())
            overlap = len(query_words & doc_words)
            score = overlap / max(len(query_words), 1)
            scored_docs.append((score, doc))
        
        # Sort and select top-k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k]]


def create_relevance_scorer() -> RelevanceScorer:
    """Factory function for relevance scorer."""
    return RelevanceScorer()
