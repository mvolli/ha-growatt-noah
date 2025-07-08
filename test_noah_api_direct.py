#!/usr/bin/env python3
"""Direct test of Noah API endpoints to understand response structure."""

import asyncio
import aiohttp
import hashlib
import json

async def test_noah_api():
    """Test Noah API directly to understand response structure."""
    
    def hash_password(password: str) -> str:
        """Hash password using Growatt's MD5 algorithm."""
        password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
        for i in range(0, len(password_md5), 2):
            if password_md5[i] == '0':
                password_md5 = password_md5[0:i] + 'c' + password_md5[i + 1:]
        return password_md5
    
    print("🔋 Testing Noah API Direct Access")
    print("=" * 50)
    
    # Setup session
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        # Authenticate
        print("🔐 Authenticating...")
        hashed_password = hash_password("123456")
        
        login_data = {
            "userName": "mvolli",
            "password": hashed_password,
        }
        
        async with session.post("https://openapi.growatt.com/newTwoLoginAPI.do", data=login_data) as response:
            if response.status == 200:
                result = await response.json()
                login_result = result.get("back", {})
                
                if login_result.get("success"):
                    auth_token = login_result.get("user", {}).get("id")
                    print(f"✅ Authentication successful! User ID: {auth_token}")
                    
                    # Test Noah system status
                    print("\n📊 Testing Noah system status...")
                    device_sn = "0PVPH6ZR23QT01AX"
                    
                    async with session.post(
                        "https://openapi.growatt.com/noahDeviceApi/noah/getSystemStatus",
                        data={"deviceSn": device_sn}
                    ) as noah_response:
                        if noah_response.status == 200:
                            noah_result = await noah_response.json()
                            print(f"✅ Noah API Response Status: {noah_response.status}")
                            print(f"📋 Full Response: {json.dumps(noah_result, indent=2)}")
                            
                            if noah_result.get("result"):
                                noah_data = noah_result.get("obj", {})
                                print(f"📊 Noah Data Keys: {list(noah_data.keys())}")
                                print(f"📊 Sample Values:")
                                for key, value in list(noah_data.items())[:10]:  # Show first 10 items
                                    print(f"   {key}: {value}")
                            else:
                                print(f"❌ Noah API returned error: {noah_result.get('msg', 'Unknown error')}")
                        else:
                            text = await noah_response.text()
                            print(f"❌ Noah API HTTP Error {noah_response.status}: {text}")
                else:
                    print(f"❌ Authentication failed: {login_result.get('msg', 'Unknown error')}")
            else:
                text = await response.text()
                print(f"❌ Login HTTP Error {response.status}: {text}")

if __name__ == "__main__":
    asyncio.run(test_noah_api())