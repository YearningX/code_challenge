import mlflow

class ECUAgentModel(mlflow.pyfunc.PythonModel):
    """
    MLflow custom PyFunc wrapper for the LangGraph ECU Agent.
    """
    def load_context(self, context):
        """
        Loads the FAISS indices from the model context.
        """
        # Move imports here to avoid serialization issues
        from me_ecu_agent.vectorstore import load_vector_stores
        from me_ecu_agent.tools import get_agent_tools
        from me_ecu_agent.graph import build_graph
        
        # The vector stores directory will be saved as an artifact
        vector_store_dir = context.artifacts["vector_stores"]
        
        # Load indexes
        store_700, store_800 = load_vector_stores(vector_store_dir)
        
        # Build tools logic
        tools = get_agent_tools(store_700, store_800)
        
        # Compile graph
        self.graph = build_graph(tools)

    def predict(self, context, model_input):
        """
        Takes a query and executes the LangGraph agent to produce a response.
        `model_input` can be a string, list of strings, or a pandas DataFrame.
        """
        import pandas as pd
        from langchain_core.messages import HumanMessage
        
        # Handle different input formats cleanly
        queries = []
        if isinstance(model_input, pd.DataFrame):
            # Assuming the question is in a column named "query" or first column
            if "query" in model_input.columns:
                queries = model_input["query"].tolist()
            else:
                queries = model_input.iloc[:, 0].tolist()
        elif isinstance(model_input, list):
            queries = model_input
        elif isinstance(model_input, str):
            queries = [model_input]
        elif isinstance(model_input, dict):
            # Single dictionary input
            queries = [model_input.get("query", "")]
        else:
            raise ValueError(f"Unsupported input type: {type(model_input)}")

        responses = []
        for query in queries:
            try:
                # Prepare initial state
                initial_state = {
                    "messages": [HumanMessage(content=query)]
                }
                
                # Execute graph
                # Using invoke for a full un-streamed run
                result = self.graph.invoke(initial_state)
                
                # Extract the last AI response
                last_message = result["messages"][-1]
                responses.append(last_message.content)
                
            except Exception as e:
                # Fallback on errors to prevent full batch failure
                responses.append(f"Error executing agent: {str(e)}")

        return responses
