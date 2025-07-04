"""Minimal test sensor for debugging."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NoahDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up minimal test sensor."""
    try:
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        
        # Create just one simple test sensor
        test_sensor = TestSensor(coordinator, entry)
        async_add_entities([test_sensor])
        
        _LOGGER.info("Test sensor created successfully")
        
    except Exception as err:
        _LOGGER.error("Failed to set up test sensor: %s", err)
        raise


class TestSensor(CoordinatorEntity, SensorEntity):
    """Test sensor."""
    
    def __init__(self, coordinator: NoahDataUpdateCoordinator, entry: ConfigEntry) -> None:
        """Initialize test sensor."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"{entry.entry_id}_test"
        self._attr_name = "Noah Test Sensor"
        self._attr_icon = "mdi:test-tube"
        
        # Minimal device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Growatt Noah 2000",
            "manufacturer": "Growatt",
            "model": "Noah 2000",
        }
    
    @property
    def native_value(self) -> str:
        """Return test value."""
        if self.coordinator.data:
            return "Connected"
        return "No Data"