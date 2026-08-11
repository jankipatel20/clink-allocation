# 🏭 Clinker Allocation & Optimization System

[![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit_Cloud-FF4B4B?style=for-the-badge&logo=streamlit)](https://clink-allocation.streamlit.app/)


[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://clink-allocation.onrender.com/docs)


A full-stack Operations Research (OR) web application designed to solve complex supply chain routing and production problems. This system uses Mixed Integer Linear Programming (MILP) to minimize total logistics and production costs for clinker distribution across multiple plants and markets.

---

## Features
- **Mathematical Optimization:** Minimizes costs based on variable production limits, market demand, and transportation freight costs.
- **Interactive Dashboard:** Beautiful UI to visualize network flow, inventory levels, and cost breakdowns using Plotly.
- **History Tracking:** Persists past optimization runs and allows users to compare different scenarios.
- **Excel Integration:** Seamlessly parses complex spreadsheet datasets into optimization matrices.

## Tech Stack
- **Frontend:** Streamlit, Plotly, Pandas
- **Backend:** FastAPI, Pyomo, Uvicorn
- **Optimization Solver:** COIN-OR Branch and Cut (CBC)
- **Infrastructure:** Docker, Docker Compose, Render, Streamlit Cloud

---

## How to Run Locally

### Prerequisites
- Docker and Docker Compose installed.

### Quick Start
1. Clone the repository:
```bash
git clone https://github.com/jankipatel20/clink-allocation.git
cd clink-allocation
```

2. Start the services using Docker Compose:
```bash
docker-compose up --build
```

3. Access the application:
- **Frontend Dashboard:** [http://localhost:8501](http://localhost:8501)
- **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

