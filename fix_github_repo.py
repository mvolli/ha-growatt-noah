#!/usr/bin/env python3
"""
Script to fix GitHub repository settings for HACS compliance
"""
import requests
import os
import sys

# GitHub repository details
REPO_OWNER = "mvolli"
REPO_NAME = "ha-growatt-noah"
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

def update_repository():
    """Update repository description and topics"""
    if not GITHUB_TOKEN:
        print("Please set GITHUB_TOKEN environment variable")
        return False
    
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Update repository description and topics
    repo_data = {
        "description": "Home Assistant integration for Growatt Noah 2000 battery systems and Neo 800 micro-inverters with support for API, MQTT, and Modbus connections",
        "topics": [
            "home-assistant",
            "homeassistant",
            "hacs",
            "integration",
            "growatt",
            "noah-2000",
            "neo-800",
            "solar",
            "battery",
            "inverter",
            "mqtt",
            "modbus",
            "api"
        ],
        "has_wiki": False,
        "has_projects": False
    }
    
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
    response = requests.patch(url, json=repo_data, headers=headers)
    
    if response.status_code == 200:
        print("✅ Repository updated successfully!")
        print(f"Description: {repo_data['description']}")
        print(f"Topics: {', '.join(repo_data['topics'])}")
        return True
    else:
        print(f"❌ Failed to update repository: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    print("Updating GitHub repository for HACS compliance...")
    success = update_repository()
    sys.exit(0 if success else 1)