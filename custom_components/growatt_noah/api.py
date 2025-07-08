"""Optimized API client for Growatt Noah 2000 battery system."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional
import hashlib

import aiohttp

from .const import CONNECTION_TYPE_API, DEVICE_TYPE_NOAH, DEFAULT_TIMEOUT
from .models import NoahData

_LOGGER = logging.getLogger(__name__)


class GrowattNoahAPI:
    """Optimized API client for Growatt Noah 2000 battery system."""
    
    def __init__(
        self,
        connection_type: str,
        device_type: str = DEVICE_TYPE_NOAH,
        username: Optional[str] = None,
        password: Optional[str] = None,
        device_id: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the API client."""
        if connection_type != CONNECTION_TYPE_API:
            raise ValueError(f"Only API connection supported, got: {connection_type}")
        if device_type != DEVICE_TYPE_NOAH:
            raise ValueError(f"Only Noah 2000 devices supported, got: {device_type}")
            
        self.connection_type = connection_type
        self.device_type = device_type
        self.username = username
        self.password = password
        self.device_id = device_id
        self.timeout = timeout
        
        self._session: Optional[aiohttp.ClientSession] = None
        self._auth_token: Optional[str] = None
    
    async def async_test_connection(self) -> bool:
        """Test the connection to the Noah 2000 device."""
        _LOGGER.debug("Testing API connection for Noah 2000: username=%s, device_id=%s", 
                     self.username, self.device_id)
        
        if not self.username or not self.password:
            _LOGGER.error("Missing username or password")
            return False
        
        try:
            await self._authenticate_api()
            if self._auth_token:
                _LOGGER.debug("Authentication successful, token=%s", self._auth_token)
                return True
            else:
                _LOGGER.error("Authentication failed - no token received")
                return False
                
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False
    
    async def async_get_data(self) -> NoahData:
        """Get Noah 2000 device data."""
        if not self._auth_token:
            await self._authenticate_api()
        
        try:
            # Get real Noah data using direct API call
            noah_status = await self._noah_system_status(self.device_id)
            _LOGGER.debug("Noah status retrieved: %s keys", len(noah_status.keys()) if noah_status else 0)
            
            # Convert Noah API response to structured data
            battery_data = self._convert_noah_response(noah_status)
            _LOGGER.debug("Converted battery data keys: %s", list(battery_data.keys()) if battery_data else "None")
            
            # Create NoahData object
            noah_data_obj = NoahData.from_api_response(battery_data)
            _LOGGER.debug("NoahData created - SOC: %s, Solar: %s, Status: %s", 
                         noah_data_obj.battery.soc, noah_data_obj.solar.power, noah_data_obj.system.status)
            
            return noah_data_obj
            
        except Exception as e:
            _LOGGER.error("Failed to get Noah data: %s", e)
            # Return empty data if API call fails
            return NoahData.from_api_response({})
    
    async def async_close(self) -> None:
        """Close the API session."""
        if self._session:
            await self._session.close()
            self._session = None
    
    def _hash_password(self, password: str) -> str:
        """Hash password using Growatt's MD5 algorithm."""
        password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
        for i in range(0, len(password_md5), 2):
            if password_md5[i] == '0':
                password_md5 = password_md5[0:i] + 'c' + password_md5[i + 1:]
        return password_md5
    
    async def _authenticate_api(self) -> None:
        """Authenticate with Growatt API using aiohttp."""
        if not self._session:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/x-www-form-urlencoded",
            }
            # Enable cookie jar to maintain session for Noah API
            cookie_jar = aiohttp.CookieJar()
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                headers=headers,
                cookie_jar=cookie_jar
            )
        
        # Hash password using Growatt's method
        hashed_password = self._hash_password(self.password)
        
        login_data = {
            "userName": self.username,
            "password": hashed_password,
        }
        
        login_url = "https://openapi.growatt.com/newTwoLoginAPI.do"
        
        async with self._session.post(login_url, data=login_data) as response:
            if response.status == 200:
                result = await response.json()
                login_result = result.get("back", {})
                
                if login_result.get("success"):
                    self._auth_token = login_result.get("user", {}).get("id")
                    _LOGGER.debug("Authentication successful")
                else:
                    raise Exception(f"Login failed: {login_result.get('msg', 'Authentication failed')}")
            else:
                text = await response.text()
                raise Exception(f"HTTP {response.status}: {text}")
    
    async def _noah_system_status(self, serial_number: str) -> dict[str, Any]:
        """Get Noah system status with comprehensive battery information."""
        if not self._auth_token:
            await self._authenticate_api()
        
        # The Noah API requires both the auth token and session cookies
        data = {
            "deviceSn": serial_number,
            "userId": self._auth_token
        }
        
        async with self._session.post(
            "https://openapi.growatt.com/noahDeviceApi/noah/getSystemStatus",
            data=data
        ) as response:
            if response.status == 200:
                try:
                    result = await response.json()
                    if result.get("result"):
                        noah_status = result.get("obj", {})
                        _LOGGER.debug("Noah system status retrieved successfully")
                        return noah_status
                    else:
                        raise Exception(f"Noah status error: {result.get('msg', 'Unknown error')}")
                except Exception as e:
                    # Check if we got redirected to login (session expired)
                    response_text = await response.text()
                    if "login" in response_text.lower():
                        _LOGGER.warning("Session expired, re-authenticating...")
                        self._auth_token = None
                        await self._authenticate_api()
                        # Retry once
                        return await self._noah_system_status(serial_number)
                    else:
                        raise Exception(f"Failed to parse Noah status response: {e}")
            else:
                raise Exception(f"Failed to get Noah status: HTTP {response.status}")
    
    def _convert_noah_response(self, noah_status: dict[str, Any]) -> dict[str, Any]:
        """Convert Noah API response to structured data format."""
        if not noah_status:
            return {}
        
        # Convert string values to appropriate numeric types
        try:
            soc = float(noah_status.get("soc", 0))
            charge_power = float(noah_status.get("chargePower", 0))
            discharge_power = float(noah_status.get("disChargePower", 0))
            solar_power = float(noah_status.get("ppv", 0))  # ppv = PV power
            grid_power = float(noah_status.get("pac", 0))   # pac = AC power
            work_mode = int(noah_status.get("workMode", 0))
            status = int(noah_status.get("status", 0))
            
            # Additional Noah fields
            groplug_power = float(noah_status.get("groplugPower", 0))  # External device power
            other_power = float(noah_status.get("otherPower", 0))      # Other connected devices
            profit_today = float(noah_status.get("profitToday", 0))   # Daily profit
            profit_total = float(noah_status.get("profitTotal", 0))   # Total profit
            
        except (ValueError, TypeError) as e:
            _LOGGER.warning("Error converting Noah data types: %s", e)
            return {}
        
        # Map work modes to readable text
        work_mode_map = {
            0: "No Response",
            1: "Load First",
            2: "Battery First", 
            3: "Grid First",
            4: "Backup Mode",
        }
        work_mode_text = work_mode_map.get(work_mode, f"Unknown ({work_mode})")
        
        # Calculate total load power including all connected devices
        # Load = Solar + Battery Discharge - Battery Charge - Grid Export + Connected Devices
        load_power = max(0, solar_power + discharge_power - charge_power - grid_power + groplug_power + other_power)
        
        return {
            # Battery fields
            "battery_soc": soc,
            "battery_power": charge_power - discharge_power,  # Net battery power
            "battery_voltage": 0,  # Not available in Noah API
            "battery_current": 0,  # Not available in Noah API
            "battery_temperature": 25,  # Default temperature
            "battery_status": "Charging" if charge_power > 0 else ("Discharging" if discharge_power > 0 else "Idle"),
            
            # Solar fields
            "solar_power": solar_power,
            "solar_voltage": 0,  # Not available in Noah API
            "solar_current": 0,  # Not available in Noah API
            "solar_energy_today": float(noah_status.get("eacToday", 0)),
            "solar_energy_total": float(noah_status.get("eacTotal", 0)),
            
            # Grid fields
            "grid_power": grid_power,
            "grid_voltage": 0,  # Not available in Noah API
            "grid_frequency": 50,  # Default frequency
            "grid_energy_imported_today": 0,  # Not available
            "grid_energy_exported_today": float(noah_status.get("eacToday", 0)),
            "grid_energy_imported_total": 0,  # Not available
            "grid_energy_exported_total": float(noah_status.get("eacTotal", 0)),
            "grid_connected": status == 1,
            
            # Load fields (calculated)
            "load_power": load_power,
            "load_energy_today": 0,  # Not available
            "load_energy_total": 0,  # Not available
            
            # System fields
            "system_status": "Online" if status == 1 else "Offline",
            "system_mode": work_mode_text,
            "serial_number": self.device_id,
            "model": noah_status.get("alias", "Noah 2000"),
            
            # Additional Noah-specific fields
            "charge_power": charge_power,
            "discharge_power": discharge_power,
            "work_mode": work_mode,
            "battery_count": int(noah_status.get("batteryNum", 1)),
            "plant_id": noah_status.get("plantId", ""),
            "associated_inverter": noah_status.get("associatedInvSn", ""),
            
            # Economic data
            "profit_today": profit_today,
            "profit_total": profit_total,
            "money_unit": noah_status.get("moneyUnit", "$"),
            
            # Connected devices
            "groplug_power": groplug_power,
            "groplug_count": int(noah_status.get("groplugNum", 0)),
            "other_power": other_power,
        }