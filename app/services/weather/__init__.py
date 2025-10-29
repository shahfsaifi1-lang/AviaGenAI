from .metservice import MetServiceProvider
from .metno import MetNoTafMetarProvider
from .base import TafMetar

_metsvc = MetServiceProvider()
_metno = MetNoTafMetarProvider()

async def get_taf_metar(icao: str) -> TafMetar:
    t = await _metsvc.fetch_taf_metar(icao)
    if t.metar_raw or t.taf_raw:
        return t
    return await _metno.fetch_taf_metar(icao)

async def get_minute(lat: float, lon: float) -> dict:
    return await _metsvc.fetch_minute(lat, lon)  # returns {} if not configured
