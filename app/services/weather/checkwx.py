import httpx
from typing import Optional
from app.services.weather.base import WeatherProvider, TafMetar
from app.core.config import settings

class CheckWXProvider(WeatherProvider):
    """CheckWX API weather provider (METAR/TAF data)"""
    
    def __init__(self):
        self.api_key = settings.CHECKWX_API_KEY
        self.base_url = "https://api.checkwx.com"
        self.headers = {
            "X-API-Key": self.api_key,
            "Accept": "application/json"
        }
    
    async def fetch_taf_metar(self, icao: str) -> TafMetar:
        """Fetch TAF and METAR data from CheckWX API"""
        if not self.api_key:
            print("CheckWX not configured - missing API key")
            return TafMetar(icao=icao, metar_raw="", taf_raw="")
        
        try:
            async with httpx.AsyncClient() as client:
                # Fetch METAR data
                metar_url = f"{self.base_url}/metar/{icao}"
                metar_response = await client.get(metar_url, headers=self.headers)
                metar_raw = ""
                if metar_response.status_code == 200:
                    data = metar_response.json()
                    if data.get("results", 0) > 0 and data.get("data"):
                        metar_raw = data["data"][0]  # Get the first METAR
                
                # Fetch TAF data
                taf_url = f"{self.base_url}/taf/{icao}"
                taf_response = await client.get(taf_url, headers=self.headers)
                taf_raw = ""
                if taf_response.status_code == 200:
                    data = taf_response.json()
                    if data.get("results", 0) > 0 and data.get("data"):
                        taf_raw = data["data"][0]  # Get the first TAF
                
                return TafMetar(icao=icao, metar_raw=metar_raw, taf_raw=taf_raw)
                
        except Exception as e:
            print(f"Error fetching weather from CheckWX: {e}")
            return TafMetar(icao=icao, metar_raw="", taf_raw="")
