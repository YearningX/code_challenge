"""
Unit tests for DocumentProcessor module.

Tests Story 1.1 acceptance criteria:
- Load all Markdown files successfully
- Split using header-aware chunking
- Create chunks of 500 chars with 50 overlap
- Separate by product line
- Enrich metadata
- Pylint score >85%
"""

import pytest
from pathlib import Path
from me_ecu_agent.document_processor import DocumentProcessor, load_and_split_documents


class TestDocumentProcessor:
    """Test suite for DocumentProcessor class."""

    @pytest.fixture
    def processor(self):
        """Create a DocumentProcessor instance for testing."""
        return DocumentProcessor(
            chunk_size=500,
            chunk_overlap=50,
        )

    @pytest.fixture
    def data_dir(self, tmp_path):
        """
        Create temporary directory with test Markdown files.

        Creates 3 test files simulating ECU documentation structure.
        """
        # Create ECU-700 test document
        ecu700_content = """# ECU-750 Specifications

## Processor
ARM Cortex-A53 quad-core processor

## Memory
2GB DDR4

## CAN Interface
Single CAN channel at 1Mbps

## Operating Temperature
Maximum 85°C
"""
        (tmp_path / "ECU-700_Series_Manual.md").write_text(ecu700_content)

        # Create ECU-800 test documents
        ecu800_base_content = """# ECU-850 Specifications

## Processor
ARM Cortex-A72 quad-core processor

## Memory
4GB DDR4

## CAN Interface
Dual CAN channels at 2Mbps

## Operating Temperature
Maximum 105°C
"""
        (tmp_path / "ECU-800_Series_Base.md").write_text(ecu800_base_content)

        ecu800_plus_content = """# ECU-850b Specifications

## Processor
ARM Cortex-A72 with AI acceleration

## Memory
8GB DDR4

## AI Capabilities
Neural processing unit for edge AI

## Operating Temperature
Maximum 105°C
"""
        (tmp_path / "ECU-800_Series_Plus.md").write_text(ecu800_plus_content)

        return tmp_path

    def test_load_markdown_files_success(self, processor, data_dir):
        """
        AC: Load all Markdown files successfully.
        Given: Valid data directory with .md files
        When: load_markdown_files() is called
        Then: Returns list of Documents
        And: All 3 files are loaded
        """
        documents = processor.load_markdown_files(data_dir)

        assert len(documents) == 3
        assert all(doc.metadata.get("source") for doc in documents)

    def test_split_by_size_respects_limits(self, processor, data_dir):
        """
        AC: Create chunks of 500 characters with 50-character overlap.
        Given: Documents of various sizes
        When: split_by_size() is called
        Then: All chunks are <= 500 characters
        """
        documents = processor.load_markdown_files(data_dir)
        header_splits = processor.split_by_headers(documents)
        size_splits = processor.split_by_size(header_splits)

        for chunk in size_splits:
            chunk_length = len(chunk.page_content)
            assert chunk_length <= 500, f"Chunk length {chunk_length} exceeds 500"

    def test_separate_by_product_line(self, processor, data_dir):
        """
        AC: Separate chunks by product line (ECU-700 vs ECU-800).
        Given: Document chunks from multiple files
        When: separate_by_product_line() is called
        Then: Returns dictionary with 'ECU-700' and 'ECU-800' keys
        And: Chunks are correctly classified
        """
        documents = processor.load_markdown_files(data_dir)
        header_splits = processor.split_by_headers(documents)
        size_splits = processor.split_by_size(header_splits)
        product_chunks = processor.separate_by_product_line(size_splits)

        assert "ECU-700" in product_chunks
        assert "ECU-800" in product_chunks
        assert len(product_chunks["ECU-700"]) > 0
        assert len(product_chunks["ECU-800"]) > 0

    def test_process_documents_end_to_end(self, processor, data_dir):
        """
        AC: Complete processing pipeline works correctly.
        Given: Data directory with ECU documentation
        When: process_documents() is called
        Then: Returns dictionary with processed chunks
        And: Chunks have enriched metadata
        And: Chunk sizes respect limits
        """
        result = processor.process_documents(str(data_dir))

        assert "ECU-700" in result
        assert "ECU-800" in result
        assert len(result["ECU-700"]) > 0
        assert len(result["ECU-800"]) > 0

        # Verify all chunks have required metadata
        for product_line in ["ECU-700", "ECU-800"]:
            for chunk in result[product_line]:
                assert "source" in chunk.metadata
                assert "file_path" in chunk.metadata
                assert len(chunk.page_content) <= 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
