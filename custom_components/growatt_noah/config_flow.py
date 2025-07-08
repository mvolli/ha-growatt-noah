"""Config flow for Growatt Noah 2000 integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api import GrowattNoahAPI
from .const import (
    DOMAIN,
    CONNECTION_TYPE_API,
    CONNECTION_TYPE_MQTT,
    CONNECTION_TYPE_MODBUS_TCP,
    CONNECTION_TYPE_MODBUS_RTU,
    DEVICE_TYPE_NOAH,
    DEVICE_TYPE_NEO800,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_PORT_MODBUS,
    DEFAULT_PORT_MQTT,
)

_LOGGER = logging.getLogger(__name__)

# Configuration step schemas
STEP_DEVICE_TYPE_SCHEMA = vol.Schema(
    {
        vol.Required("device_type", default=DEVICE_TYPE_NOAH): vol.In([
            DEVICE_TYPE_NOAH,
            DEVICE_TYPE_NEO800,
        ]),
    }
)

STEP_CONNECTION_TYPE_SCHEMA = vol.Schema(
    {
        vol.Required("connection_type"): vol.In([
            CONNECTION_TYPE_API,
            CONNECTION_TYPE_MQTT,
            CONNECTION_TYPE_MODBUS_TCP,
            CONNECTION_TYPE_MODBUS_RTU,
        ]),
    }
)

STEP_API_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional("device_id", description="Device serial number (leave empty for auto-detection)"): str,
        vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.Coerce(int),
    }
)

STEP_MQTT_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("mqtt_broker"): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT_MQTT): vol.Coerce(int),
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
        vol.Optional("mqtt_topic", default="noah"): str,
        vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.Coerce(int),
    }
)

STEP_MODBUS_TCP_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT_MODBUS): vol.Coerce(int),
        vol.Optional("device_id", default=1): vol.Coerce(int),
        vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.Coerce(int),
    }
)

STEP_MODBUS_RTU_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("serial_port"): str,
        vol.Optional("baudrate", default=9600): vol.In([1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]),
        vol.Optional("device_id", default=1): vol.Coerce(int),
        vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.Coerce(int),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    
    # Create API client for testing
    api_client = GrowattNoahAPI(
        connection_type=data["connection_type"],
        device_type=data.get("device_type", DEVICE_TYPE_NOAH),
        host=data.get(CONF_HOST) or data.get("serial_port"),
        port=data.get(CONF_PORT) or data.get("baudrate"),
        username=data.get(CONF_USERNAME),
        password=data.get(CONF_PASSWORD),
        mqtt_broker=data.get("mqtt_broker"),
        mqtt_topic=data.get("mqtt_topic", "noah"),
        device_id=data.get("device_id"),
        # Don't pass server_url - let growattServer use defaults
    )
    
    try:
        _LOGGER.info("Testing connection with config: connection_type=%s, device_type=%s, username=%s, device_id=%s", 
                    data["connection_type"], data.get("device_type"), data.get(CONF_USERNAME), data.get("device_id"))
        
        # Test the connection
        connection_result = await api_client.async_test_connection()
        _LOGGER.info("Connection test result: %s", connection_result)
        
        if not connection_result:
            _LOGGER.error("Connection test returned False - authentication or network issue")
            raise CannotConnect("Connection test failed - check credentials and network")
        
        # If we get here, connection is successful
        device_name = "Neo 800" if data.get("device_type") == DEVICE_TYPE_NEO800 else "Noah 2000"
        _LOGGER.info("Connection successful for %s", device_name)
        return {"title": f"Growatt {device_name} ({data['connection_type'].upper()})"}
    
    except CannotConnect as err:
        _LOGGER.error("Connection failed: %s", err)
        raise
    except ImportError as err:
        _LOGGER.error("Missing dependency: %s", err)
        raise CannotConnect(f"Missing dependency: {str(err)} - try restarting Home Assistant")
    except Exception as err:
        _LOGGER.exception("Unexpected error during connection test: %s", err)
        raise CannotConnect(f"Connection test failed: {str(err)}")
    finally:
        try:
            await api_client.async_close()
        except Exception as err:
            _LOGGER.warning("Error closing API client: %s", err)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Growatt Noah 2000 and Neo 800."""
    
    VERSION = 1
    
    def __init__(self) -> None:
        """Initialize the config flow."""
        self.device_type: str | None = None
        self.connection_type: str | None = None
        self.config_data: dict[str, Any] = {}
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - device type selection."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            self.device_type = user_input["device_type"]
            self.config_data["device_type"] = self.device_type
            
            # Move to connection type selection
            return await self.async_step_connection_type()
        
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_DEVICE_TYPE_SCHEMA,
            errors=errors,
        )
    
    async def async_step_connection_type(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle connection type selection."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            self.connection_type = user_input["connection_type"]
            
            # Route to the appropriate step based on connection type
            if self.connection_type == CONNECTION_TYPE_API:
                return await self.async_step_api()
            elif self.connection_type == CONNECTION_TYPE_MQTT:
                return await self.async_step_mqtt()
            elif self.connection_type == CONNECTION_TYPE_MODBUS_TCP:
                return await self.async_step_modbus_tcp()
            elif self.connection_type == CONNECTION_TYPE_MODBUS_RTU:
                return await self.async_step_modbus_rtu()
        
        return self.async_show_form(
            step_id="connection_type",
            data_schema=STEP_CONNECTION_TYPE_SCHEMA,
            errors=errors,
        )
    
    async def async_step_api(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle API configuration step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            user_input["connection_type"] = self.connection_type
            user_input["device_type"] = self.device_type
            
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)
        
        return self.async_show_form(
            step_id="api",
            data_schema=STEP_API_DATA_SCHEMA,
            errors=errors,
        )
    
    async def async_step_mqtt(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle MQTT configuration step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            user_input["connection_type"] = self.connection_type
            user_input["device_type"] = self.device_type
            
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)
        
        return self.async_show_form(
            step_id="mqtt",
            data_schema=STEP_MQTT_DATA_SCHEMA,
            errors=errors,
        )
    
    async def async_step_modbus_tcp(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle Modbus TCP configuration step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            user_input["connection_type"] = self.connection_type
            user_input["device_type"] = self.device_type
            
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)
        
        return self.async_show_form(
            step_id="modbus_tcp",
            data_schema=STEP_MODBUS_TCP_DATA_SCHEMA,
            errors=errors,
        )
    
    async def async_step_modbus_rtu(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle Modbus RTU configuration step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            user_input["connection_type"] = self.connection_type
            user_input[CONF_HOST] = user_input["serial_port"]  # Map serial_port to host
            user_input[CONF_PORT] = user_input["baudrate"]  # Map baudrate to port
            
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)
        
        return self.async_show_form(
            step_id="modbus_rtu",
            data_schema=STEP_MODBUS_RTU_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""