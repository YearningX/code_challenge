"""
Qwen Embeddings Wrapper

Compatible implementation for Qwen (DashScope) embeddings API.
Works around OpenAI SDK format incompatibilities.
"""

import os
from typing import List
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings


class QwenEmbeddings(Embeddings):
    """
    Qwen-specific embeddings wrapper that handles API compatibility.

    Qwen API has some differences from standard OpenAI API format.
    This wrapper ensures proper request formatting.
    """

    def __init__(
        self,
        model: str = "text-embedding-v2",
        qwen_api_key: str = None,
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    ):
        self.model = model
        self.api_key = qwen_api_key or os.getenv("QWEN_API_KEY")
        self.base_url = base_url

        # Initialize OpenAI embeddings with Qwen-compatible settings
        self._embeddings = OpenAIEmbeddings(
            model=model,
            api_key=self.api_key,
            base_url=base_url,
            # Qwen-specific: don't send extra parameters
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search documents."""
        try:
            # Call OpenAI embeddings - it will format for Qwen
            return self._embeddings.embed_documents(texts)
        except Exception as e:
            # If OpenAI SDK fails, try manual request
            return self._embed_with_fallback(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        try:
            return self._embeddings.embed_query(text)
        except Exception as e:
            # If OpenAI SDK fails, try manual request
            return self._embed_with_fallback([text])[0]

    def _embed_with_fallback(self, texts: List[str]) -> List[List[float]]:
        """
        Fallback method using direct HTTP requests to Qwen API.

        This bypasses OpenAI SDK formatting issues.
        """
        import requests

        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Qwen expects simple input format
        data = {
            "model": self.model,
            "input": texts  # Qwen expects list of strings directly
        }

        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()

        result = response.json()

        # Extract embeddings from response
        embeddings = []
        for item in result["data"]:
            embeddings.append(item["embedding"])

        return embeddings
