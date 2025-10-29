from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.services.checklists import checklist_service

router = APIRouter()

@router.get("/checklists/phases")
async def get_all_phases():
    """Get list of all checklist phases"""
    try:
        phases = checklist_service.get_all_phases()
        return {
            "phases": phases,
            "count": len(phases)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/checklists/phase/{phase}")
async def get_phase_checklist(phase: str):
    """Get checklist items for a specific phase"""
    try:
        items = checklist_service.get_phase_checklist(phase)
        if not items:
            raise HTTPException(status_code=404, detail=f"No checklist found for phase: {phase}")
        
        return {
            "phase": phase,
            "items": items,
            "count": len(items)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/checklists/all")
async def get_all_checklists():
    """Get all checklists organized by phase"""
    try:
        checklists = checklist_service.get_all_checklists()
        return {
            "checklists": checklists,
            "total_phases": len(checklists),
            "total_items": sum(len(items) for items in checklists.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/checklists/search")
async def search_checklists(
    q: str = Query(..., description="Search term for checklist items"),
    phase: Optional[str] = Query(None, description="Filter by specific phase")
):
    """Search checklists for specific terms"""
    try:
        if phase:
            # Search within specific phase
            phase_items = checklist_service.get_phase_checklist(phase)
            if not phase_items:
                raise HTTPException(status_code=404, detail=f"No checklist found for phase: {phase}")
            
            search_term = q.lower()
            matching_items = [
                item for item in phase_items 
                if search_term in item.lower()
            ]
            
            return {
                "phase": phase,
                "search_term": q,
                "items": matching_items,
                "count": len(matching_items)
            }
        else:
            # Search across all phases
            results = checklist_service.search_checklists(q)
            return {
                "search_term": q,
                "results": results,
                "total_matches": sum(len(items) for items in results.values())
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/checklists/summary")
async def get_checklist_summary():
    """Get summary of all checklists"""
    try:
        summary = checklist_service.get_checklist_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/checklists/training-flow")
async def get_training_flow():
    """Get complete training flow with all checklists"""
    try:
        checklists = checklist_service.get_all_checklists()
        
        # Create training flow with phase descriptions
        training_flow = {
            "preflight": {
                "description": "Pre-flight inspection and preparation",
                "items": checklists.get("preflight", [])
            },
            "before_start": {
                "description": "Cockpit preparation before engine start",
                "items": checklists.get("before_start", [])
            },
            "after_start": {
                "description": "Post-start checks and systems verification",
                "items": checklists.get("after_start", [])
            },
            "before_takeoff": {
                "description": "Final checks before takeoff",
                "items": checklists.get("before_takeoff", [])
            },
            "after_landing": {
                "description": "Post-landing procedures",
                "items": checklists.get("after_landing", [])
            }
        }
        
        return {
            "training_flow": training_flow,
            "total_phases": len(training_flow),
            "total_items": sum(len(phase["items"]) for phase in training_flow.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
