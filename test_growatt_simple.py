#!/usr/bin/env python3
"""Simple test for growattServer library authentication."""

import sys

def test_growatt_server():
    """Test growattServer library authentication."""
    try:
        # Test import
        try:
            import growattServer
            print("✅ growattServer library is available")
        except ImportError as e:
            print(f"❌ growattServer library not found: {e}")
            print("Please install it with: pip install growattServer==1.6.0")
            return False
        
        # Test authentication
        print("Testing authentication...")
        username = "mvolli"
        password = "123456"
        
        api = growattServer.GrowattApi(add_random_user_id=True, agent_identifier="ha-noah-test")
        
        # Test login
        login_response = api.login(username, password)
        print(f"Login response: {login_response}")
        
        if login_response and login_response.get('success'):
            print("✅ Authentication successful!")
            user_id = login_response['user']['id']
            print(f"User ID: {user_id}")
            
            # Test plant list
            try:
                plants = api.plant_list(user_id)
                print(f"✅ Retrieved plants: {len(plants) if isinstance(plants, list) else 'unknown count'}")
                if plants:
                    print(f"First plant: {plants[0] if isinstance(plants, list) else plants}")
                    
                    # Test device list
                    plant_id = plants[0].get('id') if isinstance(plants, list) else plants.get('data', [{}])[0].get('id')
                    if plant_id:
                        devices = api.device_list(plant_id)
                        print(f"✅ Retrieved devices: {len(devices) if isinstance(devices, list) else 'unknown count'}")
                        
            except Exception as e:
                print(f"❌ Error retrieving plant/device data: {e}")
                
        else:
            print("❌ Authentication failed!")
            error_msg = login_response.get('msg', 'Unknown error') if login_response else 'No response'
            print(f"Error: {error_msg}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_growatt_server()
    sys.exit(0 if success else 1)