import httpx

class DataFoundationClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    async def fetch_reports(self, limit: int = 10, offset: int = 0):
        """Fetch a list of reports from the Data Foundation API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/reports", params={"limit": limit, "offset": offset})
            response.raise_for_status()
            return response.json()

    async def fetch_report_by_id(self, report_id: int):
        """Fetch a single report by its ID from the Data Foundation API."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/reports/{report_id}")
            response.raise_for_status()
            return response.json()
