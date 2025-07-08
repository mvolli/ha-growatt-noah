#!/usr/bin/env python3
"""
Test the simplified authentication that matches the official Growatt integration exactly.
"""

import sys
from pathlib import Path

# Add the growattServer library
sys.path.insert(0, str(Path(__file__).parent.parent / "growatt-test" / "growattServer-1.6.0"))

try:
    from growattServer import GrowattApi
    
    # Test the exact same authentication as the official integration
    print("🔋 Testing Simplified Authentication (Matching Official Integration)")
    print("=" * 60)
    
    # Create API instance exactly like official integration
    api = GrowattApi(add_random_user_id=True, agent_identifier="ha-noah-integration")
    
    # Login with user's credentials
    print("🔐 Attempting login...")
    login_response = api.login("mvolli", "123456")
    
    print(f"📋 Login Response:")
    print(f"   Success: {login_response.get('success')}")
    print(f"   User ID: {login_response.get('user', {}).get('id')}")
    print(f"   Message: {login_response.get('msg', 'No message')}")
    
    if login_response.get('success'):
        user_id = login_response['user']['id']
        print(f"\n✅ Authentication SUCCESSFUL!")
        print(f"   User ID: {user_id}")
        
        # Test a simple API call to verify connection
        print(f"\n🔍 Testing plant list retrieval...")
        plants = api.plant_list(user_id)
        plant_list = plants.get('data', []) if isinstance(plants, dict) else plants
        
        if plant_list:
            print(f"✅ Found {len(plant_list)} plant(s):")
            for plant in plant_list[:2]:  # Show first 2 plants
                print(f"   - {plant.get('plantName', 'Unknown')} (ID: {plant.get('id', 'Unknown')})")
        else:
            print(f"⚠️  No plants found")
            
        print(f"\n🎉 SUCCESS: This authentication method works!")
        print("The Noah integration should now work with the same approach.")
        
    else:
        error_msg = login_response.get('msg', 'Unknown error')
        print(f"\n❌ Authentication FAILED: {error_msg}")
        print("This would explain why the HA integration fails.")
        
except ImportError as e:
    print(f"❌ growattServer library not available: {e}")
    print("This means the library needs to be installed in HA environment.")
    
except Exception as e:
    print(f"❌ Test failed with error: {e}")
    import traceback
    traceback.print_exc()