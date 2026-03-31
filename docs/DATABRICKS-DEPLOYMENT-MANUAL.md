# Databricks Deployment Manual Guide

**Date**: 2026-03-31
**Workspace**: https://dbc-89361048-7185.cloud.databricks.com
**Workspace ID**: 7474647436450526
**Region**: us-west-2
**Notification Email**: xiazhichao9612@gmail.com

---

## Overview

This guide provides step-by-step instructions for deploying the ME ECU Agent to your Databricks workspace. Due to API limitations with the current token permissions, we'll use the Databricks UI for deployment.

---

## Prerequisites

### Completed:
- ✅ Databricks workspace configured
- ✅ Authentication token generated
- ✅ Git repository committed (Epic 3)
- ✅ Databricks SDK installed locally

### Required:
- OpenAI API key
- Access to Databricks workspace
- Permissions to create jobs and secrets

---

## Step 1: Configure Databricks Secrets

### 1.1 Create Secret Scope

1. Go to: https://dbc-89361048-7185.cloud.databricks.com/#secrets/createScope

2. Create a new secret scope:
   - **Scope Name**: `me-ecu-agent-scope`
   - **Manage Principal**: Your email address
   - Click "Create"

### 1.2 Add OpenAI API Key

1. Go to: https://dbc-89361048-7185.cloud.databricks.com/#secrets/createSecret

2. Add the secret:
   - **Scope**: `me-ecu-agent-scope`
   - **Key**: `openai_api_key`
   - **Value**: Your OpenAI API key (starts with `sk-`)
   - Click "Create"

---

## Step 2: Upload Files to Workspace

### 2.1 Upload Source Code

1. Navigate to: https://dbc-89361048-7185.cloud.databricks.com/#workspace

2. Go to your user folder:
   - `/Workspace/Users/xiazhichao9612@gmail.com/`

3. Create folder structure:
   ```
   /Workspace/Users/xiazhichao9612@gmail.com/me-ecu-agent/
   ├── src/
   │   └── me_ecu_agent/
   ├── scripts/
   │   ├── deployment/
   │   └── log_mlflow_model.py
   ├── data/
   │   ├── ECU-700.md
   │   ├── ECU-750.md
   │   └── ECU-800.md
   └── pyproject.toml
   ```

4. Upload files from local project:
   - `src/me_ecu_agent/` → Upload all Python files
   - `scripts/deployment/` → Upload all deployment scripts
   - `scripts/log_mlflow_model.py` → Upload model logging script
   - `data/*.md` → Upload all ECU documentation files
   - `pyproject.toml` → Upload package configuration

### 2.2 Verify File Upload

Check that all files are uploaded:
- Navigate to `/Workspace/Users/xiazhichao9612@gmail.com/me-ecu-agent/`
- Verify folder structure matches above

---

## Step 3: Create MLflow Experiment

### 3.1 Create Experiment Folder

1. Go to: https://dbc-89361048-7185.cloud.databricks.com/#workspace

2. Navigate to your user folder

3. Create experiment folder:
   ```
   /Workspace/Users/xiazhichao9612@gmail.com/experiments/ME_ECU_Assistant
   ```

This will serve as the MLflow experiment for tracking model runs.

---

## Step 4: Create Databricks Job

### 4.1 Navigate to Workflows

1. Go to: https://dbc-89361048-7185.cloud.databricks.com/#job/list

2. Click "Create Job"

### 4.2 Configure Job Details

- **Job Name**: `[DEV] ME ECU Agent - Build and Log Model`
- **Description**: Automated deployment pipeline for ME ECU Agent

### 4.3 Add Task 1: Validate Environment

1. Click "Add Task"

2. Configure task:
   - **Task name**: `validate_environment`
   - **Type**: Python script
   - **Source**: Workspace
   - **Path**: `/Workspace/Users/xiazhichao9612@gmail.com/me-ecu-agent/scripts/deployment/validate_environment.py`
   - **Cluster**: New cluster
     - Spark version: Latest LTS
     - Node type: i3.xlarge (4 cores, 30GB RAM)
     - Drivers: Single node
   - **Timeout**: 600 seconds (10 minutes)
   - **Retry on failure**: 0

3. Click "Save"

### 4.4 Add Task 2: Build and Log Model

1. Click "Add Task"

2. Configure task:
   - **Task name**: `build_and_log`
   - **Type**: Python script
   - **Source**: Workspace
   - **Path**: `/Workspace/Users/xiazhichao9612@gmail.com/me-ecu-agent/scripts/log_mlflow_model.py`
   - **Depends on**: `validate_environment`
   - **Cluster**: New cluster
     - Spark version: Latest LTS
     - Node type: i3.xlarge (4 cores, 30GB RAM)
     - Drivers: Single node
   - **Environment Variables**:
     - `OPENAI_API_KEY`: `{{secrets/me-ecu-agent-scope/openai_api_key}}`
     - `MLFLOW_TRACKING_URI`: `databricks`
   - **Libraries**:
     - PyPI: `mlflow`
     - PyPI: `langchain>=0.2.0`
     - PyPI: `langchain-openai`
     - PyPI: `faiss-cpu`
     - PyPI: `databricks-sdk`
   - **Timeout**: 3600 seconds (60 minutes)

3. Click "Save"

### 4.5 Add Task 3: Validate Model

1. Click "Add Task"

2. Configure task:
   - **Task name**: `validate_model`
   - **Type**: Python script
   - **Source**: Workspace
   - **Path**: `/Workspace/Users/xiazhichao9612@gmail.com/me-ecu-agent/scripts/deployment/validate_model.py`
   - **Depends on**: `build_and_log`
   - **Cluster**: New cluster
     - Spark version: Latest LTS
     - Node type: i3.xlarge (4 cores, 30GB RAM)
     - Drivers: Single node
   - **Libraries**:
     - PyPI: `mlflow`
   - **Timeout**: 1800 seconds (30 minutes)

3. Click "Save"

### 4.6 Configure Notifications

1. In job settings, click "Notifications"

2. Add email notifications:
   - **On failure**: xiazhichao9612@gmail.com
   - **On success**: xiazhichao9612@gmail.com (optional for dev)

3. Click "Save"

### 4.7 Create Job

1. Review all tasks and settings

2. Click "Create Job"

3. Note the **Job ID** for reference

---

## Step 5: Run Initial Deployment

### 5.1 Manual Job Execution

1. Go to your created job:
   - Navigate to Workflows → Jobs
   - Click on `[DEV] ME ECU Agent - Build and Log Model`

2. Click "Run Now"

3. Monitor job execution:
   - Watch task progress in real-time
   - All 3 tasks should complete successfully
   - Total time: ~100 minutes (max)

### 5.2 Verify Deployment

#### Check Task 1: validate_environment
Should output:
```
============================================================
Environment Validation
============================================================

[1] Python Version
  [PASS] Python 3.10.x

[2] Environment Variables
  [PASS] OPENAI_API_KEY: Set
  [PASS] MLFLOW_TRACKING_URI: Set

[3] File Structure
  [PASS] src/me_ecu_agent: Found
  [PASS] data: Found

[SUCCESS] All validations passed
```

#### Check Task 2: build_and_log
Should output:
```
[OK] Loading ECU documentation...
[OK] Creating vector stores...
[OK] ECU-700: 4 chunks
[OK] ECU-800: 10 chunks
[OK] Initializing agent...
[OK] Logging model to MLflow...
[OK] Model logged successfully
```

#### Check Task 3: validate_model
Should output:
```
[1] Loading model...
[PASS] Model loaded successfully

[2] Running test queries...
  Query 1: What is ECU-750?
    Latency: X.XXs
    Keywords: X/4 found
    [PASS] Query 1

[SUCCESS] Model validation passed!
```

---

## Step 6: Verify MLflow Model

### 6.1 Check MLflow Experiment

1. Go to: https://dbc-89361048-7185.cloud.databricks.com/#experiments

2. Navigate to: `ME_ECU_Assistant`

3. Verify:
   - ✅ New run created
   - ✅ Parameters logged
   - ✅ Metrics recorded
   - ✅ Artifacts saved (vector stores, model code)

### 6.2 View Model Details

Click on the latest run to view:
- **Parameters**: chunk_size, ecu_700_k, ecu_800_k, etc.
- **Metrics**: total_chunks, validation_passed
- **Artifacts**: ecu_700_index/, ecu_800_index/, model/

---

## Step 7: Test Model Inference (Optional)

### 7.1 Create Test Notebook

1. Go to: https://dbc-89361048-7185.cloud.databricks.com/#workspace

2. Create new Python notebook:
   - **Name**: `Test ME ECU Agent`
   - **Cluster**: Use existing cluster from job
   - **Language**: Python

3. Add code:

```python
import mlflow

# Load model
model_uri = "runs:/<RUN-ID>/ecu_agent_model"
model = mlflow.pyfunc.load_model(model_uri)

# Test query
test_query = "What is ECU-750?"
result = model.predict({"query": test_query})

print(f"Query: {test_query}")
print(f"Response: {result['response']}")
```

4. Replace `<RUN-ID>` with actual run ID from MLflow

5. Run notebook and verify output

---

## Troubleshooting

### Issue 1: Secret Not Found

**Error**: `Secret not found: me-ecu-agent-scope/openai_api_key`

**Solution**:
1. Verify secret scope exists
2. Check secret key name matches exactly
3. Ensure secret value is set

### Issue 2: File Not Found

**Error**: `File not found: /Workspace/Users/...`

**Solution**:
1. Verify all files uploaded correctly
2. Check file paths in job tasks
3. Ensure workspace paths are correct

### Issue 3: Module Import Error

**Error**: `ModuleNotFoundError: No module named 'me_ecu_agent'`

**Solution**:
1. Verify `src/me_ecu_agent/` uploaded
2. Check `__init__.py` files present
3. Ensure package structure is correct

### Issue 4: Validation Timeout

**Error**: Task timeout exceeded

**Solution**:
1. Check cluster resources
2. Increase timeout if needed
3. Verify network connectivity

---

## Next Steps

### After Successful Dev Deployment:

1. **Monitor Job Runs**
   - Check job execution logs
   - Verify all tasks succeed
   - Review MLflow metrics

2. **Test Model Queries**
   - Use MLflow model UI
   - Run test queries
   - Verify response quality

3. **Deploy to Staging**
   - Create new job for staging
   - Add schedule (Weekdays 6 AM UTC)
   - Enable success/failure notifications

4. **Deploy to Production**
   - Create job for production
   - Add schedule (Daily 2 AM UTC)
   - Set up monitoring and alerts

---

## Deployment Checklist

### Pre-Deployment:
- [ ] OpenAI API key set as secret
- [ ] All source files uploaded to workspace
- [ ] MLflow experiment created
- [ ] Job configured with 3 tasks
- [ ] Email notifications set up

### Post-Deployment:
- [ ] Job executed successfully
- [ ] All 3 tasks completed
- [ ] MLflow model logged
- [ ] Model validation passed
- [ ] Test queries working

### Validation:
- [ ] Response latency < 10s
- [ ] Response quality acceptable
- [ ] Keywords present in responses
- [ ] No errors in job logs

---

## Success Criteria

Your deployment is successful when:

✅ **Job Execution**: All 3 tasks complete without errors
✅ **MLflow Model**: Model logged with parameters and artifacts
✅ **Validation**: Model validation passes with 100% success rate
✅ **Performance**: Query latency under 10 seconds
✅ **Quality**: Test queries return relevant, accurate responses

---

## Support and Resources

### Documentation:
- Epic 3 Deployment Guide: `docs/EPIC-3-DEPLOYMENT-GUIDE.md`
- Epic 3 Completion: `docs/EPIC-3-COMPLETE.md`
- Epic 3 Validation: `docs/EPIC-3-VALIDATION.md`

### Databricks Resources:
- Workspace: https://dbc-89361048-7185.cloud.databricks.com
- Jobs UI: https://dbc-89361048-7185.cloud.databricks.com/#job/list
- MLflow UI: https://dbc-89361048-7185.cloud.databricks.com/#experiments
- Secrets UI: https://dbc-89361048-7185.cloud.databricks.com/#secrets

### Contact:
- Email: xiazhichao9612@gmail.com
- Region: us-west-2
- Workspace ID: 7474647436450526

---

**Status**: Ready for Manual Deployment
**Last Updated**: 2026-03-31
**Version**: 0.2.0
