"""API client for Growatt Noah 2000."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional
import json
import ssl

import aiohttp
from aiomqtt import Client as MQTTClient
from pymodbus.client import AsyncModbusTcpClient, AsyncModbusSerialClient
from pymodbus.exceptions import ModbusException

from .const import (
    CONNECTION_TYPE_API,
    CONNECTION_TYPE_MQTT,
    CONNECTION_TYPE_MODBUS_TCP,
    CONNECTION_TYPE_MODBUS_RTU,
    DEVICE_TYPE_NOAH,
    DEVICE_TYPE_NEO800,
    GROWATT_API_BASE_URL,
    GROWATT_API_LOGIN,
    GROWATT_API_PLANT_LIST,
    GROWATT_API_INVERTER_DATA,
    NOAH_MODBUS_REGISTERS,
    NEO800_MODBUS_REGISTERS,
    DEFAULT_TIMEOUT,
)
from .models import NoahData, Neo800Data

_LOGGER = logging.getLogger(__name__)


class GrowattNoahAPI:
    """Main API client for Growatt Noah 2000 and Neo 800."""
    
    def __init__(
        self,
        connection_type: str,
        device_type: str = DEVICE_TYPE_NOAH,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        mqtt_broker: Optional[str] = None,
        mqtt_topic: str = "noah",
        device_id: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the API client."""
        self.connection_type = connection_type
        self.device_type = device_type
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.mqtt_broker = mqtt_broker
        self.mqtt_topic = mqtt_topic
        self.device_id = device_id
        self.timeout = timeout
        
        self._session: Optional[aiohttp.ClientSession] = None
        self._mqtt_client: Optional[MQTTClient] = None
        self._modbus_client: Optional[AsyncModbusTcpClient | AsyncModbusSerialClient] = None
        self._auth_token: Optional[str] = None
        self._user_data: dict[str, Any] = {}
        self._mqtt_data: dict[str, Any] = {}
    
    async def async_test_connection(self) -> bool:
        """Test the connection to the device."""
        try:
            if self.connection_type == CONNECTION_TYPE_API:
                return await self._test_api_connection()
            elif self.connection_type == CONNECTION_TYPE_MQTT:
                return await self._test_mqtt_connection()
            elif self.connection_type in [CONNECTION_TYPE_MODBUS_TCP, CONNECTION_TYPE_MODBUS_RTU]:
                return await self._test_modbus_connection()
            else:
                _LOGGER.error("Unknown connection type: %s", self.connection_type)
                return False
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False
    
    async def async_get_data(self) -> NoahData | Neo800Data:
        """Get device data."""
        if self.connection_type == CONNECTION_TYPE_API:
            return await self._get_api_data()
        elif self.connection_type == CONNECTION_TYPE_MQTT:
            return await self._get_mqtt_data()
        elif self.connection_type in [CONNECTION_TYPE_MODBUS_TCP, CONNECTION_TYPE_MODBUS_RTU]:
            return await self._get_modbus_data()
        else:
            raise ValueError(f"Unknown connection type: {self.connection_type}")
    
    async def async_close(self) -> None:
        """Close all connections."""
        if self._session:
            await self._session.close()
        if self._mqtt_client:
            await self._mqtt_client.disconnect()
        if self._modbus_client:
            try:
                if hasattr(self._modbus_client, 'close'):
                    await self._modbus_client.close()
                else:
                    self._modbus_client.close()
            except Exception:
                pass  # Ignore close errors
    
    # API methods
    async def _test_api_connection(self) -> bool:
        """Test Growatt API connection."""
        if not self.username or not self.password:
            return False
        
        try:
            await self._authenticate_api()
            return self._auth_token is not None
        except Exception:
            return False
    
    async def _authenticate_api(self) -> None:
        """Authenticate with Growatt API using correct 2024 format."""
        if not self._session:
            # Create session with correct headers for Growatt API
            headers = {
                "User-Agent": "Noah2000-Integration/2.0.0",
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://server.growatt.com/",
            }
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers=headers,
                connector=connector
            )
        
        # Growatt API requires specific form data format
        login_data = {
            "account": self.username,
            "password": self.password,
            "validateCode": "",
            "isReadPact": "0",
        }
        
        async with self._session.post(
            f"{GROWATT_API_BASE_URL}{GROWATT_API_LOGIN}",
            data=login_data,
        ) as response:
            if response.status == 200:
                result = await response.json()
                # Growatt API returns different response structure
                if result.get("result") == 1:
                    # Store user info for subsequent requests
                    self._auth_token = result.get("user", {}).get("id")
                    self._user_data = result.get("user", {})
                else:
                    error_msg = result.get("msg", "Unknown error")
                    raise Exception(f"Login failed: {error_msg}")
            else:
                text = await response.text()
                raise Exception(f"HTTP {response.status}: {text}")
    
    async def _get_api_data(self) -> NoahData | Neo800Data:
        """Get data from Growatt API using correct endpoints."""
        if not self._auth_token:
            await self._authenticate_api()
        
        if not self._session:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        
        # First get plant list to find our device
        plant_params = {
            "currPage": "1",
            "plantName": "",
        }
        
        async with self._session.post(
            f"{GROWATT_API_BASE_URL}{GROWATT_API_PLANT_LIST}",
            data=plant_params,
        ) as response:
            if response.status != 200:
                raise Exception(f"Failed to get plant list: HTTP {response.status}")
            
            plants_result = await response.json()
            if plants_result.get("result") != 1:
                raise Exception(f"Plant list error: {plants_result.get('msg', 'Unknown error')}")
            
            plants = plants_result.get("datas", {}).get("data", [])
            if not plants:
                raise Exception("No plants found in account")
            
            # Use the first plant or find by device_id if specified
            target_plant = plants[0]
            if self.device_id:
                for plant in plants:
                    if plant.get("id") == self.device_id or plant.get("plantName") == self.device_id:
                        target_plant = plant
                        break
            
            plant_id = target_plant.get("id")
            if not plant_id:
                raise Exception("Could not determine plant ID")
        
        # Now get device data for the plant
        device_params = {
            "plantId": plant_id,
            "currPage": "1",
        }
        
        async with self._session.post(
            f"{GROWATT_API_BASE_URL}{GROWATT_API_INVERTER_DATA}",
            data=device_params,
        ) as response:
            if response.status == 200:
                result = await response.json()
                if result.get("result") == 1:
                    data = result.get("obj", {})
                    # Convert Growatt API response to our format
                    converted_data = self._convert_growatt_response(data)
                    
                    if self.device_type == DEVICE_TYPE_NEO800:
                        return Neo800Data.from_api_response(converted_data)
                    else:
                        return NoahData.from_api_response(converted_data)
                else:
                    raise Exception(f"API error: {result.get('msg', 'Unknown error')}")
            else:
                raise Exception(f"HTTP {response.status}: {await response.text()}")
    
    def _convert_growatt_response(self, data: dict[str, Any]) -> dict[str, Any]:
        """Convert Growatt API response format to our expected format."""
        # This method maps Growatt's response fields to our data model
        converted = {}
        
        # Map common fields
        if "pac" in data:
            converted["solar_power"] = data["pac"]
        if "eToday" in data:
            converted["solar_energy_today"] = data["eToday"]
        if "eTotal" in data:
            converted["solar_energy_total"] = data["eTotal"]
        if "vpv1" in data:
            converted["pv1_voltage"] = data["vpv1"]
        if "ipv1" in data:
            converted["pv1_current"] = data["ipv1"]
        if "ppv1" in data:
            converted["pv1_power"] = data["ppv1"]
        if "vpv2" in data:
            converted["pv2_voltage"] = data["vpv2"]
        if "ipv2" in data:
            converted["pv2_current"] = data["ipv2"]
        if "ppv2" in data:
            converted["pv2_power"] = data["ppv2"]
        if "vac1" in data:
            converted["grid_voltage"] = data["vac1"]
        if "fac1" in data:
            converted["grid_frequency"] = data["fac1"]
        if "tempperature" in data:  # Note: Growatt has a typo in their API
            converted["inverter_temperature"] = data["tempperature"]
        if "status" in data:
            converted["system_status"] = self._convert_status(data["status"])
        
        return converted
    
    def _convert_status(self, status: int) -> str:
        """Convert Growatt status code to readable string."""
        status_map = {
            0: "Offline",
            1: "Normal",
            2: "Fault",
            3: "Checking",
        }
        return status_map.get(status, f"Unknown ({status})")
    
    # MQTT methods
    async def _test_mqtt_connection(self) -> bool:
        """Test MQTT connection."""
        if not self.mqtt_broker:
            return False
        
        try:
            async with MQTTClient(
                hostname=self.mqtt_broker,
                port=self.port or 1883,
                username=self.username,
                password=self.password,
            ) as client:
                # Try to subscribe to test topic
                await client.subscribe(f"{self.mqtt_topic}/status")
                return True
        except Exception:
            return False
    
    async def _setup_mqtt_client(self) -> None:
        """Set up MQTT client and subscriptions."""
        if not self._mqtt_client:
            self._mqtt_client = MQTTClient(
                hostname=self.mqtt_broker,
                port=self.port or 1883,
                username=self.username,
                password=self.password,
            )
            
            await self._mqtt_client.connect()
            
            # Subscribe to all relevant topics
            topics = ["status", "battery", "solar", "grid", "load"]
            for topic in topics:
                await self._mqtt_client.subscribe(f"{self.mqtt_topic}/{topic}")
            
            # Start listening for messages
            asyncio.create_task(self._mqtt_message_handler())
    
    async def _mqtt_message_handler(self) -> None:
        """Handle incoming MQTT messages."""
        if not self._mqtt_client:
            return
        
        async for message in self._mqtt_client.messages:
            try:
                topic_parts = message.topic.value.split("/")
                if len(topic_parts) >= 2:
                    data_type = topic_parts[-1]
                    payload = json.loads(message.payload.decode())
                    self._mqtt_data[data_type] = payload
            except Exception as err:
                _LOGGER.warning("Failed to process MQTT message: %s", err)
    
    async def _get_mqtt_data(self) -> NoahData | Neo800Data:
        """Get data from MQTT."""
        if not self._mqtt_client:
            await self._setup_mqtt_client()
        
        # Wait a bit for data to arrive
        await asyncio.sleep(1)
        
        if self.device_type == DEVICE_TYPE_NEO800:
            return Neo800Data.from_mqtt_data(self._mqtt_data)
        else:
            return NoahData.from_mqtt_data(self._mqtt_data)
    
    # Modbus methods
    async def _test_modbus_connection(self) -> bool:
        """Test Modbus connection."""
        try:
            await self._setup_modbus_client()
            if self._modbus_client:
                # Try to read a test register
                result = await self._modbus_client.read_holding_registers(1000, 1)
                return not result.isError()
            return False
        except Exception:
            return False
    
    async def _setup_modbus_client(self) -> None:
        """Set up Modbus client."""
        if not self._modbus_client:
            if self.connection_type == CONNECTION_TYPE_MODBUS_TCP:
                self._modbus_client = AsyncModbusTcpClient(
                    host=self.host,
                    port=self.port or 502,
                    timeout=self.timeout,
                )
            elif self.connection_type == CONNECTION_TYPE_MODBUS_RTU:
                self._modbus_client = AsyncModbusSerialClient(
                    port=self.host,  # Serial port path
                    baudrate=self.port or 9600,  # Using port field for baudrate
                    timeout=self.timeout,
                )
            
            if self._modbus_client:
                await self._modbus_client.connect()
    
    async def _get_modbus_data(self) -> NoahData | Neo800Data:
        """Get data from Modbus."""
        if not self._modbus_client:
            await self._setup_modbus_client()
        
        if not self._modbus_client:
            raise Exception("Failed to connect to Modbus device")
        
        # Read all registers based on device type
        register_data = {}
        registers = NEO800_MODBUS_REGISTERS if self.device_type == DEVICE_TYPE_NEO800 else NOAH_MODBUS_REGISTERS
        
        for name, address in registers.items():
            try:
                result = await self._modbus_client.read_holding_registers(address, 1)
                if not result.isError():
                    register_data[name] = result.registers[0]
                else:
                    _LOGGER.warning("Failed to read register %s at address %d", name, address)
            except ModbusException as err:
                _LOGGER.warning("Modbus error reading %s: %s", name, err)
        
        if self.device_type == DEVICE_TYPE_NEO800:
            return Neo800Data.from_modbus_data(register_data)
        else:
            return NoahData.from_modbus_data(register_data)