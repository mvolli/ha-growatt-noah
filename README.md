# Growatt Noah 2000 & Neo 800 Integration for Home Assistant

A comprehensive Home Assistant integration for monitoring Growatt Noah 2000 battery systems and Neo 800 micro-inverters.

## Features

- **Dual Device Support**: Monitor both Noah 2000 battery systems and Neo 800 micro-inverters
- **Multiple Connection Types**: API, MQTT, Modbus TCP, and Modbus RTU
- **Comprehensive Monitoring**: 40+ sensors covering battery, solar, grid, and system metrics
- **HACS Compatible**: Easy installation through Home Assistant Community Store

## Supported Devices

### Noah 2000 (Battery System)
- Battery: State of charge, voltage, current, power, temperature, health
- Solar: Power generation, voltage, current, daily/total energy
- Grid: Import/export power and energy, voltage, frequency
- Load: Power consumption, daily/total energy
- System: Status, mode, firmware version, error codes

### Neo 800 (Micro-Inverter)
- PV Panels: Dual MPPT monitoring (PV1 & PV2 voltage, current, power)
- Solar: Total power generation, daily/total energy
- Grid: Output power, voltage, frequency, energy export
- Inverter: Temperature, power factor, derating mode
- System: Status, fault codes, warning codes, firmware version

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click "Integrations"
3. Click the three dots in the top right
4. Select "Custom repositories"
5. Add `https://github.com/mvolli/ha-growatt-noah` as repository
6. Select "Integration" as category
7. Click "Add"
8. Search for "Growatt Noah 2000 & Neo 800"
9. Click "Install"
10. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Copy `custom_components/growatt_noah` to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services → Add Integration
2. Search for "Growatt Noah 2000 & Neo 800"
3. Select your device type (Noah 2000 or Neo 800)
4. Choose connection method:

### Connection Methods

#### 🌐 API Connection
- **Requirements**: Growatt account credentials
- **Limitations**: ⚠️ **API access restricted for individual users as of 2024**
- **Use cases**: If you have installer account or API access approval from Growatt
- **Configuration**: Username, password, optional plant ID

#### 📡 MQTT Connection (Recommended)
- **Requirements**: MQTT broker, device publishing data
- **Benefits**: Local communication, real-time updates
- **Use cases**: When device publishes to local MQTT broker
- **Configuration**: MQTT broker, credentials, topic prefix

#### 🔌 Modbus TCP/RTU (Best for Local)
- **Requirements**: Direct network/serial connection to device
- **Benefits**: Direct local communication, most reliable
- **Use cases**: Local network access to device
- **Configuration**: IP address/serial port, device ID

## API Access Important Notes

⚠️ **Growatt API Limitations (2024)**:
- Individual user accounts **cannot directly access** the Growatt API
- API access requires **installer account approval** from Growatt
- Existing API keys for individual users are being **phased out**
- **Recommended alternatives**: MQTT or Modbus connections for local access

For API access, you need:
1. Installer account at https://oss.growatt.com/login
2. Approval request submitted to Growatt
3. Official API credentials provided by Growatt

## Device Compatibility

### Tested Devices
- ✅ Growatt Noah 2000 Battery System
- ✅ Growatt Neo 800M-X Micro-Inverter

### Communication Protocols
- ✅ Growatt Cloud API (with proper credentials)
- ✅ MQTT over TLS (Neo 800 native protocol)
- ✅ Modbus RTU/TCP (standard industrial protocol)

## Troubleshooting

### API Connection Issues
- **Error**: "Permission denied" or "error_code: 10011"
  - **Solution**: Use MQTT or Modbus connection instead
  - **Reason**: Individual API access restricted

### MQTT Connection Issues
- **Check**: MQTT broker accessibility and credentials
- **Verify**: Device is publishing to specified topics
- **Topics**: `{prefix}/status`, `{prefix}/solar`, `{prefix}/battery`, etc.

### Modbus Connection Issues
- **TCP**: Verify IP address and port (default 502)
- **RTU**: Check serial port, baudrate, and device ID
- **Registers**: Ensure device supports Modbus communication

## Advanced Configuration

### Multiple Devices
To monitor multiple devices, add separate integration instances for each device with unique configurations.

### Custom Scan Intervals
Adjust polling frequency based on your needs:
- **Fast**: 10-30 seconds (local connections)
- **Normal**: 30-60 seconds (API/MQTT)
- **Slow**: 60-300 seconds (limited API access)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

- **Issues**: [GitHub Issues](https://github.com/mvolli/ha-growatt-noah/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mvolli/ha-growatt-noah/discussions)
- **Home Assistant**: [Community Forum](https://community.home-assistant.io/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Note**: This integration is not affiliated with Growatt. Use at your own risk and ensure compliance with your device warranty and local regulations.