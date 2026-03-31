import os
import time
import pandas as pd
import mlflow
from dotenv import load_dotenv

def evaluate_model():
    """
    Evaluates the latest logged MLflow pyfunc model against test-questions.csv.
    Logs latency and accuracy metrics.
    """
    load_dotenv()
    
    csv_path = "data/test-questions.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    # Set tracking URI to our local DB
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("ME_ECU_Assistant")
    
    # Get the latest run that IS NOT an evaluation run
    runs = mlflow.search_runs(
        experiment_names=["ME_ECU_Assistant"], 
        filter_string="tags.mlflow.runName != 'agent_evaluation'",
        order_by=["start_time DESC"], 
        max_results=1
    )
    if runs.empty:
        print("No logged models found in MLflow. Run log_model.py first.")
        return
        
    latest_run_id = runs.iloc[0]["run_id"]
    model_uri = f"runs:/{latest_run_id}/ecu_agent_model"
    print(f"Loading latest model: {model_uri}")
    
    # Load model
    agent_model = mlflow.pyfunc.load_model(model_uri)
    
    # Load dataset
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} test questions.")
    
    results = []
    
    print("\n--- Starting Evaluation ---")
    for idx, row in df.iterrows():
        question = row["Question"]
        expected = row["Expected_Answer"]
        
        start_time = time.time()
        
        try:
            # Predict using our pyfunc model, passing it as a dictionary to match signature
            response = agent_model.predict({"query": question})[0]
        except Exception as e:
            response = str(e)
            
        latency = time.time() - start_time
        
        print(f"\nQ: {question}")
        print(f"Agent A ({latency:.2f}s): {response}")
        print(f"Expected: {expected}")
        
        results.append({
            "Question_ID": row["Question_ID"],
            "Question": question,
            "Expected_Answer": expected,
            "Agent_Response": response,
            "Latency_Seconds": latency
        })
        
        # Brief pause to avoid API rate limits
        time.sleep(1)

    print("\n--- Evaluation Complete ---")
    results_df = pd.DataFrame(results)
    avg_latency = results_df["Latency_Seconds"].mean()
    print(f"Average Response Time: {avg_latency:.2f} seconds")
    
    # Optionally use mlflow.evaluate to formally log the metrics
    # We will log the results dataframe as an artifact
    with mlflow.start_run(run_name="agent_evaluation") as eval_run:
        mlflow.log_metric("avg_latency_seconds", avg_latency)
        
        # Save detailed results to CSV and log it
        os.makedirs("eval_results", exist_ok=True)
        results_path = "eval_results/evaluation_results.csv"
        results_df.to_csv(results_path, index=False)
        mlflow.log_artifact(results_path, "evaluation_metrics")
        
        print(f"Evaluation metrics logged. Run ID: {eval_run.info.run_id}")

if __name__ == "__main__":
    evaluate_model()
