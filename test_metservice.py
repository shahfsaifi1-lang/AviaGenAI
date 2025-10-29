#!/usr/bin/env python3
"""
Test script for MetService NZ API integration
"""
import asyncio
import httpx
from app.core.config import settings

async def test_metservice_api():
    """Test MetService NZ API with your API key"""
    print("🧪 Testing MetService NZ API...")
    print(f"API Key: {settings.METSERVICE_API_KEY[:8]}...")
    
    if not settings.METSERVICE_API_KEY:
        print("❌ No MetService API key found in .env file")
        return
    
    headers = {
        "Accept": "application/json"
    }
    
    # Test with Auckland coordinates (MetService might use lat/lon instead of ICAO)
    url = "https://api.metservice.com/point-forecast/v1"
    params = {
        "api_key": settings.METSERVICE_API_KEY,
        "latitude": -36.8485,  # Auckland latitude
        "longitude": 174.7633,  # Auckland longitude
        "variables": "temperature,wind_speed,wind_direction,visibility,cloud_cover"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"🌤️  Fetching weather for Auckland (-36.8485, 174.7633)...")
            response = await client.get(url, headers=headers, params=params)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API call successful!")
                print(f"Response keys: {list(data.keys())}")
                
                if 'forecasts' in data and len(data['forecasts']) > 0:
                    forecast = data['forecasts'][0]
                    print(f"Temperature: {forecast.get('temperature', 'N/A')}°C")
                    print(f"Wind: {forecast.get('wind_direction', 'N/A')}° at {forecast.get('wind_speed', 'N/A')} m/s")
                    print(f"Visibility: {forecast.get('visibility', 'N/A')} km")
                    print(f"Cloud Cover: {forecast.get('cloud_cover', 'N/A')}%")
                else:
                    print("No forecast data in response")
            else:
                print(f"❌ API call failed: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_metservice_api())
