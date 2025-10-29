from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

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

# T-6II Pre-Flight Briefing Schemas
class PrelimsData(BaseModel):
    showstoppers: Optional[Dict[str, bool]] = Field(default_factory=dict, description="IMSAFE, Qualified, Current status")
    admin: Optional[Dict[str, str]] = Field(default_factory=dict, description="Crew & A/C, Configuration/Limits, Bookings, Decon, EFB")

class EnvironmentData(BaseModel):
    met: Optional[Dict[str, str]] = Field(default_factory=dict, description="Wind, CLD, Vis, Ice, SIGMET, Alternate, Sea State, ECT")
    area_of_operations: Optional[Dict[str, str]] = Field(default_factory=dict, description="ATC, Airspace, NOTAMS, AIPSUP, RAIM")
    performance: Optional[Dict[str, str]] = Field(default_factory=dict, description="Max Power, TOLD (Max Abort/Touchdown)")

class MissionData(BaseModel):
    sortie_aim: Optional[str] = None
    airex_overview: Optional[str] = None

class CoordinatingInstructions(BaseModel):
    fuel: Optional[Dict[str, str]] = Field(default_factory=dict, description="Bingo fuel requirements")
    communications: Optional[Dict[str, str]] = Field(default_factory=dict, description="Comm frequencies and procedures")
    timings: Optional[Dict[str, str]] = Field(default_factory=dict, description="Walk, Line, Duration")

class ExecutionData(BaseModel):
    scheme_of_manoeuvre: Optional[Dict[str, str]] = Field(default_factory=dict, description="Departure, Exercises, Arrival")
    teach_points: Optional[List[str]] = Field(default_factory=list, description="QFI/Board Brief points")

class ActionsOnData(BaseModel):
    orm: Optional[Dict[str, str]] = Field(default_factory=dict, description="MRP, FARM, Mitigation, Most likely limit exceedance")
    environment: Optional[Dict[str, str]] = Field(default_factory=dict, description="Bad WX Plan")
    ac_systems: Optional[Dict[str, str]] = Field(default_factory=dict, description="ACE, TTWS, PBN")
    emergencies: Optional[Dict[str, str]] = Field(default_factory=dict, description="Ejection, Bird Strike, Divert Options")

class SummaryData(BaseModel):
    focus: Optional[str] = None
    simulated_emergencies: Optional[List[str]] = Field(default_factory=list)
    crm: Optional[str] = None
    next_event: Optional[Dict[str, str]] = Field(default_factory=dict, description="Authorisation, Walk, F700, Out Brief")

class T6BriefingRequest(BaseModel):
    """Request to create/update a T-6II pre-flight briefing"""
    briefing_id: Optional[str] = None
    icao: Optional[str] = Field(None, description="Airport ICAO code")
    briefing_type: Optional[str] = Field(None, description="Briefing type")
    pilot_pitc: Optional[str] = None
    visual_fm: Optional[str] = None
    
    # Briefing sections
    prelims: Optional[PrelimsData] = None
    environment: Optional[EnvironmentData] = None
    mission: Optional[MissionData] = None
    coordinating_instructions: Optional[CoordinatingInstructions] = None
    execution: Optional[ExecutionData] = None
    actions_on: Optional[ActionsOnData] = None
    summary: Optional[SummaryData] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: str = Field(default="draft", description="draft, completed, archived")

class T6BriefingResponse(BaseModel):
    """Response for T-6II pre-flight briefing"""
    briefing_id: str
    icao: str
    briefing_type: str
    pilot_pitc: Optional[str] = None
    visual_fm: Optional[str] = None
    
    # Briefing sections
    prelims: Optional[PrelimsData] = None
    environment: Optional[EnvironmentData] = None
    mission: Optional[MissionData] = None
    coordinating_instructions: Optional[CoordinatingInstructions] = None
    execution: Optional[ExecutionData] = None
    actions_on: Optional[ActionsOnData] = None
    summary: Optional[SummaryData] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    status: str
    completion_percentage: float = Field(..., description="Percentage of briefing completed")

class BriefingTemplateRequest(BaseModel):
    """Request to get a briefing template"""
    icao: str = Field(..., description="Airport ICAO code")
    briefing_type: str = Field(default="IF A to Instrun", description="Briefing type")
    auto_fill_weather: bool = Field(default=True, description="Auto-fill weather data")

class BriefingListResponse(BaseModel):
    """Response for listing briefings"""
    briefings: List[T6BriefingResponse]
    total: int
    page: int
    page_size: int