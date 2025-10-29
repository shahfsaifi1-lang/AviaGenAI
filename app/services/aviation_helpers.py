import math
from typing import Tuple

def wind_components(wind_dir_deg: float, wind_speed: float, rwy_deg: float) -> Tuple[float, float]:
    """
    Calculate headwind and crosswind components for runway operations.
    
    Args:
        wind_dir_deg: Wind direction in degrees (meteorological)
        wind_speed: Wind speed in knots
        rwy_deg: Runway heading in degrees
    
    Returns:
        Tuple of (headwind, crosswind) in knots
        Positive headwind = headwind, negative = tailwind
        Positive crosswind = from right, negative = from left
    """
    rad = math.radians((wind_dir_deg - rwy_deg) % 360)
    head = wind_speed * math.cos(rad)
    cross = wind_speed * math.sin(rad)
    return round(head, 1), round(cross, 1)

def density_altitude(pressure_alt_ft: float, oat_c: float) -> float:
    """
    Calculate density altitude for performance planning.
    
    Args:
        pressure_alt_ft: Pressure altitude in feet
        oat_c: Outside air temperature in Celsius
    
    Returns:
        Density altitude in feet
    """
    isa_temp = 15 - 2.0 * (pressure_alt_ft / 1000.0)
    delta = oat_c - isa_temp
    return round(pressure_alt_ft + (120 * delta), 0)
