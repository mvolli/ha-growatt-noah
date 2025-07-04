# Troubleshooting Guide

## Common Connection Issues

### Modbus TCP Connection Refused (Your Current Issue)

**Error**: `Failed to connect [Errno 111] Connect call failed ('192.168.1.118', 502)`

**Root Cause**: Most Growatt devices (including Noah 2000 and Neo 800) do not support Modbus TCP by default.

**Solutions**:

#### 1. Switch to MQTT Connection (Recommended for Neo 800)
```yaml
# Configuration for Neo 800 with local MQTT
Connection Type: MQTT
MQTT Broker: localhost  # or your MQTT broker IP
Port: 1883
Topic Prefix: growatt/neo800
```

#### 2. Switch to API Connection
```yaml
# Configuration for Growatt Cloud API
Connection Type: API
Username: your-growatt-username
Password: your-growatt-password
Plant ID: (leave empty for auto-detection)
```

#### 3. Check if Your Device Has RS485 Port
Some Growatt devices have RS485 communication ports that can be used with:
- RS485-to-USB converter
- RS485-to-Ethernet gateway
- Modbus RTU over RS485

### API Connection Issues

**Error**: `error_permission_denied (code 10011)`

**Solution**: 
- Use MQTT or Modbus RTU connection
- API access is restricted for individual users in 2024

### MQTT Connection Setup

For Neo 800 devices that support MQTT:

1. **Check device MQTT settings**:
   - Access device web interface (usually at device IP)
   - Look for MQTT configuration
   - Note: Neo 800 primarily sends to Growatt's cloud MQTT

2. **Set up local MQTT bridge**:
   ```bash
   # Install Mosquitto MQTT broker
   sudo apt install mosquitto mosquitto-clients
   
   # Test MQTT connection
   mosquitto_sub -h localhost -t "growatt/+"
   ```

3. **Configure MQTT bridge** (advanced):
   You may need to set up an MQTT bridge to capture data from your devices.

### Device Discovery

To identify what services your devices are running:

```bash
# Check if devices respond to ping
ping 192.168.1.118
ping 192.168.1.117

# Scan for open ports (if nmap is available)
nmap -p 1-1000 192.168.1.118

# Test specific ports
nc -zv 192.168.1.118 80    # Web interface
nc -zv 192.168.1.118 1883  # MQTT
nc -zv 192.168.1.118 502   # Modbus TCP
nc -zv 192.168.1.118 8080  # Alternative web port
```

### Alternative Data Collection Methods

#### 1. Growatt Server Integration (Official HA)
Use the official Home Assistant Growatt Server integration for basic monitoring:
```yaml
# Add via UI: Settings → Devices & Services → Add Integration
# Search for: "Growatt Server"
```

#### 2. Custom MQTT Bridge
Create a bridge to capture device data:
- [noah-mqtt](https://github.com/mtrossbach/noah-mqtt) for Noah 2000
- Custom ESP32/Arduino bridge for local data capture

#### 3. Web Scraping (Advanced)
If devices have web interfaces:
- Access device IP in browser
- Look for JSON API endpoints
- Create custom scraper integration

### Debugging Steps

1. **Verify device network connectivity**:
   ```bash
   ping 192.168.1.118
   ```

2. **Check device web interface**:
   - Open `http://192.168.1.118` in browser
   - Look for configuration or status pages

3. **Enable debug logging in Home Assistant**:
   ```yaml
   # configuration.yaml
   logger:
     default: info
     logs:
       custom_components.growatt_noah: debug
       pymodbus: debug
   ```

4. **Check Home Assistant logs**:
   - Settings → System → Logs
   - Look for detailed error messages

### Device-Specific Solutions

#### Noah 2000 Battery System
- **Best**: Growatt Cloud API (if you have access)
- **Alternative**: Local MQTT bridge using noah-mqtt project
- **Last resort**: Web scraping from device interface

#### Neo 800 Micro-Inverter
- **Best**: MQTT connection to local broker
- **Alternative**: Growatt Cloud API
- **Note**: Check if device publishes to mqtt.growatt.com:7006

### Getting Help

If you're still having issues:

1. **Check device documentation** for communication protocols
2. **Contact Growatt support** for Modbus or local API documentation
3. **Join Home Assistant community** for device-specific solutions
4. **Consider professional installation** for complex setups

### Next Steps for Your Setup

Based on your error, I recommend:

1. **Try MQTT connection first** - most likely to work with your devices
2. **Check device web interfaces** at 192.168.1.118 and 192.168.1.117
3. **Look for MQTT settings** in device configuration
4. **Set up local MQTT broker** if devices support local MQTT
5. **Use API connection as fallback** if you have Growatt account access

Remember: Modbus TCP is rarely supported on consumer Growatt devices without additional hardware or firmware modifications.