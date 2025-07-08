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
    temperature: Optional[float] = None  # Inverter temperature (°C)


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
    # Additional system fields
    inverter_temperature: Optional[float] = None  # Inverter temperature (°C)
    output_power_factor: Optional[float] = None  # Output power factor
    derating_mode: Optional[str] = None  # Derating mode status
    fault_codes: Optional[list[str]] = None  # Fault codes
    warning_codes: Optional[list[str]] = None  # Warning codes
    # Noah 2000 specific fields
    charge_power: Optional[float] = None  # Battery charge power (W)
    discharge_power: Optional[float] = None  # Battery discharge power (W)
    work_mode: Optional[int] = None  # Work mode number
    battery_count: Optional[int] = None  # Number of batteries
    profit_today: Optional[float] = None  # Today's profit
    profit_total: Optional[float] = None  # Total profit
    groplug_power: Optional[float] = None  # External device power
    other_power: Optional[float] = None  # Other connected device power


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
            temperature=data.get("inverter_temperature"),
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
            inverter_temperature=data.get("inverter_temperature"),
            output_power_factor=data.get("output_power_factor"),
            derating_mode=data.get("derating_mode"),
            fault_codes=data.get("fault_codes"),
            warning_codes=data.get("warning_codes"),
            # Noah specific fields
            charge_power=data.get("charge_power"),
            discharge_power=data.get("discharge_power"),
            work_mode=data.get("work_mode"),
            battery_count=data.get("battery_count"),
            profit_today=data.get("profit_today"),
            profit_total=data.get("profit_total"),
            groplug_power=data.get("groplug_power"),
            other_power=data.get("other_power"),
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
    
    @classmethod
    def from_comprehensive_data(cls, comprehensive_data: dict[str, Any], battery_data: dict[str, Any]) -> NoahData:
        """Create NoahData from comprehensive Growatt API data."""
        timestamp = datetime.now()
        
        # Extract data from comprehensive response
        noah_status = comprehensive_data.get("noah_status", {})
        noah_info = comprehensive_data.get("noah_info", {}).get("noah", {})
        plant_data = comprehensive_data.get("plant", {})
        device_sn = comprehensive_data.get("device_sn", "")
        
        # Enhanced battery data from comprehensive sources
        battery = BatteryData(
            soc=float(battery_data.get("soc", 0)),
            voltage=float(battery_data.get("battery_voltage", 0)),
            current=float(battery_data.get("battery_current", 0)),
            power=float(battery_data.get("battery_power", 0)),
            temperature=float(battery_data.get("battery_temperature", 25)),
            status=cls._convert_noah_status(battery_data.get("status", True)),
            health=battery_data.get("health"),
            capacity=battery_data.get("capacity") or battery_data.get("rated_capacity"),
            energy_charged_today=battery_data.get("energy_today"),
            energy_discharged_today=battery_data.get("discharge_today"),
        )
        
        # Solar data from Noah status
        solar_power = noah_status.get("ppv", 0)
        solar = SolarData(
            power=float(solar_power),
            voltage=0,  # Not available in Noah API
            current=0,  # Not available in Noah API  
            energy_today=float(noah_status.get("eacToday", 0)),
            energy_total=float(noah_status.get("eacTotal", 0)),
            efficiency=None,
            temperature=None,
        )
        
        # Grid data from Noah status
        grid_power = noah_status.get("pac", 0)  # Export power
        grid = GridData(
            power=float(grid_power),
            voltage=0,  # Not directly available
            frequency=50,  # Default
            energy_imported_today=0,  # Not directly available
            energy_exported_today=float(noah_status.get("eacToday", 0)),
            energy_imported_total=0,  # Not directly available
            energy_exported_total=float(noah_status.get("eacTotal", 0)),
            grid_connected=battery_data.get("status", True),
        )
        
        # Load data (calculated from battery + solar - grid)
        charge_power = float(battery_data.get("charge_power", 0))
        discharge_power = float(battery_data.get("discharge_power", 0))
        load_power = float(solar_power) + discharge_power - charge_power - float(grid_power)
        
        load = LoadData(
            power=max(0, load_power),  # Ensure positive
            energy_today=0,  # Not directly available
            energy_total=0,  # Not directly available
        )
        
        # System data
        work_mode_map = {0: "Load First", 1: "Battery First", 2: "Grid First"}
        work_mode = work_mode_map.get(battery_data.get("work_mode", 0), "Unknown")
        
        system = SystemData(
            status="Online" if battery_data.get("status", True) else "Offline",
            mode=work_mode,
            error_code=None,
            error_message=None,
            firmware_version=battery_data.get("version"),
            serial_number=device_sn,
            model=battery_data.get("model", "Noah 2000"),
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
    
    @staticmethod
    def _convert_noah_status(status: Any) -> str:
        """Convert Noah status to readable string."""
        if isinstance(status, bool):
            return "Online" if status else "Offline"
        elif isinstance(status, (int, float)):
            return "Online" if status > 0 else "Offline"
        else:
            return str(status)

