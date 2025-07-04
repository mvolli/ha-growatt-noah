# Installation Guide

## Prerequisites

- Home Assistant 2023.1 or later
- One of the following connection methods:
  - Growatt account for cloud API access
  - MQTT broker with noah-mqtt bridge
  - Direct network/serial access to the Noah 2000

## Installation Methods

### Method 1: HACS (Recommended)

1. Install [HACS](https://hacs.xyz/) if not already installed
2. In HACS, go to "Integrations"
3. Click the "+" button and search for "Growatt Noah 2000"
4. Install the integration
5. Restart Home Assistant
6. Go to Settings → Devices & Services → Add Integration
7. Search for "Growatt Noah 2000" and follow the setup wizard

### Method 2: Manual Installation

1. Download the latest release from GitHub
2. Extract the `growatt_noah` folder to your `custom_components` directory:
   ```
   config/
   └── custom_components/
       └── growatt_noah/
           ├── __init__.py
           ├── manifest.json
           ├── config_flow.py
           └── ...
   ```
3. Restart Home Assistant
4. Go to Settings → Devices & Services → Add Integration
5. Search for "Growatt Noah 2000" and follow the setup wizard

## Connection Setup

### Option 1: Growatt Cloud API

**Pros:** Easy setup, no additional hardware needed
**Cons:** Requires internet, may have rate limits, data goes through Growatt servers

1. You need your Growatt account credentials
2. Find your device ID in the Growatt app or web portal
3. Configure with reasonable update intervals (30-60 seconds recommended)

### Option 2: MQTT (Recommended)

**Pros:** Fast, reliable, local communication
**Cons:** Requires MQTT broker and noah-mqtt bridge

1. Set up an MQTT broker (like Mosquitto)
2. Install and configure [noah-mqtt](https://github.com/mtrossbach/noah-mqtt)
3. Configure the integration to use your MQTT broker
4. Default topic base is "noah" but can be customized

### Option 3: Modbus TCP

**Pros:** Direct communication, fastest response
**Cons:** Requires network access to the device, may need port configuration

1. Ensure your Noah 2000 has Modbus TCP enabled
2. Find the device's IP address
3. Default port is 502
4. Configure appropriate Modbus device ID (usually 1)

### Option 4: Modbus RTU

**Pros:** Direct serial communication, very reliable
**Cons:** Requires physical serial connection

1. Connect a USB-to-RS485 adapter to your Home Assistant system
2. Connect the adapter to the Noah 2000's serial port
3. Configure the correct serial port path (e.g., `/dev/ttyUSB0`)
4. Set appropriate baud rate (typically 9600)

## Post-Installation

After successful setup, you'll see:

- **Sensors:** Battery SoC, power values, energy counters, etc.
- **Binary Sensors:** Grid connection status, charging status, etc.
- **Switches:** Enable/disable various functions (if supported)
- **Numbers:** Configure charge limits and power settings (if supported)

All entities will be organized under a single device called "Growatt Noah 2000".

## Troubleshooting

See the [Troubleshooting Guide](troubleshooting.md) for common issues and solutions.