#!/usr/bin/env python3
"""Direct test of Noah API using only standard library."""

import urllib.request
import urllib.parse
import json
import hashlib

def hash_password(password: str) -> str:
    """Hash password using Growatt's MD5 algorithm."""
    password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
    for i in range(0, len(password_md5), 2):
        if password_md5[i] == '0':
            password_md5 = password_md5[0:i] + 'c' + password_md5[i + 1:]
    return password_md5

def test_noah_api():
    """Test Noah API directly."""
    print("🔋 Testing Noah API Direct Access (Standard Library)")
    print("=" * 55)
    
    try:
        # Setup headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        # Authenticate
        print("🔐 Authenticating...")
        hashed_password = hash_password("123456")
        
        login_data = urllib.parse.urlencode({
            "userName": "mvolli",
            "password": hashed_password,
        }).encode()
        
        login_request = urllib.request.Request(
            "https://openapi.growatt.com/newTwoLoginAPI.do",
            data=login_data,
            headers=headers
        )
        
        with urllib.request.urlopen(login_request) as response:
            result = json.loads(response.read().decode())
            login_result = result.get("back", {})
            
            if login_result.get("success"):
                auth_token = login_result.get("user", {}).get("id")
                print(f"✅ Authentication successful! User ID: {auth_token}")
                
                # Test Noah system status
                print("\n📊 Testing Noah system status...")
                device_sn = "0PVPH6ZR23QT01AX"
                
                noah_data = urllib.parse.urlencode({
                    "deviceSn": device_sn
                }).encode()
                
                noah_request = urllib.request.Request(
                    "https://openapi.growatt.com/noahDeviceApi/noah/getSystemStatus",
                    data=noah_data,
                    headers=headers
                )
                
                with urllib.request.urlopen(noah_request) as noah_response:
                    raw_response = noah_response.read().decode()
                    print(f"✅ Noah API Response received")
                    print(f"📋 Raw Response: {repr(raw_response)}")
                    print(f"📋 HTTP Status: {noah_response.status}")
                    print(f"📋 Response Headers: {dict(noah_response.headers)}")
                    
                    try:
                        noah_result = json.loads(raw_response)
                        print(f"📋 Parsed JSON: {json.dumps(noah_result, indent=2)}")
                    except json.JSONDecodeError as je:
                        print(f"❌ JSON Decode Error: {je}")
                        print(f"📋 First 200 chars of response: {raw_response[:200]}")
                        return
                    
                    if noah_result.get("result"):
                        noah_data = noah_result.get("obj", {})
                        print(f"\n📊 Noah Data Keys Available: {list(noah_data.keys())}")
                        print(f"📊 Sample Values:")
                        for key, value in list(noah_data.items())[:15]:  # Show first 15 items
                            print(f"   {key}: {value}")
                            
                        # Specific keys we're looking for
                        key_mappings = {
                            "soc": "State of Charge",
                            "chargePower": "Charge Power", 
                            "disChargePower": "Discharge Power",
                            "vBat": "Battery Voltage",
                            "iBat": "Battery Current",
                            "pvPower": "Solar Power",
                            "gridPower": "Grid Power", 
                            "loadPower": "Load Power",
                            "status": "System Status"
                        }
                        
                        print(f"\n🔍 Key Fields for Integration:")
                        for key, description in key_mappings.items():
                            if key in noah_data:
                                print(f"   ✅ {key} ({description}): {noah_data[key]}")
                            else:
                                print(f"   ❌ {key} ({description}): NOT FOUND")
                                
                    else:
                        print(f"❌ Noah API returned error: {noah_result.get('msg', 'Unknown error')}")
            else:
                print(f"❌ Authentication failed: {login_result.get('msg', 'Unknown error')}")
                
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_noah_api()