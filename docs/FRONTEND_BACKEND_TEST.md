# Quick Test - Frontend to Backend Connection

## 1. Start Backend
```powershell
# Terminal 1
uvicorn backend.main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## 2. Test Backend Health
```powershell
# Terminal 2
curl http://localhost:8000/health
```

Expected: `{"status":"ok"}`

## 3. Start Frontend
```powershell
# Terminal 2 (or new terminal)
streamlit run client/main.py
```

Expected:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

## 4. Test Connection

1. Open browser: `http://localhost:8501`
2. Click **"Run Optimization"** button
3. Should see:
   - ✓ "Connecting to backend..."
   - ✓ "Running optimization..."
   - ✓ "Optimization completed successfully!"

## What Happens Behind the Scenes

```
Frontend (Streamlit :8501)
    ↓
    POST /optimize
    ↓
Backend (FastAPI :8000)
    ↓
1. Uses default Excel (backend/dataset.xlsx) OR uploaded Excel
2. Extracts sheets to CSV files
3. Loads data from CSVs
4. Runs optimization model
5. Returns results
    ↓
Frontend displays results
```

## File Upload Flow

### Without Upload:
- Click "Run Optimization"
- Backend uses `backend/dataset.xlsx` (default file)

### With Upload:
1. Click "Browse Files" button
2. Select `.xlsx` file
3. See "✓ filename.xlsx ready"
4. Click "Run Optimization"
5. Backend uses your uploaded file

## Troubleshooting

### Backend won't start
```powershell
# Install dependencies
pip install -r backend/requirements.txt
```

### Frontend won't start
```powershell
# Install dependencies  
pip install -r client/requirements.txt
```

### "Backend is not running" error
- Make sure backend is started first
- Check backend terminal for errors
- Verify backend URL: `http://localhost:8000`

### Connection refused
- Check both services are on correct ports:
  - Backend: 8000
  - Frontend: 8501
- Check firewall settings

## Quick Check Commands

```powershell
# Check if backend is running
curl http://localhost:8000/health

# Check if frontend is running
# Open: http://localhost:8501 in browser
```

## Current Setup Status

✅ **Completed:**
- API client created (`client/api_client.py`)
- File uploader updated to call backend
- Backend CORS enabled for frontend
- Health check endpoint added
- Excel file upload support

🔄 **Ready to Test:**
- Start both backend and frontend
- Test optimization with/without file upload
