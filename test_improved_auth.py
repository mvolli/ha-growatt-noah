#!/usr/bin/env python3
"""
Test the improved authentication method with growattServer fallback.
This tests the exact same flow that would happen in Home Assistant.
"""

import asyncio
import sys
import json
from pathlib import Path

# Add the custom component to path
sys.path.insert(0, str(Path(__file__).parent / "custom_components" / "growatt_noah"))

# Add the growattServer library
sys.path.insert(0, str(Path(__file__).parent.parent / "growatt-test" / "growattServer-1.6.0"))

try:
    from api import GrowattNoahAPI
    from const import CONNECTION_TYPE_API, DEVICE_TYPE_NOAH
    print("✅ Successfully imported integration modules")
except ImportError as e:
    print(f"❌ Failed to import integration modules: {e}")
    sys.exit(1)

async def test_improved_authentication():
    """Test the improved authentication with growattServer fallback."""
    print("🔋 Testing Improved Authentication (HA Integration Simulation)")
    print("=" * 60)
    
    # Configuration as would be used in HA
    config = {
        "username": "mvolli",
        "password": "123456",
        "device_id": "0PVPH6ZR23QT01AX",
        "connection_type": CONNECTION_TYPE_API,
        "device_type": DEVICE_TYPE_NOAH,
        "server_url": "https://openapi.growatt.com/"
    }
    
    print(f"Configuration: {json.dumps(config, indent=2)}")
    
    # Create API instance exactly as HA would
    api = GrowattNoahAPI(
        connection_type=config["connection_type"],
        device_type=config["device_type"],
        username=config["username"],
        password=config["password"],
        device_id=config["device_id"],
        server_url=config["server_url"]
    )
    
    try:
        print("\n🔍 Testing async_test_connection() with improved authentication...")
        connection_ok = await api.async_test_connection()
        
        if connection_ok:
            print("✅ Connection test PASSED with improved authentication!")
            
            print("\n📊 Testing data retrieval...")
            noah_data = await api.async_get_data()
            
            print(f"✅ Data retrieved successfully!")
            print(f"🔋 Battery SOC: {noah_data.battery.soc}%")
            print(f"⚡ Solar Power: {noah_data.solar.power}W")
            print(f"📊 System Status: {noah_data.system.status}")
            
            print(f"\n🎉 SUCCESS: Improved integration works perfectly!")
            print("This should now work in Home Assistant.")
            return True
            
        else:
            print("❌ Connection test still failed!")
            print("The improved authentication didn't resolve the issue.")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        print("Error details:")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await api.async_close()

async def test_dependencies():
    """Test if required dependencies are available."""
    print("\n🔍 Testing Dependencies")
    print("-" * 30)
    
    dependencies = {
        "aiohttp": "HTTP client for async requests",
        "growattServer": "Official Growatt API library", 
        "asyncio": "Async programming support",
        "hashlib": "Password hashing",
        "json": "JSON handling"
    }
    
    missing_deps = []
    available_deps = []
    
    for dep, description in dependencies.items():
        try:
            if dep == "aiohttp":
                import aiohttp
                available_deps.append(f"{dep}: {aiohttp.__version__}")
            elif dep == "growattServer":
                from growattServer import GrowattApi
                available_deps.append(f"{dep}: Available")
            elif dep == "asyncio":
                import asyncio
                available_deps.append(f"{dep}: Built-in")
            elif dep == "hashlib":
                import hashlib
                available_deps.append(f"{dep}: Built-in")
            elif dep == "json":
                import json
                available_deps.append(f"{dep}: Built-in")
                
        except ImportError:
            missing_deps.append(f"{dep}: {description}")
    
    print("✅ Available dependencies:")
    for dep in available_deps:
        print(f"   {dep}")
    
    if missing_deps:
        print("\n❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   {dep}")
        return False
    else:
        print("\n✅ All dependencies available!")
        return True

async def main():
    """Main test function."""
    print("🔧 Home Assistant Integration Authentication Test")
    print("=" * 55)
    
    # Test dependencies first
    deps_ok = await test_dependencies()
    
    if not deps_ok:
        print("\n❌ Dependency issues found - this explains HA connection failures")
        return False
    
    # Test improved authentication
    auth_ok = await test_improved_authentication()
    
    print(f"\n📋 TEST SUMMARY")
    print("=" * 30)
    
    if auth_ok:
        print("✅ Integration authentication test PASSED")
        print("🎯 The improved integration should work in Home Assistant")
        print("\n🔧 If HA still shows connection errors:")
        print("1. Restart Home Assistant to ensure dependencies are loaded")
        print("2. Check if growattServer library is installed in HA environment")
        print("3. Remove and re-add the integration to clear any cache")
        return True
    else:
        print("❌ Integration authentication test FAILED")
        print("🔧 Additional troubleshooting needed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)