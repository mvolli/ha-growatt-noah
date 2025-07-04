# Growatt Noah 2000 Home Assistant Integration

A comprehensive Home Assistant integration for the Growatt Noah 2000 Solar Battery system.

## Features

- 🔋 Real-time battery monitoring (SoC, power, temperature)
- ☀️ Solar generation tracking
- ⚡ Power consumption and grid status
- 🏠 Energy management and statistics
- 🔧 Easy configuration through Home Assistant UI
- 🌐 Multiple data source support (API, MQTT, Modbus)
- 📊 Historical data and energy analytics

## Supported Data Points

### Battery Information
- State of Charge (%)
- Battery voltage and current
- Battery temperature
- Charging/discharging power
- Battery health status

### Solar Generation
- Current solar power generation
- Daily/monthly/yearly energy production
- Solar panel voltage and current
- Weather-dependent efficiency

### Grid & Load
- Grid power consumption/export
- Load power consumption
- Grid voltage and frequency
- Energy costs and savings

### System Status
- Device connectivity status
- Error codes and alerts
- Operational mode
- Firmware version

## Installation

### HACS (Recommended)
1. Install HACS if not already installed
2. Add this repository as a custom repository in HACS
3. Install the "Growatt Noah 2000" integration
4. Restart Home Assistant
5. Configure the integration via UI

### Manual Installation
1. Copy the `growatt_noah` folder to your `custom_components` directory
2. Restart Home Assistant
3. Configure the integration via UI

## Configuration

The integration supports multiple connection methods:

### Method 1: Growatt Cloud API
- Easiest setup
- Requires Growatt account credentials
- May have rate limits

### Method 2: Local MQTT (Recommended)
- Fastest updates
- Requires MQTT broker
- Most reliable for local network

### Method 3: Direct Modbus TCP/RTU
- Direct device communication
- Fastest response times
- Requires network/serial access to device

## Quick Start

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "Growatt Noah 2000"
4. Choose your connection method
5. Enter required credentials/settings
6. Enjoy your solar battery monitoring!

## Supported Models

- Growatt Noah 2000
- Other Growatt battery systems (limited support)

## Project Structure

```
ha-noah/
├── custom_components/growatt_noah/    # Main integration code
│   ├── __init__.py                    # Integration setup and coordinator
│   ├── manifest.json                  # Integration metadata
│   ├── config_flow.py                 # Configuration UI flow
│   ├── const.py                       # Constants and configuration
│   ├── models.py                      # Data models and parsing
│   ├── api.py                         # API clients for all connection methods
│   ├── sensor.py                      # Sensor entities (power, energy, etc.)
│   ├── binary_sensor.py               # Binary sensors (status indicators)
│   ├── switch.py                      # Control switches (future implementation)
│   ├── number.py                      # Configuration numbers (future implementation)
│   └── translations/en.json           # UI text translations
├── docs/                              # Documentation
│   ├── installation.md                # Installation guide
│   └── troubleshooting.md             # Troubleshooting guide
├── tests/                             # Unit tests
├── example_configurations.yaml        # Example HA configurations
└── README.md                          # This file
```

## Current Status

✅ **Working Features:**
- Multiple connection methods (API, MQTT, Modbus TCP/RTU)
- Comprehensive sensor coverage (20+ sensors)
- Binary sensors for status monitoring
- Easy configuration through Home Assistant UI
- Energy dashboard integration
- Device discovery and organization

🚧 **In Development:**
- Control functionality (switches and numbers)
- Advanced configuration options
- Better error handling and diagnostics

📋 **Planned Features:**
- Firmware update notifications
- Advanced automation triggers
- Historical data analysis
- Energy cost calculations

## Compatibility

- **Home Assistant:** 2023.1.0 or later
- **Python:** 3.10 or later
- **Noah 2000 Firmware:** All known versions
- **Connection Methods:** API, MQTT, Modbus TCP/RTU

## Performance

- **Update Interval:** Configurable (default: 30 seconds)
- **Resource Usage:** Minimal CPU and memory impact
- **Network Traffic:** Optimized for local connections
- **Reliability:** Automatic reconnection and error recovery

## Troubleshooting

See the [Troubleshooting Guide](docs/troubleshooting.md) for common issues and solutions.

## Contributing

Contributions are welcome! Please read the [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/VoLLi/ha-growatt-noah/issues)
- 💡 **Feature Requests:** [GitHub Discussions](https://github.com/VoLLi/ha-growatt-noah/discussions)
- 📖 **Documentation:** [docs/](docs/)
- 🤝 **Community:** Home Assistant Community Forum

## Acknowledgments

- [mtrossbach/noah-mqtt](https://github.com/mtrossbach/noah-mqtt) - Inspiration and MQTT bridge
- [Growatt](https://www.growatt.com/) - Device manufacturer
- [Home Assistant](https://www.home-assistant.io/) - The best home automation platform# ha-growatt-noah
