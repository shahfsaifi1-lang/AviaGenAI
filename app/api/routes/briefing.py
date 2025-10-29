from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.api.schemas import (
    T6BriefingRequest, T6BriefingResponse, BriefingTemplateRequest,
    BriefingListResponse
)
from app.services.briefing import briefing_service

router = APIRouter()

@router.post("/briefing/template", response_model=T6BriefingResponse)
async def create_briefing_template(request: BriefingTemplateRequest):
    """Create a new T-6II pre-flight briefing template"""
    try:
        briefing = await briefing_service.create_briefing_template(request)
        return briefing
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/briefing/{briefing_id}", response_model=T6BriefingResponse)
async def get_briefing(briefing_id: str):
    """Get a specific briefing by ID"""
    briefing = briefing_service.get_briefing(briefing_id)
    if not briefing:
        raise HTTPException(status_code=404, detail="Briefing not found")
    return briefing

@router.put("/briefing/{briefing_id}", response_model=T6BriefingResponse)
async def update_briefing(briefing_id: str, updates: T6BriefingRequest):
    """Update an existing briefing"""
    try:
        briefing = await briefing_service.update_briefing(briefing_id, updates)
        if not briefing:
            raise HTTPException(status_code=404, detail="Briefing not found")
        return briefing
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/briefings", response_model=BriefingListResponse)
async def list_briefings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """List all briefings with pagination"""
    try:
        result = briefing_service.list_briefings(page, page_size)
        return BriefingListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/briefing/{briefing_id}/complete")
async def complete_briefing(briefing_id: str):
    """Mark a briefing as completed"""
    try:
        briefing = briefing_service.get_briefing(briefing_id)
        if not briefing:
            raise HTTPException(status_code=404, detail="Briefing not found")
        
        # Update status to completed
        updates = T6BriefingRequest(status="completed")
        updated_briefing = await briefing_service.update_briefing(briefing_id, updates)
        return {"message": "Briefing marked as completed", "briefing_id": briefing_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/briefing/template/fields")
async def get_briefing_fields():
    """Get the structure of briefing fields for form generation"""
    return {
        "briefing_structure": {
            "prelims": {
                "showstoppers": {
                    "imsafe": "bool",
                    "qualified": "bool", 
                    "current": "bool"
                },
                "admin": {
                    "crew_ac": "text",
                    "configuration_limits": "text",
                    "bookings": "text",
                    "decon": "text",
                    "efb": "text"
                }
            },
            "environment": {
                "met": {
                    "wind": "text",
                    "visibility": "text",
                    "ceiling": "text",
                    "ice": "text",
                    "sigmet": "text",
                    "alternate": "text",
                    "sea_state": "text",
                    "ect": "text"
                },
                "area_of_operations": {
                    "atc": "text",
                    "airspace": "text",
                    "notams": "text",
                    "aipsup": "text",
                    "raim": "text"
                },
                "performance": {
                    "max_power": "text",
                    "told": "text"
                }
            },
            "mission": {
                "sortie_aim": "text",
                "airex_overview": "text"
            },
            "coordinating_instructions": {
                "fuel": {
                    "bingo": "text"
                },
                "communications": "object",
                "timings": {
                    "walk": "text",
                    "line": "text", 
                    "duration": "text"
                }
            },
            "execution": {
                "scheme_of_manoeuvre": {
                    "departure": "text",
                    "exercises": "text",
                    "arrival": "text"
                },
                "teach_points": "array"
            },
            "actions_on": {
                "orm": {
                    "mrp": "text",
                    "farm": "text",
                    "mitigation": "text",
                    "most_likely_limit_exceedance": "text"
                },
                "environment": {
                    "bad_wx_plan": "text"
                },
                "ac_systems": {
                    "ace": "text",
                    "ttws": "text",
                    "pbn": "text"
                },
                "emergencies": {
                    "ejection": "text",
                    "bird_strike": "text",
                    "divert_options": "text"
                }
            },
            "summary": {
                "focus": "text",
                "simulated_emergencies": "array",
                "crm": "text",
                "next_event": {
                    "authorisation": "text",
                    "walk": "text",
                    "f700": "text",
                    "out_brief": "text"
                }
            }
        }
    }
