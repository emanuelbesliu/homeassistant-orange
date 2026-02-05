# 🚀 Publishing to GitHub - Step by Step Guide

## ✅ Pre-Publish Checklist (COMPLETED)

- ✅ All personal data removed (phone numbers, profile IDs, SSO IDs)
- ✅ Test files deleted (test_*.py, *.har, analyze_har.py)
- ✅ Strong disclaimer added to all files
- ✅ LICENSE file created (MIT with disclaimer)
- ✅ .gitignore configured
- ✅ Initial commit created
- ✅ Version tagged as v0.1.0

## 📋 Steps to Publish

### 1. Create GitHub Repository

```bash
# Go to https://github.com/new
# Repository name: homeassistant-orange
# Description: Orange Romania integration for Home Assistant (Reverse Engineered - Unofficial)
# Public repository
# DO NOT initialize with README (we already have one)
```

### 2. Add Remote and Push

```bash
cd /Users/mac-ria-ebesliu/agents/homeassistant/orange

# Add GitHub remote (replace with your actual repo URL)
git remote add origin https://github.com/emanuelbesliu/homeassistant-orange.git

# Push code and tags
git push -u origin main
git push origin --tags
```

### 3. Create GitHub Release

```bash
# Option 1: Via GitHub UI
# Go to: https://github.com/emanuelbesliu/homeassistant-orange/releases/new
# Tag: v0.1.0
# Title: Release v0.1.0 - Initial Public Release
# Description: (see below)

# Option 2: Via GitHub CLI (if installed)
gh release create v0.1.0 \
  --title "Release v0.1.0 - Initial Public Release" \
  --notes-file RELEASE_NOTES.md
```

### 4. Release Notes Template

```markdown
# 🎉 Orange Romania - Home Assistant Integration v0.1.0

**First public release!**

⚠️ **IMPORTANT DISCLAIMER:** This integration is developed independently through **REVERSE ENGINEERING** for personal and educational use only. It is **NOT affiliated with, endorsed by, or supported by Orange Romania S.A.** Use at your own risk.

---

## ✨ Features

- 🔐 **OAuth Authentication** - Secure login with Orange.ro credentials
- 📱 **Multi-Profile Support** - Track multiple customer profiles
- 🎯 **Multi-Subscription Tracking** - Mobile, internet, TV subscriptions
- ⭐ **Loyalty Points** - Monitor Orange loyalty points and rewards
- 💰 **Unpaid Bills Tracking** - View unpaid bills and due dates
- 📊 **Account Monitoring** - Customer info, subscription status
- 🔄 **Auto-Update** - Hourly automatic data refresh
- 🌍 **Bilingual UI** - Romanian and English

## 📊 Sensors Created

### Global Sensors (4)
- `sensor.orange_profile_count` - Number of customer profiles
- `sensor.orange_subscriber_count` - Number of subscriptions
- `sensor.orange_loyalty_points` - Total loyalty points
- `sensor.orange_total_unpaid_bills` - Total unpaid bills (RON)

### Per-Profile Sensors
- `sensor.orange_profile_{id}` - Profile information
- `sensor.orange_profile_{id}_unpaid_bills` - Unpaid bills for profile

### Per-Subscriber Sensors
- `sensor.orange_subscriber_{id}` - Subscription status and details

## 📦 Installation

### Manual Installation

1. Download the latest release ZIP
2. Extract to `/config/custom_components/orange/`
3. Restart Home Assistant
4. Go to Settings → Devices & Services → Add Integration
5. Search for "Orange Romania"
6. Enter your Orange.ro credentials

### HACS Installation (Coming Soon)

Will be submitted to HACS after community testing.

## 📖 Documentation

- [README.md](README.md) - Full documentation
- [INSTALLATION.md](INSTALLATION.md) - Detailed installation guide
- [AGENTS.md](AGENTS.md) - Development guidelines

## 🐛 Known Issues

- None reported yet!

## 🙏 Contributing

Contributions welcome! Please read AGENTS.md for development guidelines.

## ⚠️ Legal Notice

This integration is developed independently through reverse engineering for personal and educational use only. It is NOT affiliated with, endorsed by, or supported by Orange Romania S.A. Orange Romania has no responsibility or liability for this integration.

The Orange name and logo are trademarks of Orange S.A. This project is not endorsed by or affiliated with Orange S.A. or Orange Romania S.A.

**Use at your own risk.**

---

**Developed by Emanuel Besliu (@emanuelbesliu)**
```

## 🔍 Post-Publish Checklist

After publishing to GitHub:

- [ ] Verify README renders correctly
- [ ] Check all links work
- [ ] Test installation from GitHub
- [ ] Create GitHub issue templates
- [ ] Set up GitHub Actions (optional)
- [ ] Add topics/tags: `home-assistant`, `integration`, `orange-romania`, `hacs`
- [ ] Update manifest.json documentation URL if needed

## 📢 Promotion (Optional)

Consider sharing on:
- Home Assistant Community Forum
- Reddit (r/homeassistant)
- Home Assistant Romania groups

**Always include the disclaimer that this is unofficial and reverse-engineered!**

---

## 🚨 Important Reminders

1. **Never commit credentials** or personal data
2. **Keep .gitignore updated** to exclude test files
3. **Update version numbers** in manifest.json before each release
4. **Always include disclaimer** in communications
5. **Be transparent** about reverse engineering approach

---

**Ready to publish! All personal data has been removed. Code is clean.**
