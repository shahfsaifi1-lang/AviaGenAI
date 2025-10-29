from fastapi import APIRouter, HTTPException
from app.api.schemas import WeatherRequest, WeatherResponse, WeatherAnalysisRequest, WeatherAnalysisResponse
from app.services.weather import get_taf_metar, get_minute
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

@router.post("/weather/analyze", response_model=WeatherAnalysisResponse)
async def analyze_weather(req: WeatherAnalysisRequest):
    """Get weather data and AI analysis for aviation decision making"""
    try:
        # Get weather data
        weather_result = await get_taf_metar(req.icao)
        
        # Create weather response
        weather_response = WeatherResponse(
            icao=weather_result.icao,
            metar=weather_result.metar_raw if weather_result.metar_raw else None,
            taf=weather_result.taf_raw if weather_result.taf_raw else None,
            provider="Weather Service",
            success=bool(weather_result.metar_raw or weather_result.taf_raw),
            error=None if (weather_result.metar_raw or weather_result.taf_raw) else "No weather data available"
        )
        
        # Prepare weather context for AI analysis
        weather_context = ""
        if weather_result.metar_raw:
            weather_context += f"METAR: {weather_result.metar_raw}\n"
        if weather_result.taf_raw:
            weather_context += f"TAF: {weather_result.taf_raw}\n"
        
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
