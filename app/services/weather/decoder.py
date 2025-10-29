from typing import Optional, Dict
import re
from app.services.aviation_helpers import wind_components, density_altitude

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
            wind_dir = int(wind_match.group(1))
            wind_speed = int(wind_match.group(2))
            wind_gust = int(wind_match.group(3)) if wind_match.group(3) else None
            
            result["wind"] = {
                "dir_deg": wind_dir,
                "speed_kt": wind_speed,
                "gust_kt": wind_gust
            }
            
            # Add wind components for common runway headings (T-6II operations)
            common_runways = [18, 36, 9, 27]  # Add more as needed
            wind_components_data = {}
            for rwy in common_runways:
                headwind, crosswind = wind_components(wind_dir, wind_speed, rwy)
                wind_components_data[f"rwy_{rwy:02d}"] = {
                    "headwind_kt": headwind,
                    "crosswind_kt": crosswind
                }
            result["wind_components"] = wind_components_data
        
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
        
        # Extract temperature and dewpoint
        temp_match = re.search(r'(\d{2})/(\d{2})', raw)
        if temp_match:
            temp_c = int(temp_match.group(1))
            dewpoint_c = int(temp_match.group(2))
            result["temperature"] = {
                "temp_c": temp_c,
                "dewpoint_c": dewpoint_c
            }
            
            # Calculate density altitude if we have pressure altitude
            # For now, assume sea level (0 ft) - in real implementation, get from QNH
            pressure_alt_ft = 0  # This should be calculated from QNH in real implementation
            result["density_altitude_ft"] = density_altitude(pressure_alt_ft, temp_c)
        
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
