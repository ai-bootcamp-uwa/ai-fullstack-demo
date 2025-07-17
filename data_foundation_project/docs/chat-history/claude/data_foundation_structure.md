# Module 1: Data Foundation - Simple Structure

```
data-foundation/                       # Root directory (Port 3001)
├── 📄 main.py                        # FastAPI app entry point
├── 📄 database.py                    # Database connection
├── 📄 models.py                      # Data models
├── 📄 routes.py                      # API endpoints
│
├── 📁 data/                          # Data files
│   ├── 📄 sample_sites.json         # Sample geological data
│   └── 📄 wamex_sample.json         # WAMEX sample response
│
├── 📄 requirements.txt               # Dependencies
├── 📄 .env                          # Environment variables (NOT in Git)
├── 📄 .env.example                  # Environment template (in Git)
├── 📄 .gitignore                    # Git ignore rules
├── 📄 Dockerfile                    # Container setup
└── 📄 README.md                     # Documentation
```

## Code Implementation

### **1. main.py** - Entry Point
```python
from fastapi import FastAPI
from routes import router

app = FastAPI(title="Geological Data API")
app.include_router(router, prefix="/api/data")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
```

### **2. models.py** - Data Models
```python
from pydantic import BaseModel
from typing import List, Optional

class GeologicalSite(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    mineral_type: str
    
class SpatialQuery(BaseModel):
    latitude: float
    longitude: float
    radius_km: float

class HealthResponse(BaseModel):
    status: str
    record_count: int
```

### **3. database.py** - Data Layer
```python
import json
from typing import List
from models import GeologicalSite

class DataStore:
    def __init__(self):
        self.sites = self._load_sample_data()
    
    def _load_sample_data(self) -> List[GeologicalSite]:
        """Load sample geological data"""
        with open("data/sample_sites.json", "r") as f:
            data = json.load(f)
        return [GeologicalSite(**site) for site in data]
    
    def get_all_sites(self) -> List[GeologicalSite]:
        return self.sites
    
    def spatial_query(self, lat: float, lng: float, radius: float) -> List[GeologicalSite]:
        """Simple distance-based filtering"""
        result = []
        for site in self.sites:
            # Simple distance calculation (for demo)
            distance = abs(site.latitude - lat) + abs(site.longitude - lng)
            if distance <= radius / 100:  # Rough approximation
                result.append(site)
        return result

# Global data store instance
data_store = DataStore()
```

### **4. routes.py** - API Endpoints
```python
from fastapi import APIRouter
from typing import List
from models import GeologicalSite, SpatialQuery, HealthResponse
from database import data_store

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        record_count=len(data_store.get_all_sites())
    )

@router.get("/geological-sites", response_model=List[GeologicalSite])
def get_geological_sites():
    return data_store.get_all_sites()

@router.get("/quality-metrics")
def get_quality_metrics():
    sites = data_store.get_all_sites()
    return {
        "total_records": len(sites),
        "data_quality_score": 0.99,
        "last_updated": "2024-12-01"
    }

@router.post("/spatial-query", response_model=List[GeologicalSite])
def spatial_query(query: SpatialQuery):
    return data_store.spatial_query(
        query.latitude, 
        query.longitude, 
        query.radius_km
    )
```

### **5. requirements.txt** - Dependencies
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
```

### **6. .env** - Configuration
```
# Database (for future Snowflake integration)
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password

# Application
DEBUG=true
LOG_LEVEL=INFO
```

### **7. data/sample_sites.json** - Sample Data
```json
[
  {
    "id": 1,
    "name": "Kalgoorlie Gold Mine",
    "latitude": -30.7489,
    "longitude": 121.4656,
    "mineral_type": "gold"
  },
  {
    "id": 2,
    "name": "Mount Gibson Iron",
    "latitude": -29.1167,
    "longitude": 117.2167,
    "mineral_type": "iron_ore"
  },
  {
    "id": 3,
    "name": "Greenbushes Lithium",
    "latitude": -33.8500,
    "longitude": 116.0500,
    "mineral_type": "lithium"
  }
]
```

### **8. .gitignore** - Git Rules
```
# Environment
.env
__pycache__/
*.pyc
.venv/
venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

### **9. .env.example** - Environment Template
```
# Database (for future Snowflake integration)
SNOWFLAKE_ACCOUNT=your_account_here
SNOWFLAKE_USER=your_user_here
SNOWFLAKE_PASSWORD=your_password_here

# Application
DEBUG=true
LOG_LEVEL=INFO
```

### **10. Dockerfile** - Simple Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 3001

CMD ["python", "main.py"]
```

## GitHub Setup & Workflow

### **Repository Setup**
```bash
# 1. Initialize repository
git init
git add .
git commit -m "Initial data foundation setup"

# 2. Create GitHub repository
# Go to GitHub → Create new repo: "geological-data-foundation"

# 3. Connect to GitHub
git remote add origin https://github.com/bootcamp-team/geological-data-foundation.git
git branch -M main
git push -u origin main
```

### **Rotation Workflow**
```bash
# Week 1 (Chris): Setup foundation
git checkout -b week1-foundation
# Implement basic structure
git add .
git commit -m "Add basic API endpoints and sample data"
git push origin week1-foundation
# Create PR: week1-foundation → main

# Week 2 (Jinwen): Add Snowflake
git checkout main
git pull origin main
git checkout -b week2-snowflake
# Add Snowflake integration
git add .
git commit -m "Add Snowflake database connection"
git push origin week2-snowflake
# Create PR: week2-snowflake → main

# Week 3 (Liam): Optimize performance
git checkout main
git pull origin main
git checkout -b week3-optimization
# Add performance improvements
git add .
git commit -m "Optimize queries for AI workloads"
git push origin week3-optimization

# Week 4 (Daniel): Production deployment
git checkout main
git pull origin main
git checkout -b week4-production
# Add monitoring and deployment
git add .
git commit -m "Add production monitoring and deployment"
git push origin week4-production
```

### **Branch Strategy**
```
main                 # Production-ready code
├── week1-foundation # Chris's implementation
├── week2-snowflake  # Jinwen's additions
├── week3-optimization # Liam's improvements
└── week4-production # Daniel's deployment
```

## Simple Lifecycle Workflow

### **Development Steps**
```bash
# 1. Setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 2. Run locally
python main.py

# 3. Test endpoints
curl http://localhost:3001/api/data/health
curl http://localhost:3001/api/data/geological-sites

# 4. Deploy with Docker
docker build -t data-foundation .
docker run -p 3001:3001 data-foundation
```

### **Integration Points**
```python
# Other modules can call:
# GET http://localhost:3001/api/data/health
# GET http://localhost:3001/api/data/geological-sites
# POST http://localhost:3001/api/data/spatial-query
```

## Week-by-Week Evolution

**Week 1 (Chris)**: Build this basic structure
**Week 2 (Jinwen)**: Add Snowflake connection to `database.py`
**Week 3 (Liam)**: Optimize for AI workloads
**Week 4 (Daniel)**: Add monitoring and deployment

This keeps it **simple** but **professional** with clear **architecture** and **growth path**.