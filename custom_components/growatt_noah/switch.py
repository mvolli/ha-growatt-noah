"""Switch platform for Growatt Noah 2000."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory

from . import NoahDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Define switch entities (for devices that support control)
SWITCHES: tuple[SwitchEntityDescription, ...] = (
    SwitchEntityDescription(
        key="battery_charge_enable",
        name="Battery Charge Enable",
        icon="mdi:battery-charging",
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key="battery_discharge_enable",
        name="Battery Discharge Enable",
        icon="mdi:battery-minus",
        entity_category=EntityCategory.CONFIG,
    ),
    SwitchEntityDescription(
        key="grid_export_enable",
        name="Grid Export Enable",
        icon="mdi:transmission-tower-export",
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the switch platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api_client = hass.data[DOMAIN][entry.entry_id]["api"]
    
    entities = []
    for description in SWITCHES:
        entities.append(NoahSwitch(coordinator, description, entry, api_client))
    
    async_add_entities(entities)


class NoahSwitch(CoordinatorEntity[NoahDataUpdateCoordinator], SwitchEntity):
    """Representation of a Noah switch."""
    
    def __init__(
        self,
        coordinator: NoahDataUpdateCoordinator,
        description: SwitchEntityDescription,
        entry: ConfigEntry,
        api_client,
    ) -> None:
        """Initialize the switch."""
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
    
    def _get_firmware_version(self) -> str | None:
        """Safely get firmware version from coordinator data."""
        try:
            if self.coordinator.data and hasattr(self.coordinator.data, 'system'):
                return getattr(self.coordinator.data.system, 'firmware_version', None)
        except Exception:
            pass
        return None
    
    @property
    def is_on(self) -> bool | None:
        """Return the state of the switch."""
        if not self.coordinator.data:
            return None
        
        # Note: These are placeholder implementations
        # Actual implementation would depend on the device's actual API/control capabilities
        # For now, these switches will be read-only status indicators
        
        data = self.coordinator.data
        
        if self.entity_description.key == "battery_charge_enable":
            # Could be determined by system mode or specific settings
            return data.system.mode in ["Auto", "Charge"]
        
        elif self.entity_description.key == "battery_discharge_enable":
            # Could be determined by system mode or specific settings
            return data.system.mode in ["Auto", "Discharge"]
        
        elif self.entity_description.key == "grid_export_enable":
            # Could be determined by grid power flow
            return data.grid.power < 0  # Negative power = exporting
        
        return None
    
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        try:
            device_id = self._entry.data.get("device_id")
            if not device_id:
                _LOGGER.error("No device ID available for %s", self.entity_description.key)
                return
            
            success = await self._api_client.async_set_noah_parameter(
                device_id, 
                self.entity_description.key, 
                True
            )
            
            if success:
                await self.coordinator.async_request_refresh()
                _LOGGER.info("Successfully turned on %s", self.entity_description.key)
            else:
                _LOGGER.error("Failed to turn on %s", self.entity_description.key)
                
        except Exception as err:
            _LOGGER.error("Error turning on %s: %s", self.entity_description.key, err)
    
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        try:
            device_id = self._entry.data.get("device_id")
            if not device_id:
                _LOGGER.error("No device ID available for %s", self.entity_description.key)
                return
            
            success = await self._api_client.async_set_noah_parameter(
                device_id, 
                self.entity_description.key, 
                False
            )
            
            if success:
                await self.coordinator.async_request_refresh()
                _LOGGER.info("Successfully turned off %s", self.entity_description.key)
            else:
                _LOGGER.error("Failed to turn off %s", self.entity_description.key)
                
        except Exception as err:
            _LOGGER.error("Error turning off %s: %s", self.entity_description.key, err)
    
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
        
        return {
            "last_update": self.coordinator.data.timestamp.isoformat(),
            "note": "Control functionality not yet implemented",
        }