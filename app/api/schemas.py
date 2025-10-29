from pydantic import BaseModel, Field
from typing import Optional

class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)

class AskResponse(BaseModel):
    answer: str

class WeatherRequest(BaseModel):
    icao: str = Field(..., min_length=3, max_length=4, description="ICAO airport code (e.g., NZAA, KLAX)")

class WeatherResponse(BaseModel):
    icao: str
    metar: Optional[str] = None
    taf: Optional[str] = None
    provider: str
    success: bool
    error: Optional[str] = None

class WeatherAnalysisRequest(BaseModel):
    icao: str = Field(..., min_length=3, max_length=4)
    question: str = Field(..., min_length=3, max_length=500)

class WeatherAnalysisResponse(BaseModel):
    icao: str
    weather_data: WeatherResponse
    analysis: str
    recommendation: str