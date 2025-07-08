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
import hashlib
from datetime import datetime

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
    """Main API client for Growatt Noah 2000 and Neo 800 with advanced battery management."""
    
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
        server_url: str = None,
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
        # Don't store server_url - let growattServer use its defaults
        # self.server_url = server_url
        
        self._session: Optional[aiohttp.ClientSession] = None
        self._mqtt_client: Optional[MQTTClient] = None
        self._modbus_client: Optional[AsyncModbusTcpClient | AsyncModbusSerialClient] = None
        self._auth_token: Optional[str] = None
        self._user_data: dict[str, Any] = {}
        self._mqtt_data: dict[str, Any] = {}
        self._login_response: dict[str, Any] = {}
        self._plant_list: list[dict[str, Any]] = []
        self._device_list: list[dict[str, Any]] = []
        self._growatt_api: Optional[Any] = None  # Store growattServer API instance
    
    async def async_test_connection(self) -> bool:
        """Test the connection to the device."""
        _LOGGER.info("Starting connection test: type=%s, username=%s, device_id=%s", 
                    self.connection_type, self.username, self.device_id)
        try:
            if self.connection_type == CONNECTION_TYPE_API:
                result = await self._test_api_connection()
                _LOGGER.info("API connection test result: %s", result)
                return result
            elif self.connection_type == CONNECTION_TYPE_MQTT:
                result = await self._test_mqtt_connection()
                _LOGGER.info("MQTT connection test result: %s", result)
                return result
            elif self.connection_type in [CONNECTION_TYPE_MODBUS_TCP, CONNECTION_TYPE_MODBUS_RTU]:
                result = await self._test_modbus_connection()
                _LOGGER.info("Modbus connection test result: %s", result)
                return result
            else:
                _LOGGER.error("Unknown connection type: %s", self.connection_type)
                return False
        except Exception as err:
            _LOGGER.exception("Connection test failed with exception: %s", err)
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
        if self._growatt_api:
            # Clean up growattServer API instance
            self._growatt_api = None
    
    # API methods
    async def _test_api_connection(self) -> bool:
        """Test Growatt API connection."""
        _LOGGER.info("Testing API connection with username=%s", self.username)
        
        if not self.username or not self.password:
            _LOGGER.error("Missing username or password for API connection")
            return False
        
        # Test dependencies first
        try:
            import aiohttp
            _LOGGER.info("aiohttp dependency available: %s", aiohttp.__version__)
        except ImportError as err:
            _LOGGER.error("aiohttp dependency missing: %s", err)
            return False
        
        try:
            from growattServer import GrowattApi
            _LOGGER.info("growattServer dependency available")
        except ImportError as err:
            _LOGGER.warning("growattServer dependency missing: %s - will use aiohttp fallback", err)
        
        try:
            _LOGGER.info("Attempting authentication...")
            await self._authenticate_api()
            
            if self._auth_token:
                _LOGGER.info("Authentication successful, auth_token=%s", self._auth_token)
                return True
            else:
                _LOGGER.error("Authentication failed - no auth token received")
                return False
                
        except ImportError as err:
            _LOGGER.error("Missing dependency for API connection: %s", err)
            return False
        except Exception as err:
            _LOGGER.exception("API connection test failed with exception: %s", err)
            import traceback
            _LOGGER.error("Full traceback: %s", traceback.format_exc())
            return False
    
    def _hash_password(self, password: str) -> str:
        """Hash password using Growatt's MD5 algorithm."""
        password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
        for i in range(0, len(password_md5), 2):
            if password_md5[i] == '0':
                password_md5 = password_md5[0:i] + 'c' + password_md5[i + 1:]
        return password_md5
    
    async def _authenticate_api(self) -> None:
        """Authenticate with Growatt API using official growattServer method."""
        _LOGGER.info("Starting authentication with username=%s", self.username)
        
        # Use growattServer library exclusively - this is what the official integration uses
        try:
            from growattServer import GrowattApi
            _LOGGER.info("Using growattServer library for authentication")
            
            # Create API instance with the same parameters as official integration
            api = GrowattApi(add_random_user_id=True, agent_identifier="ha-noah-integration")
            
            # Don't override server_url - let growattServer use its default
            # This is key difference from your original code
            
            # Synchronous login call from growattServer (this is blocking but fast)
            login_response = api.login(self.username, self.password)
            _LOGGER.info("growattServer login response keys: %s", list(login_response.keys()) if login_response else "None")
            
            if login_response and login_response.get('success'):
                self._auth_token = login_response['user']['id']
                self._user_data = login_response.get('user', {})
                self._login_response = login_response
                # Store the growattServer API instance for later use
                self._growatt_api = api
                _LOGGER.info("Successfully authenticated with growattServer, user_id=%s", self._auth_token)
                return
            else:
                error_msg = login_response.get('msg', 'Unknown error') if login_response else 'No response'
                _LOGGER.error("growattServer login failed: %s", error_msg)
                raise Exception(f"Login failed: {error_msg}")
                
        except ImportError:
            _LOGGER.error("growattServer library not available - this is required for authentication")
            raise Exception("growattServer library is required but not available")
            
        except Exception as e:
            _LOGGER.error("growattServer authentication failed: %s", e)
            raise Exception(f"Authentication failed: {e}")
    
    async def _get_api_data(self) -> NoahData | Neo800Data:
        """Get data from Growatt API using advanced methods."""
        if self.device_type == DEVICE_TYPE_NOAH:
            # Use comprehensive Noah data collection
            comprehensive_data = await self.get_comprehensive_noah_data()
            
            # Extract battery status from Noah data
            battery_data = self._extract_battery_status_from_noah(comprehensive_data)
            
            # Convert to our NoahData format
            return NoahData.from_comprehensive_data(comprehensive_data, battery_data)
        
        else:
            # For Neo 800, use simpler API approach
            if not self._auth_token:
                await self._authenticate_api()
            
            plants = await self.get_plant_list()
            if not plants:
                raise Exception("No plants found in account")
            
            target_plant = plants[0]
            if self.device_id:
                for plant in plants:
                    if (plant.get("id") == self.device_id or 
                        plant.get("plantId") == self.device_id or
                        plant.get("plantName") == self.device_id):
                        target_plant = plant
                        break
            
            plant_id = target_plant.get("id") or target_plant.get("plantId")
            devices = await self.get_device_list(str(plant_id))
            
            # Find Neo 800 inverter data
            neo_data = {}
            for device in devices:
                device_type = str(device.get("deviceType", "")).lower()
                if "inverter" in device_type or "neo" in device_type:
                    neo_data = device
                    break
            
            # Convert to Neo800Data format
            converted_data = self._convert_growatt_response(neo_data)
            return Neo800Data.from_api_response(converted_data)
    
    def _extract_battery_status_from_noah(self, comprehensive_data: dict[str, Any]) -> dict[str, Any]:
        """Extract comprehensive battery status from Noah data."""
        battery_status = {}
        
        # Extract from Noah status
        noah_status = comprehensive_data.get("noah_status", {})
        if noah_status:
            battery_status.update({
                "soc": noah_status.get("soc"),
                "charge_power": noah_status.get("chargePower"),
                "discharge_power": noah_status.get("disChargePower"),
                "work_mode": noah_status.get("workMode"),
                "battery_num": noah_status.get("batteryNum"),
                "status": noah_status.get("status"),
            })
        
        # Extract from Noah info
        noah_info = comprehensive_data.get("noah_info", {}).get("noah", {})
        if noah_info:
            battery_status.update({
                "charging_soc_high_limit": noah_info.get("chargingSocHighLimit"),
                "charging_soc_low_limit": noah_info.get("chargingSocLowLimit"),
                "default_power": noah_info.get("defaultPower"),
                "version": noah_info.get("version"),
                "model": noah_info.get("model"),
                "bat_sns": noah_info.get("batSns", []),
                "formula_money": noah_info.get("formulaMoney"),
                "money_unit": noah_info.get("moneyUnitText"),
            })
        
        # Extract from storage data
        storage_data = comprehensive_data.get("storage_data", {})
        if storage_data:
            # Storage detail
            detail = storage_data.get("detail", {})
            if detail and isinstance(detail, dict):
                obj = detail.get("obj", {})
                if obj:
                    battery_status.update({
                        "battery_voltage": obj.get("vBat"),
                        "battery_current": obj.get("iBat"),
                        "battery_power": obj.get("pBat"),
                        "battery_temperature": obj.get("tempBat"),
                        "capacity": obj.get("capacity"),
                    })
            
            # Storage params
            params = storage_data.get("params", {})
            if params and isinstance(params, dict):
                obj = params.get("obj", {})
                if obj:
                    battery_status.update({
                        "rated_capacity": obj.get("ratedCapacity"),
                        "actual_capacity": obj.get("actualCapacity"),
                        "charge_cycles": obj.get("chargeCycles"),
                        "health": obj.get("health"),
                    })
            
            # Storage overview
            overview = storage_data.get("overview", {})
            if overview:
                battery_status.update({
                    "energy_today": overview.get("eChargeToday"),
                    "energy_total": overview.get("eChargeTotal"),
                    "discharge_today": overview.get("eDischargeToday"),
                    "discharge_total": overview.get("eDischargeTotal"),
                })
        
        # Remove None values
        return {k: v for k, v in battery_status.items() if v is not None}
    
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
        except Exception as err:
            _LOGGER.error(
                "Modbus connection failed: %s. "
                "Note: Most Growatt devices (Noah 2000, Neo 800) do not support Modbus TCP by default. "
                "Consider using MQTT or API connection instead.",
                err
            )
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
    
    # Advanced Noah 2000 API methods from official growattServer library
    async def get_plant_list(self) -> list[dict[str, Any]]:
        """Get list of plants connected to this account."""
        if not self._auth_token:
            await self._authenticate_api()
        
        if not self._growatt_api:
            await self._authenticate_api()
        
        try:
            # Use growattServer library method directly
            plants_response = self._growatt_api.plant_list(self._auth_token)
            _LOGGER.info("Plant list response type: %s", type(plants_response))
            
            # Handle different response formats from growattServer
            if isinstance(plants_response, dict):
                plants = plants_response.get('data', [])
            elif isinstance(plants_response, list):
                plants = plants_response
            else:
                _LOGGER.error("Unexpected plant list response format: %s", plants_response)
                plants = []
            
            self._plant_list = plants
            return self._plant_list
            
        except Exception as e:
            _LOGGER.error("Failed to get plant list: %s", e)
            raise Exception(f"Failed to get plant list: {e}")
    
    async def get_device_list(self, plant_id: str) -> list[dict[str, Any]]:
        """Get list of devices for a plant."""
        if not self._growatt_api:
            await self._authenticate_api()
        
        try:
            # Use growattServer library method directly
            device_response = self._growatt_api.device_list(plant_id)
            _LOGGER.info("Device list response type: %s", type(device_response))
            
            # Handle different response formats from growattServer
            if isinstance(device_response, dict):
                device_list = device_response.get('deviceList', [])
            elif isinstance(device_response, list):
                device_list = device_response
            else:
                _LOGGER.error("Unexpected device list response format: %s", device_response)
                device_list = []
            
            self._device_list = device_list
            return device_list
            
        except Exception as e:
            _LOGGER.error("Failed to get device list: %s", e)
            raise Exception(f"Failed to get device list: {e}")
    
    async def is_plant_noah_system(self, plant_id: str) -> dict[str, Any]:
        """Check if plant is a Noah system."""
        if not self._growatt_api:
            await self._authenticate_api()
        
        try:
            # Use growattServer library method directly
            noah_response = self._growatt_api.is_plant_noah_system(plant_id)
            _LOGGER.info("Noah system check response: %s", noah_response)
            return noah_response
            
        except Exception as e:
            _LOGGER.error("Failed to check Noah system: %s", e)
            raise Exception(f"Failed to check Noah system: {e}")
    
    async def noah_system_status(self, serial_number: str) -> dict[str, Any]:
        """Get Noah system status with comprehensive battery information."""
        if not self._growatt_api:
            await self._authenticate_api()
        
        try:
            # Use growattServer library method directly
            noah_status = self._growatt_api.noah_system_status(serial_number)
            _LOGGER.info("Noah system status response: %s", noah_status)
            return noah_status
            
        except Exception as e:
            _LOGGER.error("Failed to get Noah system status: %s", e)
            raise Exception(f"Failed to get Noah system status: {e}")
    
    async def noah_info(self, serial_number: str) -> dict[str, Any]:
        """Get detailed Noah device information and configuration."""
        if not self._growatt_api:
            await self._authenticate_api()
        
        try:
            # Use growattServer library method directly
            noah_info = self._growatt_api.noah_info(serial_number)
            _LOGGER.info("Noah info response: %s", noah_info)
            return noah_info
            
        except Exception as e:
            _LOGGER.error("Failed to get Noah info: %s", e)
            raise Exception(f"Failed to get Noah info: {e}")
    
    async def storage_detail(self, storage_id: str) -> dict[str, Any]:
        """Get detailed storage/battery parameters."""
        if not self._session:
            await self._authenticate_api()
        
        async with self._session.get(
            f"{self.server_url}newStorageAPI.do",
            params={
                "op": "getStorageInfo_sacolar",
                "storageId": storage_id
            }
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to get storage detail: HTTP {response.status}")
    
    async def storage_params(self, storage_id: str) -> dict[str, Any]:
        """Get comprehensive storage parameters."""
        if not self._session:
            await self._authenticate_api()
        
        async with self._session.get(
            f"{self.server_url}newStorageAPI.do",
            params={
                "op": "getStorageParams_sacolar",
                "storageId": storage_id
            }
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to get storage params: HTTP {response.status}")
    
    async def storage_energy_overview(self, plant_id: str, storage_id: str) -> dict[str, Any]:
        """Get storage energy overview."""
        if not self._session:
            await self._authenticate_api()
        
        async with self._session.post(
            f"{self.server_url}newStorageAPI.do?op=getEnergyOverviewData_sacolar",
            params={
                "plantId": plant_id,
                "storageSn": storage_id
            }
        ) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("obj", {})
            else:
                raise Exception(f"Failed to get energy overview: HTTP {response.status}")
    
    async def get_comprehensive_noah_data(self) -> dict[str, Any]:
        """Get comprehensive Noah 2000 data using all available endpoints."""
        if self.device_type != DEVICE_TYPE_NOAH:
            raise ValueError("This method is only for Noah 2000 devices")
        
        try:
            # Prefer growattServer API if available
            if self._growatt_api and self._auth_token:
                _LOGGER.info("Using growattServer API for comprehensive data")
                
                # Get plant list using growattServer
                plants_response = self._growatt_api.plant_list(self._auth_token)
                plants = plants_response.get('data', []) if isinstance(plants_response, dict) else plants_response
                
                if not plants:
                    raise Exception("No plants found")
                
                # Use first plant or find by device_id
                target_plant = plants[0]
                if self.device_id:
                    for plant in plants:
                        if (plant.get("id") == self.device_id or 
                            plant.get("plantId") == self.device_id or
                            plant.get("plantName") == self.device_id):
                            target_plant = plant
                            break
                
                plant_id = target_plant.get("id") or target_plant.get("plantId")
                
                # Check if it's a Noah system using growattServer
                noah_check = self._growatt_api.is_plant_noah_system(str(plant_id))
                noah_obj = noah_check.get("obj", {})
                
                if not noah_obj.get("isPlantNoahSystem") and not noah_obj.get("isPlantHaveNoah"):
                    _LOGGER.warning("Plant %s doesn't appear to be a Noah system", plant_id)
                
                # Get Noah device status directly
                device_sn = self.device_id or noah_obj.get("deviceSn")
                if not device_sn:
                    raise Exception("No device serial number available")
                
                # Get comprehensive data using growattServer
                noah_status = self._growatt_api.noah_system_status(device_sn)
                noah_info = self._growatt_api.noah_info(device_sn)
                
                return {
                    "plant": target_plant,
                    "noah_check": noah_obj,
                    "devices": [],  # Not needed when using growattServer directly
                    "noah_status": noah_status,
                    "noah_info": noah_info,
                    "storage_data": {},  # Will add if needed
                    "device_sn": device_sn,
                    "plant_id": plant_id
                }
            
            # If growattServer is not available, we cannot proceed reliably
            # The async methods below depend on aiohttp which is not as reliable
            # for authentication as the growattServer library
            raise Exception("growattServer library is required for reliable Noah 2000 authentication")
            
        except Exception as e:
            _LOGGER.error("Failed to get comprehensive Noah data: %s", e)
            raise