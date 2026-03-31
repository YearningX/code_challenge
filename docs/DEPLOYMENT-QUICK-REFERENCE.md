# Databricks Deployment Quick Reference

**Print this page for easy reference during deployment**

---

## 🔐 Required Information

```
Workspace URL: https://dbc-89361048-7185.cloud.databricks.com
Workspace ID: 7474647436450526
Email: xiazhichao9612@gmail.com
Region: us-west-2
```

---

## 📋 Step 1: Secret Scope (2 min)

**URL**: https://dbc-89361048-7185.cloud.databricks.com/#secrets/createScope

**Create Scope**:
- Name: `me-ecu-agent-scope`
- Principal: `xiazhichao9612@gmail.com`

**Add Secret**:
- Scope: `me-ecu-agent-scope`
- Key: `openai_api_key`
- Value: `sk-...` (your OpenAI key)

---

## 📁 Step 2: Upload Files (10 min)

**URL**: https://dbc-89361048-7185.cloud.databricks.com/#workspace

**Path**: `/Workspace/Users/xiazhichao9612@gmail.com/me-ecu-agent/`

**Files to Upload**:
```
src/me_ecu_agent/*.py     (18 files)
scripts/deployment/*.py    (2 files)
scripts/log_mlflow_model.py (1 file)
data/*.md                  (3 files)
pyproject.toml             (1 file)
```

**Total**: 25 files

---

## 🧪 Step 3: MLflow Experiment (1 min)

**URL**: https://dbc-89361048-7185.cloud.databricks.com/#experiments

**Path**: `/Workspace/Users/xiazhichao9612@gmail.com/experiments/ME_ECU_Assistant`

---

## ⚙️ Step 4: Create Job (15 min)

**URL**: https://dbc-89361048-7185.cloud.databricks.com/#job/list

**Job Name**: `[DEV] ME ECU Agent - Build and Log Model`

### Task 1: validate_environment
- Script: `scripts/deployment/validate_environment.py`
- Cluster: i3.xlarge (Single Node)
- Libraries: `mlflow`
- Timeout: 600s

### Task 2: build_and_log
- Script: `scripts/log_mlflow_model.py`
- Depends on: Task 1
- Cluster: i3.xlarge (Single Node)
- Env Vars:
  - `OPENAI_API_KEY={{secrets/me-ecu-agent-scope/openai_api_key}}`
  - `MLFLOW_TRACKING_URI=databricks`
- Libraries: `mlflow`, `langchain>=0.2.0`, `langchain-openai`, `faiss-cpu`, `databricks-sdk`
- Timeout: 3600s

### Task 3: validate_model
- Script: `scripts/deployment/validate_model.py`
- Depends on: Task 2
- Cluster: i3.xlarge (Single Node)
- Libraries: `mlflow`
- Timeout: 1800s

---

## ▶️ Step 5: Run Job (5 min start)

**Action**: Click "Run Now"

**Monitor**:
- Task 1: ~10 min
- Task 2: ~60 min
- Task 3: ~30 min
- **Total**: ~100 min

---

## ✅ Step 6: Verify (15 min)

**Check Job Outputs**:
- Task 1: All validations pass
- Task 2: Model logged successfully
- Task 3: Validation passed (3/3 queries)

**Check MLflow**:
- URL: https://dbc-89361048-7185.cloud.databricks.com/#experiments
- Experiment: `ME_ECU_Assistant`
- Verify: Parameters, metrics, artifacts present

---

## 🔗 Quick Links

| Purpose | URL |
|---------|-----|
| Secrets | https://dbc-89361048-7185.cloud.databricks.com/#secrets |
| Workspace | https://dbc-89361048-7185.cloud.databricks.com/#workspace |
| Jobs | https://dbc-89361048-7185.cloud.databricks.com/#job/list |
| Experiments | https://dbc-89361048-7185.cloud.databricks.com/#experiments |

---

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| Secret not found | Verify scope name: `me-ecu-agent-scope` |
| File not found | Check file paths, verify uploads |
| Module import error | Ensure `__init__.py` files uploaded |
| Job timeout | Increase timeout, check cluster resources |
| API error | Verify OPENAI_API_KEY is valid |

---

## 📞 Support

**Email**: xiazhichao9612@gmail.com
**Documentation**: `docs/STEP-BY-STEP-DEPLOYMENT.md`
**Full Guide**: `docs/DATABRICKS-DEPLOYMENT-MANUAL.md`

---

## ✅ Success Criteria

- [ ] All 3 tasks complete successfully
- [ ] MLflow model logged with artifacts
- [ ] Model validation passes (3/3 queries)
- [ ] Response latency < 10 seconds
- [ ] Quality acceptable

---

**Estimated Total Time**: 45-50 minutes (setup) + 100 minutes (job execution)

**Start Time**: ___________
**Expected Completion**: ___________
