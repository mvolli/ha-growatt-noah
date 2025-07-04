"""Growatt Noah 2000 integration for Home Assistant."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .api import GrowattNoahAPI
from .models import NoahData

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
    Platform.NUMBER,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Growatt Noah from a config entry."""
    
    # Initialize the API client based on connection method
    api_client = GrowattNoahAPI(
        connection_type=entry.data["connection_type"],
        host=entry.data.get("host"),
        port=entry.data.get("port"),
        username=entry.data.get("username"),
        password=entry.data.get("password"),
        mqtt_broker=entry.data.get("mqtt_broker"),
        mqtt_topic=entry.data.get("mqtt_topic", "noah"),
        device_id=entry.data.get("device_id"),
    )
    
    # Test the connection
    try:
        await api_client.async_test_connection()
    except Exception as err:
        _LOGGER.error("Failed to connect to Growatt Noah: %s", err)
        raise ConfigEntryNotReady from err
    
    # Create data coordinator
    coordinator = NoahDataUpdateCoordinator(
        hass,
        api_client,
        entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL),
    )
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator and API client
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api_client,
    }
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Clean up data
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await data["api"].async_close()
    
    return unload_ok


class NoahDataUpdateCoordinator(DataUpdateCoordinator[NoahData]):
    """Class to manage fetching Noah data from the API."""
    
    def __init__(
        self,
        hass: HomeAssistant,
        api_client: GrowattNoahAPI,
        scan_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        self.api_client = api_client
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
    
    async def _async_update_data(self) -> NoahData:
        """Update data via library."""
        try:
            return await self.api_client.async_get_data()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err