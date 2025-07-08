# Growatt Noah 2000 Integration for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

A comprehensive Home Assistant integration for monitoring Growatt Noah 2000 battery systems with optimized code for Raspberry Pi deployment.

## Features

- **Noah 2000 Support**: Complete monitoring of Noah 2000 battery systems
- **API Connection**: Growatt Cloud API integration with real-time data
- **Energy Dashboard Ready**: Battery energy sensors for HA energy dashboard
- **Optimized Performance**: Slim codebase designed for Raspberry Pi
- **HACS Compatible**: Easy installation through Home Assistant Community Store

## Supported Device

### Noah 2000 (Battery System)
- **Battery**: State of charge, voltage, current, power, temperature, status
- **Solar**: Power generation, voltage, current, daily/total energy
- **Grid**: Import/export power and energy, voltage, frequency
- **Load**: Power consumption calculations
- **System**: Status, mode, firmware version, work modes
- **Energy Tracking**: Battery charge/discharge energy for energy dashboard

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click "Integrations"
3. Click the three dots in the top right
4. Select "Custom repositories"
5. Add `https://github.com/mvolli/ha-growatt-noah` as repository
6. Select "Integration" as category
7. Click "Add"
8. Search for "Growatt Noah 2000"
9. Click "Install"
10. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Copy `custom_components/growatt_noah` to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services → Add Integration
2. Search for "Growatt Noah 2000"
3. Enter your Growatt account credentials
4. Provide your Noah 2000 device serial number

### Connection Method

#### 🌐 API Connection
- **Requirements**: Growatt account credentials and device serial number
- **Benefits**: Real-time data directly from Growatt Cloud
- **Configuration**: Username, password, device serial number
- **Data Update**: Every 30 seconds with real Noah data

## Energy Dashboard Setup

This integration provides battery energy sensors for Home Assistant's energy dashboard:

### Step 1: Install Integration
Install and configure the Noah 2000 integration as described above.

### Step 2: Add Energy Integration to configuration.yaml
```yaml
sensor:
  # Battery Energy Charged Today
  - platform: integration
    source: sensor.noah2000_battery_charge_power
    name: "Noah2000 Battery Energy Charged Today"
    unique_id: "noah2000_battery_energy_charged_today"
    unit_prefix: k
    round: 3
    method: left
    
  # Battery Energy Discharged Today
  - platform: integration
    source: sensor.noah2000_battery_discharge_power
    name: "Noah2000 Battery Energy Discharged Today"
    unique_id: "noah2000_battery_energy_discharged_today"
    unit_prefix: k
    round: 3
    method: left

# Daily reset
utility_meter:
  noah2000_battery_charged_daily:
    source: sensor.noah2000_battery_energy_charged_today
    cycle: daily
    name: "Noah2000 Battery Charged Daily"
    
  noah2000_battery_discharged_daily:
    source: sensor.noah2000_battery_energy_discharged_today  
    cycle: daily
    name: "Noah2000 Battery Discharged Daily"
```

### Step 3: Configure Energy Dashboard

#### Option A: Use Native Energy Sensors (Recommended)
1. Go to Settings → Dashboards → Energy
2. Add Battery System
3. **Energy into battery**: `sensor.noah2000_battery_energy_charged_today`
4. **Energy from battery**: `sensor.noah2000_battery_energy_discharged_today`

#### Option B: Use Integration Sensors (Alternative)
If you prefer to use the integration method, use:
3. **Energy into battery**: `sensor.noah2000_battery_charged_daily`
4. **Energy from battery**: `sensor.noah2000_battery_discharged_daily`

## Available Sensors

All sensors use the naming format: `sensor.noah2000_{sensor_name}`

### Battery Sensors
- `sensor.noah2000_battery_soc` - State of Charge (%)
- `sensor.noah2000_battery_power` - Net Battery Power (W)
- `sensor.noah2000_battery_charge_power` - Charging Power (W)
- `sensor.noah2000_battery_discharge_power` - Discharging Power (W)
- `sensor.noah2000_battery_energy_charged_today` - Energy Charged Today (kWh) ⚡ **Energy Dashboard Ready**
- `sensor.noah2000_battery_energy_discharged_today` - Energy Discharged Today (kWh) ⚡ **Energy Dashboard Ready**
- `sensor.noah2000_battery_voltage` - Battery Voltage (V)
- `sensor.noah2000_battery_current` - Battery Current (A)
- `sensor.noah2000_battery_temperature` - Temperature (°C)
- `sensor.noah2000_battery_status` - Status (Charging/Discharging/Idle)

### Solar Sensors
- `sensor.noah2000_solar_power` - Solar Power (W)
- `sensor.noah2000_solar_energy_today` - Solar Energy Today (kWh)
- `sensor.noah2000_solar_energy_total` - Total Solar Energy (kWh)

### Grid Sensors
- `sensor.noah2000_grid_power` - Grid Power (W)
- `sensor.noah2000_grid_energy_exported_today` - Grid Export Today (kWh)
- `sensor.noah2000_grid_energy_exported_total` - Total Grid Export (kWh)

### System Sensors
- `sensor.noah2000_system_status` - System Status
- `sensor.noah2000_system_mode` - Work Mode
- `sensor.noah2000_load_power` - Load Power (W)

## Performance Optimization

This integration is optimized for Raspberry Pi deployment:
- **Minimal Dependencies**: Only requires `aiohttp`
- **Efficient API Calls**: Single endpoint with comprehensive data
- **Smart Session Management**: Cookie-based authentication
- **Reduced Memory Usage**: Streamlined data models

## Troubleshooting

### API Connection Issues

#### Error 507 - API Temporarily Unavailable
- **Issue**: `Login failed: 507` in logs
- **Cause**: Growatt server-side issues or temporary outages
- **Solution**: Wait and retry - integration will automatically retry with fallback servers
- **Note**: This is a Growatt server issue, not an integration problem

#### Authentication Failed
- **Error**: Authentication failed
- **Solution**: Verify Growatt account credentials
- **Check**: Device serial number is correct
- **Tip**: Try logging into https://server.growatt.com/ manually to verify credentials

### Template Errors in Automations

#### Solar Power Sensor Not Found
- **Error**: `Template error: round got invalid input 'unknown'` with `sensor.solar_power`
- **Issue**: Automation references wrong entity ID
- **Solution**: Update your automation to use correct entity ID:
  ```yaml
  # Wrong:
  "{{ states('sensor.solar_power') | round(0) }}W"
  
  # Correct:
  "{{ states('sensor.noah2000_solar_power') | round(0, default=0) }}W"
  ```
- **Note**: All Noah 2000 sensors use the prefix `sensor.noah2000_`

### Missing Energy Sensors
- **Issue**: Battery energy sensors not appearing
- **Solution**: Add the integration sensors to configuration.yaml
- **Restart**: Home Assistant after configuration changes

### Performance Issues
- **Slow Updates**: Check network connectivity to Growatt Cloud
- **High CPU**: Ensure only Noah 2000 integration is running
- **Rate Limiting**: Integration includes automatic rate limiting to prevent IP blocking

## Device Compatibility

### Tested Devices
- ✅ Growatt Noah 2000 Battery System

### API Compatibility
- ✅ Growatt Cloud API v2.0
- ✅ Noah System Status endpoint
- ✅ Real-time data retrieval

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

[buymecoffee]: https://www.buymeacoffee.com/mvolli
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/mvolli/ha-growatt-noah.svg?style=for-the-badge
[commits]: https://github.com/mvolli/ha-growatt-noah/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/mvolli/ha-growatt-noah.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40mvolli-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/mvolli/ha-growatt-noah.svg?style=for-the-badge
[releases]: https://github.com/mvolli/ha-growatt-noah/releases