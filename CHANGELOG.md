# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-07-04

### Added
- Initial release of Growatt Noah 2000 Home Assistant integration
- Multiple connection methods support:
  - Growatt Cloud API
  - MQTT (compatible with noah-mqtt bridge)
  - Modbus TCP
  - Modbus RTU
- Comprehensive sensor coverage (20+ sensors):
  - Battery monitoring (SoC, power, voltage, current, temperature)
  - Solar generation tracking (power, energy, efficiency)
  - Grid status monitoring (import/export, voltage, frequency)
  - Load consumption tracking
  - System status and diagnostics
- Binary sensors for status indicators:
  - Grid connection status
  - Battery charging/discharging
  - Solar generation active
  - System errors
  - Battery low warnings
- Configuration flow for easy setup through Home Assistant UI
- Energy dashboard integration
- Device discovery and organization
- Multi-language support (English)
- Comprehensive documentation and examples

### Technical Features
- Async/await throughout for non-blocking operation
- Automatic reconnection and error recovery
- Configurable update intervals
- Type hints and proper error handling
- Home Assistant 2023.1+ compatibility
- HACS integration support

### Documentation
- Complete installation guide
- Troubleshooting documentation
- Example configurations for automations
- Contributing guidelines
- Unit tests for data models

### Future Planned
- Device control functionality (switches and numbers)
- Advanced configuration options
- Firmware update notifications
- Enhanced automation triggers