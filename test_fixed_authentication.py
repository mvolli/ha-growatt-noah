#!/usr/bin/env python3
"""Test script to validate the fixed authentication method."""

import asyncio
import logging
import sys
import os

# Add the custom component path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "custom_components"))

from growatt_noah.api import GrowattNoahAPI
from growatt_noah.const import CONNECTION_TYPE_API, DEVICE_TYPE_NOAH

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_authentication():
    """Test the fixed authentication method."""
    logger.info("Testing fixed authentication method")
    
    # Test credentials - replace with actual credentials
    username = "mvolli"
    password = "123456"
    
    # Create API instance
    api = GrowattNoahAPI(
        connection_type=CONNECTION_TYPE_API,
        device_type=DEVICE_TYPE_NOAH,
        username=username,
        password=password,
    )
    
    try:
        # Test connection
        logger.info("Testing connection...")
        result = await api.async_test_connection()
        logger.info("Connection test result: %s", result)
        
        if result:
            logger.info("✅ Authentication successful!")
            
            # Try to get plant list
            try:
                plants = await api.get_plant_list()
                logger.info("✅ Successfully retrieved %d plants", len(plants))
                
                if plants:
                    plant = plants[0]
                    logger.info("First plant: %s", plant)
                    
                    # Try to get device list
                    plant_id = plant.get("id") or plant.get("plantId")
                    if plant_id:
                        devices = await api.get_device_list(str(plant_id))
                        logger.info("✅ Successfully retrieved %d devices", len(devices))
                        
                        if devices:
                            logger.info("First device: %s", devices[0])
                            
            except Exception as e:
                logger.error("❌ Failed to get plant/device data: %s", e)
        else:
            logger.error("❌ Authentication failed!")
            
    except Exception as e:
        logger.error("❌ Test failed with exception: %s", e)
        import traceback
        logger.error("Full traceback: %s", traceback.format_exc())
    
    finally:
        # Clean up
        await api.async_close()

if __name__ == "__main__":
    asyncio.run(test_authentication())