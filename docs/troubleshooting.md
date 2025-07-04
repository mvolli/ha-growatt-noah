# Troubleshooting Guide

## Common Issues

### Connection Issues

#### "Cannot connect to device"

**For Cloud API:**
- Verify your Growatt username and password
- Check that your device ID is correct
- Ensure your Growatt account has access to the device
- Try logging into the Growatt web portal to verify credentials

**For MQTT:**
- Verify MQTT broker is running and accessible
- Check MQTT credentials if authentication is enabled
- Ensure noah-mqtt bridge is properly configured and running
- Check MQTT topic configuration matches noah-mqtt setup

**For Modbus TCP:**
- Verify the device IP address and port
- Check network connectivity between Home Assistant and the device
- Ensure Modbus TCP is enabled on the Noah 2000
- Try connecting with a Modbus testing tool first

**For Modbus RTU:**
- Check serial port path is correct (`/dev/ttyUSB0`, `/dev/ttyAMA0`, etc.)
- Verify baud rate matches device configuration
- Ensure no other applications are using the serial port
- Check physical connections and cable quality

#### "Device already configured"

This error occurs when trying to add the same device twice.
- Go to Settings → Devices & Services
- Find the existing Growatt Noah 2000 integration
- Remove it and try again, or configure options instead

### Data Issues

#### "No data received" or sensors showing "Unknown"

- Check the update interval isn't too aggressive (minimum 10 seconds recommended)
- For MQTT: Verify noah-mqtt is publishing data to the correct topics
- For API: Check if you've hit rate limits
- For Modbus: Verify register addresses are correct for your device model

#### "Sensors show wrong values"

- Different Noah 2000 firmware versions may use different scaling factors
- Check if values need to be divided/multiplied by 10, 100, etc.
- For Modbus: Verify register mapping matches your device documentation

### Performance Issues

#### "Integration is slow to respond"

- Increase the update interval in integration options
- For cloud API: Reduce frequency to avoid rate limits
- For MQTT: Check broker performance and network latency
- For Modbus: Ensure no communication conflicts with other devices

#### "Home Assistant becomes unresponsive"

- This may indicate a communication deadlock
- Try increasing timeout values in the integration code
- Disable the integration temporarily and check HA logs

## Debugging

### Enable Debug Logging

Add to your `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.growatt_noah: debug
    custom_components.growatt_noah.api: debug
```

Then restart Home Assistant and check the logs for detailed information.

### MQTT Debugging

Monitor MQTT messages to verify data flow:

```bash
mosquitto_sub -h your-broker -t "noah/+"
```

### Modbus Debugging

Test Modbus connectivity with command-line tools:

```bash
# For Modbus TCP
modpoll -m tcp -a 1 -r 1000 -c 10 192.168.1.100

# For Modbus RTU  
modpoll -m rtu -b 9600 -a 1 -r 1000 -c 10 /dev/ttyUSB0
```

## Getting Help

1. **Check the logs** first for error messages
2. **Search existing issues** on the GitHub repository
3. **Create a new issue** with:
   - Home Assistant version
   - Integration version
   - Connection method used
   - Relevant log entries
   - Description of the problem

## Known Limitations

- **Control features** (switches/numbers) are not yet implemented
- **Register mapping** may need adjustment for different firmware versions
- **Cloud API** may have undocumented rate limits
- **MQTT autodiscovery** depends on noah-mqtt configuration

## Advanced Configuration

### Custom Modbus Registers

If your device uses different register addresses, you can modify `const.py`:

```python
MODBUS_REGISTERS = {
    "battery_soc": 1000,  # Your actual register address
    "battery_voltage": 1001,
    # ... add your mappings
}
```

### Custom MQTT Topics

For non-standard MQTT topic structures, modify the `api.py` file to handle your specific topic layout.

### Scaling Factors

Some devices may require different scaling factors for values. Check the `from_modbus_data` method in `models.py` to adjust scaling.