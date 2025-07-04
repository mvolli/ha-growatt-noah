# MQTT Setup Guide for Growatt Devices

## Quick Setup Steps

### 1. Install MQTT Broker in Home Assistant

1. Go to **Settings** → **Add-ons** → **Add-on Store**
2. Search for **"Mosquitto broker"**
3. Click **Install**
4. Go to **Configuration** tab and add:
   ```yaml
   logins:
     - username: growatt
       password: your_secure_password
   anonymous: false
   require_certificate: false
   ```
5. **Start** the add-on and enable **"Start on boot"**

### 2. Check Your Device Web Interfaces

Visit your device IPs in a browser:
- http://192.168.1.118
- http://192.168.1.117

Look for:
- MQTT settings
- Status/data pages
- API endpoints
- Local configuration options

### 3. Option A: Direct Device MQTT (If Supported)

If your devices have MQTT settings:
1. Configure them to publish to your local broker
2. Set broker IP to your Home Assistant IP
3. Use the credentials you created above

### 4. Option B: Use MQTT Bridge (Recommended)

Since most Growatt devices don't support local MQTT directly, use the included bridge:

#### Install the Bridge:
```bash
# Download the bridge files (already in your repo)
cd /path/to/ha-noah
chmod +x setup_mqtt_bridge.sh
./setup_mqtt_bridge.sh
```

#### Configure the Bridge:
Edit `mqtt_bridge.py` and update:
```python
MQTT_BROKER = "192.168.1.XXX"  # Your Home Assistant IP
MQTT_USERNAME = "growatt"
MQTT_PASSWORD = "your_secure_password"

DEVICES = [
    {
        "name": "neo800_1",
        "ip": "192.168.1.118",
        "type": "neo800"
    },
    {
        "name": "noah2000_1", 
        "ip": "192.168.1.117",
        "type": "noah2000"
    }
]
```

#### Run the Bridge:
```bash
source growatt_mqtt_env/bin/activate
python3 mqtt_bridge.py
```

### 5. Configure Home Assistant Integration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **"Growatt Noah 2000 & Neo 800"**
3. Select your device type
4. Choose **MQTT** as connection type
5. Configure:
   ```
   MQTT Broker: localhost
   Port: 1883
   Username: growatt
   Password: your_secure_password
   Topic Prefix: growatt/neo800_1 (or growatt/noah2000_1)
   ```

### 6. Test MQTT Data Flow

#### Check MQTT Messages:
1. Go to **Developer Tools** → **MQTT**
2. Subscribe to topic: `growatt/+/+`
3. You should see data flowing from your devices

#### Check Logs:
1. **Settings** → **System** → **Logs**
2. Look for messages from the Growatt integration
3. Enable debug logging if needed:
   ```yaml
   # configuration.yaml
   logger:
     default: info
     logs:
       custom_components.growatt_noah: debug
   ```

## Troubleshooting

### No Data from Bridge
1. Check device web interfaces work in browser
2. Verify MQTT broker is running
3. Check bridge logs for errors
4. Ensure correct IP addresses and credentials

### Integration Not Finding Data
1. Verify MQTT topic structure
2. Check topic prefix matches configuration
3. Ensure MQTT credentials are correct
4. Test MQTT manually in Developer Tools

### Device Web Interface Issues
1. Try different endpoints:
   - http://DEVICE_IP/status
   - http://DEVICE_IP/api/data
   - http://DEVICE_IP/data.json
2. Check device documentation
3. Look for firmware update options

## Alternative: MQTT Discovery

If the bridge finds working endpoints, you can also use MQTT Discovery:

```yaml
# configuration.yaml
mqtt:
  sensor:
    - name: "Neo 800 Solar Power"
      state_topic: "growatt/neo800_1/solar_power"
      unit_of_measurement: "W"
      device_class: power
      
    - name: "Neo 800 Energy Today"
      state_topic: "growatt/neo800_1/energy_today"
      unit_of_measurement: "kWh"
      device_class: energy
```

## Next Steps

1. **Start with device web interface check**
2. **Install MQTT broker**
3. **Try the bridge approach**
4. **Configure integration with MQTT**
5. **Monitor logs and adjust as needed**

The bridge will automatically discover working endpoints on your devices and publish the data to MQTT topics that the integration can consume.