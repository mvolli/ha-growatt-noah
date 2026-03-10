"""Constants for the Growatt Noah 2000 integration."""
from typing import Final

DOMAIN: Final = "growatt_noah"

# Default configuration
DEFAULT_SCAN_INTERVAL: Final = 300  # seconds (5 min – safe for openapi.growatt.com rate limits)
DEFAULT_TIMEOUT: Final = 10  # seconds

# Connection types - Only API is supported
CONNECTION_TYPE_API: Final = "api"

# Device types - Only Noah 2000 is supported
DEVICE_TYPE_NOAH: Final = "noah_2000"

# Config keys
CONF_API_KEY: Final = "api_key"       # Growatt OpenAPI token (Settings → API Key)
CONF_DEVICE_ID: Final = "device_id"  # Device serial number

