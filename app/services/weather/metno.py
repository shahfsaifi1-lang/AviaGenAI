import os
import httpx
from app.services.weather.base import WeatherProvider, TafMetar

UA = os.getenv("METNO_USER_AGENT", "AviaGenAI/0.1 (contact: you@example.com)")

class MetNoTafMetarProvider(WeatherProvider):
    BASE = "https://api.met.no/weatherapi/tafmetar/1.0"

    async def fetch_taf_metar(self, icao: str) -> TafMetar:
        headers = {"User-Agent": UA, "Accept": "text/plain"}
        metar_raw, taf_raw = None, None
        async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
            m = await client.get(f"{self.BASE}/metar.txt", params={"icao": icao})
            if m.status_code == 200:
                metar_raw = m.text
            t = await client.get(f"{self.BASE}/taf.txt", params={"icao": icao})
            if t.status_code == 200:
                taf_raw = t.text
        return TafMetar(icao, metar_raw, taf_raw)
