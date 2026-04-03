"""
Document Processing Module for ME ECU Agent.

This module provides functionality for loading and processing ECU documentation
with header-aware chunking and metadata enrichment.

Architecture Decision Record (ADR-001): Chunking Strategy
- Header-aware chunking preserves document structure
- 500 character chunks balance context completeness with retrieval precision
- 50 character overlap mitigates boundary information loss
"""

from pathlib import Path
from typing import List, Dict
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter


class DocumentProcessor:
    """
    Processes ECU documentation with header-aware chunking.

    This class implements a two-stage splitting strategy:
    1. Markdown header-based splitting (preserves document structure)
    2. Recursive character splitting (ensures chunks fit in context window)

    Attributes:
        chunk_size (int): Maximum characters per chunk (default: 500)
        chunk_overlap (int): Character overlap between chunks (default: 50)
        headers_to_split_on (list): Markdown headers to split on
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        headers_to_split_on: List[tuple] = None
    ):
        """
        Initialize the DocumentProcessor.

        Args:
            chunk_size: Maximum characters per chunk (default: 500 per ADR-001)
            chunk_overlap: Character overlap between chunks (default: 50 per ADR-001)
            headers_to_split_on: Markdown headers to split on (default: H1, H2, H3)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Default to splitting on H1, H2, H3 headers
        if headers_to_split_on is None:
            headers_to_split_on = [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]

        self.headers_to_split_on = headers_to_split_on

        # Initialize splitters
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def load_markdown_files(self, directory: Path) -> List[Document]:
        """
        Load all Markdown files from the specified directory.

        Args:
            directory: Path to directory containing .md files

        Returns:
            List of Documents with source file metadata

        Raises:
            FileNotFoundError: If directory doesn't exist
            ValueError: If no .md files found in directory
        """
        data_path = Path(directory)

        if not data_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        markdown_files = list(data_path.glob("*.md"))

        if not markdown_files:
            raise ValueError(f"No Markdown files found in {directory}")

        documents = []

        for file_path in sorted(markdown_files):
            # Try UTF-8 first, fallback to latin-1 for compatibility
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(file_path, "r", encoding="latin-1") as f:
                    content = f.read()

            # Create document with metadata
            doc = Document(
                page_content=content,
                metadata={
                    "source": file_path.name,
                    "file_path": str(file_path),
                }
            )
            documents.append(doc)

        return documents

    def split_by_headers(self, documents: List[Document]) -> List[Document]:
        """
        Split documents by Markdown headers to preserve structure.

        Args:
            documents: List of Documents to split

        Returns:
            List of Documents split by headers with enriched metadata
        """
        split_docs = []

        for doc in documents:
            # Split by markdown headers
            md_splits = self.markdown_splitter.split_text(doc.page_content)

            # Enrich metadata with header information
            for split_doc in md_splits:
                # Preserve original metadata
                split_doc.metadata.update(doc.metadata)

                # Add header context to metadata
                for header_name in ["Header 1", "Header 2", "Header 3"]:
                    if header_name in split_doc.metadata:
                        # Store headers for better context retrieval
                        split_doc.metadata[f"header_{header_name.lower().replace(' ', '_')}"] = \
                            split_doc.metadata[header_name]

                split_docs.append(split_doc)

        return split_docs

    def split_by_size(self, chunks: List[Document]) -> List[Document]:
        """
        Further split chunks by character size to ensure context window fit.

        Args:
            chunks: List of Documents to split

        Returns:
            List of Documents with appropriate chunk sizes
        """
        return self.text_splitter.split_documents(chunks)

    def separate_by_product_line(
        self,
        chunks: List[Document]
    ) -> Dict[str, List[Document]]:
        """
        Separate document chunks into ECU-700 and ECU-800 product lines.

        Args:
            chunks: List of Document chunks

        Returns:
            Dictionary with keys 'ECU-700' and 'ECU-800' containing respective chunks
        """
        product_lines = {
            "ECU-700": [],
            "ECU-800": [],
        }

        for chunk in chunks:
            source_file = chunk.metadata.get("source", "")

            if "700" in source_file:
                product_lines["ECU-700"].append(chunk)
            elif "800" in source_file:
                product_lines["ECU-800"].append(chunk)
            else:
                # Log warning but don't fail - handle gracefully
                print(f"Warning: Could not classify document {source_file} into ECU-700/800")

        return product_lines

    def process_documents(self, data_dir: str) -> Dict[str, List[Document]]:
        """
        Complete processing pipeline: load, split, and separate documents.

        This is the main entry point that orchestrates all processing steps.

        Args:
            data_dir: Path to directory containing ECU documentation

        Returns:
            Dictionary with 'ECU-700' and 'ECU-800' keys containing processed chunks

        Example:
            >>> processor = DocumentProcessor()
            >>> chunks = processor.process_documents("data/")
            >>> print(f"ECU-700 chunks: {len(chunks['ECU-700'])}")
            >>> print(f"ECU-800 chunks: {len(chunks['ECU-800'])}")
        """
        # Step 1: Load all Markdown files
        documents = self.load_markdown_files(Path(data_dir))

        # Step 2: Split by headers (preserve structure)
        header_splits = self.split_by_headers(documents)

        # Step 3: Split by size (ensure context window fit)
        size_splits = self.split_by_size(header_splits)

        # Step 4: Separate by product line
        product_chunks = self.separate_by_product_line(size_splits)

        return product_chunks


# Convenience function for backward compatibility
def load_and_split_documents(data_dir: str):
    """
    Legacy function for backward compatibility.

    Deprecated: Use DocumentProcessor.process_documents() instead.
    """
    processor = DocumentProcessor()
    product_chunks = processor.process_documents(data_dir)
    return product_chunks["ECU-700"], product_chunks["ECU-800"]
