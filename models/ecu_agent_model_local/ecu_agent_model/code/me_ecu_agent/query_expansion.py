"""
Query Expansion Module

OPTIMIZED (2026-03-30): Generates related queries to improve retrieval coverage.
Uses LLM to create alternative query formulations.
"""

from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class QueryExpander:
    """
    Expands user queries with related formulations to improve retrieval.

    Strategy:
    1. Rephrase query in different ways
    2. Add technical terminology
    3. Include alternative model references
    4. Generate comparison variants
    """

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)
        self.expansion_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a query expansion expert for Bosch ECU technical documentation. "
             "Generate 2-3 alternative formulations of the user's query. "
             "Rules: "
             "- Include technical synonyms (e.g., 'memory' -> 'RAM') "
             "- Add model variant alternatives (e.g., 'ECU-850' -> 'ECU-850 and ECU-850b') "
             "- Rephrase while keeping intent "
             "- Return one query per line, no numbering"),
            ("human", "Original query: {query}\n\nGenerate alternative queries:")
        ])

    def expand(self, query: str) -> List[str]:
        """
        Generate expanded queries.

        Args:
            query: Original user query

        Returns:
            List of original + expanded queries
        """
        # Generate alternatives
        chain = self.expansion_prompt | self.llm
        result = chain.invoke({"query": query})

        # Parse response
        alternatives = [line.strip() for line in result.content.split('\n')
                        if line.strip() and len(line.strip()) > 3]

        # Combine original with alternatives (max 4 total)
        expanded_queries = [query] + alternatives[:3]

        return list(set(expanded_queries))  # Remove duplicates


def create_query_expander() -> QueryExpander:
    """Factory function for query expander."""
    return QueryExpander()
