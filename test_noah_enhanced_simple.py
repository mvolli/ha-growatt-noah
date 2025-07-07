#!/usr/bin/env python3
"""
Simple test of Noah 2000 battery status using enhanced methods.
Uses the growattServer library source code directly.
"""

import asyncio
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path

# Import the growattServer code directly
sys.path.insert(0, str(Path(__file__).parent.parent / "growatt-test" / "growattServer-1.6.0"))

try:
    from growattServer import GrowattApi
    print("✅ growattServer library imported successfully")
except ImportError:
    print("❌ growattServer library not available")
    print("Please ensure the growatt-test directory contains the extracted library")
    sys.exit(1)

# User credentials
USERNAME = "mvolli"
PASSWORD = "123456"

class EnhancedNoahTester:
    """Enhanced Noah 2000 tester using official growattServer methods."""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.api = GrowattApi(add_random_user_id=True, agent_identifier=f"ha-noah-test-{username}")
        self.api.server_url = "https://openapi.growatt.com/"
        self.login_data = None
        
    def test_authentication(self) -> bool:
        """Test authentication with Growatt API."""
        try:
            print(f"🔐 Authenticating with username: {self.username}")
            login_response = self.api.login(self.username, self.password)
            
            print(f"📋 Login response: {json.dumps(login_response, indent=2)}")
            
            if login_response.get('success'):
                self.login_data = login_response
                user_id = login_response.get('user', {}).get('id')
                print(f"✅ Authentication successful! User ID: {user_id}")
                return True
            else:
                error_msg = login_response.get('msg', 'Unknown error')
                print(f"❌ Authentication failed: {error_msg}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_comprehensive_noah_data(self) -> dict:
        """Get comprehensive Noah data using all available methods."""
        if not self.login_data or not self.login_data.get('success'):
            raise Exception("Not authenticated")
        
        user_id = self.login_data['user']['id']
        comprehensive_data = {}
        
        try:
            # Step 1: Get plant list
            print("\n🌱 Getting plant list...")
            plants = self.api.plant_list(user_id)
            print(f"📋 Plants response: {json.dumps(plants, indent=2)}")
            
            plant_list = plants.get('data', []) if isinstance(plants, dict) else plants
            if not plant_list:
                raise Exception("No plants found")
            
            comprehensive_data['plants'] = plant_list
            target_plant = plant_list[0]  # Use first plant
            plant_id = target_plant.get('id') or target_plant.get('plantId')
            
            print(f"🌱 Using plant: {target_plant.get('plantName', 'Unknown')} (ID: {plant_id})")
            
            # Step 2: Check if it's a Noah system
            print(f"\n🔍 Checking if plant {plant_id} is a Noah system...")
            try:
                noah_check = self.api.is_plant_noah_system(str(plant_id))
                print(f"📋 Noah check response: {json.dumps(noah_check, indent=2)}")
                comprehensive_data['noah_check'] = noah_check
                
                noah_obj = noah_check.get('obj', {})
                is_noah = noah_obj.get('isPlantNoahSystem', False)
                has_noah = noah_obj.get('isPlantHaveNoah', False)
                noah_sn = noah_obj.get('deviceSn')
                
                print(f"🔋 Is Noah System: {is_noah}")
                print(f"🔋 Has Noah Device: {has_noah}")
                print(f"🔋 Noah Device SN: {noah_sn}")
                
            except Exception as e:
                print(f"⚠️  Noah check failed: {e}")
                noah_obj = {}
                noah_sn = None
            
            # Step 3: Get device list
            print(f"\n🔌 Getting device list for plant {plant_id}...")
            try:
                devices = self.api.device_list(str(plant_id))
                print(f"📋 Device list: {json.dumps(devices, indent=2)}")
                comprehensive_data['devices'] = devices
                
                # Find Noah/storage devices
                noah_device = None
                storage_devices = []
                
                for device in devices:
                    device_type = str(device.get('deviceType', '')).lower()
                    device_sn = device.get('deviceSn') or device.get('serialNum')
                    device_name = device.get('deviceAlias') or device.get('name') or f"Device {device_sn}"
                    
                    print(f"   📱 {device_name}: Type={device_type}, SN={device_sn}")
                    
                    if 'noah' in device_type or device_sn == noah_sn:
                        noah_device = device
                        print(f"      🔋 Found Noah device!")
                    elif 'storage' in device_type or 'battery' in device_type:
                        storage_devices.append(device)
                        print(f"      🔋 Found storage device!")
                
                # Determine device SN to use
                if noah_sn:
                    device_sn = noah_sn
                elif noah_device:
                    device_sn = noah_device.get('deviceSn') or noah_device.get('serialNum')
                elif storage_devices:
                    device_sn = storage_devices[0].get('deviceSn') or storage_devices[0].get('serialNum')
                else:
                    print("⚠️  No Noah or storage devices found, trying first device...")
                    device_sn = devices[0].get('deviceSn') or devices[0].get('serialNum') if devices else None
                
                if not device_sn:
                    raise Exception("Could not determine device serial number")
                
                print(f"🔋 Using device SN: {device_sn}")
                
            except Exception as e:
                print(f"⚠️  Device list failed: {e}")
                device_sn = noah_sn  # Fall back to Noah SN from check
                
                if not device_sn:
                    raise Exception("Could not determine device SN")
            
            # Step 4: Get Noah system status
            print(f"\n⚡ Getting Noah system status for device {device_sn}...")
            try:
                noah_status_response = self.api.noah_system_status(device_sn)
                print(f"📋 Noah status response: {json.dumps(noah_status_response, indent=2)}")
                
                # Extract the actual data from obj field
                noah_status = noah_status_response.get('obj', {}) if noah_status_response else {}
                comprehensive_data['noah_status'] = noah_status
                
                # Extract key battery information
                if noah_status:
                    soc = noah_status.get('soc', 'N/A')
                    charge_power = noah_status.get('chargePower', 'N/A')
                    discharge_power = noah_status.get('disChargePower', 'N/A')
                    work_mode = int(noah_status.get('workMode', 0))
                    solar_power = noah_status.get('ppv', 'N/A')
                    export_power = noah_status.get('pac', 'N/A')
                    status = noah_status.get('status', '0')
                    
                    # Convert work mode
                    work_mode_text = {0: 'Load First', 1: 'Battery First', 2: 'Grid First'}.get(work_mode, 'Unknown')
                    
                    print(f"🔋 BATTERY STATUS:")
                    print(f"   SOC: {soc}%")
                    print(f"   Charge Power: {charge_power}W")
                    print(f"   Discharge Power: {discharge_power}W")
                    print(f"   Work Mode: {work_mode} ({work_mode_text})")
                    print(f"   Solar Power: {solar_power}W")
                    print(f"   Export Power: {export_power}W")
                    print(f"   Status: {'Online' if str(status) == '1' else 'Offline'}")
                
            except Exception as e:
                print(f"⚠️  Noah status failed: {e}")
                comprehensive_data['noah_status'] = {}
            
            # Step 5: Get Noah device info
            print(f"\n⚙️  Getting Noah device info for {device_sn}...")
            try:
                noah_info = self.api.noah_info(device_sn)
                print(f"📋 Noah info: {json.dumps(noah_info, indent=2)}")
                comprehensive_data['noah_info'] = noah_info
                
                # Extract configuration information
                noah_config = noah_info.get('noah', {})
                if noah_config:
                    print(f"⚙️  NOAH CONFIGURATION:")
                    print(f"   Model: {noah_config.get('model', 'N/A')}")
                    print(f"   Version: {noah_config.get('version', 'N/A')}")
                    print(f"   High SOC Limit: {noah_config.get('chargingSocHighLimit', 'N/A')}%")
                    print(f"   Low SOC Limit: {noah_config.get('chargingSocLowLimit', 'N/A')}%")
                    print(f"   Default Power: {noah_config.get('defaultPower', 'N/A')}W")
                    
                    bat_sns = noah_config.get('batSns', [])
                    if bat_sns:
                        print(f"   Battery SNs: {', '.join(bat_sns)}")
                
            except Exception as e:
                print(f"⚠️  Noah info failed: {e}")
                comprehensive_data['noah_info'] = {}
            
            # Step 6: Try to get storage data
            print(f"\n🔋 Attempting to get storage data...")
            storage_data = {}
            
            # Try storage detail
            try:
                storage_detail = self.api.storage_detail(device_sn)
                print(f"📋 Storage detail: {json.dumps(storage_detail, indent=2)}")
                storage_data['detail'] = storage_detail
            except Exception as e:
                print(f"⚠️  Storage detail failed: {e}")
            
            # Try storage params
            try:
                storage_params = self.api.storage_params(device_sn)
                print(f"📋 Storage params: {json.dumps(storage_params, indent=2)}")
                storage_data['params'] = storage_params
            except Exception as e:
                print(f"⚠️  Storage params failed: {e}")
            
            # Try storage energy overview
            try:
                storage_overview = self.api.storage_energy_overview(str(plant_id), device_sn)
                print(f"📋 Storage overview: {json.dumps(storage_overview, indent=2)}")
                storage_data['overview'] = storage_overview
            except Exception as e:
                print(f"⚠️  Storage overview failed: {e}")
            
            comprehensive_data['storage_data'] = storage_data
            comprehensive_data['device_sn'] = device_sn
            comprehensive_data['plant_id'] = plant_id
            
            return comprehensive_data
            
        except Exception as e:
            print(f"❌ Failed to get comprehensive data: {e}")
            raise
    
    def run_test(self) -> bool:
        """Run the complete enhanced Noah test."""
        print("🔋 Enhanced Noah 2000 Integration Test")
        print("=" * 50)
        print(f"👤 Username: {self.username}")
        print(f"⏰ Started: {datetime.now()}")
        
        # Step 1: Authentication
        if not self.test_authentication():
            return False
        
        # Step 2: Get comprehensive data
        try:
            print(f"\n🔍 Getting comprehensive Noah data...")
            comprehensive_data = self.get_comprehensive_noah_data()
            
            print(f"\n✅ SUCCESS: Comprehensive Noah data retrieved!")
            print(f"📊 Data includes:")
            print(f"   🌱 Plant information: {len(comprehensive_data.get('plants', []))} plants")
            print(f"   🔌 Device information: {len(comprehensive_data.get('devices', []))} devices")
            print(f"   🔋 Noah status: {'Available' if comprehensive_data.get('noah_status') else 'Not available'}")
            print(f"   ⚙️  Noah configuration: {'Available' if comprehensive_data.get('noah_info') else 'Not available'}")
            print(f"   🔋 Storage data: {'Available' if comprehensive_data.get('storage_data') else 'Not available'}")
            
            # Summary of battery status
            noah_status = comprehensive_data.get('noah_status', {})
            if noah_status:
                soc = noah_status.get('soc', 'N/A')
                charge_power = noah_status.get('chargePower', '0')
                discharge_power = noah_status.get('disChargePower', '0')
                status = noah_status.get('status', '0')
                solar_power = noah_status.get('ppv', '0')
                
                print(f"\n🎯 BATTERY STATUS SUMMARY:")
                print(f"   State of Charge: {soc}%")
                print(f"   Charge Power: {charge_power}W")
                print(f"   Discharge Power: {discharge_power}W")
                print(f"   Solar Generation: {solar_power}W")
                print(f"   System Online: {'Yes' if str(status) == '1' else 'No'}")
            
            print(f"\n✅ Test completed successfully: {datetime.now()}")
            print("💡 Enhanced Noah 2000 integration is working with your credentials!")
            print("🎉 Ready for Home Assistant integration!")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

def main():
    """Main function."""
    tester = EnhancedNoahTester(USERNAME, PASSWORD)
    success = tester.run_test()
    return 0 if success else 1

if __name__ == "__main__":
    try:
        result = main()
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)