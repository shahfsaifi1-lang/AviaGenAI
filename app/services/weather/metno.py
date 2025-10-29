import httpx
from typing import Optional
from app.services.weather.base import WeatherProvider, TafMetar
from app.core.config import settings

class MetNoProvider(WeatherProvider):
    """MET Norway weather provider (free, public API)"""
    
    def __init__(self):
        self.base_url = "https://api.met.no/weatherapi/tafmetar/1.0"
        self.headers = {
            "User-Agent": settings.METNO_USER_AGENT,
            "Accept": "application/json"
        }
    
    async def fetch_taf_metar(self, icao: str) -> TafMetar:
        """Fetch TAF and METAR data from MET Norway"""
        try:
            async with httpx.AsyncClient() as client:
                # Fetch METAR
                metar_url = f"{self.base_url}/metar/{icao}"
                metar_response = await client.get(metar_url, headers=self.headers)
                metar_raw = ""
                if metar_response.status_code == 200:
                    data = metar_response.json()
                    if data and len(data) > 0:
                        metar_raw = data[0].get("rawMETAR", "")
                
                # Fetch TAF
                taf_url = f"{self.base_url}/taf/{icao}"
                taf_response = await client.get(taf_url, headers=self.headers)
                taf_raw = ""
                if taf_response.status_code == 200:
                    data = taf_response.json()
                    if data and len(data) > 0:
                        taf_raw = data[0].get("rawTAF", "")
                
                return TafMetar(icao=icao, metar_raw=metar_raw, taf_raw=taf_raw)
                
        except Exception as e:
            print(f"Error fetching weather from MET Norway: {e}")
            return TafMetar(icao=icao, metar_raw="", taf_raw="")
