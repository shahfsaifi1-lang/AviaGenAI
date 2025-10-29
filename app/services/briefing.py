import uuid
from datetime import datetime
from typing import Dict, List, Optional
from app.api.schemas import (
    T6BriefingRequest, T6BriefingResponse, BriefingTemplateRequest,
    PrelimsData, EnvironmentData, MissionData, CoordinatingInstructions,
    ExecutionData, ActionsOnData, SummaryData
)
from app.services.weather import get_taf_metar

class T6BriefingService:
    """Service for managing T-6II pre-flight briefings"""
    
    def __init__(self):
        # In-memory storage for now (can be replaced with database later)
        self.briefings: Dict[str, T6BriefingResponse] = {}
    
    async def create_briefing_template(self, request: BriefingTemplateRequest) -> T6BriefingResponse:
        """Create a new briefing template with auto-filled data where possible"""
        briefing_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Auto-fill weather data if requested
        environment_data = None
        if request.auto_fill_weather:
            weather_data = await get_taf_metar(request.icao)
            environment_data = EnvironmentData(
                met={
                    "wind": "Auto-filled from weather service",
                    "visibility": "Auto-filled from weather service", 
                    "ceiling": "Auto-filled from weather service",
                    "ice": "Check current SIGMET",
                    "sigmet": "Check current SIGMET",
                    "alternate": "Select based on weather",
                    "sea_state": "N/A for land operations",
                    "ect": "Check current weather"
                },
                area_of_operations={
                    "atc": "Check current frequencies",
                    "airspace": "Review airspace restrictions",
                    "notams": "Check current NOTAMs",
                    "aipsup": "Review AIP supplements",
                    "raim": "Check GPS availability"
                },
                performance={
                    "max_power": "Check aircraft performance charts",
                    "told": "Calculate takeoff/landing distances"
                }
            )
        
        # Create briefing template
        briefing = T6BriefingResponse(
            briefing_id=briefing_id,
            icao=request.icao,
            briefing_type=request.briefing_type,
            pilot_pitc=None,
            visual_fm=None,
            prelims=PrelimsData(
                showstoppers={
                    "imsafe": False,
                    "qualified": False,
                    "current": False
                },
                admin={
                    "crew_ac": "",
                    "configuration_limits": "",
                    "bookings": "",
                    "decon": "",
                    "efb": ""
                }
            ),
            environment=environment_data,
            mission=MissionData(
                sortie_aim="",
                airex_overview=""
            ),
            coordinating_instructions=CoordinatingInstructions(
                fuel={"bingo": ""},
                communications={},
                timings={"walk": "", "line": "", "duration": ""}
            ),
            execution=ExecutionData(
                scheme_of_manoeuvre={
                    "departure": "",
                    "exercises": "",
                    "arrival": ""
                },
                teach_points=[]
            ),
            actions_on=ActionsOnData(
                orm={
                    "mrp": "",
                    "farm": "",
                    "mitigation": "",
                    "most_likely_limit_exceedance": ""
                },
                environment={"bad_wx_plan": ""},
                ac_systems={"ace": "", "ttws": "", "pbn": ""},
                emergencies={
                    "ejection": "",
                    "bird_strike": "",
                    "divert_options": ""
                }
            ),
            summary=SummaryData(
                focus="",
                simulated_emergencies=[],
                crm="",
                next_event={
                    "authorisation": "",
                    "walk": "",
                    "f700": "",
                    "out_brief": ""
                }
            ),
            created_at=now,
            updated_at=now,
            status="draft",
            completion_percentage=0.0
        )
        
        # Store briefing
        self.briefings[briefing_id] = briefing
        
        return briefing
    
    async def update_briefing(self, briefing_id: str, updates: T6BriefingRequest) -> Optional[T6BriefingResponse]:
        """Update an existing briefing"""
        if briefing_id not in self.briefings:
            return None
        
        briefing = self.briefings[briefing_id]
        
        # Update fields if provided
        if updates.pilot_pitc is not None:
            briefing.pilot_pitc = updates.pilot_pitc
        if updates.visual_fm is not None:
            briefing.visual_fm = updates.visual_fm
        if updates.prelims is not None:
            briefing.prelims = updates.prelims
        if updates.environment is not None:
            briefing.environment = updates.environment
        if updates.mission is not None:
            briefing.mission = updates.mission
        if updates.coordinating_instructions is not None:
            briefing.coordinating_instructions = updates.coordinating_instructions
        if updates.execution is not None:
            briefing.execution = updates.execution
        if updates.actions_on is not None:
            briefing.actions_on = updates.actions_on
        if updates.summary is not None:
            briefing.summary = updates.summary
        
        # Update metadata
        briefing.updated_at = datetime.now()
        briefing.completion_percentage = self._calculate_completion_percentage(briefing)
        
        return briefing
    
    def get_briefing(self, briefing_id: str) -> Optional[T6BriefingResponse]:
        """Get a specific briefing by ID"""
        return self.briefings.get(briefing_id)
    
    def list_briefings(self, page: int = 1, page_size: int = 10) -> Dict:
        """List all briefings with pagination"""
        briefings_list = list(self.briefings.values())
        total = len(briefings_list)
        
        # Simple pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_briefings = briefings_list[start:end]
        
        return {
            "briefings": paginated_briefings,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    def _calculate_completion_percentage(self, briefing: T6BriefingResponse) -> float:
        """Calculate completion percentage of briefing"""
        total_fields = 0
        completed_fields = 0
        
        # Count fields in each section
        sections = [
            briefing.prelims,
            briefing.environment, 
            briefing.mission,
            briefing.coordinating_instructions,
            briefing.execution,
            briefing.actions_on,
            briefing.summary
        ]
        
        for section in sections:
            if section is None:
                continue
                
            # Count fields in section
            section_dict = section.dict()
            for key, value in section_dict.items():
                if isinstance(value, dict):
                    total_fields += len(value)
                    completed_fields += sum(1 for v in value.values() if v and str(v).strip())
                elif isinstance(value, list):
                    total_fields += 1
                    completed_fields += 1 if value else 0
                else:
                    total_fields += 1
                    completed_fields += 1 if value and str(value).strip() else 0
        
        return (completed_fields / total_fields * 100) if total_fields > 0 else 0.0

# Global briefing service instance
briefing_service = T6BriefingService()
