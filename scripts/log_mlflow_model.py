"""
Enhanced MLflow Model Logging Script

OPTIMIZED (2026-03-31): Production-ready model logging with comprehensive
metadata, parameters, and validation.

Features:
- Automatic model signature inference
- Parameter and metric logging
- Vector store artifact management
- Model validation before logging
- Detailed logging and error handling
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Tuple

import mlflow
import mlflow.models.signature
from dotenv import load_dotenv
from langchain_core.documents import Document

from me_ecu_agent.config import ChunkingConfig, LLMConfig, RetrievalConfig
from me_ecu_agent.document_processor import load_and_split_documents
from me_ecu_agent.vectorstore import create_vector_stores, save_vector_stores
from me_ecu_agent.mlflow_model import ECUAgentMLflowModel


# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_environment() -> None:
    """
    Validate that required environment variables are set.

    Raises:
        ValueError: If required environment variables are missing
    """
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    logger.info("Environment validation passed")


def load_documents(data_dir: str) -> Tuple[list[Document], list[Document]]:
    """
    Load and split ECU documents.

    Args:
        data_dir: Path to data directory containing markdown files

    Returns:
        Tuple of (ecu_700_docs, ecu_800_docs)

    Raises:
        FileNotFoundError: If data directory doesn't exist
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    logger.info(f"Loading documents from {data_dir}...")
    ecu_700_docs, ecu_800_docs = load_and_split_documents(data_dir)

    logger.info(
        f"Loaded {len(ecu_700_docs)} chunks for ECU-700 "
        f"and {len(ecu_800_docs)} chunks for ECU-800"
    )

    return ecu_700_docs, ecu_800_docs


def create_and_save_vector_stores(
    ecu_700_docs: list[Document],
    ecu_800_docs: list[Document],
    temp_dir: str
) -> None:
    """
    Create FAISS vector stores and save to temporary directory.

    Args:
        ecu_700_docs: ECU-700 document chunks
        ecu_800_docs: ECU-800 document chunks
        temp_dir: Temporary directory for saving vector stores
    """
    logger.info("Building FAISS vector stores...")
    store_700, store_800 = create_vector_stores(ecu_700_docs, ecu_800_docs)

    # Clean and create temp directory
    if os.path.exists(temp_dir):
        logger.info(f"Cleaning existing temp directory: {temp_dir}")
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    logger.info(f"Saving vector stores to {temp_dir}...")
    save_vector_stores(store_700, store_800, temp_dir)

    # Log vector store sizes
    store_700_size = sum(
        os.path.getsize(os.path.join(temp_dir, f))
        for f in os.listdir(temp_dir)
        if f.startswith("ecu700")
    )
    store_800_size = sum(
        os.path.getsize(os.path.join(temp_dir, f))
        for f in os.listdir(temp_dir)
        if f.startswith("ecu800")
    )

    logger.info(f"Vector store sizes - ECU-700: {store_700_size / 1024:.2f} KB, "
                f"ECU-800: {store_800_size / 1024:.2f} KB")


def log_model_parameters(configs: dict) -> None:
    """
    Log model configuration parameters to MLflow.

    Args:
        configs: Dictionary of configuration objects
    """
    logger.info("Logging model parameters...")

    # Chunking parameters
    chunking = configs["chunking"]
    mlflow.log_params({
        "chunk_size": chunking.chunk_size,
        "chunk_overlap": chunking.chunk_overlap,
    })

    # Retrieval parameters
    retrieval = configs["retrieval"]
    mlflow.log_params({
        "ecu_700_k": retrieval.ecu700_k,
        "ecu_800_k": retrieval.ecu800_k,
    })

    # LLM parameters
    llm = configs["llm"]
    mlflow.log_params({
        "model_name": llm.model_name,
        "temperature": llm.temperature,
        "max_tokens": llm.max_tokens
    })


def log_model_metrics(ecu_700_docs: list[Document], ecu_800_docs: list[Document]) -> None:
    """
    Log model metrics to MLflow.

    Args:
        ecu_700_docs: ECU-700 document chunks
        ecu_800_docs: ECU-800 document chunks
    """
    logger.info("Logging model metrics...")

    mlflow.log_metrics({
        "total_chunks": len(ecu_700_docs) + len(ecu_800_docs),
        "ecu_700_chunks": len(ecu_700_docs),
        "ecu_800_chunks": len(ecu_800_docs),
        "chunk_ratio": len(ecu_800_docs) / max(len(ecu_700_docs), 1)
    })


def infer_model_signature() -> mlflow.models.signature.ModelSignature:
    """
    Infer model signature from example inputs and outputs.

    Returns:
        ModelSignature object
    """
    logger.info("Inferring model signature...")

    # Example inputs
    example_inputs = [
        {"query": "What is the maximum operating temperature for ECU-750?"},
        {"query": "Compare ECU-850 and ECU-850b"}
    ]

    # Example outputs
    example_outputs = [
        ["The maximum operating temperature for ECU-750 is +85°C."],
        ["ECU-850b has three key upgrades compared to ECU-850..."]
    ]

    signature = mlflow.models.signature.infer_signature(
        model_input=example_inputs,
        model_output=example_outputs
    )

    logger.info(f"Model signature inferred: {signature}")
    return signature


def validate_model(model_uri: str) -> bool:
    """
    Validate logged model by loading and running test prediction.

    Args:
        model_uri: MLflow model URI

    Returns:
        True if validation successful, False otherwise
    """
    try:
        logger.info("Validating logged model...")

        # Load model
        model = mlflow.pyfunc.load_model(model_uri)

        # Test prediction
        test_query = {"query": "What is ECU-850?"}
        result = model.predict(test_query)

        if result and len(result) > 0:
            logger.info(f"Model validation successful. Test response: {result[0][:100]}...")
            return True
        else:
            logger.warning("Model validation returned empty response")
            return False

    except Exception as e:
        logger.error(f"Model validation failed: {e}")
        return False


def main():
    """
    Main function to build and log MLflow model.
    """
    try:
        # Load environment variables
        load_dotenv()

        # Validate environment
        validate_environment()

        # Configure MLflow
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        mlflow.set_experiment("ME_ECU_Assistant")

        logger.info("Starting MLflow model logging...")

        with mlflow.start_run() as run:
            logger.info(f"MLflow run started: {run.info.run_id}")

            # Load documents
            ecu_700_docs, ecu_800_docs = load_documents("data")

            # Create and save vector stores
            temp_vector_dir = tempfile.mkdtemp(prefix="vector_stores_")
            create_and_save_vector_stores(ecu_700_docs, ecu_800_docs, temp_vector_dir)

            # Log parameters and metrics
            configs = {
                "chunking": ChunkingConfig(),
                "retrieval": RetrievalConfig(),
                "llm": LLMConfig()
            }
            log_model_parameters(configs)
            log_model_metrics(ecu_700_docs, ecu_800_docs)

            # Infer model signature
            signature = infer_model_signature()

            # Define artifacts
            artifacts = {
                "vector_stores": temp_vector_dir
            }

            # Log model
            logger.info("Logging model to MLflow...")
            model_info = mlflow.pyfunc.log_model(
                artifact_path="ecu_agent_model",
                python_model=ECUAgentMLflowModel(),
                code_paths=["src/me_ecu_agent"],
                artifacts=artifacts,
                pip_requirements=[
                    "langchain>=0.2.0",
                    "langchain-openai>=0.1.0",
                    "langchain-community>=0.2.0",
                    "langchain-core>=0.2.0",
                    "langgraph>=0.1.0",
                    "faiss-cpu>=1.8.0",
                    "mlflow>=2.14.0",
                    "tiktoken>=0.7.0",
                    "python-dotenv>=1.0.0",
                ],
                signature=signature,
                input_example={"query": "What is the operating temperature?"}
            )

            # Validate model
            validation_passed = validate_model(model_info.model_uri)

            # Log validation result
            mlflow.log_metric("validation_passed", 1 if validation_passed else 0)

            # Clean up temp directory
            logger.info(f"Cleaning up temp directory: {temp_vector_dir}")
            shutil.rmtree(temp_vector_dir)

            # Print summary
            print("\n" + "="*60)
            print("[OK] Model Logged Successfully")
            print("="*60)
            print(f"Model URI: {model_info.model_uri}")
            print(f"Run ID: {run.info.run_id}")
            print(f"Experiment: ME_ECU_Assistant")
            print(f"Validation: {'[PASS]' if validation_passed else '[FAIL]'}")
            print("\nModel Statistics:")
            print(f"  - Total chunks: {len(ecu_700_docs) + len(ecu_800_docs)}")
            print(f"  - ECU-700 chunks: {len(ecu_700_docs)}")
            print(f"  - ECU-800 chunks: {len(ecu_800_docs)}")
            print("\nTesting Commands:")
            print(f'  import mlflow.pyfunc')
            print(f'  model = mlflow.pyfunc.load_model("{model_info.model_uri}")')
            print(f'  result = model.predict({{"query": "What is ECU-850?"}})')
            print(f'  print(result)')
            print("\nServing Command:")
            print(f'  mlflow models serve -m "{model_info.model_uri}" -p 5000')
            print("="*60 + "\n")

    except Exception as e:
        logger.error(f"Model logging failed: {e}")
        raise


if __name__ == "__main__":
    main()
