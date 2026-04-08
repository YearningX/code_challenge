"""
Query Expansion Module

OPTIMIZED (2026-03-30): Generates related queries to improve retrieval coverage.
Uses LLM to create alternative query formulations.

SMART STRATEGY (2026-04-06): Only expand complex queries to optimize performance.
"""

from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import re


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
        from me_ecu_agent.model_config import get_model_config
        model_config = get_model_config()
        self.llm = ChatOpenAI(
            model=model_config.model_name,
            api_key=model_config.api_key,
            base_url=model_config.base_url,
            temperature=0.0
        )
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

    def is_simple_query(self, query: str) -> bool:
        """
        Determine if a query is simple enough to skip expansion.

        OPTIMIZED (2026-04-08): Now treats ECU-850 vs ECU-850b comparisons as simple
        since they're within the same product family.

        Simple queries (NO expansion needed):
        - Single model, single attribute lookup
        - Direct questions (What is X of ECU-850?)
        - ECU-850 vs ECU-850b comparisons (same family!)
        - Short and specific

        Complex queries (expansion recommended):
        - Cross-family comparisons (ECU-750 vs ECU-850)
        - Cross-model analysis (all models, each, across)
        - Multiple unrelated model mentions
        - Open-ended aggregation

        Returns:
            True if query is simple (no expansion needed)
        """
        query_lower = query.lower()

        # ECU-850 vs ECU-850b is now considered SIMPLE (same family)
        if ('ecu-850' in query_lower or '850' in query_lower) and \
           'ecu-850b' in query_lower or '850b' in query_lower:
            # Check if it's ONLY comparing 850 and 850b (no 750)
            if 'ecu-750' not in query_lower and '750' not in query_lower:
                return True

        # Strong complexity indicators - these definitely need expansion
        strong_complex_keywords = [
            'compare', 'difference', 'versus', 'vs', 'vary',
            'across', 'all models', 'all ecu', 'each model', 'every'
        ]

        for keyword in strong_complex_keywords:
            if keyword in query_lower:
                # Exception: if it's just 850 vs 850b, still simple
                if 'ecu-750' not in query_lower and '750' not in query_lower:
                    return True
                return False

        # Check for multiple model mentions (but allow ECU-850 and ECU-850b)
        model_count = 0
        if 'ecu-750' in query_lower or '750' in query_lower:
            model_count += 1
        # Only count 850 if 850b is NOT present (they're related)
        if 'ecu-850' in query_lower or '850' in query_lower:
            if '850b' not in query_lower:
                model_count += 1
        if 'ecu-850b' in query_lower or '850b' in query_lower:
            model_count += 1

        if model_count > 1:
            return False

        # Check query length
        if len(query) > 80:
            return False

        # Default: treat as simple
        return True

    def expand(self, query: str) -> List[str]:
        """
        Generate expanded queries.

        Args:
            query: Original user query

        Returns:
            List of original + expanded queries
        """
        # Skip expansion for simple queries
        if self.is_simple_query(query):
            return [query]

        # Generate alternatives for complex queries
        chain = self.expansion_prompt | self.llm
        result = chain.invoke({"query": query})

        # Parse response
        alternatives = [line.strip() for line in result.content.split('\n')
                        if line.strip() and len(line.strip()) > 3]

        # Combine original with alternatives (max 2 total for performance)
        expanded_queries = [query] + alternatives[:1]

        return list(set(expanded_queries))  # Remove duplicates


def create_query_expander() -> QueryExpander:
    """Factory function for query expander."""
    return QueryExpander()
