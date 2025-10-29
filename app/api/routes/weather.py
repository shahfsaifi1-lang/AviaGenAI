from fastapi import APIRouter, HTTPException
from app.api.schemas import WeatherRequest, WeatherResponse, WeatherAnalysisRequest, WeatherAnalysisResponse
from app.services.weather import get_taf_metar, get_taf_metar_decoded, get_minute
from app.services.llm_client import chat_completion

router = APIRouter()

@router.get("/weather/providers")
async def get_weather_providers():
    """Get information about configured weather providers"""
    from app.core.config import settings
    providers = []
    
    # Check CheckWX (via MetServiceProvider)
    if settings.CHECKWX_API_KEY:
        providers.append("CheckWX: configured")
    else:
        providers.append("CheckWX: not configured")
    
    # MET Norway is always available
    providers.append("MET Norway: available (free)")
    
    return {
        "providers": providers,
        "count": len(providers)
    }

@router.post("/weather", response_model=WeatherResponse)
async def get_weather(req: WeatherRequest):
    """Get current weather data (METAR/TAF) for an airport"""
    try:
        result = await get_taf_metar(req.icao)
        
        # Determine which provider was used based on data availability
        provider_name = "CheckWX" if (result.metar_raw or result.taf_raw) else "MET Norway"
        
        return WeatherResponse(
            icao=result.icao,
            metar=result.metar_raw if result.metar_raw else None,
            taf=result.taf_raw if result.taf_raw else None,
            provider=provider_name,
            success=bool(result.metar_raw or result.taf_raw),
            error=None if (result.metar_raw or result.taf_raw) else "No weather data available"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/weather/decoded")
async def get_weather_decoded(req: WeatherRequest):
    """Get weather data with decoded METAR/TAF information"""
    try:
        decoded_data = await get_taf_metar_decoded(req.icao)
        return decoded_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/weather/analyze", response_model=WeatherAnalysisResponse)
async def analyze_weather(req: WeatherAnalysisRequest):
    """Get weather data and AI analysis for aviation decision making"""
    try:
        # Get decoded weather data for better analysis
        decoded_weather = await get_taf_metar_decoded(req.icao)
        
        # Create weather response
        weather_response = WeatherResponse(
            icao=decoded_weather["icao"],
            metar=decoded_weather["metar_raw"] if decoded_weather["metar_raw"] else None,
            taf=decoded_weather["taf_raw"] if decoded_weather["taf_raw"] else None,
            provider="Weather Service",
            success=bool(decoded_weather["metar_raw"] or decoded_weather["taf_raw"]),
            error=None if (decoded_weather["metar_raw"] or decoded_weather["taf_raw"]) else "No weather data available"
        )
        
        # Prepare enhanced weather context for AI analysis
        weather_context = ""
        if decoded_weather["metar_raw"]:
            weather_context += f"METAR: {decoded_weather['metar_raw']}\n"
            # Add decoded METAR data for better analysis
            metar_data = decoded_weather["metar_decoded"]
            if metar_data and "flight_rules" in metar_data:
                weather_context += f"Flight Rules: {metar_data['flight_rules']}\n"
            if metar_data and "wind" in metar_data:
                wind = metar_data["wind"]
                if wind.get("dir_deg") and wind.get("speed_kt"):
                    weather_context += f"Wind: {wind['dir_deg']}° at {wind['speed_kt']} kt"
                    if wind.get("gust_kt"):
                        weather_context += f" (gusts {wind['gust_kt']} kt)"
                    weather_context += "\n"
            if metar_data and "visibility_km" in metar_data:
                weather_context += f"Visibility: {metar_data['visibility_km']} km\n"
            if metar_data and "ceiling_ft" in metar_data:
                weather_context += f"Ceiling: {metar_data['ceiling_ft']} ft\n"
        
        if decoded_weather["taf_raw"]:
            weather_context += f"TAF: {decoded_weather['taf_raw']}\n"
            # Add TAF summary if available
            taf_data = decoded_weather["taf_decoded"]
            if taf_data and "summary" in taf_data:
                weather_context += f"TAF Summary: {taf_data['summary']}\n"
        
        if not weather_context:
            weather_context = "No current weather data available for this airport."
        
        # Create AI analysis prompt
        analysis_prompt = f"""
You are an aviation weather expert. Analyze the following weather data and provide guidance for T-6II flight operations.

Weather Data for {req.icao}:
{weather_context}

Question: {req.question}

Please provide:
1. Weather analysis (visibility, ceiling, wind, precipitation, etc.)
2. VFR/MVFR/IFR conditions assessment
3. Specific recommendations for T-6II operations
4. Any safety considerations or limitations

Be concise but thorough in your analysis.
"""
        
        # Get AI analysis
        messages = [
            {"role": "system", "content": "You are an expert aviation weather analyst specializing in T-6II operations."},
            {"role": "user", "content": analysis_prompt}
        ]
        
        analysis = chat_completion(messages)
        
        # Extract recommendation (first part of analysis)
        recommendation = analysis.split('\n')[0] if analysis else "Unable to analyze weather data"
        
        return WeatherAnalysisResponse(
            icao=req.icao,
            weather_data=weather_response,
            analysis=analysis,
            recommendation=recommendation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
