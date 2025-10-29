import httpx
from typing import Optional
from app.services.weather.base import WeatherProvider, TafMetar
from app.core.config import settings

class MetServiceProvider(WeatherProvider):
    """MetService NZ weather provider (requires API key)"""
    
    def __init__(self):
        self.base_url = settings.METSERVICE_BASE_URL
        self.api_key = settings.METSERVICE_API_KEY
        self.metar_path = settings.METSERVICE_METAR_PATH
        self.taf_path = settings.METSERVICE_TAF_PATH
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
    
    async def fetch_taf_metar(self, icao: str) -> TafMetar:
        """Fetch TAF and METAR data from MetService NZ"""
        if not self.api_key or not self.base_url:
            print("MetService NZ not configured - missing API key or base URL")
            return TafMetar(icao=icao, metar_raw="", taf_raw="")
        
        try:
            async with httpx.AsyncClient() as client:
                # Fetch METAR
                metar_url = f"{self.base_url}{self.metar_path}/{icao}"
                metar_response = await client.get(metar_url, headers=self.headers)
                metar_raw = ""
                if metar_response.status_code == 200:
                    data = metar_response.json()
                    metar_raw = data.get("rawMETAR", "")
                
                # Fetch TAF
                taf_url = f"{self.base_url}{self.taf_path}/{icao}"
                taf_response = await client.get(taf_url, headers=self.headers)
                taf_raw = ""
                if taf_response.status_code == 200:
                    data = taf_response.json()
                    taf_raw = data.get("rawTAF", "")
                
                return TafMetar(icao=icao, metar_raw=metar_raw, taf_raw=taf_raw)
                
        except Exception as e:
            print(f"Error fetching weather from MetService NZ: {e}")
            return TafMetar(icao=icao, metar_raw="", taf_raw="")
