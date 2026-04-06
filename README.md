# ME ECU Engineering Assistant Agent

A production-ready AI agent for answering technical questions about Bosch ECU (Electronic Control Unit) specifications across ECU-700 and ECU-800 product lines.

## 🚀 Key Features

- **🤖 Intelligent Query Routing**: Automatically detects product line (ECU-700 vs ECU-800) and routes to relevant documentation
- **⚡ Smart Query Expansion**: Skips unnecessary LLM calls for simple queries (75% reduction in API calls)
- **🔍 Optimized Retrieval**: Hybrid vector + keyword search with adaptive depth (k=6/10)
- **🌍 Dual LLM Support**: Works with both Qwen (Alibaba Cloud) and OpenAI for flexible deployment
- **📊 Real-time Observability**: Integrated with Langfuse for detailed tracing and performance monitoring
- **🐳 Docker-Ready**: One-command deployment with Docker Compose
- **🎨 Web UI**: Interactive interface for testing and evaluation

## 🏗️ Architecture

Built with **RAG (Retrieval-Augmented Generation)** orchestrated by **LangGraph**:

```
User Query → Query Analysis → Product Line Detection → Smart Expansion → Parallel Retrieval → Response Synthesis
```

### Core Components

- **Intelligent Routing**: LangGraph StateGraph for autonomous product line selection
- **Smart Query Expansion**: 
  - Simple queries (single model, direct questions) → No expansion
  - Complex queries (comparisons, cross-model) → 1 alternative query
- **RAG Engine**:
  - **Hybrid Retrieval**: FAISS vector search + BM25 keyword matching
  - **Adaptive Depth**: ECU-700 (k=6), ECU-800 (k=10)
  - **Embedding Models**: Qwen text-embedding-v2 or OpenAI embeddings
- **MLOps Pipeline**:
  - MLflow PyFunc packaging
  - Docker containerization
  - Langfuse tracing integration

## 📁 Project Structure

```text
├── data/                           # ECU documentation and test questions
│   ├── ECU-700_Series_Manual.md   # ECU-700 specifications
│   ├── ECU-800_Series_Base.md     # ECU-850 specifications
│   └── ECU-800_Series_Plus.md     # ECU-850b specifications
├── src/me_ecu_agent/              # Core agent logic
│   ├── graph.py                   # LangGraph workflow with smart routing
│   ├── query_expansion.py         # Intelligent query expansion
│   ├── hybrid_retrieval.py        # Hybrid vector + keyword search
│   ├── model_config.py            # Multi-provider LLM configuration
│   └── vectorstore.py             # FAISS index management
├── web/                           # FastAPI web server
│   ├── api_server.py              # REST API endpoints
│   ├── index.html                 # Interactive web UI
│   └── Dockerfile                 # Container configuration
├── models/ecu_agent_model_local/  # MLflow packaged model
└── docker-compose.yml             # One-command deployment
```

## ⚙️ Setup & Deployment

### Quick Start with Docker

1. **Clone and configure:**
```bash
git clone <repository-url>
cd BOSCH_Code_Challenge
cp .env.example .env
```

2. **Configure API keys** (edit `.env`):
```bash
# For Qwen (Alibaba Cloud) - Recommended for China
LLM_PROVIDER=qwen
QWEN_API_KEY=your-qwen-api-key
EMBEDDING_MODEL=text-embedding-v2

# OR for OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
```

3. **Deploy with Docker:**
```bash
docker compose up -d
```

4. **Access the UI:**
```
http://localhost:18500
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
cd web
python api_server.py
```

## 🧪 Testing

### Automated Evaluation

Run the built-in test suite:

```bash
# Via Web UI
# Navigate to http://localhost:18500 and click "Run Evaluation"

# Or via API
curl http://localhost:18500/api/evaluate
```

### Test Questions

The system includes 10 predefined test questions covering:
- Single-source queries (ECU-700 or ECU-800)
- Cross-series comparisons
- Technical specifications
- Feature availability queries

## 📊 Performance

### Optimization Impact

| Feature | Before | After | Improvement |
|---------|--------|-------|-------------|
| **Simple Query LLM Calls** | 4 calls | 1 call | **75% ↓** |
| **Complex Query LLM Calls** | 4 calls | 2 calls | **50% ↓** |
| **Retrieval Depth** | k=8/12 | k=6/10 | **25% ↓** |
| **First Query Latency** | ~10s | ~10s | Model loading |
| **Subsequent Queries** | ~10s | ~5-7s | **30-50% ↓** |

### Benchmarks

- **Average Latency**: 5-7 seconds (after model loading)
- **Product Line Detection**: 100% accuracy
- **Query Success Rate**: >95% on test set
- **Simple Query Ratio**: ~80% of typical queries

## 🔍 Observability

Integrated with **Langfuse** for detailed tracing:

- Query analysis timing
- Retrieval performance
- LLM call latency
- Token usage tracking
- Error tracking

Access traces at: `https://langfuse.cccoder.top`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | qwen, openai, or auto | `qwen` |
| `LLM_MODEL` | qwen-plus, qwen-turbo, gpt-3.5-turbo | `qwen-plus` |
| `EMBEDDING_MODEL` | text-embedding-v2, v3, ada-002 | `text-embedding-v2` |
| `API_PORT` | Server port | `18500` |
| `LANGFUSE_SECRET_KEY` | Observability tracking | Required |

### Model Selection

**Qwen Models** (Alibaba Cloud):
- `qwen-plus`: Balanced quality and speed (default)
- `qwen-turbo`: Faster for simple queries
- `qwen-max`: Highest quality

**OpenAI Models**:
- `gpt-3.5-turbo`: Fast and cost-effective
- `gpt-4`: Highest quality

## 🐛 Troubleshooting

### Common Issues

**Problem**: "No relevant content found"
- **Solution**: Check vector stores are loaded in `models/ecu_agent_model_local/ecu_agent_model/artifacts/`

**Problem**: High latency (>10s)
- **Solution**: First query includes model loading (~8s). Subsequent queries should be faster.

**Problem**: API key errors
- **Solution**: Verify `QWEN_API_KEY` or `OPENAI_API_KEY` in `.env` file

## 📈 Recent Improvements

### v1.2.0 (Current)
- ✨ Smart query expansion (skip for simple queries)
- ⚡ Optimized retrieval depth (k=6/10)
- 🔧 Fixed critical retrieval bugs
- 📊 Enhanced Langfuse integration

### v1.1.0
- 🌍 Qwen/Alibaba Cloud integration
- 🐳 Docker deployment support
- 🎨 Web UI with evaluation tools

## 🤝 Contributing

This is a coding challenge project. For suggestions or issues:
1. Check existing documentation in `web/*.md`
2. Review Langfuse traces for performance insights
3. Test with the 10 predefined questions

## 📄 License

Proprietary - Bosch Coding Challenge Project

## 🙏 Acknowledgments

Built with:
- **LangGraph** - Agent workflow orchestration
- **LangChain** - RAG framework
- **FAISS** - Vector similarity search
- **Qwen (Alibaba Cloud)** - LLM provider
- **Langfuse** - LLM observability
