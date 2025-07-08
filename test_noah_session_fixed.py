#!/usr/bin/env python3
"""Test Noah API with proper session handling using urllib with cookie support."""

import urllib.request
import urllib.parse
import json
import hashlib
from http.cookiejar import CookieJar

def hash_password(password: str) -> str:
    """Hash password using Growatt's MD5 algorithm."""
    password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
    for i in range(0, len(password_md5), 2):
        if password_md5[i] == '0':
            password_md5 = password_md5[0:i] + 'c' + password_md5[i + 1:]
    return password_md5

def test_noah_api_with_session():
    """Test Noah API with proper session management."""
    print("🔋 Testing Noah API with Session Management")
    print("=" * 50)
    
    try:
        # Create cookie jar to maintain session
        cookie_jar = CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
        
        # Setup headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        # Authenticate first
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
        
        with opener.open(login_request) as response:
            result = json.loads(response.read().decode())
            login_result = result.get("back", {})
            
            if login_result.get("success"):
                auth_token = login_result.get("user", {}).get("id")
                print(f"✅ Authentication successful! User ID: {auth_token}")
                print(f"🍪 Cookies after login: {len(cookie_jar)} cookies")
                
                # Test Noah system status with session cookies
                print("\n📊 Testing Noah system status with session...")
                device_sn = "0PVPH6ZR23QT01AX"
                
                # Include userId in the request data
                noah_data = urllib.parse.urlencode({
                    "deviceSn": device_sn,
                    "userId": auth_token  # Include user ID
                }).encode()
                
                noah_request = urllib.request.Request(
                    "https://openapi.growatt.com/noahDeviceApi/noah/getSystemStatus",
                    data=noah_data,
                    headers=headers
                )
                
                try:
                    with opener.open(noah_request) as noah_response:
                        raw_response = noah_response.read().decode()
                        print(f"✅ Noah API Response received")
                        print(f"📋 HTTP Status: {noah_response.status}")
                        
                        # Check if we got HTML (redirect to login) or JSON
                        if raw_response.strip().startswith('<'):
                            print("❌ Got HTML response (likely login redirect)")
                            print(f"📋 First 200 chars: {raw_response[:200]}")
                            
                            # Try alternative endpoint or different approach
                            print("\n🔄 Trying alternative approach...")
                            
                        else:
                            try:
                                noah_result = json.loads(raw_response)
                                print(f"✅ Successfully parsed JSON response!")
                                print(f"📋 Noah Result: {json.dumps(noah_result, indent=2)}")
                                
                                if noah_result.get("result"):
                                    noah_data = noah_result.get("obj", {})
                                    print(f"\n📊 Noah Data Keys: {list(noah_data.keys())}")
                                    print(f"📊 Sample Values:")
                                    for key, value in list(noah_data.items())[:10]:
                                        print(f"   {key}: {value}")
                                else:
                                    print(f"❌ Noah API error: {noah_result.get('msg', 'Unknown error')}")
                                    
                            except json.JSONDecodeError as je:
                                print(f"❌ JSON Decode Error: {je}")
                                print(f"📋 Raw response: {raw_response[:500]}")
                                
                except urllib.error.HTTPError as he:
                    print(f"❌ HTTP Error: {he.code} - {he.reason}")
                    error_response = he.read().decode()
                    print(f"📋 Error response: {error_response[:200]}")
                    
            else:
                print(f"❌ Authentication failed: {login_result.get('msg', 'Unknown error')}")
                
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_noah_api_with_session()