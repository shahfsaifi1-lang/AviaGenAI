from typing import Optional, Dict
import re

def decode_metar(raw: Optional[str]) -> Dict:
    """Basic METAR decoding without external dependencies"""
    if not raw:
        return {}
    
    raw = raw.strip()
    result = {"raw": raw}
    
    try:
        # Basic METAR parsing
        parts = raw.split()
        if len(parts) < 3:
            return result
        
        # Extract basic wind information
        wind_match = re.search(r'(\d{3})(\d{2,3})(?:G(\d{2,3}))?KT', raw)
        if wind_match:
            result["wind"] = {
                "dir_deg": int(wind_match.group(1)),
                "speed_kt": int(wind_match.group(2)),
                "gust_kt": int(wind_match.group(3)) if wind_match.group(3) else None
            }
        
        # Extract visibility
        vis_match = re.search(r'(\d{4})SM|(\d{1,2})SM', raw)
        if vis_match:
            if vis_match.group(1):
                result["visibility_km"] = int(vis_match.group(1)) * 1.609  # Convert SM to km
            else:
                result["visibility_km"] = int(vis_match.group(2)) * 1.609
        
        # Extract ceiling information
        ceiling_match = re.search(r'(BKN|OVC)(\d{3})', raw)
        if ceiling_match:
            result["ceiling_ft"] = int(ceiling_match.group(2)) * 100
        
        # Basic flight rules determination
        if "OVC" in raw or "BKN" in raw:
            result["flight_rules"] = "IFR" if "OVC" in raw else "MVFR"
        elif "FEW" in raw or "SCT" in raw:
            result["flight_rules"] = "VFR"
        else:
            result["flight_rules"] = "VFR"
            
    except Exception as e:
        result["error"] = str(e)
    
    return result

def decode_taf(raw: Optional[str]) -> Dict:
    """Basic TAF decoding without external dependencies"""
    if not raw:
        return {}
    
    raw = raw.strip()
    result = {"raw": raw}
    
    try:
        # Basic TAF parsing - extract key information
        parts = raw.split()
        
        # Extract wind information
        wind_match = re.search(r'(\d{3})(\d{2,3})KT', raw)
        if wind_match:
            result["wind"] = {
                "dir_deg": int(wind_match.group(1)),
                "speed_kt": int(wind_match.group(2))
            }
        
        # Extract visibility
        vis_match = re.search(r'(\d{4})SM|(\d{1,2})SM', raw)
        if vis_match:
            if vis_match.group(1):
                result["visibility_km"] = int(vis_match.group(1)) * 1.609
            else:
                result["visibility_km"] = int(vis_match.group(2)) * 1.609
        
        # Extract weather conditions
        weather_conditions = []
        if "SH" in raw:
            weather_conditions.append("showers")
        if "RA" in raw:
            weather_conditions.append("rain")
        if "SN" in raw:
            weather_conditions.append("snow")
        if "FG" in raw:
            weather_conditions.append("fog")
        
        if weather_conditions:
            result["weather"] = weather_conditions
        
        # Basic summary
        summary_parts = []
        if "wind" in result:
            summary_parts.append(f"Wind {result['wind']['dir_deg']}° at {result['wind']['speed_kt']} kt")
        if "visibility_km" in result:
            summary_parts.append(f"Visibility {result['visibility_km']:.1f} km")
        if weather_conditions:
            summary_parts.append(f"Weather: {', '.join(weather_conditions)}")
        
        result["summary"] = "; ".join(summary_parts) if summary_parts else "TAF data available"
        
    except Exception as e:
        result["error"] = str(e)
    
    return result
