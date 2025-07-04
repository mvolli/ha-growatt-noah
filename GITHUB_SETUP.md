# GitHub Repository Setup Instructions

## Step 1: Create GitHub Repository

1. Go to [GitHub.com](https://github.com) and log in
2. Click the "+" icon in the top right → "New repository"
3. Set the repository name: `ha-growatt-noah`
4. Add description: "Home Assistant integration for Growatt Noah 2000 solar battery system"
5. Make it **Public** (required for HACS)
6. **DO NOT** initialize with README, .gitignore, or license (we have them already)
7. Click "Create repository"

## Step 2: Add Topics (Required for HACS)

After creating the repository:
1. Go to the repository page
2. Click the gear icon ⚙️ next to "About"
3. Add these topics:
   - `home-assistant`
   - `hacs`
   - `growatt`
   - `noah-2000`
   - `solar-battery`
   - `integration`

## Step 3: Enable Issues and Discussions

1. Go to Settings tab in your repository
2. Scroll down to "Features"
3. Make sure "Issues" is checked ✅
4. Enable "Discussions" ✅

## Step 4: Push the Code

Run these commands in your terminal:

```bash
cd "/mnt/c/Users/VoLLi/ha-noah"
git remote add origin https://github.com/mvolli/ha-growatt-noah.git
git push -u origin main
```

## Step 5: Create a Release (Required for HACS)

1. Go to your repository on GitHub
2. Click "Releases" on the right side
3. Click "Create a new release"
4. Tag version: `v1.0.0`
5. Release title: `v1.0.0 - Initial Release`
6. Description (copy from CHANGELOG.md):
   ```
   🎉 **Initial release of Growatt Noah 2000 Home Assistant Integration**
   
   ### Features
   - Multiple connection methods (API, MQTT, Modbus TCP/RTU)
   - 20+ sensors for comprehensive monitoring
   - Binary sensors for status indicators
   - Easy configuration through Home Assistant UI
   - Energy dashboard integration
   - HACS support
   
   ### Installation
   Install via HACS by adding this repository as a custom repository:
   `https://github.com/mvolli/ha-growatt-noah`
   ```
7. Click "Publish release"

## Step 6: Install via HACS

### Method 1: Custom Repository (Immediate)
1. In Home Assistant, go to HACS
2. Click the three dots in the top right
3. Select "Custom repositories"
4. Add repository URL: `https://github.com/mvolli/ha-growatt-noah`
5. Category: "Integration"
6. Click "Add"
7. Find "Growatt Noah 2000" in the integrations list
8. Click "Download"
9. Restart Home Assistant
10. Add the integration via Settings → Devices & Services

### Method 2: Official HACS (Later)
To get it included in the official HACS default repository list:
1. Wait for GitHub Actions to pass (validate workflow)
2. Submit a PR to [HACS default repositories](https://github.com/hacs/default)
3. Follow their submission guidelines

## Verification

After pushing, verify:
- ✅ Repository is public
- ✅ Topics are set
- ✅ Issues and discussions enabled
- ✅ GitHub Actions pass (check the Actions tab)
- ✅ Release is created
- ✅ HACS installation works

## Next Steps

1. Test the integration with your actual Noah 2000 device
2. Adjust Modbus register mappings if needed
3. Implement control features (switches/numbers)
4. Add more device-specific features
5. Submit to official HACS repository list

## Repository URL

Your repository will be available at:
`https://github.com/mvolli/ha-growatt-noah`

Users can install it via HACS using this URL.