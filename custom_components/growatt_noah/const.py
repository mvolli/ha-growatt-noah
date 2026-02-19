"""Constants for the Growatt Noah 2000 integration."""
from typing import Final

DOMAIN: Final = "growatt_noah"

# Default configuration
DEFAULT_SCAN_INTERVAL: Final = 900  # seconds (15 minutes - conservative to avoid API rate limits)
DEFAULT_TIMEOUT: Final = 10  # seconds

# Connection types - Only API is supported
CONNECTION_TYPE_API: Final = "api"

# Device types - Only Noah 2000 is supported
DEVICE_TYPE_NOAH: Final = "noah_2000"

