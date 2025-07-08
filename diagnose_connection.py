#!/usr/bin/env python3
"""
Diagnostic script to troubleshoot Noah 2000 connection issues.
Tests various connection methods and provides detailed error information.
"""

import asyncio
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path

# Add the custom component to path
sys.path.insert(0, str(Path(__file__).parent / "custom_components" / "growatt_noah"))

try:
    from api import GrowattNoahAPI
    from const import CONNECTION_TYPE_API, DEVICE_TYPE_NOAH
    print("✅ Successfully imported HA integration modules")
except ImportError as e:
    print(f"❌ Failed to import HA integration modules: {e}")
    sys.exit(1)

# Configuration
USERNAME = "mvolli"
PASSWORD = "123456"
DEVICE_ID = "0PVPH6ZR23QT01AX"

async def diagnose_connection_issues():
    """Comprehensive connection diagnosis."""
    print("🔍 Noah 2000 Connection Diagnostic Tool")
    print("=" * 50)
    print(f"👤 Username: {USERNAME}")
    print(f"🔋 Device ID: {DEVICE_ID}")
    print(f"⏰ Started: {datetime.now()}")
    print()
    
    # Test 1: Basic API Connection
    print("📋 Test 1: Basic API Connection")
    print("-" * 30)
    
    api = GrowattNoahAPI(
        connection_type=CONNECTION_TYPE_API,
        device_type=DEVICE_TYPE_NOAH,
        username=USERNAME,
        password=PASSWORD,
        device_id=DEVICE_ID,
        server_url="https://openapi.growatt.com/"
    )
    
    try:
        print("🔍 Testing async_test_connection()...")
        connection_result = await api.async_test_connection()
        if connection_result:
            print("✅ async_test_connection() passed")
        else:
            print("❌ async_test_connection() failed")
            
    except Exception as e:
        print(f"❌ async_test_connection() error: {e}")
        print(f"📋 Full traceback:\n{traceback.format_exc()}")
    
    # Test 2: Authentication Details
    print(f"\n📋 Test 2: Authentication Process")
    print("-" * 30)
    
    try:
        print("🔍 Testing authentication...")
        await api._authenticate_api()
        if api._auth_token:
            print(f"✅ Authentication successful")
            print(f"🔑 Auth token: {api._auth_token}")
            print(f"👤 User data: {api._user_data.get('accountName', 'Unknown')}")
        else:
            print("❌ Authentication failed - no token received")
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        print(f"📋 Full traceback:\n{traceback.format_exc()}")
    
    # Test 3: Data Retrieval
    print(f"\n📋 Test 3: Data Retrieval")
    print("-" * 30)
    
    try:
        print("🔍 Testing async_get_data()...")
        noah_data = await api.async_get_data()
        print("✅ Data retrieval successful!")
        print(f"🔋 Battery SOC: {noah_data.battery.soc}%")
        print(f"⚡ Battery Power: {noah_data.battery.power}W")
        print(f"☀️  Solar Power: {noah_data.solar.power}W")
        print(f"🔌 Grid Power: {noah_data.grid.power}W")
        print(f"📊 System Status: {noah_data.system.status}")
        
    except Exception as e:
        print(f"❌ Data retrieval error: {e}")
        print(f"📋 Full traceback:\n{traceback.format_exc()}")
    
    # Test 4: Individual API Methods
    print(f"\n📋 Test 4: Individual API Methods")
    print("-" * 30)
    
    try:
        print("🔍 Testing get_plant_list()...")
        plants = await api.get_plant_list()
        print(f"✅ Found {len(plants)} plant(s)")
        
        if plants:
            plant_id = plants[0].get('id') or plants[0].get('plantId')
            print(f"🌱 First plant: {plants[0].get('plantName', 'Unknown')} (ID: {plant_id})")
            
            print("🔍 Testing is_plant_noah_system()...")
            noah_check = await api.is_plant_noah_system(str(plant_id))
            noah_obj = noah_check.get('obj', {})
            print(f"🔋 Is Noah System: {noah_obj.get('isPlantNoahSystem', False)}")
            print(f"🔋 Has Noah Device: {noah_obj.get('isPlantHaveNoah', False)}")
            
            if DEVICE_ID:
                print(f"🔍 Testing noah_system_status() with device {DEVICE_ID}...")
                noah_status = await api.noah_system_status(DEVICE_ID)
                print(f"✅ Noah status retrieved: SOC {noah_status.get('soc', 'N/A')}%")
            
    except Exception as e:
        print(f"❌ Individual method error: {e}")
        print(f"📋 Full traceback:\n{traceback.format_exc()}")
    
    # Test 5: Network and Server Issues
    print(f"\n📋 Test 5: Network Diagnostics")
    print("-" * 30)
    
    try:
        import aiohttp
        print("🔍 Testing direct HTTP connection to Growatt server...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://openapi.growatt.com/") as response:
                print(f"✅ Server reachable: HTTP {response.status}")
                
    except Exception as e:
        print(f"❌ Network error: {e}")
    
    # Test 6: Configuration Issues
    print(f"\n📋 Test 6: Configuration Check")
    print("-" * 30)
    
    print(f"🔍 Checking configuration...")
    print(f"   Username: {'✅ Set' if USERNAME else '❌ Missing'}")
    print(f"   Password: {'✅ Set' if PASSWORD else '❌ Missing'}")
    print(f"   Device ID: {'✅ Set' if DEVICE_ID else '❌ Missing'}")
    print(f"   Connection Type: {CONNECTION_TYPE_API}")
    print(f"   Device Type: {DEVICE_TYPE_NOAH}")
    
    await api.async_close()
    
    print(f"\n📋 Diagnostic Summary")
    print("=" * 30)
    print("If you're seeing connection errors in Home Assistant:")
    print("1. Check Home Assistant logs for specific error messages")
    print("2. Verify the integration configuration matches these working settings")
    print("3. Ensure the integration is using the enhanced API methods")
    print("4. Try reloading the integration in Home Assistant")
    print("5. Check if the device_id field is set correctly in the integration config")

async def main():
    """Main function."""
    try:
        await diagnose_connection_issues()
        return 0
    except Exception as e:
        print(f"💥 Diagnostic failed: {e}")
        print(f"📋 Full traceback:\n{traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n⚠️  Diagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)