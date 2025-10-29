from typing import Optional

class TafMetar:
    def __init__(self, icao: str, metar_raw: Optional[str], taf_raw: Optional[str]):
        self.icao = icao.upper()
        self.metar_raw = metar_raw or ""
        self.taf_raw = taf_raw or ""

class WeatherProvider:
    async def fetch_taf_metar(self, icao: str) -> TafMetar:
        raise NotImplementedError
