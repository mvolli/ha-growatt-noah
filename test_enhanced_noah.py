#!/usr/bin/env python3
"""
Test script for enhanced Noah 2000 integration with advanced battery management.
Tests the new comprehensive API methods integrated from growattServer library.
"""

import asyncio
import sys
import json
from datetime import datetime
from pathlib import Path

# Add the custom component to path
sys.path.insert(0, str(Path(__file__).parent / "custom_components" / "growatt_noah"))

from api import GrowattNoahAPI
from const import CONNECTION_TYPE_API, DEVICE_TYPE_NOAH

# User credentials
USERNAME = "mvolli"
PASSWORD = "123456"

async def test_enhanced_noah_integration():
    """Test the enhanced Noah 2000 integration."""
    print("🔋 Enhanced Noah 2000 Integration Test")
    print("=" * 50)
    print(f"👤 Username: {USERNAME}")
    print(f"⏰ Started: {datetime.now()}")
    print()
    
    # Initialize API client with enhanced features
    api = GrowattNoahAPI(
        connection_type=CONNECTION_TYPE_API,
        device_type=DEVICE_TYPE_NOAH,
        username=USERNAME,
        password=PASSWORD,
        server_url="https://openapi.growatt.com/"
    )
    
    try:
        # Test 1: Connection
        print("🔍 Step 1: Testing API connection...")
        is_connected = await api.async_test_connection()
        if is_connected:
            print("✅ API connection successful!")
        else:
            print("❌ API connection failed!")
            return False
        
        # Test 2: Get comprehensive Noah data
        print("\n🔍 Step 2: Getting comprehensive Noah data...")
        try:
            comprehensive_data = await api.get_comprehensive_noah_data()
            print("✅ Comprehensive data retrieved successfully!")
            
            # Display key information
            print(f"\n📊 COMPREHENSIVE NOAH DATA:")
            print("=" * 40)
            
            # Plant information
            plant = comprehensive_data.get("plant", {})
            print(f"🌱 Plant: {plant.get('plantName', 'Unknown')} (ID: {plant.get('id', 'Unknown')})")
            
            # Device information
            device_sn = comprehensive_data.get("device_sn", "Unknown")
            print(f"🔌 Device SN: {device_sn}")
            
            # Noah check
            noah_check = comprehensive_data.get("noah_check", {})
            is_noah = noah_check.get("isPlantNoahSystem", False)
            has_noah = noah_check.get("isPlantHaveNoah", False)
            print(f"🔋 Is Noah System: {is_noah}")
            print(f"🔋 Has Noah Device: {has_noah}")
            
            # Noah status (main battery data)
            noah_status = comprehensive_data.get("noah_status", {})
            if noah_status:
                print(f"\n⚡ NOAH STATUS:")
                print(f"   SOC: {noah_status.get('soc', 'N/A')}%")
                print(f"   Charge Power: {noah_status.get('chargePower', 'N/A')}")
                print(f"   Discharge Power: {noah_status.get('disChargePower', 'N/A')}")
                print(f"   Work Mode: {noah_status.get('workMode', 'N/A')} ({'Load First' if noah_status.get('workMode') == 0 else 'Battery First' if noah_status.get('workMode') == 1 else 'Unknown'})")
                print(f"   Battery Count: {noah_status.get('batteryNum', 'N/A')}")
                print(f"   Solar Power: {noah_status.get('ppv', 'N/A')}W")
                print(f"   Export Power: {noah_status.get('pac', 'N/A')}W")
                print(f"   Today Export: {noah_status.get('eacToday', 'N/A')}kWh")
                print(f"   Total Export: {noah_status.get('eacTotal', 'N/A')}kWh")
                print(f"   Status: {'Online' if noah_status.get('status') else 'Offline'}")
            
            # Noah configuration
            noah_info = comprehensive_data.get("noah_info", {}).get("noah", {})
            if noah_info:
                print(f"\n⚙️  NOAH CONFIGURATION:")
                print(f"   Model: {noah_info.get('model', 'N/A')}")
                print(f"   Version: {noah_info.get('version', 'N/A')}")
                print(f"   High SOC Limit: {noah_info.get('chargingSocHighLimit', 'N/A')}%")
                print(f"   Low SOC Limit: {noah_info.get('chargingSocLowLimit', 'N/A')}%")
                print(f"   Default Power: {noah_info.get('defaultPower', 'N/A')}W")
                print(f"   Currency: {noah_info.get('moneyUnitText', 'N/A')}")
                print(f"   Energy Cost: {noah_info.get('formulaMoney', 'N/A')} per kWh")
                
                # Battery serial numbers
                bat_sns = noah_info.get('batSns', [])
                if bat_sns:
                    print(f"   Battery SNs: {', '.join(bat_sns)}")
            
            # Storage data (if available)
            storage_data = comprehensive_data.get("storage_data", {})
            if storage_data:
                print(f"\n🔋 STORAGE DATA:")
                
                # Storage overview
                overview = storage_data.get("overview", {})
                if overview:
                    print(f"   Charge Today: {overview.get('eChargeToday', 'N/A')}kWh")
                    print(f"   Charge Total: {overview.get('eChargeTotal', 'N/A')}kWh")
                    print(f"   Discharge Today: {overview.get('eDischargeToday', 'N/A')}kWh")
                    print(f"   Discharge Total: {overview.get('eDischargeTotal', 'N/A')}kWh")
                
                # Storage details
                detail = storage_data.get("detail", {})
                if detail and isinstance(detail, dict):
                    obj = detail.get("obj", {})
                    if obj:
                        print(f"   Battery Voltage: {obj.get('vBat', 'N/A')}V")
                        print(f"   Battery Current: {obj.get('iBat', 'N/A')}A")
                        print(f"   Battery Power: {obj.get('pBat', 'N/A')}W")
                        print(f"   Battery Temp: {obj.get('tempBat', 'N/A')}°C")
                        print(f"   Capacity: {obj.get('capacity', 'N/A')}kWh")
                
                # Storage parameters
                params = storage_data.get("params", {})
                if params and isinstance(params, dict):
                    obj = params.get("obj", {})
                    if obj:
                        print(f"   Rated Capacity: {obj.get('ratedCapacity', 'N/A')}kWh")
                        print(f"   Actual Capacity: {obj.get('actualCapacity', 'N/A')}kWh")
                        print(f"   Charge Cycles: {obj.get('chargeCycles', 'N/A')}")
                        print(f"   Health: {obj.get('health', 'N/A')}%")
            
        except Exception as e:
            print(f"❌ Failed to get comprehensive data: {e}")
            return False
        
        # Test 3: Get standard Noah data format
        print(f"\n🔍 Step 3: Converting to standard data format...")
        try:
            noah_data = await api.async_get_data()
            print("✅ Data conversion successful!")
            
            print(f"\n📊 STANDARD FORMAT DATA:")
            print("=" * 40)
            print(f"🔋 Battery:")
            print(f"   SOC: {noah_data.battery.soc}%")
            print(f"   Voltage: {noah_data.battery.voltage}V")
            print(f"   Current: {noah_data.battery.current}A")
            print(f"   Power: {noah_data.battery.power}W")
            print(f"   Temperature: {noah_data.battery.temperature}°C")
            print(f"   Status: {noah_data.battery.status}")
            print(f"   Health: {noah_data.battery.health}%")
            print(f"   Capacity: {noah_data.battery.capacity}kWh")
            
            print(f"\n☀️  Solar:")
            print(f"   Power: {noah_data.solar.power}W")
            print(f"   Energy Today: {noah_data.solar.energy_today}kWh")
            print(f"   Energy Total: {noah_data.solar.energy_total}kWh")
            
            print(f"\n🔌 Grid:")
            print(f"   Power: {noah_data.grid.power}W")
            print(f"   Export Today: {noah_data.grid.energy_exported_today}kWh")
            print(f"   Export Total: {noah_data.grid.energy_exported_total}kWh")
            print(f"   Connected: {noah_data.grid.grid_connected}")
            
            print(f"\n🏠 Load:")
            print(f"   Power: {noah_data.load.power}W")
            
            print(f"\n⚙️  System:")
            print(f"   Status: {noah_data.system.status}")
            print(f"   Mode: {noah_data.system.mode}")
            print(f"   Serial: {noah_data.system.serial_number}")
            print(f"   Model: {noah_data.system.model}")
            print(f"   Firmware: {noah_data.system.firmware_version}")
            print(f"   Last Update: {noah_data.timestamp}")
            
        except Exception as e:
            print(f"❌ Failed to convert data: {e}")
            return False
        
        print(f"\n✅ Test completed successfully: {datetime.now()}")
        print("💡 The enhanced integration is working with your credentials!")
        print("🎉 Battery status and comprehensive data are available for Home Assistant!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        await api.async_close()

async def main():
    """Main function."""
    success = await test_enhanced_noah_integration()
    return 0 if success else 1

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)