# ME ECU Engineering Assistant Agent

This project implements a production-ready AI agent designed to assist engineers with questions about Electronic Control Unit (ECU) specifications across different product lines (ECU-700 and ECU-800 series).

## Architecture

The system is built using a **RAG (Retrieval-Augmented Generation)** architecture orchestrated by **LangGraph**, providing a modular and robust approach to multi-source documentation handling.

### Key Components

- **Intelligent Routing**: Uses LangGraph's `StateGraph` to autonomously select between ECU-700 and ECU-800 documentation based on the user's query.
- **RAG Engine**:
  - **Document Processor**: Parses Markdown files with header-aware splitting.
  - **Vector Storage**: Uses **FAISS** (in-memory) for sub-second retrieval.
  - **Embedding Model**: OpenAI `text-embedding-3-small` (local平替) or Databricks Embedding models.
- **MLOps Lifecycle**: 
  - **Packaging**: Standardized as a Python package (`me_ecu_agent`).
  - **Model Serving**: Logged as a **Custom MLflow PyFunc** model with a "Models from Code" approach to ensure portability and avoid serialization issues.
  - **DABs Integration**: Configured with Databricks Asset Bundles for automated deployment.

## Project Structure

```text
├── data/                    # ECU Markdown manuals and test questions
├── src/me_ecu_agent/        # Core agent logic
│   ├── document_processor.py # MD parsing and chunking
│   ├── vectorstore.py        # FAISS index management
│   ├── tools.py             # LangChain retriever tools
│   ├── graph.py              # LangGraph workflow definition
│   ├── model.py              # MLflow PyFunc wrapper
│   └── __init__.py
├── scripts/                 # Deployment and logging scripts
│   ├── log_model.py         # Build indices and log to MLflow
│   └── entrypoint.py        # MLflow model entrypoint
├── tests/                   # Evaluation framework
│   └── evaluate.py          # Batch evaluation script
├── databricks.yml           # DABs configuration
└── pyproject.toml           # Project dependencies
```

## Setup & Deployment

### 1. Environment Configuration
Ensure you have a `.env` file with your `OPENAI_API_KEY` (or configured Databricks secrets).

```bash
conda activate bosch
pip install -e .
```

### 2. Locally Log Model & Evaluate
Run the following commands to initialize the vector database and log the model to a local MLflow instance:

```bash
python scripts/log_model.py
python tests/evaluate.py
```

### 3. Deploy to Databricks (DABs)
To deploy as a Databricks Job, use the `databricks bundle` CLI:

```bash
databricks bundle deploy
```

## Testing & Validation Strategy

The project employs a tiered evaluation approach:
1. **Automated Batch Testing**: `tests/evaluate.py` runs all questions from `data/test-questions.csv` against the logged model.
2. **Metrics Tracking**: Each evaluation run logs `avg_latency_seconds` and response quality results as MLflow artifacts.
3. **Continuous Monitoring**: The system is designed to be integrated into CI/CD pipelines where the evaluation job triggers on every model change.

## Performance
- **Average Latency**: ~2.7s per query (Requirement: <10s)
- **Accuracy**: Successfully identifies correctly between ECU-750 (Legacy 700) and ECU-850/850b (Modern 800) specs.
