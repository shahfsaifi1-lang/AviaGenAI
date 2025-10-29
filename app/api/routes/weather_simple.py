from fastapi import APIRouter, HTTPException, Query
from app.services.weather.select import get_taf_metar, get_minute
from app.services.weather.decode import decode_metar, decode_taf

router = APIRouter()

@router.get("/weather/tafmetar")
async def tafmetar(icao: str = Query(..., min_length=4, max_length=4)):
    try:
        data = await get_taf_metar(icao)
        return {"icao": data.icao, "metar": decode_metar(data.metar_raw), "taf": decode_taf(data.taf_raw)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weather/minute")
async def minute(lat: float, lon: float):
    try:
        # Returns {} unless you configure MetService minute endpoint
        return await get_minute(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
