"""Constants for the Growatt Noah 2000 integration."""
from typing import Final

DOMAIN: Final = "growatt_noah"

# Default configuration
DEFAULT_SCAN_INTERVAL: Final = 30  # seconds
DEFAULT_TIMEOUT: Final = 10  # seconds
DEFAULT_PORT_MODBUS: Final = 502
DEFAULT_PORT_MQTT: Final = 1883

# Connection types
CONNECTION_TYPE_API: Final = "api"
CONNECTION_TYPE_MQTT: Final = "mqtt"
CONNECTION_TYPE_MODBUS_TCP: Final = "modbus_tcp"
CONNECTION_TYPE_MODBUS_RTU: Final = "modbus_rtu"

# API endpoints
GROWATT_API_BASE_URL: Final = "https://server.growatt.com"
GROWATT_API_LOGIN: Final = "/login"
GROWATT_API_DEVICE_LIST: Final = "/device/getDeviceList"
GROWATT_API_DEVICE_DATA: Final = "/device/getDeviceData"

# MQTT topics structure
MQTT_TOPIC_STATUS: Final = "status"
MQTT_TOPIC_BATTERY: Final = "battery"
MQTT_TOPIC_SOLAR: Final = "solar"
MQTT_TOPIC_GRID: Final = "grid"
MQTT_TOPIC_LOAD: Final = "load"

# Modbus register addresses (example - need actual Noah 2000 register map)
MODBUS_REGISTERS = {
    # Battery information
    "battery_soc": 1000,
    "battery_voltage": 1001,
    "battery_current": 1002,
    "battery_power": 1003,
    "battery_temperature": 1004,
    
    # Solar information
    "solar_power": 1010,
    "solar_voltage": 1011,
    "solar_current": 1012,
    "solar_energy_today": 1013,
    "solar_energy_total": 1014,
    
    # Grid information
    "grid_power": 1020,
    "grid_voltage": 1021,
    "grid_frequency": 1022,
    "grid_energy_imported": 1023,
    "grid_energy_exported": 1024,
    
    # Load information
    "load_power": 1030,
    "load_energy_today": 1031,
    "load_energy_total": 1032,
    
    # System status
    "device_status": 1040,
    "error_code": 1041,
    "firmware_version": 1042,
}

# Device classes for sensors
DEVICE_CLASS_BATTERY = "battery"
DEVICE_CLASS_ENERGY = "energy"
DEVICE_CLASS_POWER = "power"
DEVICE_CLASS_VOLTAGE = "voltage"
DEVICE_CLASS_CURRENT = "current"
DEVICE_CLASS_TEMPERATURE = "temperature"
DEVICE_CLASS_FREQUENCY = "frequency"

# State classes
STATE_CLASS_MEASUREMENT = "measurement"
STATE_CLASS_TOTAL_INCREASING = "total_increasing"

# Units of measurement
UNIT_PERCENTAGE = "%"
UNIT_VOLT = "V"
UNIT_AMPERE = "A"
UNIT_WATT = "W"
UNIT_KILOWATT = "kW"
UNIT_KILOWATT_HOUR = "kWh"
UNIT_CELSIUS = "°C"
UNIT_HERTZ = "Hz"

# Entity categories
ENTITY_CATEGORY_CONFIG = "config"
ENTITY_CATEGORY_DIAGNOSTIC = "diagnostic"