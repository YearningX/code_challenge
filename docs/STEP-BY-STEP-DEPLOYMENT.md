# Databricks Deployment - Step-by-Step Interactive Guide

**Workspace**: https://dbc-89361048-7185.cloud.databricks.com
**Date**: 2026-03-31
**Status**: Ready to Deploy

---

## Pre-Deployment Checklist ✅

- [x] Databricks workspace connection verified
- [x] Authentication token configured
- [x] databricks.yml configured
- [x] All source files committed to Git
- [x] Deployment scripts ready
- [x] Validation tests passed (35/35)

---

## Step 1: Create Databricks Secret Scope (2 minutes)

### 1.1 Navigate to Secrets Creation Page

**Action**: Click this link or copy to browser:
```
https://dbc-89361048-7185.cloud.databricks.com/#secrets/createScope
```

### 1.2 Create Secret Scope

**Fill in the form**:
- **Scope Name**: `me-ecu-agent-scope`
- **Manage Principal**: `xiazhichao9612@gmail.com` (your email)
- **Permission**: MANAGE

**Click**: "Create"

### 1.3 Add OpenAI API Key Secret

**Action**: After creating scope, click "Add Secret"

**Fill in the form**:
- **Scope**: `me-ecu-agent-scope` (select from dropdown)
- **Key**: `openai_api_key`
- **Value**: Paste your OpenAI API key (starts with `sk-`)

**Click**: "Create"

**Verify**: You should see the secret in the list

---

## Step 2: Upload Files to Workspace (10 minutes)

### 2.1 Navigate to Your Workspace

**Action**: Click this link:
```
https://dbc-89361048-7185.cloud.databricks.com/#workspace
```

### 2.2 Create Project Folder

**Navigate to**:
```
Workspace → Users → xiazhichao9612@gmail.com
```

**Create folder**: `me-ecu-agent`

### 2.3 Upload Source Files

**Create folder structure**:

```
me-ecu-agent/
├── src/
│   └── me_ecu_agent/
│       ├── __init__.py
│       ├── config.py
│       ├── graph.py
│       ├── mlflow_model.py
│       ├── vectorstore.py
│       ├── document_processor.py
│       ├── error_handling.py
│       └── [all other .py files]
├── scripts/
│   ├── deployment/
│   │   ├── validate_environment.py
│   │   └── validate_model.py
│   └── log_mlflow_model.py
├── data/
│   ├── ECU-700.md
│   ├── ECU-750.md
│   └── ECU-800.md
└── pyproject.toml
```

**Upload instructions**:
1. For each folder, right-click → "Create Folder"
2. Upload files from local project:
   - Go to: `F:\projects\BOSCH_Code_Challenge\`
   - Select files/folders
   - Drag and drop to Databricks workspace

**Verify**: All files uploaded successfully

---

## Step 3: Create MLflow Experiment (1 minute)

### 3.1 Navigate to Experiments

**Action**: Click this link:
```
https://dbc-89361048-7185.cloud.databricks.com/#experiments
```

### 3.2 Create Experiment

**Navigate to**:
```
Workspace → Users → xiazhichao9612@gmail.com
```

**Create folder**: `experiments`

**Create subfolder**: `ME_ECU_Assistant`

This creates the experiment path:
```
/Workspace/Users/xiazhichao9612@gmail.com/experiments/ME_ECU_Assistant
```

**Verify**: Experiment folder exists

---

## Step 4: Create Databricks Job (15 minutes)

### 4.1 Navigate to Workflows

**Action**: Click this link:
```
https://dbc-89361048-7185.cloud.databricks.com/#job/list
```

### 4.2 Create New Job

**Click**: "Create Job" button

### 4.3 Configure Job Details

**Basic Information**:
- **Job name**: `[DEV] ME ECU Agent - Build and Log Model`
- **Description**: Automated deployment pipeline for ME ECU Agent

### 4.4 Add Task 1: Validate Environment

**Click**: "Add Task"

**Task Configuration**:
- **Task name**: `validate_environment`
- **Type**: "Python script"
- **Source**: "Workspace"
- **Path**: `/Workspace/Users/xiazhichao9612@gmail.com/me-ecu-agent/scripts/deployment/validate_environment.py`

**Cluster**:
- **Cluster**: "New Cluster"
  - Spark version: "Latest LTS (Scala 2.12)"
  - Node type: "i3.xlarge"
  - Drivers: "Single Node"
  - Use spot instances: Unchecked

**Libraries**:
- Click "Libraries" → "Add"
  - Source: "PyPI"
  - Package: `mlflow`

**Timeout**: 600 seconds (10 minutes)

**Click**: "Save"

### 4.5 Add Task 2: Build and Log Model

**Click**: "Add Task"

**Task Configuration**:
- **Task name**: `build_and_log`
- **Type**: "Python script"
- **Source**: "Workspace"
- **Path**: `/Workspace/Users/xiazhichao9612@gmail.com/me-ecu-agent/scripts/log_mlflow_model.py`

**Dependencies**:
- **Depends on**: Select `validate_environment`

**Cluster**:
- **Cluster**: "New Cluster"
  - Spark version: "Latest LTS (Scala 2.12)"
  - Node type: "i3.xlarge"
  - Drivers: "Single Node"

**Environment Variables**:
- **Key**: `OPENAI_API_KEY`
- **Value**: `{{secrets/me-ecu-agent-scope/openai_api_key}}`
- **Key**: `MLFLOW_TRACKING_URI`
- **Value**: `databricks`

**Libraries**:
- Click "Libraries" → "Add" for each:
  1. PyPI: `mlflow`
  2. PyPI: `langchain>=0.2.0`
  3. PyPI: `langchain-openai`
  4. PyPI: `faiss-cpu`
  5. PyPI: `databricks-sdk`

**Timeout**: 3600 seconds (60 minutes)

**Click**: "Save"

### 4.6 Add Task 3: Validate Model

**Click**: "Add Task"

**Task Configuration**:
- **Task name**: `validate_model`
- **Type**: "Python script"
- **Source**: "Workspace"
- **Path**: `/Workspace/Users/xiazhichao9612@gmail.com/me-ecu-agent/scripts/deployment/validate_model.py`

**Dependencies**:
- **Depends on**: Select `build_and_log`

**Cluster**:
- **Cluster**: "New Cluster"
  - Spark version: "Latest LTS (Scala 2.12)"
  - Node type: "i3.xlarge"
  - Drivers: "Single Node"

**Libraries**:
- PyPI: `mlflow`

**Timeout**: 1800 seconds (30 minutes)

**Click**: "Save"

### 4.7 Configure Notifications

**Go to**: "Notifications" section

**Add email notifications**:
- **On failure**: xiazhichao9612@gmail.com
- **On success**: Leave empty for dev (optional)

**Click**: "Create" to create the job

**Note**: Save the **Job ID** shown after creation

---

## Step 5: Run Initial Deployment (5 minutes to start)

### 5.1 Navigate to Your Job

**Action**: Go to Workflows → Jobs

**Find**: `[DEV] ME ECU Agent - Build and Log Model`

**Click**: On the job name

### 5.2 Run Job Manually

**Click**: "Run Now" button

**Confirmation**: Click "Run" in the confirmation dialog

### 5.3 Monitor Execution

**You will see**:
- Task 1: validate_environment (10 min)
- Task 2: build_and_log (60 min)
- Task 3: validate_model (30 min)

**Estimated total time**: ~100 minutes

**Monitor progress**:
- Watch task status (Pending → Running → Succeeded/Failed)
- Check task logs for any errors
- Verify all tasks complete successfully

---

## Step 6: Verify Deployment (15 minutes)

### 6.1 Check Task Outputs

**Task 1: validate_environment**
- Expected: All validations pass
- Look for: "[PASS]" markers
- Should check: Python version, environment variables, dependencies

**Task 2: build_and_log**
- Expected: Model built and logged to MLflow
- Look for: "[OK] Model logged successfully"
- Check: Vector stores created, agent initialized

**Task 3: validate_model**
- Expected: Model validation passes
- Look for: "[SUCCESS] Model validation passed!"
- Check: 3 test queries executed, quality acceptable

### 6.2 Verify MLflow Model

**Go to**: https://dbc-89361048-7185.cloud.databricks.com/#experiments

**Navigate to**:
```
/Workspace/Users/xiazhichao9612@gmail.com/experiments/ME_ECU_Assistant
```

**Verify**:
- ✅ New run created
- ✅ Parameters logged (chunk_size, ecu_700_k, ecu_800_k, etc.)
- ✅ Metrics recorded (total_chunks, validation_passed)
- ✅ Artifacts saved (ecu_700_index/, ecu_800_index/, model/)

### 6.3 Test Model Inference (Optional)

**Create test notebook**:
1. Go to Workspace → Create → Notebook
2. Name: "Test ME ECU Agent"
3. Language: Python
4. Cluster: Use existing cluster from job

**Add test code**:
```python
import mlflow

# Load model
model_uri = "runs:/<YOUR-RUN-ID>/ecu_agent_model"
model = mlflow.pyfunc.load_model(model_uri)

# Test query
result = model.predict({"query": "What is ECU-850?"})
print(result)
```

**Run**: Execute notebook and verify output

---

## Troubleshooting

### Issue 1: Secret Not Found

**Error**: `Secret not found: me-ecu-agent-scope/openai_api_key`

**Solution**:
1. Verify secret scope exists
2. Check exact scope name and key name
3. Ensure secret value is set (not empty)

### Issue 2: File Not Found

**Error**: `File not found: /Workspace/Users/...`

**Solution**:
1. Verify all files uploaded correctly
2. Check file paths match exactly
3. Ensure folder structure is correct

### Issue 3: Module Import Error

**Error**: `ModuleNotFoundError: No module named 'me_ecu_agent'`

**Solution**:
1. Verify `src/me_ecu_agent/` uploaded
2. Check `__init__.py` files present
3. Ensure package structure is maintained

### Issue 4: Job Timeout

**Error**: Task timeout exceeded

**Solution**:
1. Check cluster resources (i3.xlarge recommended)
2. Increase timeout if needed
3. Verify network connectivity to OpenAI API

---

## Success Criteria

Your deployment is successful when:

✅ **Job Execution**: All 3 tasks complete without errors
✅ **MLflow Model**: Model logged with parameters and artifacts
✅ **Validation**: Model validation passes (3/3 test queries)
✅ **Performance**: Query latency < 10 seconds
✅ **Quality**: Test queries return relevant responses

---

## Next Steps After Successful Deployment

### Staging Environment (Optional)

1. Create new job for staging
2. Add schedule: Weekdays at 6 AM UTC
3. Enable success/failure notifications
4. Deploy to staging target

### Production Environment (Optional)

1. Create job for production
2. Add schedule: Daily at 2 AM UTC
3. Set up monitoring and alerts
4. Deploy to production target

---

## Quick Reference Links

- **Workspace**: https://dbc-89361048-7185.cloud.databricks.com
- **Jobs**: https://dbc-89361048-7185.cloud.databricks.com/#job/list
- **Experiments**: https://dbc-89361048-7185.cloud.databricks.com/#experiments
- **Secrets**: https://dbc-89361048-7185.cloud.databricks.com/#secrets
- **Your Workspace Folder**: /Workspace/Users/xiazhichao9612@gmail.com/

---

## Support

**Email**: xiazhichao9612@gmail.com
**Region**: us-west-2
**Workspace ID**: 7474647436450526

**Documentation**:
- Deployment Manual: `docs/DATABRICKS-DEPLOYMENT-MANUAL.md`
- Epic 3 Guide: `docs/EPIC-3-DEPLOYMENT-GUIDE.md`
- Validation: `docs/EPIC-3-VALIDATION.md`

---

**Ready to start? Begin with Step 1: Create Databricks Secret Scope**

Good luck with your deployment!
