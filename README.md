# Orange Romania - Home Assistant Integration

**Custom Home Assistant integration for [orange.ro](https://www.orange.ro)**

Monitor your Orange subscriptions, account balance, loyalty points, and unpaid bills directly from Home Assistant.

> **Status:** ✅ **v0.1.0 - Ready for Testing!**

---

## ⚠️ IMPORTANT DISCLAIMER

**This integration is developed independently through REVERSE ENGINEERING for personal and educational use only.**

- ❌ **NOT affiliated with** Orange Romania
- ❌ **NOT endorsed by** Orange Romania  
- ❌ **NOT supported by** Orange Romania
- ⚠️ Orange Romania has **NO responsibility or liability** for this integration
- ⚠️ **Use at your own risk**
- ⚠️ This integration may **stop working** at any time if Orange changes their API
- ⚠️ By using this integration, you acknowledge that it is **unofficial** and **unsupported**

**The author (Emanuel Besliu) provides this integration "AS IS" without any warranty.**

---

## ✨ Features

- 🔐 **Secure OAuth Authentication** - Encrypted credentials with OAuth flow
- 📱 **Multi-Profile Support** - Multiple customer profiles
- 🎯 **Multi-Subscription Tracking** - Mobile, internet, TV subscriptions
- ⭐ **Loyalty Points** - Track Orange loyalty points and rewards
- 💰 **Unpaid Bills Tracking** - Monitor unpaid bills and due dates
- 📊 **Account Monitoring** - Customer info, subscription status
- 🔄 **Auto-Update** - Hourly data refresh
- 🌍 **Bilingual** - Romanian and English UI

## 📦 Installation

### Option 1: Copy to custom_components

1. Copy the `custom_components/orange` folder to your Home Assistant `custom_components` directory:
   ```
   /config/custom_components/orange/
   ```

2. Restart Home Assistant

3. Go to **Settings** → **Devices & Services** → **Add Integration**

4. Search for "**Orange Romania**"

5. Enter your Orange.ro credentials (phone number or email + password)

### Option 2: HACS (Coming Soon)

Will be available after testing and release.

## ⚙️ Configuration

1. **Settings** → **Devices & Services** → **Add Integration**
2. Search for "**Orange Romania**"
3. Enter your **Orange.ro username** (phone number: `0700123456` or email)
4. Enter your **password**
5. Click **Submit**

The integration will authenticate using Orange's OAuth flow and create sensors automatically!

## 🛠️ Development

See [AGENTS.md](AGENTS.md) for detailed development guidelines.

### Quick Start

1. **Set up interceptor** (from hidroelectrica project):
   ```bash
   cd ../hidroelectrica
   python interceptor.py
   ```

2. **Configure browser proxy** to capture Orange.ro traffic

3. **Login to orange.ro** and navigate through account pages

4. **Analyze captured requests** to identify API endpoints

5. **Implement API client** based on captured data

## 📦 File Structure

```
custom_components/orange/
├── __init__.py          # Integration setup
├── api.py              # Orange.ro API client
├── const.py            # Constants
├── config_flow.py      # UI configuration
├── sensor.py           # Sensor entities
├── manifest.json       # Metadata
└── strings.json        # Translations
```

## 📊 Sensors Created

### Global Sensors (4)

| Entity ID | Description | Attributes |
|-----------|-------------|------------|
| `sensor.orange_profile_count` | Number of customer profiles | profile_names, profile_ids |
| `sensor.orange_subscriber_count` | Number of subscriptions | phone_numbers, subscriber_ids |
| `sensor.orange_loyalty_points` | Total loyalty points | Per-profile points breakdown |
| `sensor.orange_total_unpaid_bills` | Account balance (RON) - positive = debt, negative = credit | total_count, per-profile amounts and due dates |

**Note:** The `sensor.orange_total_unpaid_bills` sensor displays:
- **Positive values** (e.g., `129.41`) when you have outstanding bills to pay
- **Negative values** (e.g., `-129.00`) when you have credit from advance payment
- **Zero** when your account is settled

### Per-Profile Sensors

For each customer profile (e.g., "John Doe"):

| Entity ID | State | Attributes |
|-----------|-------|------------|
| `sensor.orange_profile_100000001` | Customer type (PRIVATE) | name, ocn, status, next_invoice_date |
| `sensor.orange_profile_100000001_unpaid_bills` | Account balance (RON) - positive = debt, negative = credit | services_amount, installments_amount, due_date, profile_name |

### Per-Subscriber Sensors

For each subscription (e.g., 0700123456):

| Entity ID | State | Attributes |
|-----------|-------|------------|
| `sensor.orange_subscriber_200000001` | Status (ACTIVE) | msisdn, subscription_type, contact_name, is_prepay |

## 📈 Example Data

After setup, you'll see sensors like:

```yaml
sensor.orange_profile_count: 2
  profile_names: ["John Doe", "Jane Smith"]
  
sensor.orange_subscriber_count: 1
  phone_numbers: ["0700123456"]
  
sensor.orange_loyalty_points: 4.38
  profile_100000001_points: 4.38
  profile_100000001_value_ron: 0.88

sensor.orange_total_unpaid_bills: 129.41
  total_count: 1
  profile_100000001_amount: 129.41
  profile_100000001_due_date: "2026-02-15"
  profile_100000001_name: "John Doe"

sensor.orange_profile_100000001_unpaid_bills: 129.41
  services_amount: 129.41
  installments_amount: 0.0
  due_date: "2026-02-15"
  has_invoices: true
  profile_name: "John Doe"
  
sensor.orange_subscriber_200000001: "ACTIVE"
  msisdn: "0700123456"
  subscription_type: "abonament"
  subscriber_type: "PRIVATE"
  is_prepay: false
```

## 📝 License

MIT License - Copyright (c) 2026 Emanuel Besliu

## ⚠️ Legal Notice

This integration is developed independently through reverse engineering for personal and educational use only. It is NOT affiliated with, endorsed by, or supported by Orange Romania S.A. Orange Romania has no responsibility or liability for this integration. Use at your own risk.

The Orange name and logo are trademarks of Orange S.A. This project is not endorsed by or affiliated with Orange S.A. or Orange Romania S.A.

---

**Developed by Emanuel Besliu (@emanuelbesliu)**
# Test dependency update
# Test v2
