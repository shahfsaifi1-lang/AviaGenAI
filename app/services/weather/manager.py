from typing import List, Optional
from app.services.weather.base import WeatherProvider, TafMetar
from app.services.weather.checkwx import CheckWXProvider
from app.services.weather.metno import MetNoProvider
from app.services.weather.metservice import MetServiceProvider
from app.core.config import settings

class WeatherManager:
    """Manages multiple weather providers with fallback logic"""
    
    def __init__(self):
        self.providers: List[WeatherProvider] = []
        
        # Add CheckWX first (most reliable for aviation weather)
        if settings.CHECKWX_API_KEY:
            self.providers.append(CheckWXProvider())
            print("✅ CheckWX provider configured")
        
        # Add MetService NZ (if configured)
        if settings.METSERVICE_API_KEY and settings.METSERVICE_BASE_URL:
            self.providers.append(MetServiceProvider())
            print("✅ MetService NZ provider configured")
        
        # Add MET Norway as fallback (always available)
        self.providers.append(MetNoProvider())
        print("✅ MET Norway provider configured")
    
    async def fetch_weather(self, icao: str) -> TafMetar:
        """Fetch weather data using available providers with fallback"""
        for provider in self.providers:
            try:
                result = await provider.fetch_taf_metar(icao)
                # Check if we got meaningful data
                if result.metar_raw or result.taf_raw:
                    print(f"✅ Weather data fetched from {provider.__class__.__name__}")
                    return result
            except Exception as e:
                print(f"❌ Error with {provider.__class__.__name__}: {e}")
                continue
        
        # If all providers failed, return empty result
        print("❌ All weather providers failed")
        return TafMetar(icao=icao, metar_raw="", taf_raw="")
    
    def get_provider_info(self) -> List[str]:
        """Get information about configured providers"""
        info = []
        for provider in self.providers:
            if isinstance(provider, CheckWXProvider):
                status = "configured" if settings.CHECKWX_API_KEY else "not configured"
                info.append(f"CheckWX: {status}")
            elif isinstance(provider, MetServiceProvider):
                status = "configured" if settings.METSERVICE_API_KEY else "not configured"
                info.append(f"MetService NZ: {status}")
            elif isinstance(provider, MetNoProvider):
                info.append("MET Norway: available (free)")
        return info

# Global weather manager instance
weather_manager = WeatherManager()
