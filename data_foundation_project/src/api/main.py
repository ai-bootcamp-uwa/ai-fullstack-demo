from fastapi import FastAPI, HTTPException, Query
from pathlib import Path
import sys
import os
import json

# Add parent directories to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_access import DataLoader

app = FastAPI(title="Exploration Reports API")

# Load JSON data instead of shapefile
data_path = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'sample_records.json'
if not data_path.exists():
    raise RuntimeError(f"No JSON data file found at {data_path}")

with open(data_path, 'r') as f:
    reports_data = json.load(f)

loader = DataLoader()

# TODO: Endpoint to get a list of reports
@app.get("/reports")
def list_reports(limit: int = 10, offset: int = 0):
    # Return a slice of the reports data
    return reports_data[offset:offset+limit]

# TODO: Endpoint to get a report by ID
@app.get("/reports/{report_id}")
def get_report(report_id: int):
    # Find report by ANUMBER
    for report in reports_data:
        if report.get('ANUMBER') == report_id:
            return report
    raise HTTPException(status_code=404, detail="Report not found")

# TODO: Endpoint to filter reports
@app.get("/reports/filter")
def filter_reports(
    region: str = Query(None, description="Filter by region"),
    mineral_type: str = Query(None, description="Filter by mineral type"),
    limit: int = Query(10, description="Maximum number of results")
):
    filtered_reports = reports_data
    
    if region:
        filtered_reports = [r for r in filtered_reports if r.get('region', '').lower() == region.lower()]
    
    if mineral_type:
        filtered_reports = [r for r in filtered_reports if r.get('mineral_type', '').lower() == mineral_type.lower()]
    
    return filtered_reports[:limit]

# TODO: Endpoint to get geometry for a report
@app.get("/reports/{report_id}/geometry")
def get_report_geometry(report_id: int):
    # Find report by ANUMBER and return its geometry
    for report in reports_data:
        if report.get('ANUMBER') == report_id:
            if 'geometry' in report:
                return {"geometry": report['geometry']}
            else:
                raise HTTPException(status_code=404, detail="Geometry not found for this report")
    raise HTTPException(status_code=404, detail="Report not found")

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Exploration Reports API", 
        "total_reports": len(reports_data),
        "endpoints": [
            "/reports",
            "/reports/{id}",
            "/reports/filter",
            "/reports/{id}/geometry"
        ]
    }
