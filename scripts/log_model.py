import os
import shutil
import mlflow
from dotenv import load_dotenv

from me_ecu_agent.document_processor import load_and_split_documents
from me_ecu_agent.vectorstore import create_vector_stores, save_vector_stores
from me_ecu_agent.model import ECUAgentModel

def main():
    # Load environment variables (OpenAI API Key)
    load_dotenv()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables.")
        return

    print("Loading and splitting documents...")
    data_dir = "data"
    ecu_700_docs, ecu_800_docs = load_and_split_documents(data_dir)
    print(f"Loaded {len(ecu_700_docs)} chunks for ECU-700 and {len(ecu_800_docs)} chunks for ECU-800.")

    print("Building FAISS vector stores...")
    store_700, store_800 = create_vector_stores(ecu_700_docs, ecu_800_docs)
    
    # Save the vector stores to a local temporary directory for MLflow logging
    temp_vector_dir = "vector_stores_temp"
    if os.path.exists(temp_vector_dir):
        shutil.rmtree(temp_vector_dir)
    os.makedirs(temp_vector_dir)
    
    print(f"Saving vector stores to {temp_vector_dir}...")
    save_vector_stores(store_700, store_800, temp_vector_dir)

    print("Logging model to MLflow...")
    # Set the tracking URI to a local directory for testing, or rely on MLflow defaults
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("ME_ECU_Assistant")

    with mlflow.start_run() as run:
        artifacts = {
            "vector_stores": temp_vector_dir
        }
        
        # Log the custom PyFunc model
        model_info = mlflow.pyfunc.log_model(
            artifact_path="ecu_agent_model",
            python_model="scripts/entrypoint.py",
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
            ],
            signature=mlflow.models.signature.infer_signature(
                model_input={"query": "What is the operating temperature?"}, 
                model_output=["The operating temperature is..."]
            )
        )
        
        print("\n=== Model Logged Successfully ===")
        print(f"Model URI: {model_info.model_uri}")
        print(f"Run ID: {run.info.run_id}")
        print("\nTo test the model, you can run:")
        print(f'test_model = mlflow.pyfunc.load_model("{model_info.model_uri}")')
        print('print(test_model.predict({"query": "What is the max temp for ECU-850?"}))')

if __name__ == "__main__":
    main()
