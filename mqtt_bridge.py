#!/usr/bin/env python3
"""
MQTT Bridge for Growatt Devices
Captures data from Growatt devices and publishes to local MQTT broker
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict

import aiohttp
import paho.mqtt.client as mqtt
import requests

# Configuration
MQTT_BROKER = "localhost"  # Your Home Assistant IP
MQTT_PORT = 1883
MQTT_USERNAME = "growatt"
MQTT_PASSWORD = "your_secure_password"
MQTT_TOPIC_PREFIX = "growatt"

# Device configuration
DEVICES = [
    {
        "name": "neo800_1",
        "ip": "192.168.1.118",
        "type": "neo800"
    },
    {
        "name": "noah2000_1", 
        "ip": "192.168.1.117",
        "type": "noah2000"
    }
]

# Polling interval in seconds
POLL_INTERVAL = 30

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GrowattMQTTBridge:
    def __init__(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
        
    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    def on_mqtt_disconnect(self, client, userdata, rc):
        logger.info("Disconnected from MQTT broker")
    
    async def start(self):
        """Start the MQTT bridge"""
        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.mqtt_client.loop_start()
            
            logger.info("Starting Growatt MQTT Bridge...")
            
            while True:
                await self.poll_devices()
                await asyncio.sleep(POLL_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
    
    async def poll_devices(self):
        """Poll all configured devices"""
        for device in DEVICES:
            try:
                data = await self.get_device_data(device)
                if data:
                    self.publish_device_data(device, data)
            except Exception as e:
                logger.error(f"Error polling device {device['name']}: {e}")
    
    async def get_device_data(self, device: Dict[str, Any]) -> Dict[str, Any]:
        """Get data from device (web scraping or API)"""
        try:
            # Try to get data from device web interface
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                # Common endpoints to try
                endpoints = [
                    f"http://{device['ip']}/status.cgi",
                    f"http://{device['ip']}/api/status",
                    f"http://{device['ip']}/status",
                    f"http://{device['ip']}/data.json",
                    f"http://{device['ip']}/status.json"
                ]
                
                for endpoint in endpoints:
                    try:
                        async with session.get(endpoint) as response:
                            if response.status == 200:
                                content_type = response.headers.get('content-type', '')
                                if 'json' in content_type:
                                    data = await response.json()
                                    logger.info(f"Got JSON data from {device['name']} at {endpoint}")
                                    return self.parse_device_data(device, data)
                                else:
                                    text = await response.text()
                                    if len(text) > 0:
                                        logger.info(f"Got text data from {device['name']} at {endpoint}")
                                        return self.parse_text_data(device, text)
                    except Exception as e:
                        logger.debug(f"Endpoint {endpoint} failed for {device['name']}: {e}")
                        continue
                
                logger.warning(f"No working endpoints found for {device['name']}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting data from {device['name']}: {e}")
            return {}
    
    def parse_device_data(self, device: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON data from device"""
        parsed_data = {
            "timestamp": datetime.now().isoformat(),
            "device": device["name"],
            "device_type": device["type"],
            "raw_data": data
        }
        
        # Try to extract common fields
        if device["type"] == "neo800":
            # Neo 800 specific parsing
            parsed_data.update({
                "solar_power": data.get("pac", data.get("power", 0)),
                "pv1_voltage": data.get("vpv1", data.get("pv1_voltage", 0)),
                "pv1_current": data.get("ipv1", data.get("pv1_current", 0)),
                "pv2_voltage": data.get("vpv2", data.get("pv2_voltage", 0)),
                "pv2_current": data.get("ipv2", data.get("pv2_current", 0)),
                "grid_voltage": data.get("vac1", data.get("grid_voltage", 0)),
                "grid_frequency": data.get("fac1", data.get("frequency", 50)),
                "temperature": data.get("tempperature", data.get("temperature", 0)),
                "energy_today": data.get("eToday", data.get("energy_today", 0)),
                "energy_total": data.get("eTotal", data.get("energy_total", 0)),
                "status": data.get("status", "unknown")
            })
        elif device["type"] == "noah2000":
            # Noah 2000 specific parsing
            parsed_data.update({
                "battery_soc": data.get("soc", data.get("battery_soc", 0)),
                "battery_voltage": data.get("battery_voltage", 0),
                "battery_current": data.get("battery_current", 0),
                "battery_power": data.get("battery_power", 0),
                "solar_power": data.get("solar_power", 0),
                "grid_power": data.get("grid_power", 0),
                "load_power": data.get("load_power", 0),
                "status": data.get("status", "unknown")
            })
        
        return parsed_data
    
    def parse_text_data(self, device: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Parse text/HTML data from device"""
        # Simple text parsing - you may need to customize this
        parsed_data = {
            "timestamp": datetime.now().isoformat(),
            "device": device["name"],
            "device_type": device["type"],
            "raw_text": text[:500]  # Limit text length
        }
        
        # Try to extract numbers from text (basic parsing)
        import re
        numbers = re.findall(r'\d+\.?\d*', text)
        if numbers:
            parsed_data["extracted_numbers"] = [float(n) for n in numbers[:10]]
        
        return parsed_data
    
    def publish_device_data(self, device: Dict[str, Any], data: Dict[str, Any]):
        """Publish device data to MQTT"""
        try:
            # Publish to device-specific topic
            topic = f"{MQTT_TOPIC_PREFIX}/{device['name']}/status"
            payload = json.dumps(data)
            
            result = self.mqtt_client.publish(topic, payload, qos=1, retain=True)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published data for {device['name']} to {topic}")
            else:
                logger.error(f"Failed to publish data for {device['name']}: {result.rc}")
                
            # Publish individual sensor values
            if device["type"] == "neo800":
                sensors = ["solar_power", "pv1_voltage", "pv1_current", "pv2_voltage", 
                          "pv2_current", "grid_voltage", "temperature", "energy_today"]
            else:
                sensors = ["battery_soc", "battery_voltage", "solar_power", "grid_power", "load_power"]
            
            for sensor in sensors:
                if sensor in data:
                    sensor_topic = f"{MQTT_TOPIC_PREFIX}/{device['name']}/{sensor}"
                    self.mqtt_client.publish(sensor_topic, str(data[sensor]), qos=1, retain=True)
                    
        except Exception as e:
            logger.error(f"Error publishing data for {device['name']}: {e}")

async def main():
    bridge = GrowattMQTTBridge()
    await bridge.start()

if __name__ == "__main__":
    asyncio.run(main())