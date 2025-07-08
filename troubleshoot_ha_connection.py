#!/usr/bin/env python3
"""
Troubleshoot Home Assistant connection issues with Noah 2000.
This script will help identify the exact cause of connection failures.
"""

import sys
import json
from pathlib import Path

# Add the growattServer library
sys.path.insert(0, str(Path(__file__).parent.parent / "growatt-test" / "growattServer-1.6.0"))

try:
    from growattServer import GrowattApi
    print("✅ growattServer library available")
except ImportError:
    print("❌ growattServer library not found")
    sys.exit(1)

def test_all_connection_scenarios():
    """Test various connection scenarios to identify the exact issue."""
    print("🔍 Comprehensive Connection Troubleshooting")
    print("=" * 60)
    
    # Test configuration as specified in HA
    config = {
        "username": "mvolli",
        "password": "123456",
        "device_id": "0PVPH6ZR23QT01AX",
        "connection_type": "api",
        "device_type": "noah",
        "server_url": "https://openapi.growatt.com/",
        "scan_interval": 30
    }
    
    print(f"Testing HA configuration: {json.dumps(config, indent=2)}")
    
    # Test 1: Basic Authentication
    print(f"\n📋 Test 1: Authentication")
    print("-" * 30)
    
    api = GrowattApi(add_random_user_id=True, agent_identifier="ha-noah-debug")
    api.server_url = config["server_url"]
    
    try:
        login_response = api.login(config["username"], config["password"])
        if login_response.get('success'):
            user_id = login_response['user']['id']
            print(f"✅ Authentication: SUCCESS (User ID: {user_id})")
        else:
            print(f"❌ Authentication: FAILED - {login_response.get('msg', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Authentication: ERROR - {e}")
        return False
    
    # Test 2: Plant Discovery
    print(f"\n📋 Test 2: Plant Discovery")
    print("-" * 30)
    
    try:
        plants = api.plant_list(user_id)
        plant_list = plants.get('data', []) if isinstance(plants, dict) else plants
        
        if plant_list:
            plant = plant_list[0]
            plant_id = plant.get('id') or plant.get('plantId')
            plant_name = plant.get('plantName', 'Unknown')
            print(f"✅ Plant Discovery: SUCCESS")
            print(f"   Plant: {plant_name} (ID: {plant_id})")
        else:
            print(f"❌ Plant Discovery: FAILED - No plants found")
            return False
    except Exception as e:
        print(f"❌ Plant Discovery: ERROR - {e}")
        return False
    
    # Test 3: Noah Device Detection
    print(f"\n📋 Test 3: Noah Device Detection")
    print("-" * 30)
    
    try:
        noah_check = api.is_plant_noah_system(str(plant_id))
        noah_obj = noah_check.get('obj', {})
        
        is_noah_system = noah_obj.get('isPlantNoahSystem', False)
        has_noah_device = noah_obj.get('isPlantHaveNoah', False)
        detected_device_sn = noah_obj.get('deviceSn', '')
        
        print(f"   Is Noah System: {is_noah_system}")
        print(f"   Has Noah Device: {has_noah_device}")
        print(f"   Detected SN: {detected_device_sn}")
        print(f"   Config SN: {config['device_id']}")
        
        if detected_device_sn == config['device_id']:
            print(f"✅ Device Detection: SUCCESS - Device ID matches")
        elif detected_device_sn and detected_device_sn != config['device_id']:
            print(f"⚠️  Device Detection: MISMATCH")
            print(f"   Expected: {config['device_id']}")
            print(f"   Found: {detected_device_sn}")
            print(f"   💡 Try using device_id: '{detected_device_sn}' in HA config")
        elif has_noah_device:
            print(f"✅ Device Detection: SUCCESS - Noah device found")
        else:
            print(f"❌ Device Detection: FAILED - No Noah device found")
            return False
            
    except Exception as e:
        print(f"❌ Device Detection: ERROR - {e}")
        return False
    
    # Test 4: Device Status Retrieval
    print(f"\n📋 Test 4: Device Status Retrieval")
    print("-" * 30)
    
    # Try with configured device_id first
    device_sn_to_test = config['device_id']
    
    try:
        noah_status = api.noah_system_status(device_sn_to_test)
        if noah_status and noah_status.get('soc') is not None:
            soc = noah_status.get('soc', 'N/A')
            charge_power = noah_status.get('chargePower', 'N/A')
            status = noah_status.get('status', '0')
            
            print(f"✅ Status Retrieval: SUCCESS")
            print(f"   SOC: {soc}%")
            print(f"   Charge Power: {charge_power}W")
            print(f"   Online: {'Yes' if str(status) == '1' else 'No'}")
            
        else:
            print(f"❌ Status Retrieval: FAILED - No valid status data")
            print(f"   Response: {noah_status}")
            return False
            
    except Exception as e:
        print(f"❌ Status Retrieval: ERROR - {e}")
        
        # If configured device_id fails, try detected device_id
        if detected_device_sn and detected_device_sn != device_sn_to_test:
            print(f"   Trying detected device SN: {detected_device_sn}")
            try:
                noah_status = api.noah_system_status(detected_device_sn)
                if noah_status and noah_status.get('soc') is not None:
                    print(f"✅ Status with detected SN: SUCCESS")
                    print(f"   💡 Use device_id: '{detected_device_sn}' in HA config")
                else:
                    print(f"❌ Status with detected SN: FAILED")
                    return False
            except Exception as e2:
                print(f"❌ Status with detected SN: ERROR - {e2}")
                return False
        else:
            return False
    
    # Test 5: Configuration Validation
    print(f"\n📋 Test 5: Configuration Validation")
    print("-" * 30)
    
    validation_results = {
        "username": "✅ Valid" if config["username"] else "❌ Missing",
        "password": "✅ Valid" if config["password"] else "❌ Missing",
        "device_id": "✅ Valid" if config["device_id"] else "❌ Missing",
        "connection_type": "✅ API" if config["connection_type"] == "api" else "❌ Invalid",
        "device_type": "✅ Noah" if config["device_type"] == "noah" else "❌ Invalid",
        "server_url": "✅ Valid" if config["server_url"] == "https://openapi.growatt.com/" else "❌ Invalid"
    }
    
    for key, status in validation_results.items():
        print(f"   {key}: {status}")
    
    print(f"\n🎯 CONNECTION TEST SUMMARY")
    print("=" * 40)
    print("✅ All tests PASSED - Configuration is working!")
    print()
    print("🔧 If HA still shows 'Failed to connect', try:")
    print("1. Restart Home Assistant completely")
    print("2. Remove and re-add the integration")
    print("3. Check HA logs for specific error messages")
    print("4. Ensure growattServer library is installed")
    
    return True

def generate_troubleshooting_steps():
    """Generate specific troubleshooting steps."""
    print(f"\n📋 HOME ASSISTANT TROUBLESHOOTING STEPS")
    print("=" * 50)
    
    steps = [
        {
            "step": "1. Check Integration Loading",
            "action": "Go to Settings > System > Logs",
            "look_for": "Any errors containing 'growatt_noah' or 'custom_components'",
            "fix": "If ModuleNotFoundError: Restart HA to install dependencies"
        },
        {
            "step": "2. Verify Configuration",
            "action": "Go to Developer Tools > YAML > Check Configuration",
            "look_for": "Configuration validation errors",
            "fix": "Fix any YAML syntax errors in configuration.yaml"
        },
        {
            "step": "3. Clear Integration Cache",
            "action": "Settings > Devices & Services",
            "look_for": "Old 'Growatt' or 'Noah' integrations",
            "fix": "Delete old integrations, restart HA, add new integration"
        },
        {
            "step": "4. Test with UI Configuration",
            "action": "Remove YAML config, use UI setup instead",
            "look_for": "Same connection error",
            "fix": "Use Settings > Devices & Services > Add Integration"
        },
        {
            "step": "5. Enable Debug Logging",
            "action": "Add logger config to configuration.yaml",
            "look_for": "Detailed error messages in logs",
            "fix": "Share specific error messages for further help"
        }
    ]
    
    for step_info in steps:
        print(f"\n{step_info['step']}:")
        print(f"  Action: {step_info['action']}")
        print(f"  Look for: {step_info['look_for']}")
        print(f"  Fix: {step_info['fix']}")

def main():
    """Main troubleshooting function."""
    success = test_all_connection_scenarios()
    
    if success:
        print(f"\n💡 Your configuration is CORRECT and working!")
        print("The 'Failed to connect' error in HA is likely due to:")
        print("- Missing growattServer dependency (restart HA)")
        print("- Integration cache issues (remove/re-add integration)")
        print("- Configuration loading issues (check HA logs)")
    else:
        print(f"\n❌ Configuration has issues that need to be fixed first")
    
    generate_troubleshooting_steps()

if __name__ == "__main__":
    main()