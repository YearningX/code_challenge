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
            # Result is a list of dictionaries with 'response' field
            response_text = result[0].get("response", "")
            logger.info(f"Model validation successful. Test response: {response_text[:100]}...")
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
        # Use relative path for cross-platform compatibility
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
        mlflow.set_tracking_uri(tracking_uri)
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

            # ============================================================
            # AUTO-SYNC: Copy new model to container mount point
            # ============================================================
            print("\n" + "="*60)
            print("Auto-Sync: Deploying new model to container...")
            print("="*60)

            # Define paths
            local_model_dir = Path("models/ecu_agent_model_local/ecu_agent_model")
            backup_dir = Path("models/ecu_agent_model_local/ecu_agent_model.backup")

            # Extract run ID from model URI
            run_id = run.info.run_id
            # MLflow stores models as: mlruns/<exp_id>/models/<model_id>/artifacts/
            # The artifacts folder contains the model files directly
            experiment_dirs = Path("mlruns").glob("*/")
            new_model_path = None

            for exp_dir in sorted(experiment_dirs, reverse=True):  # Latest first
                # Find all model directories
                for model_dir in exp_dir.glob("models/*/artifacts"):
                    # Check if this model has vector stores (indicates our model)
                    if list(model_dir.glob("artifacts/vector_stores_*")):
                        # This is our model
                        new_model_path = model_dir
                        logger.info(f"Found latest model: {new_model_path}")
                        break
                if new_model_path:
                    break

            # Check if new model exists in MLflow
            if new_model_path is None:
                logger.warning("New model path not found in MLflow artifacts")
                logger.info("Skipping auto-sync. Container will continue using old model.")
                print("[WARN] New model path not found. Skipping auto-sync.")
            elif not new_model_path.exists():
                logger.warning(f"New model not found at {new_model_path}")
                logger.info("Skipping auto-sync. Container will continue using old model.")
                print("[WARN] New model path not found. Skipping auto-sync.")
            else:
                print(f"New model location: {new_model_path}")
                print(f"Target location: {local_model_dir / 'artifacts'}")

                # Find the vector store directory in the new model
                vector_store_dirs = list(new_model_path.glob("artifacts/vector_stores_*"))
                if not vector_store_dirs:
                    logger.warning("No vector stores found in new model")
                    print("[WARN] No vector stores found in new model. Skipping auto-sync.")
                    return

                new_vector_store = vector_store_dirs[0]
                target_vector_store = local_model_dir / "artifacts" / new_vector_store.name

                # Initialize backup variable
                old_backup = None

                # Backup existing vector store if it exists
                if target_vector_store.exists():
                    print(f"\n[1/3] Backing up existing vector store...")
                    # Remove old backup if exists
                    old_backup = target_vector_store.parent / (new_vector_store.name + ".backup")
                    if old_backup.exists():
                        shutil.rmtree(old_backup)
                    # Create new backup
                    shutil.copytree(target_vector_store, old_backup)
                    print(f"     Backup created: {old_backup}")
                else:
                    print("\n[1/3] No existing vector store to backup (first deployment)")

                # Remove old vector store directory
                if target_vector_store.exists():
                    print(f"\n[2/3] Removing old vector store...")
                    shutil.rmtree(target_vector_store)
                    print(f"     Removed: {target_vector_store}")

                # Create target directory and copy new vector store
                print(f"\n[3/3] Copying new vector store...")
                target_vector_store.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(new_vector_store, target_vector_store)
                print(f"     Copied to: {target_vector_store}")

                print("\n" + "="*60)
                print("[SUCCESS] Vector store auto-sync completed!")
                print("="*60)
                print(f"New vector store is now active at: {target_vector_store}")
                print(f"Backup saved at: {old_backup if target_vector_store.exists() else 'N/A'}")
                print("\nNext steps:")
                print("  1. Restart container: docker compose restart ecu-assistant-api")
                print("  2. Verify: curl http://localhost:18500/api/health")
                print("\nTo rollback:")
                if target_vector_store.exists():
                    print(f"  mv {old_backup} {target_vector_store}")
                else:
                    print("  No backup to rollback")
                print("="*60 + "\n")

            # Clean up temp directory
            logger.info(f"Cleaning up temp directory: {temp_vector_dir}")
            shutil.rmtree(temp_vector_dir)

            # Print summary (simplified, details already shown above)
            print("\n" + "="*60)
            print("[OK] Vector Index Rebuild Completed")
            print("="*60)
            print(f"Model URI: {model_info.model_uri}")
            print(f"Run ID: {run.info.run_id}")
            print(f"Validation: {'[PASS]' if validation_passed else '[FAIL]'}")
            print(f"Total chunks: {len(ecu_700_docs) + len(ecu_800_docs)}")
            print(f"  - ECU-700: {len(ecu_700_docs)} chunks")
            print(f"  - ECU-800: {len(ecu_800_docs)} chunks")
            print("="*60 + "\n")

    except Exception as e:
        logger.error(f"Model logging failed: {e}")
        raise


if __name__ == "__main__":
    main()
