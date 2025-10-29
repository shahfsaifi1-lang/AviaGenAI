import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

class ChecklistService:
    """Service for managing T-6II operational checklists"""
    
    def __init__(self):
        self.checklists_data = self._load_checklists()
    
    def _load_checklists(self) -> Dict[str, Any]:
        """Load checklists from YAML file"""
        try:
            checklists_path = Path("app/data/quick_checklists.yaml")
            if not checklists_path.exists():
                return {"phases": {}}
            
            with open(checklists_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading checklists: {e}")
            return {"phases": {}}
    
    def get_all_phases(self) -> List[str]:
        """Get list of all checklist phases"""
        return list(self.checklists_data.get("phases", {}).keys())
    
    def get_phase_checklist(self, phase: str) -> List[str]:
        """Get checklist items for a specific phase"""
        return self.checklists_data.get("phases", {}).get(phase, [])
    
    def get_all_checklists(self) -> Dict[str, List[str]]:
        """Get all checklists organized by phase"""
        return self.checklists_data.get("phases", {})
    
    def search_checklists(self, search_term: str) -> Dict[str, List[str]]:
        """Search checklists for specific terms"""
        search_term = search_term.lower()
        results = {}
        
        for phase, items in self.checklists_data.get("phases", {}).items():
            matching_items = [
                item for item in items 
                if search_term in item.lower()
            ]
            if matching_items:
                results[phase] = matching_items
        
        return results
    
    def get_checklist_summary(self) -> Dict[str, Any]:
        """Get summary of all checklists"""
        phases = self.checklists_data.get("phases", {})
        total_items = sum(len(items) for items in phases.values())
        
        return {
            "total_phases": len(phases),
            "total_items": total_items,
            "phases": {
                phase: {
                    "item_count": len(items),
                    "items": items
                } for phase, items in phases.items()
            }
        }

# Global checklist service instance
checklist_service = ChecklistService()
