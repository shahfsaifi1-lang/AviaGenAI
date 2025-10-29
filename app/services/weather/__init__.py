from .metservice import MetServiceProvider
from .metno import MetNoTafMetarProvider
from .base import TafMetar
from .decoder import decode_metar, decode_taf

_metsvc = MetServiceProvider()
_metno = MetNoTafMetarProvider()

async def get_taf_metar(icao: str) -> TafMetar:
    t = await _metsvc.fetch_taf_metar(icao)
    if t.metar_raw or t.taf_raw:
        return t
    return await _metno.fetch_taf_metar(icao)

async def get_taf_metar_decoded(icao: str) -> dict:
    """Get weather data with decoded METAR/TAF information"""
    weather = await get_taf_metar(icao)
    return {
        "icao": weather.icao,
        "metar_raw": weather.metar_raw,
        "taf_raw": weather.taf_raw,
        "metar_decoded": decode_metar(weather.metar_raw),
        "taf_decoded": decode_taf(weather.taf_raw)
    }

async def get_minute(lat: float, lon: float) -> dict:
    return await _metsvc.fetch_minute(lat, lon)  # returns {} if not configured
