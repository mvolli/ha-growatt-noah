"""Test the data models."""
import pytest
from datetime import datetime
from custom_components.growatt_noah.models import NoahData, BatteryData, SolarData, GridData, LoadData, SystemData


def test_battery_data_creation():
    """Test BatteryData creation."""
    battery = BatteryData(
        soc=85.5,
        voltage=48.2,
        current=10.5,
        power=500,
        temperature=25.3,
        status="Charging"
    )
    
    assert battery.soc == 85.5
    assert battery.voltage == 48.2
    assert battery.current == 10.5
    assert battery.power == 500
    assert battery.temperature == 25.3
    assert battery.status == "Charging"


def test_noah_data_from_api_response():
    """Test NoahData creation from API response."""
    api_data = {
        "battery_soc": 75,
        "battery_voltage": 48.0,
        "battery_current": 5.0,
        "battery_power": 240,
        "battery_temperature": 22.5,
        "battery_status": "Discharging",
        "solar_power": 800,
        "solar_voltage": 35.2,
        "solar_current": 22.7,
        "solar_energy_today": 15.6,
        "solar_energy_total": 1250.8,
        "grid_power": -300,  # Exporting
        "grid_voltage": 230.5,
        "grid_frequency": 50.0,
        "grid_energy_imported_today": 5.2,
        "grid_energy_exported_today": 8.3,
        "grid_energy_imported_total": 450.6,
        "grid_energy_exported_total": 680.2,
        "grid_connected": True,
        "load_power": 1040,
        "load_energy_today": 25.8,
        "load_energy_total": 2150.4,
        "system_status": "Normal",
        "system_mode": "Auto",
        "firmware_version": "1.2.3"
    }
    
    noah_data = NoahData.from_api_response(api_data)
    
    # Test battery data
    assert noah_data.battery.soc == 75
    assert noah_data.battery.voltage == 48.0
    assert noah_data.battery.power == 240
    assert noah_data.battery.status == "Discharging"
    
    # Test solar data
    assert noah_data.solar.power == 800
    assert noah_data.solar.energy_today == 15.6
    
    # Test grid data
    assert noah_data.grid.power == -300
    assert noah_data.grid.grid_connected is True
    
    # Test load data
    assert noah_data.load.power == 1040
    
    # Test system data
    assert noah_data.system.status == "Normal"
    assert noah_data.system.firmware_version == "1.2.3"


def test_noah_data_from_modbus_data():
    """Test NoahData creation from Modbus registers."""
    modbus_registers = {
        "battery_soc": 85,
        "battery_voltage": 4820,  # 48.20V with scale factor /100
        "battery_current": 1050,  # 10.50A with scale factor /100
        "battery_power": 500,
        "battery_temperature": 253,  # 25.3°C with scale factor /10
        "solar_power": 1200,
        "solar_voltage": 3520,  # 35.20V with scale factor /100
        "solar_current": 3410,  # 34.10A with scale factor /100
        "grid_power": 450,
        "grid_voltage": 23050,  # 230.50V with scale factor /100
        "load_power": 1650
    }
    
    noah_data = NoahData.from_modbus_data(modbus_registers)
    
    # Test scaling factors are applied correctly
    assert noah_data.battery.soc == 85
    assert noah_data.battery.voltage == 48.2
    assert noah_data.battery.current == 10.5
    assert noah_data.battery.temperature == 25.3
    assert noah_data.solar.voltage == 35.2
    assert noah_data.solar.current == 34.1
    assert noah_data.grid.voltage == 230.5


def test_noah_data_from_mqtt_data():
    """Test NoahData creation from MQTT topics."""
    mqtt_topics = {
        "battery": {
            "battery_soc": 90,
            "battery_voltage": 49.1,
            "battery_current": -5.2,  # Discharging
            "battery_power": -255,
            "battery_temperature": 24.8,
            "battery_status": "Discharging"
        },
        "solar": {
            "solar_power": 650,
            "solar_voltage": 34.8,
            "solar_current": 18.7,
            "solar_energy_today": 12.4
        },
        "grid": {
            "grid_power": 150,
            "grid_voltage": 229.8,
            "grid_frequency": 49.9,
            "grid_connected": True
        }
    }
    
    noah_data = NoahData.from_mqtt_data(mqtt_topics)
    
    assert noah_data.battery.soc == 90
    assert noah_data.battery.current == -5.2  # Negative = discharging
    assert noah_data.solar.power == 650
    assert noah_data.grid.grid_connected is True


def test_empty_data_handling():
    """Test handling of empty or missing data."""
    # Test with empty dict
    noah_data = NoahData.from_api_response({})
    
    # Should have default values
    assert noah_data.battery.soc == 0
    assert noah_data.battery.voltage == 0
    assert noah_data.solar.power == 0
    assert noah_data.grid.power == 0
    assert noah_data.system.status == "Unknown"
    
    # Test with partial data
    partial_data = {
        "battery_soc": 50,
        "solar_power": 300
    }
    
    noah_data = NoahData.from_api_response(partial_data)
    
    assert noah_data.battery.soc == 50
    assert noah_data.solar.power == 300
    assert noah_data.grid.power == 0  # Should default to 0


if __name__ == "__main__":
    pytest.main([__file__])