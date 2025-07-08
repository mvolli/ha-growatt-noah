# 🔋 Enhanced Noah 2000 Integration Setup Guide

## ✅ Integration Status
Your enhanced Noah 2000 integration has been successfully updated with advanced battery management capabilities! 

**Test Results (2025-07-07):**
- ✅ Authentication: Working with mvolli/123456
- ✅ Device Detection: Noah 2000 (SN: 0PVPH6ZR23QT01AX) found
- ✅ Real-time Data: 26% SOC, 283W charging, 744W solar generation
- ✅ System Status: Online, Grid First mode

## 🚀 Home Assistant Setup Steps

### 1. Verify Integration Installation
The integration files are already in place at:
```
custom_components/growatt_noah/
├── __init__.py
├── api.py (enhanced with advanced methods)
├── models.py (updated data models)
├── config_flow.py
├── const.py
├── sensor.py
├── manifest.json (updated with growattServer dependency)
```

### 2. Restart Home Assistant
**Important:** Restart Home Assistant to ensure the new `growattServer>=1.6.0` dependency is installed.

### 3. Integration Configuration

#### Option A: Using the Configuration Flow (Recommended)
1. Go to **Settings > Devices & Services**
2. Click **+ Add Integration**
3. Search for **"Growatt Noah"**
4. Enter your configuration:
   - **Username:** `mvolli`
   - **Password:** `123456`
   - **Device Type:** `Noah 2000`
   - **Connection Type:** `API`
   - **Device ID:** `0PVPH6ZR23QT01AX` (optional, will auto-detect)
   - **Server URL:** `https://openapi.growatt.com/`

#### Option B: YAML Configuration
Add to your `configuration.yaml`:
```yaml
# Growatt Noah 2000 Integration
growatt_noah:
  username: "mvolli"
  password: "123456"
  connection_type: "api"
  device_type: "noah"
  device_id: "0PVPH6ZR23QT01AX"
  server_url: "https://openapi.growatt.com/"
  scan_interval: 30
```

### 4. Enable Debug Logging (if needed)
Add to `configuration.yaml` to troubleshoot:
```yaml
logger:
  default: info
  logs:
    custom_components.growatt_noah: debug
```

## 🔧 Troubleshooting Connection Errors

### If you're still getting connection errors:

#### 1. Check Home Assistant Logs
- Go to **Settings > System > Logs**
- Look for entries containing `growatt_noah`
- Common error patterns:
  - `ModuleNotFoundError: No module named 'growattServer'` → Restart HA
  - `401 Unauthorized` → Check credentials
  - `404 Not Found` → Check device_id
  - `Connection timeout` → Check internet/API status

#### 2. Verify Configuration
Ensure your configuration exactly matches:
- Username: `mvolli`
- Password: `123456`
- Device ID: `0PVPH6ZR23QT01AX`
- Server URL: `https://openapi.growatt.com/`

#### 3. Remove Old Configuration
If you had a previous version:
1. Go to **Settings > Devices & Services**
2. Find any existing "Growatt Noah" integration
3. Click **Delete** to remove it
4. Add the integration again with new configuration

#### 4. Clear Integration Cache
```bash
# In Home Assistant container/system
rm -rf /config/.storage/core.config_entries
# Then restart Home Assistant
```

## 📊 Available Sensors

After successful setup, you'll have these sensors:

### Battery Sensors
- `sensor.noah_battery_soc` - State of Charge (%)
- `sensor.noah_battery_voltage` - Battery Voltage (V)
- `sensor.noah_battery_current` - Battery Current (A)
- `sensor.noah_battery_power` - Battery Power (W)
- `sensor.noah_battery_temperature` - Battery Temperature (°C)
- `sensor.noah_battery_status` - Charging/Discharging status
- `sensor.noah_battery_health` - Battery Health (%)

### Solar Sensors
- `sensor.noah_solar_power` - Current Solar Generation (W)
- `sensor.noah_solar_energy_today` - Today's Solar Energy (kWh)
- `sensor.noah_solar_energy_total` - Total Solar Energy (kWh)

### Grid Sensors
- `sensor.noah_grid_power` - Grid Power (W)
- `sensor.noah_grid_frequency` - Grid Frequency (Hz)
- `sensor.noah_grid_energy_exported_today` - Today's Export (kWh)
- `sensor.noah_grid_energy_exported_total` - Total Export (kWh)

### System Sensors
- `sensor.noah_system_status` - System Status
- `sensor.noah_work_mode` - Operating Mode (Load First/Battery First/Grid First)
- `sensor.noah_firmware_version` - Firmware Version

## 🤖 Automation Examples

### Battery Low Alert
```yaml
automation:
  - alias: "Noah Battery Low"
    trigger:
      platform: numeric_state
      entity_id: sensor.noah_battery_soc
      below: 20
    action:
      service: notify.mobile_app_your_phone
      data:
        message: "Noah 2000 battery is low: {{ states('sensor.noah_battery_soc') }}%"
```

### High Solar Generation Alert
```yaml
automation:
  - alias: "High Solar Generation"
    trigger:
      platform: numeric_state
      entity_id: sensor.noah_solar_power
      above: 500
    action:
      service: notify.mobile_app_your_phone
      data:
        message: "High solar generation: {{ states('sensor.noah_solar_power') }}W"
```

## 📞 Support

If you continue to have issues:

1. **Check the logs** for specific error messages
2. **Verify network connectivity** to openapi.growatt.com
3. **Test credentials** in the official Growatt app
4. **Share error logs** with specific error messages

The integration has been tested and works with your exact credentials, so any connection issues are likely configuration-related and can be resolved by following this guide.

## 🎉 Success Indicators

You'll know the integration is working when you see:
- **Devices & Services** shows "Growatt Noah 2000" as configured
- **Battery SOC** sensor shows current percentage (around 24-26%)
- **Solar Power** sensor shows current generation
- **System Status** shows "Online"
- **No error logs** related to growatt_noah

Your Noah 2000 system should now provide comprehensive battery monitoring in Home Assistant! 🔋⚡