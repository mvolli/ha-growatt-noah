# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2024-12-XX

### 🚀 Major Refactoring
- **Raspberry Pi Optimization**: Reduced codebase by 67% for better performance
- **Noah 2000 Focus**: Removed unused Neo 800 inverter support
- **API-Only Connection**: Streamlined to only support Growatt Cloud API
- **Dependencies Minimized**: Only requires `aiohttp` (was 4 dependencies, now 1)

### ✅ Enhanced Features
- **Energy Dashboard Ready**: Added battery energy sensors for HA energy dashboard
- **Sensor Naming Convention**: All sensors now use `sensor.noah2000.{name}` format
- **Real-time Data**: Direct Noah API integration with actual battery data
- **Working Battery Energy**: Power-based integration for charge/discharge energy tracking

### 🔋 Battery Energy Sensors
- `sensor.noah2000.battery_charge_power` - Real charging power from Noah API
- `sensor.noah2000.battery_discharge_power` - Real discharging power from Noah API
- Integration sensors for daily energy totals via Home Assistant helpers

### 🧹 Code Cleanup
- Removed all MQTT functionality (unused for Noah 2000)
- Removed all Modbus functionality (unused for Noah 2000) 
- Removed Neo 800 inverter support (user only has Noah 2000)
- Removed test functions and development code
- Streamlined data models and API calls

### 📚 Documentation Updates
- Updated README to focus exclusively on Noah 2000
- Added complete energy dashboard setup guide
- Included all sensor names and configuration examples
- Removed references to unsupported connection methods

### 🛠️ Technical Improvements
- Fixed EntityCategory import errors across all platforms
- Enhanced session management with cookie support
- Improved error handling and debugging
- Optimized data polling (30-second intervals)

## [1.0.0] - 2024-07-04

### Added
- Initial release of Growatt Noah 2000 Home Assistant integration
- Growatt Cloud API connection support
- Comprehensive sensor coverage (25+ sensors):
  - Battery monitoring (SoC, power, voltage, current, temperature)
  - Solar generation tracking (power, energy)
  - Grid status monitoring (import/export, power)
  - Load consumption calculations
  - System status and diagnostics
- Binary sensors for status indicators:
  - Grid connection status
  - Battery charging/discharging
  - Solar generation active
  - System errors
  - Battery low warnings
- Configuration flow for easy setup through Home Assistant UI
- Device discovery and organization
- HACS integration support

### Technical Features
- Async/await throughout for non-blocking operation
- Automatic authentication and session management
- Configurable update intervals
- Type hints and proper error handling
- Home Assistant 2023.1+ compatibility

### Documentation
- Complete installation guide
- Energy dashboard configuration
- Sensor documentation with examples
- Troubleshooting guide