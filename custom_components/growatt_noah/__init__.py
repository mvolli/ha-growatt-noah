"""Growatt Noah 2000 integration for Home Assistant."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, DEVICE_TYPE_NOAH
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
    
    # Load cached auth token so HA restarts don't trigger a fresh login
    # (repeated logins can trigger Growatt's account rate-limiter)
    _store = Store(hass, 1, f"{DOMAIN}.{entry.entry_id}.auth")
    stored = await _store.async_load() or {}
    # Only reuse token if it belongs to the same account
    cached_token = (
        stored.get("token")
        if stored.get("username") == entry.data.get("username")
        else None
    )
    if cached_token:
        _LOGGER.debug("Reusing cached auth token from previous session")

    def _save_token(token: str) -> None:
        """Persist a fresh auth token so the next restart can reuse it."""
        hass.async_create_task(
            _store.async_save({"username": entry.data.get("username"), "token": token})
        )

    # Initialize the API client for Noah 2000
    api_client = GrowattNoahAPI(
        connection_type=entry.data["connection_type"],
        device_type=entry.data.get("device_type", DEVICE_TYPE_NOAH),
        username=entry.data.get("username"),
        password=entry.data.get("password"),
        device_id=entry.data.get("device_id"),
        cached_token=cached_token,
        on_token_saved=_save_token,
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
    
    # Fetch initial data - but don't fail setup if this fails
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.warning("Initial data fetch failed, will retry: %s", err)
        # Continue with setup anyway, coordinator will retry automatically
    
    # Store coordinator and API client
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api_client,
        "store": _store,
    }
    
    # Set up platforms
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception as err:
        _LOGGER.error("Failed to set up platforms: %s", err)
        # Clean up on failure
        hass.data[DOMAIN].pop(entry.entry_id, None)
        await api_client.async_close()
        raise ConfigEntryNotReady(f"Failed to set up platforms: {err}") from err
    
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
    """Class to manage fetching Noah 2000 data from the API."""
    
    def __init__(
        self,
        hass: HomeAssistant,
        api_client: GrowattNoahAPI,
        scan_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        self.api_client = api_client
        self.config: dict = {}  # Device configuration (charge limits, enable flags)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
            always_update=False,  # Only update when data actually changes
        )
    
    async def _async_update_data(self) -> NoahData:
        """Update data via library."""
        try:
            data = await self.api_client.async_get_data()

            if data and data.system.status:
                _LOGGER.debug("Data update successful - System status: %s", data.system.status)
            else:
                _LOGGER.warning("Received incomplete data from API")

            # Also refresh device config (non-critical — don't fail if endpoint is unavailable)
            try:
                self.config = await self.api_client.async_get_config()
                _LOGGER.debug("Config update successful: %s", self.config)
            except Exception as config_err:
                _LOGGER.debug("Device config fetch failed (non-critical): %s", config_err)

            return data

        except Exception as err:
            error_msg = str(err)
            
            # Handle specific API errors with user-friendly messages
            if "507" in error_msg:
                _LOGGER.warning("Growatt API temporarily unavailable (Error 507) - will retry automatically")
                raise UpdateFailed("Growatt API temporarily unavailable - retrying automatically")
            elif "Login failed" in error_msg:
                _LOGGER.error("Authentication failed - check credentials: %s", error_msg)
                raise UpdateFailed("Authentication failed - check Growatt credentials in integration settings")
            elif "timeout" in error_msg.lower():
                _LOGGER.warning("API timeout - will retry: %s", error_msg)
                raise UpdateFailed("API timeout - retrying automatically")
            else:
                _LOGGER.error("API communication failed: %s", err, exc_info=True)
                raise UpdateFailed(f"Error communicating with API: {err}") from err