"""Sensor platform for Orange Romania integration.

Copyright (c) 2026 Emanuel Besliu
Licensed under the MIT License

DISCLAIMER: This integration is developed independently through reverse engineering
for personal and educational use only. It is NOT affiliated with, endorsed by, or
supported by Orange Romania. Orange Romania has no responsibility or liability for
this integration. Use at your own risk.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Orange Romania sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # Global sensors
    sensors = [
        OrangeProfileCountSensor(coordinator, entry),
        OrangeSubscriberCountSensor(coordinator, entry),
        OrangeLoyaltyPointsSensor(coordinator, entry),
        OrangeTotalUnpaidBillsSensor(coordinator, entry),
    ]
    
    # Per-profile sensors
    if coordinator.data and "profiles" in coordinator.data:
        for profile in coordinator.data["profiles"]:
            profile_id = profile.get("id")
            profile_name = profile.get("name", "Unknown")
            
            if profile_id:
                sensors.append(
                    OrangeProfileSensor(coordinator, entry, profile_id, profile_name)
                )
    
    # Per-subscriber sensors
    if coordinator.data and "subscribers" in coordinator.data:
        for subscriber in coordinator.data["subscribers"]:
            subscriber_id = subscriber.get("subscriberId")
            msisdn = subscriber.get("msisdn", "Unknown")
            
            if subscriber_id:
                sensors.append(
                    OrangeSubscriberSensor(coordinator, entry, subscriber_id, msisdn)
                )
    
    # Per-profile unpaid bills sensors
    if coordinator.data and "unpaid_bills" in coordinator.data:
        unpaid_by_profile = coordinator.data["unpaid_bills"].get("by_profile", {})
        for profile_id, bill_info in unpaid_by_profile.items():
            sensors.append(
                OrangeProfileUnpaidBillsSensor(
                    coordinator,
                    entry,
                    int(profile_id),
                    bill_info.get("profile_name", "Unknown"),
                )
            )

    async_add_entities(sensors)


class OrangeBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Orange Romania sensors."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        sensor_type: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_name = f"Orange {name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Orange Romania",
            "manufacturer": "Orange Romania",
            "model": "Account",
        }


class OrangeProfileCountSensor(OrangeBaseSensor):
    """Sensor for number of profiles."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "profile_count", "Profile Count")
        self._attr_icon = "mdi:account-multiple"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data and "summary" in self.coordinator.data:
            return self.coordinator.data["summary"].get("total_profiles")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        attrs = {}
        if self.coordinator.data and "profiles" in self.coordinator.data:
            profiles = self.coordinator.data["profiles"]
            attrs["profile_names"] = [p.get("name") for p in profiles]
            attrs["profile_ids"] = [p.get("id") for p in profiles]
        return attrs


class OrangeSubscriberCountSensor(OrangeBaseSensor):
    """Sensor for number of subscribers."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "subscriber_count", "Subscriber Count")
        self._attr_icon = "mdi:sim"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data and "summary" in self.coordinator.data:
            return self.coordinator.data["summary"].get("total_subscribers")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        attrs = {}
        if self.coordinator.data and "subscribers" in self.coordinator.data:
            subscribers = self.coordinator.data["subscribers"]
            attrs["phone_numbers"] = [s.get("msisdn") for s in subscribers]
            attrs["subscriber_ids"] = [s.get("subscriberId") for s in subscribers]
        return attrs


class OrangeLoyaltyPointsSensor(OrangeBaseSensor):
    """Sensor for total loyalty points."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "loyalty_points", "Loyalty Points")
        self._attr_icon = "mdi:star-circle"
        self._attr_state_class = SensorStateClass.TOTAL

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data and "summary" in self.coordinator.data:
            return self.coordinator.data["summary"].get("total_loyalty_points")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        attrs = {}
        if self.coordinator.data and "subscriptions_summary" in self.coordinator.data:
            for profile in self.coordinator.data["subscriptions_summary"]:
                profile_id = profile.get("profileId")
                points = profile.get("totalPointsInOnlineShop", 0)
                value = profile.get("totalValueInOnlineShop", 0)
                
                if profile_id:
                    attrs[f"profile_{profile_id}_points"] = points
                    attrs[f"profile_{profile_id}_value_ron"] = value
        return attrs


class OrangeTotalUnpaidBillsSensor(OrangeBaseSensor):
    """Sensor for total unpaid bills across all profiles."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "total_unpaid_bills", "Total Unpaid Bills")
        self._attr_icon = "mdi:currency-eur"
        self._attr_native_unit_of_measurement = "RON"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data and "unpaid_bills" in self.coordinator.data:
            return self.coordinator.data["unpaid_bills"].get("total_amount", 0.0)
        return 0.0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        attrs = {}
        if self.coordinator.data and "unpaid_bills" in self.coordinator.data:
            unpaid_bills = self.coordinator.data["unpaid_bills"]
            attrs["total_count"] = unpaid_bills.get("total_count", 0)
            
            # Add breakdown by profile
            for profile_id, bill_info in unpaid_bills.get("by_profile", {}).items():
                attrs[f"profile_{profile_id}_amount"] = bill_info.get("amount", 0.0)
                attrs[f"profile_{profile_id}_due_date"] = bill_info.get("due_date")
                attrs[f"profile_{profile_id}_name"] = bill_info.get("profile_name")
        
        return attrs


class OrangeProfileUnpaidBillsSensor(OrangeBaseSensor):
    """Sensor for unpaid bills for a specific profile."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        profile_id: int,
        profile_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            entry,
            f"profile_{profile_id}_unpaid_bills",
            f"Profile {profile_name} Unpaid Bills",
        )
        self._profile_id = profile_id
        self._attr_icon = "mdi:receipt-text"
        self._attr_native_unit_of_measurement = "RON"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data and "unpaid_bills" in self.coordinator.data:
            by_profile = self.coordinator.data["unpaid_bills"].get("by_profile", {})
            profile_data = by_profile.get(str(self._profile_id), {})
            return profile_data.get("amount", 0.0)
        return 0.0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        attrs = {}
        if self.coordinator.data and "unpaid_bills" in self.coordinator.data:
            by_profile = self.coordinator.data["unpaid_bills"].get("by_profile", {})
            profile_data = by_profile.get(str(self._profile_id), {})
            
            attrs["services_amount"] = profile_data.get("services", 0.0)
            attrs["installments_amount"] = profile_data.get("installments", 0.0)
            attrs["due_date"] = profile_data.get("due_date")
            attrs["has_invoices"] = profile_data.get("has_invoices", False)
            attrs["profile_name"] = profile_data.get("profile_name")
        
        return attrs


class OrangeProfileSensor(OrangeBaseSensor):
    """Sensor for a specific profile."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        profile_id: int,
        profile_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            entry,
            f"profile_{profile_id}",
            f"Profile {profile_name}",
        )
        self._profile_id = profile_id
        self._attr_icon = "mdi:account-circle"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data and "profiles" in self.coordinator.data:
            for profile in self.coordinator.data["profiles"]:
                if profile.get("id") == self._profile_id:
                    return profile.get("customerType", "Unknown")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        attrs = {}
        if self.coordinator.data and "profiles" in self.coordinator.data:
            for profile in self.coordinator.data["profiles"]:
                if profile.get("id") == self._profile_id:
                    attrs["name"] = profile.get("name")
                    attrs["ocn"] = profile.get("ocn")
                    attrs["customer_type"] = profile.get("customerType")
                    attrs["status"] = profile.get("status")
                    attrs["is_admin"] = profile.get("admin", False)
                    
                    # Add next invoice date if available
                    next_invoice = profile.get("nextInvoicePaymentDate")
                    if next_invoice:
                        from datetime import datetime
                        attrs["next_invoice_date"] = datetime.fromtimestamp(
                            next_invoice / 1000
                        ).isoformat()
                    
                    break
        return attrs


class OrangeSubscriberSensor(OrangeBaseSensor):
    """Sensor for a specific subscriber."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        subscriber_id: int,
        msisdn: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator,
            entry,
            f"subscriber_{subscriber_id}",
            f"Subscriber {msisdn}",
        )
        self._subscriber_id = subscriber_id
        self._msisdn = msisdn
        self._attr_icon = "mdi:cellphone"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data and "subscribers" in self.coordinator.data:
            for subscriber in self.coordinator.data["subscribers"]:
                if subscriber.get("subscriberId") == self._subscriber_id:
                    return subscriber.get("status", "Unknown")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        attrs = {}
        if self.coordinator.data and "subscribers" in self.coordinator.data:
            for subscriber in self.coordinator.data["subscribers"]:
                if subscriber.get("subscriberId") == self._subscriber_id:
                    attrs["msisdn"] = subscriber.get("msisdn")
                    attrs["profile_id"] = subscriber.get("profileId")
                    attrs["status"] = subscriber.get("status")
                    attrs["subscription_type"] = subscriber.get("subscriberTypeDisplayName")
                    attrs["subscription_name"] = subscriber.get("subscriptionName")
                    attrs["subscriber_type"] = subscriber.get("subscriberType")
                    attrs["contact_name"] = subscriber.get("contactName")
                    attrs["is_prepay"] = subscriber.get("prepay", False)
                    
                    break
        return attrs
