# Contributing to Growatt Noah 2000 Integration

Thank you for your interest in contributing! This project aims to provide the most comprehensive and reliable Home Assistant integration for Growatt Noah 2000 battery systems.

## How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use the issue templates** when available
3. **Provide detailed information:**
   - Home Assistant version
   - Integration version
   - Connection method (API/MQTT/Modbus)
   - Device firmware version
   - Complete error logs
   - Steps to reproduce

### Suggesting Features

1. Check if the feature already exists or is planned
2. Explain the use case and why it would be valuable
3. Consider if it should be part of this integration or a separate component

### Code Contributions

#### Development Setup

1. Fork the repository
2. Create a development branch: `git checkout -b feature/your-feature`
3. Set up a test Home Assistant instance
4. Install the integration in development mode

#### Code Standards

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints throughout the code
- Add docstrings to all public methods
- Keep functions focused and small
- Use meaningful variable and function names

#### Testing

- Test your changes with real hardware when possible
- Test all connection methods (API, MQTT, Modbus TCP/RTU)
- Verify that entities are created correctly
- Check that data updates work as expected
- Test error conditions and edge cases

#### Submitting Changes

1. Ensure all tests pass
2. Update documentation if needed
3. Add your changes to the changelog
4. Create a pull request with a clear description
5. Link any related issues

## Development Guidelines

### Adding New Sensors

1. Add the sensor description to `sensor.py`
2. Map the data field in the `native_value` property
3. Add appropriate device class and units
4. Test with different data sources

### Adding New Connection Methods

1. Extend the `GrowattNoahAPI` class in `api.py`
2. Add configuration options to `config_flow.py`
3. Update the manifest requirements if needed
4. Add documentation and examples

### Modifying Data Models

1. Update the appropriate dataclass in `models.py`
2. Ensure all data sources can populate the fields
3. Consider backward compatibility
4. Update related sensors and entities

### Error Handling

- Always handle connection failures gracefully
- Provide meaningful error messages to users
- Log detailed information for debugging
- Don't crash Home Assistant on errors

## Specific Areas Needing Help

### 1. Device Control Implementation

The integration currently focuses on monitoring. We need:
- Implementation of parameter setting via API/Modbus
- Control switches for charge/discharge modes
- Configuration numbers for limits and settings

### 2. Modbus Register Mapping

Different firmware versions may use different registers:
- Document register mappings for various firmware versions
- Add auto-detection if possible
- Provide configuration options for custom mappings

### 3. MQTT Integration Enhancement

- Support for different MQTT topic structures
- Better integration with noah-mqtt project
- MQTT autodiscovery improvements

### 4. Testing and Validation

- Unit tests for data parsing
- Integration tests with mock devices
- Validation with different device configurations

## Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Home Assistant Architecture](https://developers.home-assistant.io/docs/architecture/)
- [Integration Quality Scale](https://developers.home-assistant.io/docs/integration_quality_scale_index/)
- [Growatt Official Documentation](https://www.growatt.com/)

## Community

- Join discussions in GitHub issues
- Help other users with their setups
- Share your configuration examples
- Report successful hardware combinations

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Recognition

Contributors will be:
- Listed in the project README
- Mentioned in release notes for significant contributions
- Credited in code comments where appropriate

Thank you for helping make this integration better for everyone!