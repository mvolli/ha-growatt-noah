#!/usr/bin/env python3
"""
Check for common integration issues that could cause connection errors.
"""

import json
from pathlib import Path

# Configuration to check
USERNAME = "mvolli"
PASSWORD = "123456"
DEVICE_ID = "0PVPH6ZR23QT01AX"

def check_integration_files():
    """Check integration files for potential issues."""
    print("🔍 Checking Home Assistant Integration Files")
    print("=" * 50)
    
    # Check manifest.json
    manifest_path = Path("custom_components/growatt_noah/manifest.json")
    if manifest_path.exists():
        print("✅ manifest.json exists")
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
            
            print(f"   Domain: {manifest.get('domain', 'Missing')}")
            print(f"   Version: {manifest.get('version', 'Missing')}")
            
            requirements = manifest.get('requirements', [])
            print(f"   Requirements: {len(requirements)} dependencies")
            for req in requirements:
                print(f"     - {req}")
                
            if 'growattServer>=1.6.0' in requirements:
                print("   ✅ growattServer dependency is present")
            else:
                print("   ❌ growattServer dependency is missing!")
                
        except Exception as e:
            print(f"   ❌ Error reading manifest: {e}")
    else:
        print("❌ manifest.json not found")
    
    # Check main files
    files_to_check = [
        "custom_components/growatt_noah/__init__.py",
        "custom_components/growatt_noah/api.py", 
        "custom_components/growatt_noah/models.py",
        "custom_components/growatt_noah/config_flow.py",
        "custom_components/growatt_noah/const.py",
        "custom_components/growatt_noah/sensor.py"
    ]
    
    print(f"\n📋 Checking core integration files:")
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"   ✅ {path.name} ({size} bytes)")
        else:
            print(f"   ❌ {path.name} missing")
    
    # Check for advanced API methods in api.py
    print(f"\n🔍 Checking for enhanced API methods:")
    api_path = Path("custom_components/growatt_noah/api.py")
    if api_path.exists():
        try:
            with open(api_path) as f:
                api_content = f.read()
            
            methods_to_check = [
                "noah_system_status",
                "noah_info", 
                "get_comprehensive_noah_data",
                "_extract_battery_status_from_noah",
                "from_comprehensive_data"
            ]
            
            for method in methods_to_check:
                if method in api_content:
                    print(f"   ✅ {method} method present")
                else:
                    print(f"   ❌ {method} method missing")
                    
        except Exception as e:
            print(f"   ❌ Error checking API methods: {e}")

def generate_ha_config():
    """Generate Home Assistant configuration example."""
    print(f"\n📋 Recommended Home Assistant Configuration")
    print("=" * 50)
    
    config_yaml = f'''# Add this to your configuration.yaml
growatt_noah:
  username: "{USERNAME}"
  password: "{PASSWORD}"
  connection_type: "api"
  device_type: "noah"
  device_id: "{DEVICE_ID}"
  server_url: "https://openapi.growatt.com/"
  scan_interval: 30  # seconds
'''
    
    print(config_yaml)
    
    print("📋 Integration Setup Steps:")
    print("1. Copy the ha-noah integration to custom_components/growatt_noah/")
    print("2. Add the configuration above to configuration.yaml")
    print("3. Restart Home Assistant")
    print("4. Go to Settings > Devices & Services > Add Integration")
    print("5. Search for 'Growatt Noah' and configure with your credentials")

def check_common_issues():
    """Check for common configuration issues."""
    print(f"\n🔍 Common Connection Issues & Solutions")
    print("=" * 50)
    
    issues = [
        {
            "issue": "401 Authentication Error",
            "cause": "Wrong username/password or API rate limiting",
            "solution": "Verify credentials work in Growatt app, wait 5 minutes if rate limited"
        },
        {
            "issue": "404 Device Not Found", 
            "cause": "Incorrect device_id or device not in account",
            "solution": f"Verify device {DEVICE_ID} exists in your Growatt account"
        },
        {
            "issue": "500 Server Error",
            "cause": "Growatt API server issues or malformed requests",
            "solution": "Check Growatt server status, ensure integration is up to date"
        },
        {
            "issue": "Connection Timeout",
            "cause": "Network issues or API server overload", 
            "solution": "Check internet connection, try increasing timeout in config"
        },
        {
            "issue": "Module Import Error",
            "cause": "Missing dependencies (aiohttp, growattServer, etc.)",
            "solution": "Restart Home Assistant to install required packages"
        },
        {
            "issue": "Integration Not Loading",
            "cause": "File permissions or syntax errors in code",
            "solution": "Check Home Assistant logs for specific error messages"
        }
    ]
    
    for i, item in enumerate(issues, 1):
        print(f"{i}. {item['issue']}")
        print(f"   Cause: {item['cause']}")
        print(f"   Solution: {item['solution']}")
        print()

def check_logs_guidance():
    """Provide guidance on checking logs."""
    print(f"📋 How to Check Home Assistant Logs")
    print("=" * 50)
    
    print("1. In Home Assistant web interface:")
    print("   Settings > System > Logs")
    print("   Look for entries containing 'growatt_noah' or 'custom_components'")
    print()
    print("2. Command line (if accessible):")
    print("   tail -f /config/home-assistant.log | grep growatt")
    print()
    print("3. Enable debug logging by adding to configuration.yaml:")
    print("   logger:")
    print("     default: info")
    print("     logs:")
    print("       custom_components.growatt_noah: debug")
    print()
    print("4. Look for specific error patterns:")
    print("   - 'Failed to connect': Network/authentication issues")
    print("   - 'ModuleNotFoundError': Missing dependencies")
    print("   - 'KeyError' or 'AttributeError': Data parsing issues")
    print("   - 'TimeoutError': API response delays")

def main():
    """Main function."""
    print("🔋 Home Assistant Growatt Noah Integration Troubleshooter")
    print("=" * 60)
    print(f"Checking configuration for:")
    print(f"Username: {USERNAME}")
    print(f"Device ID: {DEVICE_ID}")
    print()
    
    check_integration_files()
    generate_ha_config()
    check_common_issues()
    check_logs_guidance()
    
    print(f"\n💡 Next Steps:")
    print("1. Check Home Assistant logs for specific error messages")
    print("2. Verify the integration files are properly installed")
    print("3. Ensure configuration matches working test settings")
    print("4. Try reloading the integration after any changes")
    print()
    print("If you need more help, please share the specific error message from HA logs!")

if __name__ == "__main__":
    main()