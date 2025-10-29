#!/usr/bin/env python3
"""
Comprehensive test script for MetService NZ API
Tests multiple authentication methods and endpoints
"""
import asyncio
import httpx
from app.core.config import settings

async def test_authentication_methods():
    """Test different authentication methods"""
    print("🧪 Testing MetService NZ API Authentication Methods...")
    print(f"API Key: {settings.METSERVICE_API_KEY[:8]}...")
    
    if not settings.METSERVICE_API_KEY:
        print("❌ No MetService API key found in .env file")
        return
    
    # Test different base URLs and authentication methods
    test_configs = [
        {
            "name": "Method 1: Bearer Token",
            "url": "https://api.metservice.com/point-forecast/v1",
            "headers": {"Authorization": f"Bearer {settings.METSERVICE_API_KEY}"},
            "params": {"latitude": -36.8485, "longitude": 174.7633}
        },
        {
            "name": "Method 2: X-API-Key Header",
            "url": "https://api.metservice.com/point-forecast/v1",
            "headers": {"X-API-Key": settings.METSERVICE_API_KEY},
            "params": {"latitude": -36.8485, "longitude": 174.7633}
        },
        {
            "name": "Method 3: API Key in Params",
            "url": "https://api.metservice.com/point-forecast/v1",
            "headers": {},
            "params": {"api_key": settings.METSERVICE_API_KEY, "latitude": -36.8485, "longitude": 174.7633}
        },
        {
            "name": "Method 4: Different Base URL",
            "url": "https://api.metservice.com/v1/point-forecast",
            "headers": {"Authorization": f"Bearer {settings.METSERVICE_API_KEY}"},
            "params": {"latitude": -36.8485, "longitude": 174.7633}
        },
        {
            "name": "Method 5: Basic Auth",
            "url": "https://api.metservice.com/point-forecast/v1",
            "headers": {"Authorization": f"Basic {settings.METSERVICE_API_KEY}"},
            "params": {"latitude": -36.8485, "longitude": 174.7633}
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for config in test_configs:
            print(f"\n🔍 Testing {config['name']}...")
            try:
                response = await client.get(
                    config["url"], 
                    headers=config["headers"], 
                    params=config["params"],
                    timeout=10.0
                )
                
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ SUCCESS!")
                    data = response.json()
                    print(f"   Response keys: {list(data.keys())}")
                    return config  # Return successful config
                else:
                    print(f"   ❌ Failed: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print("\n❌ All authentication methods failed")
    print("\n📋 Next Steps:")
    print("1. Check your MetService NZ account status")
    print("2. Verify the API key is correct")
    print("3. Check if you need to activate the API key")
    print("4. Review the official documentation for the correct authentication method")
    print("5. Contact MetService NZ support if needed")

if __name__ == "__main__":
    asyncio.run(test_authentication_methods())
