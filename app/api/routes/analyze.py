from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from app.services.weather.select import get_taf_metar
from app.services.weather.decode import decode_metar, decode_taf
from app.services.decision_engine import analyze_weather
from app.services.llm_client import chat_completion

router = APIRouter()

@router.get("/analyze/weather")
async def analyze_weather_comprehensive(
    icao: str = Query(..., min_length=4, max_length=4, description="Airport ICAO code"),
    runway_deg: float = Query(..., description="Runway heading in degrees"),
    pressure_alt_ft: float = Query(0, description="Pressure altitude in feet"),
    question: Optional[str] = Query(None, description="Specific analysis question")
):
    """Comprehensive weather analysis with AI insights for T-6II operations."""
    try:
        import asyncio
        
        # Get weather data with timeout
        try:
            weather = await asyncio.wait_for(get_taf_metar(icao), timeout=10.0)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Weather data request timed out")
        
        if not weather.metar_raw:
            raise HTTPException(status_code=404, detail="No current weather data available")
        
        # Decode weather data
        metar_data = decode_metar(weather.metar_raw)
        taf_data = decode_taf(weather.taf_raw) if weather.taf_raw else {}
        
        # Get decision analysis
        analysis = analyze_weather(metar_data, runway_deg, pressure_alt_ft, 
                                 metar_data.get("temperature", {}).get("temp_c", 15))
        
        # Prepare AI analysis prompt
        weather_context = f"""
Airport: {icao}
Runway: {runway_deg}°
Pressure Altitude: {pressure_alt_ft} ft

Current Weather (METAR):
{weather.metar_raw}

Decoded METAR:
- Wind: {metar_data.get('wind', {}).get('dir_deg', 'N/A')}° at {metar_data.get('wind', {}).get('speed_kt', 'N/A')} kt
- Visibility: {metar_data.get('visibility_km', 'N/A')} km
- Ceiling: {metar_data.get('ceiling_ft', 'N/A')} ft
- Temperature: {metar_data.get('temperature', {}).get('temp_c', 'N/A')}°C
- Flight Rules: {metar_data.get('flight_rules', 'N/A')}

Forecast (TAF):
{weather.taf_raw if weather.taf_raw else 'No TAF available'}

Decision Analysis:
- Weather Category: {analysis['category']}
- Wind Components: {analysis['wind_components']}
- Density Altitude: {analysis['density_altitude_ft']} ft
- Considerations: {', '.join(analysis['considerations']) if analysis['considerations'] else 'None'}
"""
        
        user_question = question or "Analyze the weather conditions for T-6II flight operations and provide specific recommendations."
        
        # Get AI analysis
        messages = [
            {
                "role": "system", 
                "content": "You are an expert aviation weather analyst specializing in T-6II training operations. Provide detailed, actionable analysis with specific recommendations for flight safety and training effectiveness."
            },
            {
                "role": "user", 
                "content": f"{weather_context}\n\nQuestion: {user_question}"
            }
        ]
        
        ai_analysis = chat_completion(messages)
        
        return {
            "airport": icao,
            "runway_heading_deg": runway_deg,
            "pressure_altitude_ft": pressure_alt_ft,
            "weather_data": {
                "metar_raw": weather.metar_raw,
                "taf_raw": weather.taf_raw,
                "metar_decoded": metar_data,
                "taf_decoded": taf_data
            },
            "decision_analysis": analysis,
            "ai_analysis": ai_analysis,
            "timestamp": "2024-01-29T15:30:00Z"  # In production, use actual timestamp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/analyze/performance")
async def analyze_performance(
    icao: str = Query(..., min_length=4, max_length=4, description="Airport ICAO code"),
    pressure_alt_ft: float = Query(..., description="Pressure altitude in feet"),
    oat_c: float = Query(..., description="Outside air temperature in Celsius"),
    runway_length_ft: float = Query(5000, description="Runway length in feet"),
    aircraft_weight_lbs: float = Query(5500, description="Aircraft weight in pounds")
):
    """Analyze aircraft performance for T-6II operations."""
    try:
        from app.services.aviation_helpers import density_altitude
        
        # Calculate density altitude
        da = density_altitude(pressure_alt_ft, oat_c)
        
        # Basic performance analysis
        performance_analysis = {
            "density_altitude_ft": da,
            "pressure_altitude_ft": pressure_alt_ft,
            "outside_air_temp_c": oat_c,
            "isa_deviation_c": oat_c - (15 - 2.0 * (pressure_alt_ft / 1000.0)),
            "runway_length_ft": runway_length_ft,
            "aircraft_weight_lbs": aircraft_weight_lbs
        }
        
        # Performance impacts
        impacts = []
        if da > 3000:
            impacts.append(f"High density altitude {da} ft - expect 20-30% performance reduction")
        if da > 5000:
            impacts.append(f"Very high density altitude {da} ft - significant performance reduction expected")
        if pressure_alt_ft > 2000:
            impacts.append(f"High pressure altitude {pressure_alt_ft} ft - reduced engine power")
        if oat_c > 30:
            impacts.append(f"High temperature {oat_c}°C - reduced engine performance")
        
        performance_analysis["performance_impacts"] = impacts
        
        # T-6II specific recommendations
        recommendations = []
        if da < 1000:
            recommendations.append("✅ Excellent performance conditions")
        elif da < 3000:
            recommendations.append("✅ Good performance conditions")
        elif da < 5000:
            recommendations.append("⚠️ Moderate performance reduction expected")
        else:
            recommendations.append("❌ Significant performance reduction - consider alternatives")
        
        if runway_length_ft < 3000:
            recommendations.append("⚠️ Short runway - ensure adequate takeoff distance")
        elif runway_length_ft > 8000:
            recommendations.append("✅ Long runway - excellent margin for safety")
        
        performance_analysis["recommendations"] = recommendations
        
        return performance_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance analysis failed: {str(e)}")

@router.get("/analyze/route")
async def analyze_route(
    departure: str = Query(..., min_length=4, max_length=4, description="Departure airport ICAO"),
    arrival: str = Query(..., min_length=4, max_length=4, description="Arrival airport ICAO"),
    route_type: str = Query("VFR", description="Route type: VFR, IFR, or MIXED")
):
    """Analyze route conditions between two airports."""
    try:
        import asyncio
        
        # Get weather for both airports
        try:
            dep_weather = await asyncio.wait_for(get_taf_metar(departure), timeout=10.0)
            arr_weather = await asyncio.wait_for(get_taf_metar(arrival), timeout=10.0)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Weather data request timed out")
        
        # Decode weather data
        dep_metar = decode_metar(dep_weather.metar_raw) if dep_weather.metar_raw else {}
        arr_metar = decode_metar(arr_weather.metar_raw) if arr_weather.metar_raw else {}
        
        # Route analysis
        route_analysis = {
            "departure": {
                "icao": departure,
                "metar_raw": dep_weather.metar_raw,
                "metar_decoded": dep_metar,
                "conditions": dep_metar.get("flight_rules", "unknown")
            },
            "arrival": {
                "icao": arrival,
                "metar_raw": arr_weather.metar_raw,
                "metar_decoded": arr_metar,
                "conditions": arr_metar.get("flight_rules", "unknown")
            },
            "route_type": route_type,
            "analysis": {
                "departure_suitable": dep_metar.get("flight_rules", "unknown") in ["VFR", "MVFR"],
                "arrival_suitable": arr_metar.get("flight_rules", "unknown") in ["VFR", "MVFR"],
                "route_recommended": True  # Simplified for now
            }
        }
        
        # Generate recommendations
        recommendations = []
        if not route_analysis["analysis"]["departure_suitable"]:
            recommendations.append(f"❌ Departure {departure} conditions not suitable for {route_type}")
        if not route_analysis["analysis"]["arrival_suitable"]:
            recommendations.append(f"❌ Arrival {arrival} conditions not suitable for {route_type}")
        if route_analysis["analysis"]["departure_suitable"] and route_analysis["analysis"]["arrival_suitable"]:
            recommendations.append("✅ Both airports suitable for VFR operations")
        
        route_analysis["recommendations"] = recommendations
        
        return route_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route analysis failed: {str(e)}")
