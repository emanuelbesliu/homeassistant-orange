"""The Orange Romania integration.

Copyright (c) 2026 Emanuel Besliu
Licensed under the MIT License

DISCLAIMER: This integration is developed independently through reverse engineering
for personal and educational use only. It is NOT affiliated with, endorsed by, or
supported by Orange Romania. Orange Romania has no responsibility or liability for
this integration. Use at your own risk.
"""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OrangeAPI
from .const import DOMAIN
from .coordinator import OrangeDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Orange Romania from a config entry."""
    session = async_get_clientsession(hass)

    api = OrangeAPI(
        session,
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )

    try:
        authenticated = await api.authenticate()
        if not authenticated:
            raise ConfigEntryAuthFailed(
                "Authentication failed. Please reconfigure with valid credentials."
            )
    except ConfigEntryAuthFailed:
        raise
    except Exception as err:
        _LOGGER.error("Failed to authenticate with Orange Romania: %s", err)
        raise ConfigEntryNotReady from err

    coordinator = OrangeDataUpdateCoordinator(hass, entry, api)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
