#!/usr/bin/env python3
"""
Debug script to check if the integration files are properly structured for Home Assistant.
"""

import json
import sys
from pathlib import Path

def check_integration_structure():
    """Check if integration files are properly structured."""
    print("🔍 Checking Integration File Structure")
    print("=" * 50)
    
    # Expected file structure
    base_path = Path("custom_components/growatt_noah")
    required_files = {
        "__init__.py": "Main integration file",
        "manifest.json": "Integration metadata",
        "config_flow.py": "Configuration flow handler", 
        "api.py": "API client",
        "const.py": "Constants",
        "sensor.py": "Sensor definitions",
        "models.py": "Data models"
    }
    
    missing_files = []
    invalid_files = []
    
    for filename, description in required_files.items():
        file_path = base_path / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {filename}: {size} bytes - {description}")
            
            # Check for empty files
            if size == 0:
                invalid_files.append(f"{filename} (empty file)")
                
        else:
            print(f"❌ {filename}: Missing - {description}")
            missing_files.append(filename)
    
    return missing_files, invalid_files

def check_manifest_json():
    """Check manifest.json for required fields."""
    print(f"\n🔍 Checking manifest.json")
    print("-" * 30)
    
    manifest_path = Path("custom_components/growatt_noah/manifest.json")
    if not manifest_path.exists():
        print("❌ manifest.json not found")
        return False
    
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        required_fields = {
            "domain": "growatt_noah",
            "name": str,
            "config_flow": True,
            "requirements": list,
            "version": str,
            "codeowners": list,
            "integration_type": str,
            "iot_class": str
        }
        
        all_good = True
        for field, expected in required_fields.items():
            if field in manifest:
                value = manifest[field]
                if isinstance(expected, type) and isinstance(value, expected):
                    print(f"✅ {field}: {value}")
                elif not isinstance(expected, type) and value == expected:
                    print(f"✅ {field}: {value}")
                else:
                    print(f"⚠️  {field}: {value} (expected {expected})")
                    all_good = False
            else:
                print(f"❌ {field}: Missing")
                all_good = False
        
        # Check requirements specifically
        requirements = manifest.get("requirements", [])
        if "growattServer>=1.6.0" in requirements:
            print("✅ growattServer dependency found")
        else:
            print("❌ growattServer dependency missing")
            all_good = False
            
        return all_good
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        return False

def check_python_syntax():
    """Check Python files for syntax errors."""
    print(f"\n🔍 Checking Python Syntax")
    print("-" * 30)
    
    python_files = [
        "custom_components/growatt_noah/__init__.py",
        "custom_components/growatt_noah/config_flow.py", 
        "custom_components/growatt_noah/api.py",
        "custom_components/growatt_noah/const.py",
        "custom_components/growatt_noah/sensor.py",
        "custom_components/growatt_noah/models.py"
    ]
    
    all_good = True
    for file_path in python_files:
        path = Path(file_path)
        if path.exists():
            try:
                with open(path) as f:
                    code = f.read()
                
                # Try to compile the code
                compile(code, str(path), 'exec')
                print(f"✅ {path.name}: Syntax OK")
                
            except SyntaxError as e:
                print(f"❌ {path.name}: Syntax Error - Line {e.lineno}: {e.msg}")
                all_good = False
            except Exception as e:
                print(f"❌ {path.name}: Error - {e}")
                all_good = False
        else:
            print(f"❌ {path.name}: File not found")
            all_good = False
    
    return all_good

def check_config_flow():
    """Check config flow for common issues."""
    print(f"\n🔍 Checking Config Flow")
    print("-" * 30)
    
    config_flow_path = Path("custom_components/growatt_noah/config_flow.py")
    if not config_flow_path.exists():
        print("❌ config_flow.py not found")
        return False
    
    try:
        with open(config_flow_path) as f:
            content = f.read()
        
        required_patterns = [
            ("class.*ConfigFlow", "ConfigFlow class definition"),
            ("async def async_step_user", "User setup step"),
            ("async_test_connection", "Connection testing"),
            ("DOMAIN", "Domain constant"),
            ("vol.Required.*username", "Username field"),
            ("vol.Required.*password", "Password field")
        ]
        
        all_good = True
        for pattern, description in required_patterns:
            if pattern.replace(".*", "") in content:
                print(f"✅ {description}: Found")
            else:
                print(f"❌ {description}: Missing pattern '{pattern}'")
                all_good = False
                
        return all_good
        
    except Exception as e:
        print(f"❌ Error checking config flow: {e}")
        return False

def generate_ha_debug_steps():
    """Generate Home Assistant specific debug steps."""
    print(f"\n📋 HOME ASSISTANT DEBUG STEPS")
    print("=" * 50)
    
    print("1. Check Integration Loading in HA Logs:")
    print("   Look for these patterns after restart:")
    print("   - 'Loading custom_components.growatt_noah'")
    print("   - 'Setup of domain growatt_noah took'")
    print("   - Any errors with 'growatt_noah' in the message")
    print()
    
    print("2. Enable Component Loader Debugging:")
    print("   Add to configuration.yaml:")
    print("   logger:")
    print("     logs:")
    print("       homeassistant.loader: debug")
    print("       homeassistant.setup: debug")
    print()
    
    print("3. Check Integration Discovery:")
    print("   - Go to Settings > Devices & Services")
    print("   - Click + Add Integration")
    print("   - Search for 'growatt' or 'noah'")
    print("   - If not found, integration isn't loading properly")
    print()
    
    print("4. Manual Integration Loading Test:")
    print("   In HA Developer Tools > Template, test:")
    print("   {{ integration_entities('growatt_noah') }}")
    print("   Should return empty list if domain loads but no entities")
    print()
    
    print("5. Check Dependencies:")
    print("   In HA container/system:")
    print("   pip list | grep growatt")
    print("   Should show: growattServer>=1.6.0")

def main():
    """Main diagnostic function."""
    print("🔋 Home Assistant Integration Loading Diagnostics")
    print("=" * 60)
    
    # Check file structure
    missing, invalid = check_integration_structure()
    
    # Check manifest
    manifest_ok = check_manifest_json()
    
    # Check Python syntax
    syntax_ok = check_python_syntax()
    
    # Check config flow
    config_flow_ok = check_config_flow()
    
    # Summary
    print(f"\n📋 DIAGNOSTIC SUMMARY")
    print("=" * 30)
    
    issues = []
    if missing:
        issues.append(f"Missing files: {', '.join(missing)}")
    if invalid:
        issues.append(f"Invalid files: {', '.join(invalid)}")
    if not manifest_ok:
        issues.append("manifest.json issues")
    if not syntax_ok:
        issues.append("Python syntax errors")
    if not config_flow_ok:
        issues.append("Config flow issues")
    
    if issues:
        print("❌ Issues found:")
        for issue in issues:
            print(f"   - {issue}")
        print(f"\n🔧 Fix these issues before proceeding")
    else:
        print("✅ All integration files look good!")
        print("🔧 The issue is likely in Home Assistant loading/dependency installation")
    
    generate_ha_debug_steps()

if __name__ == "__main__":
    main()