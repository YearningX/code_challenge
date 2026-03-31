# 🚀 Quick Start Guide - ME ECU Assistant Web UI

## Step 1: Install Dependencies (1 minute)

```bash
cd web
pip install -r requirements.txt
```

## Step 2: Start the API Server

**Option A: Quick start**
```bash
python start_server.py
```

**Option B: Direct start**
```bash
python api_server.py
```

You should see:
```
============================================================
ME ECU Assistant - Configuration
============================================================
Model URI: runs:/20f8fa846aea4dd183fa8bbe3739efb6/ecu_agent_model
Server: 0.0.0.0:8000
Reload: True
============================================================

Starting ME ECU Assistant API Server...
Loading MLflow model from: runs:/...
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 3: Open the Web Interface

**Option A: Automatically** (if using `start_server.py`)
- The script will ask to open browser automatically

**Option B: Manually**
1. Open File Explorer
2. Navigate to `F:\projects\BOSCH_Code_Challenge\web\`
3. Double-click `index.html`

Or open in browser:
```
file:///F:/projects/BOSCH_Code_Challenge/web/index.html
```

## Step 4: Test the System

You should see:
- ✅ System Status: "Online" (green dot)
- ✅ Performance dashboard with metrics
- ✅ Query interface ready

**Test queries**:
1. Click "ECU-750 Specs" button
2. Click "ECU-850 Specs" button
3. Click "Compare 850 vs 850b" button

Each query should show:
- AI-generated response
- Latency (3-6 seconds)
- Product line badge

## Troubleshooting

### Issue: "MLflow model not loaded"

**Solution 1**: Check if MLflow model exists
```bash
cd ..
python -c "import mlflow; mlflow.pyfunc.load_model('runs:/20f8fa846aea4dd183fa8bbe3739efb6/ecu_agent_model')"
```

**Solution 2**: Use environment variable to specify correct model
```bash
set MLFLOW_MODEL_URI=runs:/YOUR_RUN_ID/ecu_agent_model
python api_server.py
```

### Issue: "Port 8000 already in use"

**Solution**: Use different port
```bash
set API_PORT=8001
python api_server.py
```

Then update `index.html`:
```javascript
const API_BASE_URL = 'http://localhost:8001';
```

### Issue: "Connection refused in browser"

**Solution**: Make sure API server is running
```bash
curl http://localhost:8000/api/health
```

Should return:
```json
{"status":"healthy","model_loaded":true,"uptime":...}
```

## Presentation Mode

For leadership demos, ensure:
1. ✅ Fast internet connection (for CDN resources)
2. ✅ API server running before opening browser
3. ✅ Test all 4 demo queries beforehand
4. ✅ Clear browser cache if loading is slow

## API Documentation

Once server is running:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- Health check: http://localhost:8000/api/health

## Next Steps

1. ✅ Verify system works
2. ✅ Read `DEMO-PRESENTATION-GUIDE.md` for demo script
3. ✅ Test all demo queries
4. ✅ Prepare for presentation

---

**Need Help?**
- Check `README.md` for detailed documentation
- Review server logs for error messages
- Ensure all dependencies are installed

**System Ready?** You should see:
- API server running on port 8000
- Web interface loaded in browser
- System status showing "Online"
- Performance metrics displayed

Ready for your presentation! 🎯
