"""Config flow for Growatt Noah 2000 integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api import GrowattNoahAPI
from .const import (
    DOMAIN,
    CONNECTION_TYPE_API,
    DEVICE_TYPE_NOAH,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

# Configuration schema for Noah 2000 API connection
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional("device_id", description="Device serial number (leave empty for auto-detection)"): str,
        vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=300)),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    
    # Create API client for testing
    api_client = GrowattNoahAPI(
        connection_type=CONNECTION_TYPE_API,
        device_type=DEVICE_TYPE_NOAH,
        username=data.get(CONF_USERNAME),
        password=data.get(CONF_PASSWORD),
        device_id=data.get("device_id"),
    )
    
    try:
        _LOGGER.debug("Testing connection with username=%s, device_id=%s", 
                     data.get(CONF_USERNAME), data.get("device_id"))
        
        # Test the connection
        connection_result = await api_client.async_test_connection()
        _LOGGER.debug("Connection test result: %s", connection_result)
        
        if not connection_result:
            _LOGGER.error("Connection test failed - check credentials and network")
            raise CannotConnect("Connection test failed - check credentials and network")
        
        # If we get here, connection is successful
        _LOGGER.debug("Connection successful for Noah 2000")
        return {"title": "Growatt Noah 2000"}
    
    except CannotConnect as err:
        _LOGGER.error("Connection failed: %s", err)
        raise
    except Exception as err:
        _LOGGER.exception("Unexpected error during connection test: %s", err)
        raise CannotConnect(f"Connection test failed: {str(err)}")
    finally:
        try:
            await api_client.async_close()
        except Exception as err:
            _LOGGER.warning("Error closing API client: %s", err)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Growatt Noah 2000."""
    
    VERSION = 1
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            # Add required fields for API connection
            user_input["connection_type"] = CONNECTION_TYPE_API
            user_input["device_type"] = DEVICE_TYPE_NOAH
            
            try:
                info = await validate_input(self.hass, user_input)
                
                # Set unique ID to prevent duplicate entries
                device_id = user_input.get("device_id") or user_input.get(CONF_USERNAME)
                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()
                
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
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""