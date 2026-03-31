# Databricks Deployment Checklist

**Print and use this checklist during deployment**

---

## Pre-Deployment Preparation

### Local Environment ✅
- [x] Git repository committed (b12891e)
- [x] All source files ready
- [x] Databricks CLI configured
- [x] Authentication token verified
- [x] Workspace connection tested

### Documentation ✅
- [x] Step-by-step guide created
- [x] Quick reference card created
- [x] Troubleshooting guide available
- [x] Validation scripts tested

---

## Deployment Steps

### Step 1: Create Secret Scope (2 minutes)

**URL**: https://dbc-89361048-7185.cloud.databricks.com/#secrets/createScope

- [ ] Navigate to Secrets page
- [ ] Create scope named `me-ecu-agent-scope`
- [ ] Set principal to `xiazhichao9612@gmail.com`
- [ ] Click "Create"
- [ ] Add secret: `openai_api_key`
- [ ] Paste OpenAI API key
- [ ] Click "Create" to add secret
- [ ] Verify secret appears in list

**Expected Result**: Secret scope and secret created successfully

---

### Step 2: Upload Files (10 minutes)

**URL**: https://dbc-89361048-7185.cloud.databricks.com/#workspace

**Base Path**: `/Workspace/Users/xiazhichao9612@gmail.com/me-ecu-agent/`

- [ ] Navigate to workspace
- [ ] Go to your user folder
- [ ] Create folder `me-ecu-agent`

#### Source Files
- [ ] Create `src/me_ecu_agent/` folder
- [ ] Upload all 18 Python files:
  - [ ] `__init__.py`
  - [ ] `config.py`
  - [ ] `graph.py`
  - [ ] `mlflow_model.py`
  - [ ] `vectorstore.py`
  - [ ] `document_processor.py`
  - [ ] `error_handling.py`
  - [ ] `model.py`
  - [ ] `tools.py`
  - [ ] [10 more files]

#### Script Files
- [ ] Create `scripts/deployment/` folder
- [ ] Upload `validate_environment.py`
- [ ] Upload `validate_model.py`
- [ ] Go to `scripts/` folder
- [ ] Upload `log_mlflow_model.py`

#### Data Files
- [ ] Create `data/` folder
- [ ] Upload `ECU-700.md`
- [ ] Upload `ECU-750.md`
- [ ] Upload `ECU-800.md`

#### Config File
- [ ] Upload `pyproject.toml` to root

**Expected Result**: All 25 files uploaded successfully

---

### Step 3: Create MLflow Experiment (1 minute)

**URL**: https://dbc-89361048-7185.cloud.databricks.com/#experiments

- [ ] Navigate to Experiments
- [ ] Go to your user folder
- [ ] Create folder `experiments`
- [ ] Create subfolder `ME_ECU_Assistant`

**Expected Result**: Experiment path created

---

### Step 4: Create Databricks Job (15 minutes)

**URL**: https://dbc-89361048-7185.cloud.databricks.com/#job/list

#### Job Configuration
- [ ] Click "Create Job"
- [ ] Set name: `[DEV] ME ECU Agent - Build and Log Model`
- [ ] Add description

#### Task 1: validate_environment
- [ ] Click "Add Task"
- [ ] Set name: `validate_environment`
- [ ] Select type: "Python script"
- [ ] Set source: "Workspace"
- [ ] Set path: `/Workspace/Users/xiazhichao9612@gmail.com/me-ecu-agent/scripts/deployment/validate_environment.py`
- [ ] Create new cluster:
  - [ ] Spark version: Latest LTS
  - [ ] Node type: i3.xlarge
  - [ ] Drivers: Single Node
- [ ] Add library: PyPI `mlflow`
- [ ] Set timeout: 600 seconds
- [ ] Click "Save"

#### Task 2: build_and_log
- [ ] Click "Add Task"
- [ ] Set name: `build_and_log`
- [ ] Select type: "Python script"
- [ ] Set source: "Workspace"
- [ ] Set path: `/Workspace/Users/xiazhichao9612@gmail.com/me-ecu-agent/scripts/log_mlflow_model.py`
- [ ] Set dependency: `validate_environment`
- [ ] Create new cluster:
  - [ ] Spark version: Latest LTS
  - [ ] Node type: i3.xlarge
  - [ ] Drivers: Single Node
- [ ] Add environment variables:
  - [ ] `OPENAI_API_KEY={{secrets/me-ecu-agent-scope/openai_api_key}}`
  - [ ] `MLFLOW_TRACKING_URI=databricks`
- [ ] Add libraries:
  - [ ] PyPI: `mlflow`
  - [ ] PyPI: `langchain>=0.2.0`
  - [ ] PyPI: `langchain-openai`
  - [ ] PyPI: `faiss-cpu`
  - [ ] PyPI: `databricks-sdk`
- [ ] Set timeout: 3600 seconds
- [ ] Click "Save"

#### Task 3: validate_model
- [ ] Click "Add Task"
- [ ] Set name: `validate_model`
- [ ] Select type: "Python script"
- [ ] Set source: "Workspace"
- [ ] Set path: `/Workspace/Users/xiazhichao9612@gmail.com/me-ecu-agent/scripts/deployment/validate_model.py`
- [ ] Set dependency: `build_and_log`
- [ ] Create new cluster:
  - [ ] Spark version: Latest LTS
  - [ ] Node type: i3.xlarge
  - [ ] Drivers: Single Node
- [ ] Add library: PyPI `mlflow`
- [ ] Set timeout: 1800 seconds
- [ ] Click "Save"

#### Notifications
- [ ] Go to "Notifications" section
- [ ] Add email for "On failure": `xiazhichao9612@gmail.com`

#### Create Job
- [ ] Review all tasks
- [ ] Click "Create"
- [ ] Note the Job ID: ___________

**Expected Result**: Job created with 3 tasks

---

### Step 5: Run Initial Deployment (5 minutes start)

**URL**: https://dbc-89361048-7185.cloud.databricks.com/#job/list

- [ ] Find job: `[DEV] ME ECU Agent - Build and Log Model`
- [ ] Click on job name
- [ ] Click "Run Now"
- [ ] Confirm: Click "Run"

#### Monitor Execution
- [ ] Task 1 starts (validate_environment)
- [ ] Task 1 completes (~10 min)
- [ ] Task 2 starts (build_and_log)
- [ ] Task 2 completes (~60 min)
- [ ] Task 3 starts (validate_model)
- [ ] Task 3 completes (~30 min)

**Expected Result**: All 3 tasks complete successfully

---

### Step 6: Verify Deployment (15 minutes)

#### Check Task Outputs

**Task 1: validate_environment**
- [ ] View task logs
- [ ] Verify Python version check passes
- [ ] Verify environment variables check passes
- [ ] Verify dependencies check passes
- [ ] Verify MLflow connection passes
- [ ] Verify OpenAI API connection passes
- [ ] Verify file structure check passes

**Task 2: build_and_log**
- [ ] View task logs
- [ ] Verify ECU documentation loaded
- [ ] Verify vector stores created
- [ ] Verify agent initialized
- [ ] Verify model logged to MLflow
- [ ] Verify artifacts saved

**Task 3: validate_model**
- [ ] View task logs
- [ ] Verify model loads successfully
- [ ] Verify test query 1 passes
- [ ] Verify test query 2 passes
- [ ] Verify test query 3 passes
- [ ] Verify response quality acceptable
- [ ] Verify latency < 10 seconds

#### Verify MLflow Model

**URL**: https://dbc-89361048-7185.cloud.databricks.com/#experiments

- [ ] Navigate to experiments
- [ ] Go to `ME_ECU_Assistant`
- [ ] Click on latest run
- [ ] Verify parameters logged:
  - [ ] `chunk_size`
  - [ ] `chunk_overlap`
  - [ ] `ecu_700_k`
  - [ ] `ecu_800_k`
  - [ ] `model_name`
  - [ ] `temperature`
- [ ] Verify metrics logged:
  - [ ] `total_chunks`
  - [ ] `ecu_700_chunks`
  - [ ] `ecu_800_chunks`
  - [ ] `validation_passed`
- [ ] Verify artifacts present:
  - [ ] `ecu_700_index/`
  - [ ] `ecu_800_index/`
  - [ ] `model/`

**Expected Result**: MLflow model logged with all components

---

## Post-Deployment

### Production Readiness
- [ ] All 3 tasks succeeded
- [ ] MLflow model verified
- [ ] Validation tests passed
- [ ] Performance metrics acceptable
- [ ] Error handling working

### Documentation
- [ ] Job ID saved: ___________
- [ ] Run ID saved: ___________
- [ ] Model URI saved: ___________
- [ ] Deployment notes documented

---

## Success Criteria

### Deployment Success
- [ ] Job executes without errors
- [ ] All tasks complete successfully
- [ ] MLflow model logged
- [ ] Validation passes (3/3 queries)
- [ ] Performance acceptable

### Verification Success
- [ ] Response latency < 10 seconds
- [ ] Response quality acceptable
- [ ] All artifacts present
- [ ] Metrics logged correctly

---

## Troubleshooting Notes

**Issues Encountered**:
1. __________________________________________________________
2. __________________________________________________________
3. __________________________________________________________

**Solutions Applied**:
1. __________________________________________________________
2. __________________________________________________________
3. __________________________________________________________

---

## Sign-Off

**Deployment Date**: ___________
**Deployed By**: ___________
**Reviewed By**: ___________
**Approved By**: ___________

**Status**: [ ] SUCCESS  [ ] PARTIAL  [ ] FAILED

**Notes**:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

---

**Checklist Version**: 1.0
**Last Updated**: 2026-03-31
