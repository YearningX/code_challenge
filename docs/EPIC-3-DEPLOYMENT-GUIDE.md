# Epic 3: Enterprise Deployment Automation - Deployment Guide

**Date**: 2026-03-31
**Version**: 0.2.0
**Status**: ✅ IMPLEMENTATION COMPLETE

---

## Overview

Epic 3 implements enterprise-grade deployment automation for the ME ECU Agent using Databricks Asset Bundles (DAB), providing multi-environment support, automated deployment pipelines, and production-ready configuration.

---

## Architecture

### Deployment Components

```
databricks.yml              # DAB configuration
├── targets/
│   ├── dev                # Development environment
│   ├── staging            # Staging environment
│   └── prod               # Production environment
├── resources/
│   ├── models/            # MLflow model definitions
│   ├── jobs/              # Databricks job definitions
│   └── experiments/       # MLflow experiments
└── variables/            # Environment-specific configuration

scripts/deployment/
├── validate_environment.py  # Environment validation
├── validate_model.py        # Model validation
└── deploy.sh                # Deployment automation
```

---

## Environments

### 1. Development (dev)

**Purpose**: Local development and testing

**Configuration**:
- Mode: development
- Validation: disabled
- Schedule: manual trigger only
- Notifications: failure only

**Deployment Command**:
```bash
databricks bundle deploy --target=dev
```

### 2. Staging (staging)

**Purpose**: Pre-production testing

**Configuration**:
- Mode: staging
- Validation: enabled
- Schedule: Weekdays at 6 AM UTC
- Notifications: success and failure

**Deployment Command**:
```bash
databricks bundle deploy --target=staging
```

### 3. Production (prod)

**Purpose**: Production deployment

**Configuration**:
- Mode: production
- Validation: enabled
- Schedule: Daily at 2 AM UTC
- Notifications: success and failure
- Auto-deploy: disabled (requires approval)

**Deployment Command**:
```bash
databricks bundle deploy --target=prod
```

---

## Deployment Pipeline

### Automated Job Workflow

```
┌─────────────────────────────────────────────────────────────┐
│              ME ECU Agent - Build and Log Model              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Task 1: validate_environment                                │
│  - Check Python version (>=3.10)                             │
│  - Verify environment variables (OPENAI_API_KEY, etc.)      │
│  - Validate dependencies (MLflow, LangChain, etc.)           │
│  - Test MLflow connection                                    │
│  - Check file structure                                      │
│  Timeout: 10 minutes                                         │
│                                                               │
│           │                                                 │
│           ▼                                                 │
│                                                               │
│  Task 2: build_and_log                                       │
│  - Load ECU documentation                                    │
│  - Create FAISS vector stores                                │
│  - Initialize LangGraph agent                                 │
│  - Log model to MLflow with parameters                       │
│  - Save vector stores as artifacts                           │
│  - Infer model signature                                     │
│  Timeout: 60 minutes                                         │
│                                                               │
│           │                                                 │
│           ▼                                                 │
│                                                               │
│  Task 3: validate_model                                      │
│  - Load model from MLflow                                    │
│  - Run test queries (3 queries)                              │
│  - Validate response quality                                  │
│  - Check latency (<10s)                                      │
│  - Verify keyword presence                                   │
│  Timeout: 30 minutes                                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Task Dependencies

- `validate_environment` must succeed before `build_and_log`
- `build_and_log` must succeed before `validate_model`
- Any task failure stops the pipeline

---

## Configuration

### Required Variables

```bash
# OpenAI API
export OPENAI_API_KEY="sk-..."

# Databricks (if using Databricks backend)
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi..."

# Optional: MLflow tracking (defaults to databricks)
export MLFLOW_TRACKING_URI="databricks"
```

### Optional Variables

```bash
# Model configuration
export MODEL_NAME="ME-ECU-Agent"
export EXPERIMENT_NAME="ME_ECU_Assistant"

# Job configuration
export NODE_TYPE="i3.xlarge"
export NOTIFICATION_EMAIL="team@example.com"

# Performance tuning
export MAX_QUERY_LENGTH="1000"
export RESPONSE_TIMEOUT="10"
```

---

## Deployment Commands

### 1. Initial Setup

```bash
# Install Databricks CLI
pip install databricks-cli

# Authenticate with Databricks
databricks auth login

# Configure bundle for target environment
databricks bundle configure --target=dev
databricks bundle configure --target=staging
databricks bundle configure --target=prod
```

### 2. Validate Bundle

```bash
# Validate bundle syntax and structure
databricks bundle validate

# Validate for specific target
databricks bundle validate --target=prod
```

### 3. Deploy Bundle

```bash
# Deploy to development
databricks bundle deploy --target=dev

# Deploy to staging
databricks bundle deploy --target=staging

# Deploy to production
databricks bundle deploy --target=prod
```

### 4. Run Deployment Job

```bash
# Trigger job manually
databricks jobs run --job-id <job-id>

# Or use Databricks UI to trigger
# Navigate to Workflows > ME ECU Agent - Build and Log Model > Run Now
```

---

## Deployment Artifacts

### Included Files

```
src/me_ecu_agent/**/*.py      # Source code
scripts/**/*.py                # Scripts
data/*.md                      # Documentation files
pyproject.toml                 # Package configuration
databricks.yml                 # DAB configuration
```

### Excluded Files

```
**/__pycache__/**              # Python cache
**/*.pyc                       # Compiled Python
**/.git/**                     # Git repository
**/tests/**                    # Test files
**/_bmad/**                    # BMAD framework
**/mlruns/**                   # Local MLflow runs
**/.env                        # Environment variables
```

---

## Monitoring and Logging

### MLflow Tracking

All model runs are tracked in MLflow experiment `ME_ECU_Assistant`:

**Logged Parameters**:
- `chunk_size`: Document chunking size
- `chunk_overlap`: Chunk overlap for context
- `ecu_700_k`: Retrieval k for ECU-700
- `ecu_800_k`: Retrieval k for ECU-800
- `model_name`: LLM model name
- `temperature`: LLM temperature
- `max_tokens`: Maximum tokens

**Logged Metrics**:
- `total_chunks`: Total document chunks
- `ecu_700_chunks`: ECU-700 chunk count
- `ecu_800_chunks`: ECU-800 chunk count
- `validation_passed`: Model validation result
- `latency_p50`: 50th percentile latency
- `latency_p95`: 95th percentile latency

**Logged Artifacts**:
- Vector stores (FAISS indices)
- Model code (source files)
- Model signature
- Input examples

### Job Notifications

**Failure Notifications**:
- Email sent immediately on task failure
- Includes error message and stack trace
- Includes job run link

**Success Notifications** (staging/prod):
- Email sent on successful completion
- Includes model URI and validation results
- Includes performance metrics

---

## Validation

### Environment Validation

Validates:
- ✅ Python version >= 3.10
- ✅ Required environment variables set
- ✅ Required packages installed
- ✅ MLflow connection working
- ✅ OpenAI API connection working
- ✅ File structure correct

**Script**: `scripts/deployment/validate_environment.py`

**Run**: `python scripts/deployment/validate_environment.py`

### Model Validation

Validates:
- ✅ Model loads successfully
- ✅ Test queries execute successfully
- ✅ Response quality acceptable
- ✅ Latency within requirements (<10s)
- ✅ Keywords present in responses

**Script**: `scripts/deployment/validate_model.py`

**Run**: `python scripts/deployment/validate_model.py --model-uri <uri>`

---

## Troubleshooting

### Issue: Deployment Fails - "Module not found"

**Solution**: Ensure all dependencies are included in `databricks.yml`

```yaml
libraries:
  - pypi:
      package_name: langchain>=0.2.0
```

### Issue: Job Fails - "OPENAI_API_KEY not found"

**Solution**: Set environment variable in job configuration

```yaml
env_vars:
  OPENAI_API_KEY: ${var.openai_api_key}
```

### Issue: Model Validation Fails - High latency

**Solution**: Check cluster resources, consider upgrading node type

```yaml
node_type_id: "i3.xlarge"  # Upgrade to larger node
```

### Issue: Model not loading

**Solution**: Verify vector store artifacts are included

```bash
databricks fs ls dbfs:/path/to/artifacts
```

---

## Best Practices

### Development Workflow

1. **Develop Locally**
   ```bash
   python scripts/log_mlflow_model.py
   python scripts/quick_test.py
   ```

2. **Deploy to Dev**
   ```bash
   databricks bundle deploy --target=dev
   ```

3. **Test in Dev**
   - Manually trigger job
   - Check logs and results

4. **Deploy to Staging**
   ```bash
   databricks bundle deploy --target=staging
   ```

5. **Validate in Staging**
   - Monitor scheduled runs
   - Review notifications

6. **Deploy to Production**
   ```bash
   databricks bundle deploy --target=prod
   ```

### Production Deployment

1. **Pre-deployment Checklist**:
   - [ ] All tests passing in staging
   - [ ] Performance metrics acceptable
   - [ ] Notification emails configured
   - [ ] Rollback plan documented

2. **Deployment Steps**:
   ```bash
   # Deploy during maintenance window
   databricks bundle deploy --target=prod

   # Verify deployment
   databricks bundle validate --target=prod

   # Monitor first scheduled run
   ```

3. **Post-deployment**:
   - Monitor job runs for 24 hours
   - Review metrics in MLflow UI
   - Check error rates and latency
   - Validate model quality

---

## Scaling Considerations

### Current Scale

- Documents: 3 markdown files (85 lines)
- Chunks: 14 total (4 ECU-700, 10 ECU-800)
- Vector Stores: FAISS in-memory
- Cluster: Single-node

### Scaling to Thousands of Documents

**Architecture Changes**:
1. **Vector Stores**: FAISS in-memory → Pinecone/Weaviate (distributed)
2. **Retrieval**: Top-k (3-4) → Hierarchical retrieval, hybrid search
3. **Deployment**: Single-node → Multi-cluster, load balancing
4. **Caching**: None → Redis cache for common queries
5. **Monitoring**: MLflow basic → Prometheus + Grafana

**Deployment Changes**:
- Update `node_type_id` to larger instances
- Increase `num_workers` for parallel processing
- Add multiple job clusters for high availability

---

## Rollback Procedure

### Automatic Rollback

If validation fails, deployment stops automatically - no rollback needed.

### Manual Rollback

```bash
# List previous model versions
databricks models list-versions --name "ME-ECU-Agent"

# Rollback to previous version
databricks models transition-stage-to-production --model "ME-ECU-Agent" --version <version>

# Or re-deploy previous bundle
git checkout <previous-commit>
databricks bundle deploy --target=prod
```

---

## Security Considerations

### API Keys

- ✅ Use Databricks secrets for API keys
- ✅ Never commit API keys to git
- ✅ Rotate keys regularly
- ✅ Use separate keys for dev/staging/prod

### Access Control

- ✅ Use Databricks workspace access control
- ✅ Restrict job run permissions
- ✅ Limit model serving endpoints
- ✅ Enable audit logging

### Data Security

- ✅ Internal documentation only (no PII)
- ✅ Encrypt data at rest (DBFS)
- ✅ Use TLS for API calls
- ✅ Regular security scans

---

## Success Metrics

### Deployment Metrics

- ✅ Deployment success rate: >95%
- ✅ Deployment time: <30 minutes
- ✅ Validation pass rate: 100%
- ✅ Rollback time: <10 minutes

### Operational Metrics

- ✅ Job success rate: >98%
- ✅ Average latency: <10s
- ✅ Error rate: <2%
- ✅ Model quality: >90%

### Business Metrics

- ✅ Query accuracy: >90%
- ✅ User satisfaction: >4/5
- ✅ Response quality: High
- ✅ System availability: >99%

---

## Next Steps

After Epic 3 deployment:

1. **Monitor Production**
   - Track job runs and metrics
   - Review MLflow experiments
   - Analyze query patterns

2. **Optimize Performance**
   - Tune retrieval parameters
   - Optimize chunking strategy
   - Implement caching

3. **Scale Up**
   - Add more documents
   - Upgrade cluster resources
   - Implement distributed vector stores

4. **Enhance Features**
   - Add evaluation framework (Epic 5 Option A)
   - Implement human-in-the-loop (Epic 5 Option B)
   - Advanced agent behaviors (Epic 5 Option D)

---

## Conclusion

Epic 3 provides a complete enterprise deployment automation solution with:

- ✅ Multi-environment support (dev/staging/prod)
- ✅ Automated deployment pipeline
- ✅ Comprehensive validation
- ✅ Production-grade configuration
- ✅ Monitoring and logging
- ✅ Security best practices

**Status**: ✅ READY FOR PRODUCTION DEPLOYMENT

---

**Last Updated**: 2026-03-31
**Version**: 0.2.0
**Epic**: Epic 3 - Enterprise Deployment Automation
