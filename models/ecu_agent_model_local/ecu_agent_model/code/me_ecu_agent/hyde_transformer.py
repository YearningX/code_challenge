"""
HyDE (Hypothetical Document Embeddings) Module

OPTIMIZED (2026-03-30): Uses LLM-generated hypothetical answers
to improve retrieval accuracy for technical queries.

Paper: https://arxiv.org/abs/2212.10596
"""

from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class HyDETransformer:
    """
    Transforms queries into hypothetical documents for better retrieval.

    Strategy:
    1. Generate hypothetical answer using LLM
    2. Use hypothetical answer for vector similarity search
    3. Improves recall for technical specifications
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

        # HyDE prompt for generating hypothetical answers
        self.hyde_prompt = ChatPromptTemplate.from_messages([
            ("system", "Generate a concise technical answer with specific numbers and units."
             "Generate a hypothetical answer to the user's query. "
             "Requirements: "
             "- MUST include exact model names "
             "- MUST include specific numbers and units (e.g., 2GB, 1.7A) "
             "- Generate ONLY the technical answer, no preamble "
             "- Keep it to 1-2 concise sentences "
             "- Example: 'The ECU-850 has 2 GB LPDDR4 RAM operating at 1.2 GHz'"),
            ("human", "Query: {query}\n\nGenerate a hypothetical technical answer:")
        ])

    def transform(self, query: str) -> str:
        """
        Transform query into hypothetical document.

        Args:
            query: Original user query

        Returns:
            Hypothetical answer document
        """
        try:
            chain = self.hyde_prompt | self.llm
            result = chain.invoke({"query": query})
            hypothetical = result.content.strip()

            # Clean up the response
            if "hypothetical" in hypothetical.lower():
                hypothetical = hypothetical.split("hypothetical", 1)[0].strip()

            return hypothetical

        except Exception as e:
            # Fallback to original query if HyDE fails
            print(f"HyDE generation failed: {e}, using original query")
            return query

    def transform_multi(self, queries: List[str]) -> List[str]:
        """
        Transform multiple queries.

        Args:
            queries: List of queries

        Returns:
            List of hypothetical documents
        """
        hypotheticals = []
        for query in queries:
            hypothetical = self.transform(query)
            hypotheticals.append(hypothetical)
        return hypotheticals


def create_hyde_transformer() -> HyDETransformer:
    """Factory function for HyDE transformer."""
    return HyDETransformer()
