"""
Advanced HyDE with Multi-Hypothesis Generation

OPTIMIZED: Generates multiple hypothetical answers for better coverage.
"""

from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class AdvancedHyDE:
    """
    Advanced HyDE that generates multiple hypothetical answers.
    
    Strategy:
    1. Generate 3 different hypothetical answers
    2. Each with different focus (specs, comparison, explanation)
    3. Use all for retrieval to maximize coverage
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
        
        self.spec_prompt = ChatPromptTemplate.from_messages([
            ("system", "Generate a concise technical specification answer. Include exact numbers and units. Example: 'The ECU-850 has 2 GB LPDDR4 RAM'"),
            ("human", "Query: {query}")
        ])
        
        self.comparison_prompt = ChatPromptTemplate.from_messages([
            ("system", "Generate a comparison-focused answer. Contrast between models. Example: 'ECU-750 has X while ECU-850 has Y'"),
            ("human", "Query: {query}")
        ])
    
    def transform(self, query: str) -> List[str]:
        """Generate multiple hypothetical answers."""
        hypotheticals = []
        
        # Generate spec-focused answer
        try:
            chain = self.spec_prompt | self.llm
            result = chain.invoke({"query": query})
            hypotheticals.append(result.content.strip())
        except:
            pass
        
        # Generate comparison-focused answer
        try:
            chain = self.comparison_prompt | self.llm
            result = chain.invoke({"query": query})
            hypotheticals.append(result.content.strip())
        except:
            pass
        
        # Always include original query
        hypotheticals.append(query)
        
        return hypotheticals[:3]  # Max 3 variants


def create_advanced_hyde() -> AdvancedHyDE:
    return AdvancedHyDE()
