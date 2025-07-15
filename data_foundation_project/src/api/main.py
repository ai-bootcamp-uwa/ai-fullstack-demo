from fastapi import FastAPI, HTTPException, Query
from pathlib import Path
from data_foundation_project.src.data_access import DataLoader
import geopandas as gpd

app = FastAPI(title="Exploration Reports API")
data_path = Path(__file__).parent.parent.parent / 'data' / 'raw'
shapefiles = list(data_path.rglob('*.shp'))
if not shapefiles:
    raise RuntimeError(f"No .shp file found in {data_path} or its subdirectories.")
shapefile = shapefiles[0]
loader = DataLoader()
gdf = loader.load_raw_shapefile(shapefile)

# TODO: Endpoint to get a list of reports
@app.get("/reports")
def list_reports(limit: int = 10, offset: int = 0):
    sample = gdf.iloc[offset:offset+limit].copy()
    sample['geometry'] = sample['geometry'].apply(lambda geom: geom.wkt)
    return sample.to_dict(orient='records')

# TODO: Endpoint to get a report by ID
@app.get("/reports/{report_id}")
def get_report(report_id: int):
    row = gdf[gdf['ANUMBER'] == report_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Report not found")
    record = row.iloc[0].to_dict()
    record['geometry'] = row.iloc[0].geometry.wkt
    return record

# TODO: Endpoint to filter reports by commodity, year, or company
@app.get("/reports/filter")
def filter_reports(
    commodity: str = Query(None, description="Filter by commodity (e.g., COPPER)"),
    year: int = Query(None, description="Filter by report year"),
    company: str = Query(None, description="Filter by operator/company")
):
    filtered = gdf
    if commodity:
        filtered = filtered[filtered['TARGET_COM'].str.contains(commodity, case=False, na=False)]
    if year:
        filtered = filtered[filtered['REPORT_YEA'] == year]
    if company:
        filtered = filtered[filtered['OPERATOR'].str.contains(company, case=False, na=False)]
    filtered = filtered.copy()
    filtered['geometry'] = filtered['geometry'].apply(lambda geom: geom.wkt)
    return filtered.to_dict(orient='records')

# TODO: Endpoint to return report geometry (as WKT)
@app.get("/reports/{report_id}/geometry")
def get_report_geometry(report_id: int):
    row = gdf[gdf['ANUMBER'] == report_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"geometry": row.iloc[0].geometry.wkt}
