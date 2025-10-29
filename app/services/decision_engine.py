import os
from typing import Dict, List, Any, Optional
from app.services.aviation_helpers import wind_components, density_altitude

def env_float(name: str, default: Optional[float]) -> Optional[float]:
    v = os.getenv(name, "").strip()
    if not v or v.startswith('#'):
        return default
    try:
        return float(v)
    except ValueError:
        return default

# Pull configurable thresholds from env
VFR_MIN_VIS_KM  = env_float("VFR_MIN_VIS_KM", 5.0)
VFR_MIN_CEILING = env_float("VFR_MIN_CEILING_FT", 3000.0)
MVFR_MIN_VIS_KM = env_float("MVFR_MIN_VIS_KM", 5.0)
MVFR_MIN_CEILING= env_float("MVFR_MIN_CEILING_FT", 1000.0)
T6_MAX_XWIND_KT = env_float("T6_MAX_XWIND_KT", None)  # set if you have an approved value

def classify_vmc(visibility_km: Optional[float], ceiling_ft: Optional[float]) -> str:
    # Placeholder logic; tune to your authority/AIP
    if visibility_km is None or ceiling_ft is None:
        return "unknown"
    if ceiling_ft < 500 or (visibility_km < 1.6):   # LIFR-ish placeholder
        return "LIFR"
    if ceiling_ft < MVFR_MIN_CEILING or (visibility_km < MVFR_MIN_VIS_KM):
        return "IFR"
    if ceiling_ft < VFR_MIN_CEILING or (visibility_km < VFR_MIN_VIS_KM):
        return "MVFR"
    return "VFR"

def analyze_weather(metar_dec: Dict, runway_deg: float, pa_ft: float, oat_c: float) -> Dict[str, Any]:
    wdir = (metar_dec.get("wind") or {}).get("dir_deg")
    wspd = (metar_dec.get("wind") or {}).get("speed_kt")
    head, cross = (None, None)
    if wdir is not None and wspd is not None:
        head, cross = wind_components(float(wdir), float(wspd), runway_deg)

    da = density_altitude(pa_ft, oat_c)
    category = classify_vmc(metar_dec.get("visibility_km"), metar_dec.get("ceiling_ft"))

    considerations: List[str] = []
    if category in ("IFR","LIFR"):
        considerations.append("Instrument flight likely required; confirm minima and alternates.")
    if category == "MVFR":
        considerations.append("Marginal VFR; consider clouds/terrain/escape options.")
    if cross is not None and T6_MAX_XWIND_KT is not None and cross > T6_MAX_XWIND_KT:
        considerations.append(f"Crosswind {cross} kt exceeds configured T-6 limit {T6_MAX_XWIND_KT} kt.")
    if da > 3000:
        considerations.append(f"High density altitude {da} ft; expect performance reductions.")
    return {
        "category": category,
        "wind_components": {"headwind_kt": head, "crosswind_kt": cross},
        "density_altitude_ft": da,
        "considerations": considerations
    }
