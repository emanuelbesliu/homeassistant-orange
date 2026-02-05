# Agent Guidelines for Orange.ro Home Assistant Integration

## Overview
This is a custom Home Assistant integration for Orange.ro that monitors mobile/internet subscriptions, account balance, unpaid bills, and usage data. Built using Python 3.11+ with asyncio and aiohttp for API communication.

**⚠️ IMPORTANT:** This integration is developed independently through **REVERSE ENGINEERING** for personal and educational use only. It is **NOT affiliated with, endorsed by, or supported by Orange Romania**. Orange Romania has **NO responsibility or liability** for this integration. Use at your own risk.

## Build/Test Commands

### Development Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements_dev.txt  # If exists

# Install Home Assistant for local testing
pip install homeassistant
```

### Code Quality & Validation
```bash
# Python linting
pylint custom_components/orange/  # Check code quality
flake8 custom_components/orange/  # Style checking
black custom_components/orange/   # Auto-format code
mypy custom_components/orange/    # Type checking

# YAML validation
yamllint .  # Validate manifest.json and config files
```

### Home Assistant Integration Testing
```bash
# Check configuration
ha core check  # Via HA CLI

# Developer Tools → Check Configuration in HA UI
# Settings → System → Logs (monitor for errors)
```

### Running Tests
```bash
# Unit tests (if/when created)
pytest tests/
pytest tests/test_api.py  # Single test file
pytest -v -k "test_authenticate"  # Single test by name

# Integration test: Manual testing in HA UI
# - Add integration via UI
# - Monitor logs for errors
# - Verify sensors appear and update
```

## Code Style Guidelines

### File Structure

```
custom_components/orange/
├── __init__.py          # Integration setup & coordinator
├── manifest.json        # Integration metadata
├── const.py            # Constants & API endpoints
├── config_flow.py      # UI configuration flow
├── api.py              # Orange.ro API client
├── sensor.py           # Sensor entities
└── strings.json        # Translations (ro/en)
```

### Python Code Style

#### Imports
```python
"""Module docstring with copyright.

Copyright (c) 2026 Emanuel Besliu
Licensed under the MIT License
"""
from __future__ import annotations  # Always first

import logging  # Standard library
from datetime import timedelta
from typing import Any

import aiohttp  # Third-party
from aiohttp import ClientSession

from homeassistant.config_entries import ConfigEntry  # HA imports
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OrangeAPI  # Local imports last
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
```

**Import Order:**
1. `from __future__ import annotations` (always first)
2. Standard library imports
3. Third-party imports (aiohttp, etc.)
4. Home Assistant imports
5. Local imports (from `.module`)

#### Formatting & Style
- **Line length:** Max 88 characters (Black default)
- **Indentation:** 4 spaces (Python standard)
- **Quotes:** Double quotes `"` for strings (Black default)
- **Type hints:** Use for all function parameters and returns
- **Docstrings:** Google-style, required for all public methods

```python
async def authenticate(self) -> bool:
    """Authenticate with Orange.ro platform.
    
    Returns:
        True if authentication successful, False otherwise.
        
    Raises:
        Exception: If network error or invalid credentials.
    """
```

#### Naming Conventions
- **Classes:** `PascalCase` - `OrangeAPI`, `OrangeBalanceSensor`
- **Functions/Methods:** `snake_case` - `async_setup_entry`, `get_account_data`
- **Constants:** `UPPER_SNAKE_CASE` - `DOMAIN`, `SCAN_INTERVAL`, `BASE_URL`
- **Private methods:** Prefix with `_` - `_fetch_balance`, `_extract_tokens`
- **Async functions:** Prefix with `async_` if HA convention - `async_setup_entry`

#### Type Hints & Annotations
```python
from typing import Any

# Function signatures
async def get_data(self) -> dict[str, Any]:
    """Fetch data from API."""
    
# Variable annotations
self._cookies: dict[str, str] = {}
self._authenticated: bool = False
self._subscriptions: list[dict[str, Any]] = []

# Optional types
def parse_date(date_str: str | None) -> str | None:
    """Parse date string."""
```

### Error Handling

#### Logging Levels
```python
_LOGGER.debug("Detailed info for debugging")
_LOGGER.info("Important state changes")
_LOGGER.warning("Recoverable issues")
_LOGGER.error("Errors that prevent functionality")
```

#### Exception Handling
```python
# API methods - let exceptions propagate with context
async def authenticate(self) -> bool:
    """Authenticate with Orange API."""
    try:
        async with self._session.post(LOGIN_URL, data=data) as response:
            if response.status == 200:
                return True
            else:
                _LOGGER.error(f"Login failed: {response.status}")
                return False
    except aiohttp.ClientError as err:
        _LOGGER.error(f"Network error during auth: {err}")
        raise
    except Exception as err:
        _LOGGER.error(f"Unexpected error: {err}")
        raise

# Coordinator - catch and wrap in UpdateFailed
async def async_update_data():
    """Fetch data from API."""
    try:
        return await api.get_data()
    except Exception as err:
        raise UpdateFailed(f"Error communicating with API: {err}") from err
```

### Home Assistant Patterns

#### Entity Naming
```python
# Sensor unique_id pattern
self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"

# Sensor name pattern  
self._attr_name = f"Orange {name}"  # "Orange Account Balance"

# Entity ID (auto-generated)
# sensor.orange_account_balance
# sensor.orange_subscription_mobile
```

#### Data Coordinator Pattern
```python
# Update interval
SCAN_INTERVAL = timedelta(hours=1)

# Coordinator setup in __init__.py
coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=DOMAIN,
    update_method=async_update_data,
    update_interval=SCAN_INTERVAL,
)

await coordinator.async_config_entry_first_refresh()
```

#### Sensor Implementation
```python
class OrangeBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Orange sensors."""
    
    def __init__(self, coordinator, entry, sensor_type, name):
        """Initialize sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_name = f"Orange {name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Orange Romania",
            "manufacturer": "Orange Romania",
            "model": "Account",
        }
    
    @property
    def native_value(self) -> float | None:
        """Return sensor value."""
        return self.coordinator.data.get("balance")
```

## Constants & Configuration

### const.py Structure
```python
"""Constants for Orange integration."""

DOMAIN = "orange"
CONF_PHONE_NUMBER = "phone_number"  # If needed beyond username

# API endpoints
BASE_URL = "https://www.orange.ro"
LOGIN_URL = f"{BASE_URL}/api/login"  # To be discovered
API_BALANCE = f"{BASE_URL}/api/balance"
API_SUBSCRIPTIONS = f"{BASE_URL}/api/subscriptions"
API_BILLS = f"{BASE_URL}/api/bills"

# Update interval
DEFAULT_SCAN_INTERVAL = 3600  # 1 hour
```

### manifest.json
```json
{
  "domain": "orange",
  "name": "Orange Romania",
  "codeowners": ["@emanuelbesliu"],
  "config_flow": true,
  "documentation": "https://github.com/emanuelbesliu/homeassistant-orange",
  "integration_type": "hub",
  "iot_class": "cloud_polling",
  "requirements": ["aiohttp>=3.8.0"],
  "version": "0.1.0"
}
```

## Development Workflow

### 1. API Reverse Engineering
Use the hidroelectrica project's interceptor pattern:
```bash
# Start MITM proxy to capture Orange.ro API calls
python interceptor.py  # Adapt from hidroelectrica
# Configure browser proxy, login to orange.ro
# Analyze captured_requests/ for API endpoints
```

### 2. Implementation Order
1. **const.py** - Define API endpoints and constants
2. **api.py** - Implement OrangeAPI class with auth
3. **__init__.py** - Setup coordinator and entry
4. **sensor.py** - Create sensor entities
5. **config_flow.py** - UI configuration flow
6. **strings.json** - Add translations

### 3. Testing Checklist
- [ ] Authentication works with real credentials
- [ ] Data fetching returns valid JSON
- [ ] Sensors appear in HA UI
- [ ] Values update every hour
- [ ] Error handling works (wrong password, network issues)
- [ ] Config flow validates inputs
- [ ] Integration can be removed cleanly

## Common Patterns

### API Client Authentication Flow
```python
async def authenticate(self) -> bool:
    """Authenticate with Orange.ro."""
    # 1. GET login page for session/tokens
    async with self._session.get(LOGIN_URL) as response:
        self._cookies.update({k: v.value for k, v in response.cookies.items()})
    
    # 2. POST credentials
    login_data = {
        "username": self._username,
        "password": self._password,
    }
    
    async with self._session.post(LOGIN_URL, data=login_data, cookies=self._cookies) as response:
        if response.status == 302 or response.status == 200:
            self._authenticated = True
            return True
    
    return False
```

### Sensor with Attributes
```python
@property
def extra_state_attributes(self) -> dict[str, Any]:
    """Return additional attributes."""
    attrs = {}
    if self.coordinator.data:
        attrs["subscription_type"] = self.coordinator.data.get("type")
        attrs["expires_date"] = self.coordinator.data.get("expires")
    return attrs
```

## Debugging & Troubleshooting

### Enable Debug Logging
Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.orange: debug
    custom_components.orange.api: debug
```

### Common Issues
- **401/403 errors:** Check authentication flow, cookies, CSRF tokens
- **No data returned:** Verify API endpoints with interceptor
- **Sensors not updating:** Check coordinator interval, error logs
- **Invalid JSON:** API may return HTML on error - check response.status first

---

**Development Goal:** Create a production-ready Orange.ro integration following Home Assistant standards.

**Author:** Emanuel Besliu (@emanuelbesliu)

**Legal Notice:** This integration is developed independently through reverse engineering for personal and educational use only. It is NOT affiliated with, endorsed by, or supported by Orange Romania. Orange Romania has no responsibility or liability for this integration. Use at your own risk.
