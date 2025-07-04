"""Data models for Growatt Noah 2000 integration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class BatteryData:
    """Battery information."""
    soc: float  # State of charge (%)
    voltage: float  # Voltage (V)
    current: float  # Current (A)
    power: float  # Power (W)
    temperature: float  # Temperature (°C)
    status: str  # Charging/Discharging/Idle
    health: Optional[float] = None  # Battery health (%)
    capacity: Optional[float] = None  # Total capacity (kWh)
    energy_charged_today: Optional[float] = None  # kWh
    energy_discharged_today: Optional[float] = None  # kWh


@dataclass
class SolarData:
    """Solar generation information."""
    power: float  # Current power (W)
    voltage: float  # Voltage (V)
    current: float  # Current (A)
    energy_today: float  # Energy today (kWh)
    energy_total: float  # Total energy (kWh)
    efficiency: Optional[float] = None  # Efficiency (%)


@dataclass
class GridData:
    """Grid information."""
    power: float  # Grid power (W) - positive = import, negative = export
    voltage: float  # Grid voltage (V)
    frequency: float  # Grid frequency (Hz)
    energy_imported_today: float  # Energy imported today (kWh)
    energy_exported_today: float  # Energy exported today (kWh)
    energy_imported_total: float  # Total energy imported (kWh)
    energy_exported_total: float  # Total energy exported (kWh)
    grid_connected: bool  # Grid connection status


@dataclass
class LoadData:
    """Load consumption information."""
    power: float  # Load power (W)
    energy_today: float  # Energy consumed today (kWh)
    energy_total: float  # Total energy consumed (kWh)


@dataclass
class SystemData:
    """System status information."""
    status: str  # Overall system status
    mode: str  # Operating mode
    error_code: Optional[int] = None  # Error code
    error_message: Optional[str] = None  # Error description
    firmware_version: Optional[str] = None  # Firmware version
    serial_number: Optional[str] = None  # Device serial number
    model: Optional[str] = None  # Device model
    last_update: Optional[datetime] = None  # Last data update


@dataclass
class NoahData:
    """Complete Noah device data."""
    battery: BatteryData
    solar: SolarData
    grid: GridData
    load: LoadData
    system: SystemData
    timestamp: datetime
    
    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> NoahData:
        """Create NoahData from API response."""
        timestamp = datetime.now()
        
        battery = BatteryData(
            soc=data.get("battery_soc", 0),
            voltage=data.get("battery_voltage", 0),
            current=data.get("battery_current", 0),
            power=data.get("battery_power", 0),
            temperature=data.get("battery_temperature", 0),
            status=data.get("battery_status", "Unknown"),
            health=data.get("battery_health"),
            capacity=data.get("battery_capacity"),
            energy_charged_today=data.get("battery_energy_charged_today"),
            energy_discharged_today=data.get("battery_energy_discharged_today"),
        )
        
        solar = SolarData(
            power=data.get("solar_power", 0),
            voltage=data.get("solar_voltage", 0),
            current=data.get("solar_current", 0),
            energy_today=data.get("solar_energy_today", 0),
            energy_total=data.get("solar_energy_total", 0),
            efficiency=data.get("solar_efficiency"),
        )
        
        grid = GridData(
            power=data.get("grid_power", 0),
            voltage=data.get("grid_voltage", 0),
            frequency=data.get("grid_frequency", 50),
            energy_imported_today=data.get("grid_energy_imported_today", 0),
            energy_exported_today=data.get("grid_energy_exported_today", 0),
            energy_imported_total=data.get("grid_energy_imported_total", 0),
            energy_exported_total=data.get("grid_energy_exported_total", 0),
            grid_connected=data.get("grid_connected", True),
        )
        
        load = LoadData(
            power=data.get("load_power", 0),
            energy_today=data.get("load_energy_today", 0),
            energy_total=data.get("load_energy_total", 0),
        )
        
        system = SystemData(
            status=data.get("system_status", "Unknown"),
            mode=data.get("system_mode", "Unknown"),
            error_code=data.get("error_code"),
            error_message=data.get("error_message"),
            firmware_version=data.get("firmware_version"),
            serial_number=data.get("serial_number"),
            model=data.get("model", "Noah 2000"),
            last_update=timestamp,
        )
        
        return cls(
            battery=battery,
            solar=solar,
            grid=grid,
            load=load,
            system=system,
            timestamp=timestamp,
        )
    
    @classmethod
    def from_mqtt_data(cls, topics_data: dict[str, Any]) -> NoahData:
        """Create NoahData from MQTT topic data."""
        # Combine data from different MQTT topics
        combined_data = {}
        for topic, data in topics_data.items():
            if isinstance(data, dict):
                combined_data.update(data)
        
        return cls.from_api_response(combined_data)
    
    @classmethod
    def from_modbus_data(cls, registers: dict[str, Any]) -> NoahData:
        """Create NoahData from Modbus register data."""
        # Map register values to standard data format
        mapped_data = {
            "battery_soc": registers.get("battery_soc", 0),
            "battery_voltage": registers.get("battery_voltage", 0) / 100,  # Scale factor
            "battery_current": registers.get("battery_current", 0) / 100,
            "battery_power": registers.get("battery_power", 0),
            "battery_temperature": registers.get("battery_temperature", 0) / 10,
            "solar_power": registers.get("solar_power", 0),
            "solar_voltage": registers.get("solar_voltage", 0) / 100,
            "solar_current": registers.get("solar_current", 0) / 100,
            "grid_power": registers.get("grid_power", 0),
            "grid_voltage": registers.get("grid_voltage", 0) / 100,
            "load_power": registers.get("load_power", 0),
            # Add more mappings as needed
        }
        
        return cls.from_api_response(mapped_data)