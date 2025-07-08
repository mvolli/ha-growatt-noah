"""Binary sensor platform for Growatt Noah 2000."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory

from . import NoahDataUpdateCoordinator
from .const import DOMAIN
from .models import NoahData

# Define binary sensor entities
BINARY_SENSORS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="grid_connected",
        name="Grid Connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        icon="mdi:transmission-tower",
    ),
    BinarySensorEntityDescription(
        key="battery_charging",
        name="Battery Charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        icon="mdi:battery-charging",
    ),
    BinarySensorEntityDescription(
        key="solar_generating",
        name="Solar Generating",
        device_class=BinarySensorDeviceClass.POWER,
        icon="mdi:solar-power",
    ),
    BinarySensorEntityDescription(
        key="system_error",
        name="System Error",
        device_class=BinarySensorDeviceClass.PROBLEM,
        icon="mdi:alert-circle",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinarySensorEntityDescription(
        key="battery_low",
        name="Battery Low",
        device_class=BinarySensorDeviceClass.BATTERY,
        icon="mdi:battery-low",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the binary sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    entities = []
    for description in BINARY_SENSORS:
        entities.append(NoahBinarySensor(coordinator, description, entry))
    
    async_add_entities(entities)


class NoahBinarySensor(CoordinatorEntity[NoahDataUpdateCoordinator], BinarySensorEntity):
    """Representation of a Noah binary sensor."""
    
    def __init__(
        self,
        coordinator: NoahDataUpdateCoordinator,
        description: BinarySensorEntityDescription,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        
        self.entity_description = description
        self._attr_unique_id = f"noah2000_{description.key}"
        self._attr_object_id = f"noah2000_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Growatt Noah 2000",
            "manufacturer": "Growatt",
            "model": "Noah 2000",
            "sw_version": self._get_firmware_version(),
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
        """Return the state of the binary sensor."""
        if not self.coordinator.data:
            return None
        
        data: NoahData = self.coordinator.data
        
        # Map binary sensor keys to boolean conditions
        if self.entity_description.key == "grid_connected":
            return data.grid.grid_connected
        
        elif self.entity_description.key == "battery_charging":
            return data.battery.power > 0  # Positive power = charging
        
        elif self.entity_description.key == "solar_generating":
            return data.solar.power > 10  # Consider > 10W as generating
        
        elif self.entity_description.key == "system_error":
            return data.system.error_code is not None and data.system.error_code != 0
        
        elif self.entity_description.key == "battery_low":
            return data.battery.soc < 20  # Consider < 20% as low
        
        return None
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        data: NoahData = self.coordinator.data
        
        attrs = {
            "last_update": data.timestamp.isoformat(),
        }
        
        # Add specific attributes based on sensor type
        if self.entity_description.key == "battery_charging":
            attrs["battery_power"] = f"{data.battery.power} W"
            attrs["battery_soc"] = f"{data.battery.soc}%"
        
        elif self.entity_description.key == "solar_generating":
            attrs["solar_power"] = f"{data.solar.power} W"
            attrs["energy_today"] = f"{data.solar.energy_today} kWh"
        
        elif self.entity_description.key == "system_error" and data.system.error_code:
            attrs["error_code"] = data.system.error_code
            if data.system.error_message:
                attrs["error_message"] = data.system.error_message
        
        elif self.entity_description.key == "battery_low":
            attrs["battery_soc"] = f"{data.battery.soc}%"
            attrs["low_threshold"] = "20%"
        
        return attrs