"""Sensor platform for Growatt Noah 2000."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NoahDataUpdateCoordinator
from .const import DOMAIN, ENTITY_CATEGORY_DIAGNOSTIC, DEVICE_TYPE_NEO800
from .models import NoahData, Neo800Data

_LOGGER = logging.getLogger(__name__)

# Define all sensor entities
SENSORS: tuple[SensorEntityDescription, ...] = (
    # Battery sensors
    SensorEntityDescription(
        key="battery_soc",
        name="Battery State of Charge",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:battery",
    ),
    SensorEntityDescription(
        key="battery_voltage",
        name="Battery Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        icon="mdi:flash",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="battery_current",
        name="Battery Current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        icon="mdi:current-ac",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="battery_power",
        name="Battery Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:battery-charging",
    ),
    SensorEntityDescription(
        key="battery_temperature",
        name="Battery Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="battery_status",
        name="Battery Status",
        icon="mdi:battery-heart",
    ),
    
    # Solar sensors
    SensorEntityDescription(
        key="solar_power",
        name="Solar Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:solar-power",
    ),
    SensorEntityDescription(
        key="solar_voltage",
        name="Solar Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        icon="mdi:flash",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="solar_current",
        name="Solar Current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        icon="mdi:current-ac",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="solar_energy_today",
        name="Solar Energy Today",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:solar-power",
    ),
    SensorEntityDescription(
        key="solar_energy_total",
        name="Solar Energy Total",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:solar-power",
    ),
    
    # Grid sensors
    SensorEntityDescription(
        key="grid_power",
        name="Grid Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:transmission-tower",
    ),
    SensorEntityDescription(
        key="grid_voltage",
        name="Grid Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        icon="mdi:flash",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="grid_frequency",
        name="Grid Frequency",
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        icon="mdi:sine-wave",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="grid_energy_imported_today",
        name="Grid Energy Imported Today",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:transmission-tower-import",
    ),
    SensorEntityDescription(
        key="grid_energy_exported_today",
        name="Grid Energy Exported Today",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:transmission-tower-export",
    ),
    SensorEntityDescription(
        key="grid_energy_imported_total",
        name="Grid Energy Imported Total",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:transmission-tower-import",
    ),
    SensorEntityDescription(
        key="grid_energy_exported_total",
        name="Grid Energy Exported Total",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:transmission-tower-export",
    ),
    
    # Load sensors
    SensorEntityDescription(
        key="load_power",
        name="Load Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:home-lightning-bolt",
    ),
    SensorEntityDescription(
        key="load_energy_today",
        name="Load Energy Today",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:home-lightning-bolt",
    ),
    SensorEntityDescription(
        key="load_energy_total",
        name="Load Energy Total",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        icon="mdi:home-lightning-bolt",
    ),
    
    # System sensors
    SensorEntityDescription(
        key="system_status",
        name="System Status",
        icon="mdi:information",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="system_mode",
        name="System Mode",
        icon="mdi:cog",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="firmware_version",
        name="Firmware Version",
        icon="mdi:chip",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
)

# Neo 800 specific sensors (for inverter-only functionality)
NEO800_SENSORS: tuple[SensorEntityDescription, ...] = (
    # PV1 sensors
    SensorEntityDescription(
        key="pv1_voltage",
        name="PV1 Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        icon="mdi:flash",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="pv1_current",
        name="PV1 Current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        icon="mdi:current-ac",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="pv1_power",
        name="PV1 Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:solar-panel",
    ),
    
    # PV2 sensors
    SensorEntityDescription(
        key="pv2_voltage",
        name="PV2 Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        icon="mdi:flash",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="pv2_current",
        name="PV2 Current",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        icon="mdi:current-ac",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="pv2_power",
        name="PV2 Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        icon="mdi:solar-panel",
    ),
    
    # Inverter specific sensors
    SensorEntityDescription(
        key="inverter_temperature",
        name="Inverter Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="power_factor",
        name="Power Factor",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="derating_mode",
        name="Derating Mode",
        icon="mdi:speedometer",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="fault_codes",
        name="Fault Codes",
        icon="mdi:alert-circle",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="warning_codes",
        name="Warning Codes",
        icon="mdi:alert",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the sensor platform."""
    try:
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        device_type = entry.data.get("device_type", "noah_2000")
        
        entities = []
        
        # Determine which sensors to create based on device type
        if device_type == DEVICE_TYPE_NEO800:
            # For Neo 800, use common sensors (excluding battery) plus Neo-specific sensors
            sensor_descriptions = [s for s in SENSORS if not s.key.startswith("battery_")] + list(NEO800_SENSORS)
        else:
            # For Noah 2000, use all standard sensors
            sensor_descriptions = SENSORS
        
        for description in sensor_descriptions:
            try:
                entities.append(NoahSensor(coordinator, description, entry))
            except Exception as err:
                _LOGGER.error("Failed to create sensor %s: %s", description.key, err)
                # Continue with other sensors
        
        if entities:
            async_add_entities(entities)
        else:
            _LOGGER.warning("No sensors could be created")
            
    except Exception as err:
        _LOGGER.error("Failed to set up sensor platform: %s", err)
        raise


class NoahSensor(CoordinatorEntity[NoahDataUpdateCoordinator], SensorEntity):
    """Representation of a Noah sensor."""
    
    def __init__(
        self,
        coordinator: NoahDataUpdateCoordinator,
        description: SensorEntityDescription,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        device_type = entry.data.get("device_type", "noah_2000")
        device_name = "Growatt Neo 800" if device_type == DEVICE_TYPE_NEO800 else "Growatt Noah 2000"
        device_model = "Neo 800" if device_type == DEVICE_TYPE_NEO800 else "Noah 2000"
        
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": device_name,
            "manufacturer": "Growatt",
            "model": device_model,
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
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        data = self.coordinator.data
        
        # Handle both NoahData and Neo800Data
        key_mapping = {}
        
        # Common mappings available for both device types
        key_mapping.update({
            # Solar
            "solar_power": data.solar.power,
            "solar_voltage": data.solar.voltage,
            "solar_current": data.solar.current,
            "solar_energy_today": data.solar.energy_today,
            "solar_energy_total": data.solar.energy_total,
            
            # Grid
            "grid_power": data.grid.power,
            "grid_voltage": data.grid.voltage,
            "grid_frequency": data.grid.frequency,
            "grid_energy_imported_today": data.grid.energy_imported_today,
            "grid_energy_exported_today": data.grid.energy_exported_today,
            "grid_energy_imported_total": data.grid.energy_imported_total,
            "grid_energy_exported_total": data.grid.energy_exported_total,
            
            # System
            "system_status": data.system.status,
            "system_mode": data.system.mode,
            "firmware_version": data.system.firmware_version,
            "inverter_temperature": data.system.inverter_temperature,
            "power_factor": data.system.output_power_factor,
            "derating_mode": data.system.derating_mode,
            "fault_codes": ", ".join(data.system.fault_codes) if data.system.fault_codes else None,
            "warning_codes": ", ".join(data.system.warning_codes) if data.system.warning_codes else None,
            
            # Neo 800 specific PV mappings
            "pv1_voltage": data.solar.pv1_voltage,
            "pv1_current": data.solar.pv1_current,
            "pv1_power": data.solar.pv1_power,
            "pv2_voltage": data.solar.pv2_voltage,
            "pv2_current": data.solar.pv2_current,
            "pv2_power": data.solar.pv2_power,
        })
        
        # Noah 2000 specific mappings (only if data has battery attribute)
        if hasattr(data, 'battery'):
            key_mapping.update({
                "battery_soc": data.battery.soc,
                "battery_voltage": data.battery.voltage,
                "battery_current": data.battery.current,
                "battery_power": data.battery.power,
                "battery_temperature": data.battery.temperature,
                "battery_status": data.battery.status,
            })
        
        # Noah 2000 specific mappings (only if data has load attribute)
        if hasattr(data, 'load'):
            key_mapping.update({
                "load_power": data.load.power,
                "load_energy_today": data.load.energy_today,
                "load_energy_total": data.load.energy_total,
            })
        
        return key_mapping.get(self.entity_description.key)
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        data = self.coordinator.data
        
        # Add common attributes
        attrs = {
            "last_update": data.timestamp.isoformat(),
        }
        
        # Add specific attributes based on sensor type
        if self.entity_description.key.startswith("battery_") and hasattr(data, 'battery'):
            if data.battery.health is not None:
                attrs["health"] = f"{data.battery.health}%"
            if data.battery.capacity is not None:
                attrs["capacity"] = f"{data.battery.capacity} kWh"
        
        elif self.entity_description.key.startswith("solar_") or self.entity_description.key.startswith("pv"):
            if data.solar.efficiency is not None:
                attrs["efficiency"] = f"{data.solar.efficiency}%"
            if data.solar.temperature is not None:
                attrs["inverter_temperature"] = f"{data.solar.temperature}°C"
        
        elif self.entity_description.key.startswith("system_") or self.entity_description.key in ["inverter_temperature", "power_factor", "derating_mode"]:
            if data.system.error_code is not None:
                attrs["error_code"] = data.system.error_code
            if data.system.error_message:
                attrs["error_message"] = data.system.error_message
            if data.system.serial_number:
                attrs["serial_number"] = data.system.serial_number
            if data.system.fault_codes:
                attrs["fault_codes"] = data.system.fault_codes
            if data.system.warning_codes:
                attrs["warning_codes"] = data.system.warning_codes
        
        return attrs