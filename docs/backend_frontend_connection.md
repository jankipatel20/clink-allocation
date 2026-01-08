# Connecting Backend with Frontend

## Overview
This guide explains how to connect the FastAPI backend with the Streamlit frontend for the Clinker Allocation & Optimization system.

## Architecture

```
┌─────────────────────┐         HTTP/REST API        ┌──────────────────────┐
│  Streamlit Client   │ ◄────────────────────────► │   FastAPI Backend    │
│  (Port 8501)        │                              │   (Port 8000)        │
│  client/main.py     │                              │   backend/main.py    │
└─────────────────────┘                              └──────────────────────┘
         │                                                      │
         │ Displays                                            │ Solves
         │ Results                                             │ Optimization
         ▼                                                      ▼
   [User Interface]                                    [Pyomo Model + Solver]
```

## Setup Instructions

### 1. Start the Backend Server

Open a terminal and run:

```powershell
# Navigate to project directory
cd D:\Projects\clink-allocation

# Start the FastAPI backend
uvicorn backend.main:app --reload
```

The backend will start at: `http://localhost:8000`

You can verify it's running by visiting: `http://localhost:8000/health`

### 2. Start the Frontend Application

Open a **new terminal** and run:

```powershell
# Navigate to project directory  
cd D:\Projects\clink-allocation

# Start the Streamlit frontend
streamlit run client/main.py
```

The frontend will start at: `http://localhost:8501`

## How It Works

### Backend API Endpoints

1. **Health Check**: `GET /health`
   - Checks if the backend is running
   - Returns: `{"status": "ok"}`

2. **Run Optimization**: `POST /optimize`
   - Accepts optional CSV file uploads or uses default data
   - Runs the optimization model
   - Returns:
     ```json
     {
       "status": "success",
       "total_cost": 4250000.50,
       "production": [...],
       "inventory": [...],
       "shipments": [...]
     }
     ```

### Frontend Components

1. **api_client.py**
   - `BackendAPIClient` class handles all API communication
   - Methods:
     - `health_check()`: Verify backend connection
     - `run_optimization()`: Send optimization request

2. **main.py**
   - Imports `get_api_client()` to create API client instance
   - Session state stores optimization results
   - "Run Optimization" button triggers API call
   - KPI cards display real-time results
   - Detailed tabs show production, inventory, and shipment data

## Usage Flow

1. **Initial Load**:
   - Frontend checks backend connection status
   - Shows warning if backend is not connected
   - Displays "Not Run" status in KPIs

2. **Run Optimization**:
   - User clicks "Run Optimization" button
   - Frontend sends POST request to `/optimize`
   - Backend processes data and solves model (may take 1-5 minutes)
   - Results are returned and stored in session state
   - UI automatically refreshes to show results

3. **View Results**:
   - KPI cards show total cost, status, active plants
   - Charts update with real data
   - Detailed tabs show complete production, inventory, and shipment plans
   - Download buttons allow exporting results as CSV

## Features

### Connection Status Indicator
- 🟢 Green dot: Backend connected
- 🔴 Red dot: Backend not available

### Automatic Data Updates
- Frontend uses real backend data when available
- Falls back to mock data if optimization hasn't been run
- Results persist in session until new optimization runs

### Error Handling
- Connection errors show user-friendly messages
- Timeout handling (5 min max for optimization)
- Validation of required data files

## Troubleshooting

### Backend Not Connecting
```
⚠️ Backend not connected. Start the backend server with: `uvicorn backend.main:app --reload`
```
**Solution**: Start the backend server in a separate terminal

### Optimization Timeout
**Issue**: Request takes longer than 5 minutes

**Solution**: 
- Check data size (large datasets take longer)
- Verify solver is installed correctly
- Check backend logs for errors

### Port Already in Use

**Backend (Port 8000)**:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Frontend (Port 8501)**:
```powershell
# Find process using port 8501
netstat -ano | findstr :8501

# Kill the process
taskkill /PID <PID> /F
```

## Development Notes

### Adding New Endpoints

1. Add endpoint in `backend/main.py`:
```python
@app.get("/new-endpoint")
def new_feature():
    return {"data": "value"}
```

2. Add method in `client/api_client.py`:
```python
def call_new_endpoint(self):
    response = requests.get(f"{self.base_url}/new-endpoint")
    return response.json()
```

3. Use in `client/main.py`:
```python
result = api_client.call_new_endpoint()
```

### Handling File Uploads

Files are sent as multipart/form-data:
```python
# Frontend
files_dict = [("files", (file.name, file, "text/csv"))]
response = requests.post(url, files=files_dict)

# Backend
@app.post("/optimize")
async def run_optimization(files: List[UploadFile] = File(None)):
    for file in files:
        content = await file.read()
        # process content
```

## Next Steps

- ✅ Backend and frontend are now connected
- ✅ Optimization results display in real-time
- ✅ Download functionality for results
- 🔄 Add file upload feature (future enhancement)
- 🔄 Add scenario analysis with backend API
- 🔄 Add authentication/authorization

## Testing the Connection

1. Start both servers
2. Open Streamlit UI: http://localhost:8501
3. Check backend status indicator (should be 🟢)
4. Click "Run Optimization"
5. Wait for results (1-5 minutes)
6. View updated KPIs and detailed results
7. Download CSV files if needed
