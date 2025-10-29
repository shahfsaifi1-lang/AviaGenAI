from fastapi import APIRouter, HTTPException, Query
from app.services.aviation_helpers import wind_components, density_altitude
from typing import Optional

router = APIRouter()

@router.get("/aviation/wind-components")
async def calculate_wind_components(
    wind_dir_deg: float = Query(..., description="Wind direction in degrees (meteorological)"),
    wind_speed: float = Query(..., description="Wind speed in knots"),
    rwy_deg: float = Query(..., description="Runway heading in degrees")
):
    """Calculate headwind and crosswind components for runway operations."""
    try:
        headwind, crosswind = wind_components(wind_dir_deg, wind_speed, rwy_deg)
        return {
            "wind_direction_deg": wind_dir_deg,
            "wind_speed_kt": wind_speed,
            "runway_heading_deg": rwy_deg,
            "headwind_kt": headwind,
            "crosswind_kt": crosswind,
            "tailwind_kt": -headwind if headwind < 0 else 0,
            "interpretation": {
                "headwind_effect": "favorable" if headwind > 0 else "unfavorable",
                "crosswind_effect": "manageable" if abs(crosswind) < 10 else "challenging",
                "t6_limitations": "within limits" if abs(crosswind) < 15 else "exceeds recommended"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/aviation/density-altitude")
async def calculate_density_altitude(
    pressure_alt_ft: float = Query(..., description="Pressure altitude in feet"),
    oat_c: float = Query(..., description="Outside air temperature in Celsius")
):
    """Calculate density altitude for performance planning."""
    try:
        density_alt = density_altitude(pressure_alt_ft, oat_c)
        isa_temp = 15 - 2.0 * (pressure_alt_ft / 1000.0)
        temp_deviation = oat_c - isa_temp
        
        return {
            "pressure_altitude_ft": pressure_alt_ft,
            "outside_air_temp_c": oat_c,
            "isa_temperature_c": round(isa_temp, 1),
            "temperature_deviation_c": round(temp_deviation, 1),
            "density_altitude_ft": density_alt,
            "performance_impact": {
                "takeoff_distance": "increased" if density_alt > pressure_alt_ft else "normal",
                "climb_rate": "reduced" if density_alt > pressure_alt_ft else "normal",
                "engine_power": "reduced" if density_alt > pressure_alt_ft else "normal"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/aviation/runway-analysis")
async def analyze_runway_conditions(
    icao: str = Query(..., min_length=4, max_length=4, description="Airport ICAO code"),
    rwy_deg: float = Query(..., description="Runway heading in degrees")
):
    """Analyze runway conditions using current weather data."""
    try:
        from app.services.weather.select import get_taf_metar
        from app.services.weather.decode import decode_metar
        
        # Get current weather
        weather = await get_taf_metar(icao)
        if not weather.metar_raw:
            raise HTTPException(status_code=404, detail="No current weather data available")
        
        # Decode METAR
        metar_data = decode_metar(weather.metar_raw)
        
        if "wind" not in metar_data:
            raise HTTPException(status_code=400, detail="No wind data in METAR")
        
        wind = metar_data["wind"]
        headwind, crosswind = wind_components(wind["dir_deg"], wind["speed_kt"], rwy_deg)
        
        # T-6II specific analysis
        t6_max_crosswind = 15  # knots - adjust based on your training standards
        t6_max_tailwind = 5    # knots - adjust based on your training standards
        
        return {
            "airport": icao,
            "runway_heading_deg": rwy_deg,
            "wind_data": {
                "direction_deg": wind["dir_deg"],
                "speed_kt": wind["speed_kt"],
                "gust_kt": wind.get("gust_kt"),
                "headwind_kt": headwind,
                "crosswind_kt": crosswind,
                "tailwind_kt": -headwind if headwind < 0 else 0
            },
            "t6_analysis": {
                "crosswind_within_limits": abs(crosswind) <= t6_max_crosswind,
                "tailwind_within_limits": abs(headwind) <= t6_max_tailwind if headwind < 0 else True,
                "recommended_runway": "suitable" if abs(crosswind) <= t6_max_crosswind and (headwind >= 0 or abs(headwind) <= t6_max_tailwind) else "not_recommended",
                "limitations": {
                    "max_crosswind_kt": t6_max_crosswind,
                    "max_tailwind_kt": t6_max_tailwind,
                    "current_crosswind_kt": abs(crosswind),
                    "current_tailwind_kt": abs(headwind) if headwind < 0 else 0
                }
            },
            "weather_conditions": {
                "visibility_km": metar_data.get("visibility_km"),
                "ceiling_ft": metar_data.get("ceiling_ft"),
                "flight_rules": metar_data.get("flight_rules")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
