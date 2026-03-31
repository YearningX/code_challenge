"""
Test HyDE effectiveness on specific questions
"""
import sys
sys.path.insert(0, 'src')

from me_ecu_agent.hyde_transformer import create_hyde_transformer
from me_ecu_agent.document_processor import DocumentProcessor
from me_ecu_agent.vectorstore import VectorStoreManager
from me_ecu_agent.hyde_retriever import create_hyde_retriever


def test_hyde_transformation():
    """Test HyDE query transformation."""
    print("="*80)
    print("Testing HyDE Transformation")
    print("="*80)
    
    transformer = create_hyde_transformer()
    
    # Test queries
    queries = [
        "How much RAM does the ECU-850 have?",
        "What is the power consumption of the ECU-850b under load?",
        "Compare the CAN bus capabilities of ECU-750 and ECU-850."
    ]
    
    for query in queries:
        print(f"\nOriginal Query: {query}")
        hypothetical = transformer.transform(query)
        print(f"Hypothetical Answer: {hypothetical}")
        print("-" * 80)


def test_hyde_vs_baseline():
    """Compare HyDE vs baseline retrieval."""
    print("\n" + "="*80)
    print("Testing HyDE vs Baseline Retrieval")
    print("="*80)
    
    # Setup
    processor = DocumentProcessor()
    chunks = processor.process_documents("data")
    manager = VectorStoreManager()
    manager.create_stores(chunks)
    
    base_retriever = manager.get_retriever("ECU-800", k=5)
    hyde_retriever = create_hyde_retriever(base_retriever)
    
    # Test query
    query = "What is the power consumption of the ECU-850b under load?"
    
    print(f"\nQuery: {query}")
    print("-" * 80)
    
    # Baseline retrieval
    print("\nBaseline Retrieval:")
    base_docs = base_retriever.invoke(query)
    for i, doc in enumerate(base_docs[:3]):
        print(f"  {i+1}. {doc.page_content[:100]}...")
    
    # HyDE retrieval
    print("\nHyDE Retrieval:")
    hyde_docs = hyde_retriever.invoke(query)
    for i, doc in enumerate(hyde_docs[:3]):
        print(f"  {i+1}. {doc.page_content[:100]}...")
    
    # Compare
    base_content = " ".join([d.page_content for d in base_docs])
    hyde_content = " ".join([d.page_content for d in hyde_docs])
    
    # Check if power consumption mentioned
    if "1.7A" in hyde_content or "1.7 a" in hyde_content.lower():
        print("\n✅ HyDE found correct power consumption (1.7A)")
    else:
        print("\n⚠️  HyDE did not find 1.7A")
    
    if "1.7A" in base_content or "1.7 a" in base_content.lower():
        print("✅ Baseline found correct power consumption (1.7A)")
    else:
        print("⚠️  Baseline did not find 1.7A")


if __name__ == "__main__":
    test_hyde_transformation()
    test_hyde_vs_baseline()
