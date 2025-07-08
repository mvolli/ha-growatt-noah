"""Number platform for Growatt Noah 2000."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory

from . import NoahDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Define number entities for configuration
NUMBERS: tuple[NumberEntityDescription, ...] = (
    NumberEntityDescription(
        key="battery_charge_limit",
        name="Battery Charge Limit",
        icon="mdi:battery-plus",
        native_min_value=50,
        native_max_value=100,
        native_step=5,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
    ),
    NumberEntityDescription(
        key="battery_discharge_limit",
        name="Battery Discharge Limit",
        icon="mdi:battery-minus",
        native_min_value=10,
        native_max_value=50,
        native_step=5,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
    ),
    NumberEntityDescription(
        key="max_charge_power",
        name="Maximum Charge Power",
        icon="mdi:lightning-bolt",
        native_min_value=100,
        native_max_value=2000,
        native_step=100,
        native_unit_of_measurement=UnitOfPower.WATT,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
    NumberEntityDescription(
        key="max_discharge_power",
        name="Maximum Discharge Power",
        icon="mdi:lightning-bolt-outline",
        native_min_value=100,
        native_max_value=2000,
        native_step=100,
        native_unit_of_measurement=UnitOfPower.WATT,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the number platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api_client = hass.data[DOMAIN][entry.entry_id]["api"]
    
    entities = []
    for description in NUMBERS:
        entities.append(NoahNumber(coordinator, description, entry, api_client))
    
    async_add_entities(entities)


class NoahNumber(CoordinatorEntity[NoahDataUpdateCoordinator], NumberEntity):
    """Representation of a Noah number entity."""
    
    def __init__(
        self,
        coordinator: NoahDataUpdateCoordinator,
        description: NumberEntityDescription,
        entry: ConfigEntry,
        api_client,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        
        self.entity_description = description
        self._attr_unique_id = f"noah2000_{description.key}"
        self._api_client = api_client
        self._entry = entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Growatt Noah 2000",
            "manufacturer": "Growatt",
            "model": "Noah 2000",
            "sw_version": self._get_firmware_version(),
            "serial_number": entry.data.get("device_id"),
            "configuration_url": "https://server.growatt.com/",
        }
        
        # Store default values (these would normally come from device)
        self._default_values = {
            "battery_charge_limit": 95,
            "battery_discharge_limit": 20,
            "max_charge_power": 2000,
            "max_discharge_power": 2000,
        }
    
    def _get_firmware_version(self) -> str | None:
        """Safely get firmware version from coordinator data."""
        try:
            if self.coordinator.data and hasattr(self.coordinator.data, 'system'):
                return getattr(self.coordinator.data.system, 'firmware_version', None)
        except Exception:
            pass
        return None
    
    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if not self.coordinator.data:
            return None
        
        # Note: These are placeholder implementations
        # Actual values would come from device configuration/settings
        # For now, return default values
        
        return self._default_values.get(self.entity_description.key)
    
    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        try:
            # Get device serial number from entry data
            device_id = self._entry.data.get("device_id")
            if not device_id:
                _LOGGER.error("No device ID available for %s", self.entity_description.key)
                return
            
            # Call the API to set the parameter
            success = await self._api_client.async_set_noah_parameter(
                device_id, 
                self.entity_description.key, 
                int(value)
            )
            
            if success:
                # Update the local value
                self._default_values[self.entity_description.key] = value
                self.async_write_ha_state()
                
                # Request a refresh to get updated values
                await self.coordinator.async_request_refresh()
                
                _LOGGER.info("Successfully set %s to %s", self.entity_description.key, value)
            else:
                _LOGGER.error("Failed to set %s to %s", self.entity_description.key, value)
                
        except Exception as err:
            _LOGGER.error("Error setting %s to %s: %s", self.entity_description.key, value, err)
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            super().available and 
            self.coordinator.data is not None and
            hasattr(self.coordinator.data, 'system') and
            self.coordinator.data.system.status not in ["Offline", "Error", "Unknown"]
        )
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        attrs = {
            "last_update": self.coordinator.data.timestamp.isoformat(),
            "note": "Control functionality not yet implemented",
        }
        
        # Add relevant current status
        if self.entity_description.key in ["battery_charge_limit", "battery_discharge_limit"]:
            attrs["current_soc"] = f"{self.coordinator.data.battery.soc}%"
        
        elif self.entity_description.key in ["max_charge_power", "max_discharge_power"]:
            attrs["current_power"] = f"{self.coordinator.data.battery.power} W"
        
        return attrs