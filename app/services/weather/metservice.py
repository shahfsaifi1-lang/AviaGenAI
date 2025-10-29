import os
import httpx
from typing import Optional, Dict
from app.services.weather.base import WeatherProvider, TafMetar
from app.core.config import settings

class MetServiceProvider(WeatherProvider):
    """CheckWX API provider (most reliable aviation weather)"""
    
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
        
        metar_raw, taf_raw = None, None
        
        async with httpx.AsyncClient(timeout=20.0, headers=self.headers) as client:
            try:
                # Fetch METAR data
                metar_response = await client.get(f"{self.base_url}/metar/{icao}")
                if metar_response.status_code == 200:
                    data = metar_response.json()
                    if data.get("results", 0) > 0 and data.get("data"):
                        metar_raw = data["data"][0]  # Get the first METAR
            except Exception as e:
                print(f"Error fetching METAR from CheckWX: {e}")
            
            try:
                # Fetch TAF data
                taf_response = await client.get(f"{self.base_url}/taf/{icao}")
                if taf_response.status_code == 200:
                    data = taf_response.json()
                    if data.get("results", 0) > 0 and data.get("data"):
                        taf_raw = data["data"][0]  # Get the first TAF
            except Exception as e:
                print(f"Error fetching TAF from CheckWX: {e}")
        
        return TafMetar(icao=icao, metar_raw=metar_raw or "", taf_raw=taf_raw or "")

    async def fetch_minute(self, lat: float, lon: float) -> Dict:
        """Fetch minute-by-minute weather data (if available)"""
        if not self.api_key:
            return {}
        
        async with httpx.AsyncClient(timeout=20.0, headers=self.headers) as client:
            try:
                # CheckWX doesn't have minute-by-minute data, but we can get current conditions
                # This is a placeholder for future implementation
                response = await client.get(f"{self.base_url}/metar/lat/{lat}/lon/{lon}")
                if response.status_code == 200:
                    data = response.json()
                    return data
            except Exception as e:
                print(f"Error fetching minute data from CheckWX: {e}")
                return {}
        return {}
