# GitHub Repository Setup for HACS Compliance

To fix the HACS validation errors, you need to update your GitHub repository settings:

## 1. Add Repository Description

1. Go to https://github.com/mvolli/ha-growatt-noah
2. Click the ⚙️ gear icon (Settings) next to "About"
3. Add this description:
   ```
   Home Assistant integration for Growatt Noah 2000 battery systems and Neo 800 micro-inverters with support for API, MQTT, and Modbus connections
   ```

## 2. Add Repository Topics

In the same "About" section, add these topics (separated by spaces):
```
home-assistant homeassistant hacs integration growatt noah-2000 neo-800 solar battery inverter mqtt modbus api
```

## 3. Alternative: Use the Fix Script

If you have a GitHub token, you can run the automated fix script:

```bash
# Set your GitHub token
export GITHUB_TOKEN="your_github_token_here"

# Run the fix script
python3 fix_github_repo.py
```

## 4. Verify HACS Compliance

After making these changes, the HACS validation should pass. The key requirements are:

✅ **Repository has description**
✅ **Repository has topics** 
✅ **hacs.json is valid** (fixed in this commit)
✅ **manifest.json is valid**

## 5. Optional: Brands Integration

For full HACS compliance, you may also need to submit a PR to the Home Assistant brands repository:
https://github.com/home-assistant/brands

This adds official brand recognition for Growatt devices.

## Current Status

After this commit, 3 out of 4 HACS validation errors should be fixed:
- ✅ hacs.json validation (removed invalid fields)
- ⏳ Repository description (manual step required)
- ⏳ Repository topics (manual step required)
- ⏳ Brands validation (optional, requires separate PR)

The integration should work perfectly even without full brands compliance.