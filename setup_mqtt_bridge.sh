#!/bin/bash

# MQTT Bridge Setup Script for Growatt Devices

echo "Setting up Growatt MQTT Bridge..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 first."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv growatt_mqtt_env
source growatt_mqtt_env/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements_bridge.txt

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit mqtt_bridge.py and update the configuration:"
echo "   - MQTT_BROKER: Your Home Assistant IP address"
echo "   - MQTT_USERNAME/PASSWORD: Your MQTT credentials"
echo "   - DEVICES: Your device IP addresses"
echo ""
echo "2. Test the bridge:"
echo "   source growatt_mqtt_env/bin/activate"
echo "   python3 mqtt_bridge.py"
echo ""
echo "3. Run as service (optional):"
echo "   sudo cp growatt_mqtt_bridge.service /etc/systemd/system/"
echo "   sudo systemctl enable growatt_mqtt_bridge"
echo "   sudo systemctl start growatt_mqtt_bridge"