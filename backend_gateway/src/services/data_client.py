import httpx
from typing import List, Dict, Any, Optional

from ..core.config import settings

class DataFoundationClient:
    """Client for Data Foundation API (Module 1) - Port 8000"""
    
    def __init__(self):
        self.base_url = settings.data_foundation_url

    async def get_reports(self, limit: int = 5, offset: int = 0):
        """Get reports using actual Module 1 endpoint: GET /reports"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/reports",
                    params={"limit": limit, "offset": offset}
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise Exception(f"Data Foundation service unavailable: {e}")
            except httpx.HTTPStatusError as e:
                raise Exception(f"Data Foundation error: {e.response.status_code}")

    async def get_report_by_id(self, report_id: int):
        """Get single report using actual Module 1 endpoint: GET /reports/{id}"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/reports/{report_id}")
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise Exception(f"Data Foundation service unavailable: {e}")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise Exception(f"Report {report_id} not found")
                raise Exception(f"Data Foundation error: {e.response.status_code}")

    async def filter_reports(self, commodity: str = None, year: int = None, company: str = None, limit: int = 5):
        """Filter reports using actual Module 1 endpoint: GET /reports/filter"""
        params = {"limit": limit}
        if commodity:
            params["commodity"] = commodity
        if year:
            params["year"] = year
        if company:
            params["company"] = company

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/reports/filter", params=params)
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise Exception(f"Data Foundation service unavailable: {e}")
            except httpx.HTTPStatusError as e:
                raise Exception(f"Data Foundation error: {e.response.status_code}")

    async def get_report_geometry(self, report_id: int):
        """Get report geometry using actual Module 1 endpoint: GET /reports/{id}/geometry"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/reports/{report_id}/geometry")
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise Exception(f"Data Foundation service unavailable: {e}")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise Exception(f"Geometry for report {report_id} not found")
                raise Exception(f"Data Foundation error: {e.response.status_code}") 