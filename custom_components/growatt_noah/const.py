"""Constants for the Growatt Noah 2000 integration."""
from typing import Final

DOMAIN: Final = "growatt_noah"

# Default configuration
DEFAULT_SCAN_INTERVAL: Final = 30  # seconds
DEFAULT_TIMEOUT: Final = 10  # seconds

# Connection types - Only API is supported
CONNECTION_TYPE_API: Final = "api"

# Device types - Only Noah 2000 is supported
DEVICE_TYPE_NOAH: Final = "noah_2000"

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