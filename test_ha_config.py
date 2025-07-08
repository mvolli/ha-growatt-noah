#!/usr/bin/env python3
"""
Test the exact configuration that would be used in Home Assistant.
This mimics how HA would call the integration.
"""

import asyncio
import sys
import json
from pathlib import Path

# Add the custom component to path
sys.path.insert(0, str(Path(__file__).parent / "custom_components" / "growatt_noah"))

# Import the growattServer library directly
sys.path.insert(0, str(Path(__file__).parent.parent / "growatt-test" / "growattServer-1.6.0"))

try:
    from api import GrowattNoahAPI
    from const import CONNECTION_TYPE_API, DEVICE_TYPE_NOAH
    print("✅ Successfully imported integration modules")
except ImportError as e:
    print(f"❌ Failed to import: {e}")
    # Try using the simpler approach
    print("Falling back to direct growattServer test...")
    
    try:
        from growattServer import GrowattApi
        
        async def test_direct_connection():
            print("🔋 Testing Direct Connection (How HA Integration Should Work)")
            print("=" * 60)
            
            # Exact configuration as would be used in HA
            config = {
                "username": "mvolli",
                "password": "123456", 
                "device_id": "0PVPH6ZR23QT01AX",
                "connection_type": "api",
                "device_type": "noah",
                "server_url": "https://openapi.growatt.com/"
            }
            
            print(f"Configuration: {json.dumps(config, indent=2)}")
            
            # Initialize API exactly as HA would
            api = GrowattApi(add_random_user_id=True, agent_identifier="ha-noah-integration")
            api.server_url = config["server_url"]
            
            try:
                # Test login
                print("\n🔐 Testing login...")
                login_response = api.login(config["username"], config["password"])
                
                if login_response.get('success'):
                    user_id = login_response['user']['id']
                    print(f"✅ Login successful! User ID: {user_id}")
                    
                    # Test device detection with the specific device_id
                    print(f"\n🔍 Testing device detection with device_id: {config['device_id']}")
                    
                    # Get plants
                    plants = api.plant_list(user_id)
                    plant_list = plants.get('data', []) if isinstance(plants, dict) else plants
                    
                    if plant_list:
                        target_plant = plant_list[0]
                        plant_id = target_plant.get('id') or target_plant.get('plantId')
                        print(f"✅ Found plant: {target_plant.get('plantName')} (ID: {plant_id})")
                        
                        # Check Noah system
                        noah_check = api.is_plant_noah_system(str(plant_id))
                        noah_obj = noah_check.get('obj', {})
                        
                        detected_device_id = noah_obj.get('deviceSn')
                        print(f"🔋 Detected Noah device: {detected_device_id}")
                        
                        if detected_device_id == config['device_id']:
                            print("✅ Device ID matches configuration!")
                        else:
                            print(f"⚠️  Device ID mismatch: Expected {config['device_id']}, Found {detected_device_id}")
                        
                        # Test getting status with configured device_id
                        print(f"\n⚡ Testing status with configured device_id...")
                        try:
                            noah_status = api.noah_system_status(config['device_id'])
                            print(f"✅ Status retrieved: SOC {noah_status.get('soc')}%")
                            
                            return {
                                "success": True,
                                "user_id": user_id,
                                "plant_id": plant_id,
                                "device_id": detected_device_id,
                                "config_device_id": config['device_id'],
                                "status": noah_status
                            }
                            
                        except Exception as e:
                            print(f"❌ Status retrieval failed: {e}")
                            return {"success": False, "error": f"Status error: {e}"}
                    
                    else:
                        print("❌ No plants found")
                        return {"success": False, "error": "No plants found"}
                        
                else:
                    error_msg = login_response.get('msg', 'Unknown error')
                    print(f"❌ Login failed: {error_msg}")
                    return {"success": False, "error": f"Login failed: {error_msg}"}
                    
            except Exception as e:
                print(f"❌ Connection test failed: {e}")
                return {"success": False, "error": str(e)}
        
        # Run the test
        result = asyncio.run(test_direct_connection())
        
        print(f"\n📋 Test Summary:")
        print("=" * 30)
        if result.get("success"):
            print("✅ Connection test PASSED")
            print("🎯 This exact configuration should work in Home Assistant")
            print(f"📊 Device ID: {result.get('config_device_id')} ✅")
            print(f"📊 Detected ID: {result.get('device_id')}")
            
            print(f"\n💡 Recommended Home Assistant Config:")
            print("=" * 40)
            ha_config = {
                "username": "mvolli",
                "password": "123456",
                "device_id": result.get('device_id', '0PVPH6ZR23QT01AX'),
                "connection_type": "api",
                "device_type": "noah",
                "server_url": "https://openapi.growatt.com/"
            }
            print(json.dumps(ha_config, indent=2))
            
        else:
            print("❌ Connection test FAILED")
            print(f"Error: {result.get('error')}")
            print("🔧 This explains why HA integration is failing")
            
        sys.exit(0 if result.get("success") else 1)
        
    except ImportError:
        print("❌ growattServer library not available")
        sys.exit(1)

# If we get here, the integration imports worked
async def test_integration_config():
    """Test integration with exact HA configuration."""
    print("🔋 Testing HA Integration Configuration")
    print("=" * 50)
    
    # Exact configuration as would be used in HA
    config = {
        "username": "mvolli",
        "password": "123456",
        "device_id": "0PVPH6ZR23QT01AX",
        "connection_type": CONNECTION_TYPE_API,
        "device_type": DEVICE_TYPE_NOAH,
        "server_url": "https://openapi.growatt.com/"
    }
    
    print(f"Testing with config: {json.dumps(config, indent=2)}")
    
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
        # Test connection as HA would
        print("\n🔍 Testing async_test_connection()...")
        connection_ok = await api.async_test_connection()
        
        if connection_ok:
            print("✅ Connection test passed!")
            
            # Test data retrieval as HA would  
            print("\n📊 Testing async_get_data()...")
            noah_data = await api.async_get_data()
            
            print(f"✅ Data retrieved successfully!")
            print(f"🔋 Battery SOC: {noah_data.battery.soc}%")
            print(f"⚡ Solar Power: {noah_data.solar.power}W")
            print(f"📊 System Status: {noah_data.system.status}")
            
            print(f"\n🎉 SUCCESS: Integration config works perfectly!")
            print("This exact configuration should work in Home Assistant.")
            
        else:
            print("❌ Connection test failed!")
            print("This is likely why HA integration is failing.")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        print("This error explains the HA connection issues.")
        
    finally:
        await api.async_close()

if __name__ == "__main__":
    try:
        asyncio.run(test_integration_config())
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)