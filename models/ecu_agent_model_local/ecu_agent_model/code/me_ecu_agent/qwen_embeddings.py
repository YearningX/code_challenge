"""
Qwen Embeddings - Custom implementation for LangChain compatibility

Direct call to Qwen/Alibaba Cloud embeddings API, independent of OpenAI format.
"""

import os
from typing import List
from langchain.embeddings.base import Embeddings
from pydantic import BaseModel, Field


class QwenEmbeddings(BaseModel, Embeddings):
    """
    Qwen embeddings implementation for LangChain.

    Direct call to DashScope API using Qwen's text-embedding-v2 model.
    """

    # Qwen API configuration
    api_key: str = Field(..., description="Qwen/DashScope API key")
    base_url: str = Field(
        default="https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding",
        description="Qwen embeddings API endpoint"
    )
    model: str = Field(default="text-embedding-v2", description="Embedding model name")

    class Config:
        arbitrary_types_allowed = True

    def _embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        import requests

        embeddings = []
        for text in texts:
            try:
                response = requests.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "input": {
                            "texts": [text]
                        }
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    embedding = result["output"]["embeddings"][0]["embedding"]
                    embeddings.append(embedding)
                else:
                    raise Exception(f"Qwen API error: {response.status_code} - {response.text}")

            except Exception as e:
                print(f"Error embedding document: {e}")
                # Return zero vector on error
                embeddings.append([0.0] * 1536)

        return embeddings

    def _embed_query(self, text: str) -> List[float]:
        """Embed a query string."""
        return self._embed_documents([text])[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents using Qwen API.

        Args:
            texts: List of text documents to embed

        Returns:
            List of embedding vectors
        """
        print(f"Embedding {len(texts)} documents with Qwen {self.model}...")
        return self._embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed a query text using Qwen API.

        Args:
            text: Query text to embed

        Returns:
            Embedding vector
        """
        return self._embed_query(text)


def create_qwen_embeddings(api_key: str = None, base_url: str = None) -> QwenEmbeddings:
    """
    Factory function to create Qwen embeddings instance.

    Args:
        api_key: Qwen API key (defaults to QWEN_API_KEY env var)
        base_url: Custom base URL (optional)

    Returns:
        QwenEmbeddings instance
    """
    if api_key is None:
        api_key = os.getenv("QWEN_API_KEY")

    if not api_key:
        raise ValueError("QWEN_API_KEY not configured")

    return QwenEmbeddings(
        api_key=api_key,
        base_url=base_url or "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding",
        model="text-embedding-v2"
    )
