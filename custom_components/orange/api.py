"""API client for Orange Romania.

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

import aiohttp
from aiohttp import ClientSession

from .const import (
    BASE_URL,
    LOGIN_PAGE_URL,
    API_USER_DATA,
    API_PROFILES,
    API_SUBSCRIBERS,
    API_SUBSCRIPTIONS_SUMMARY,
    API_PROFILE_CUSTOMER_INFO,
    API_PROFILE_INVOICE_INFO,
    API_PROFILE_TRANSACTIONS,
)

_LOGGER = logging.getLogger(__name__)


class OrangeAPI:
    """API client for Orange Romania platform."""

    def __init__(self, session: ClientSession, username: str, password: str) -> None:
        """Initialize the API client.
        
        Args:
            session: aiohttp ClientSession
            username: Orange.ro account username (phone number or email)
            password: Orange.ro account password
        """
        self._session = session
        self._username = username
        self._password = password
        self._authenticated = False
        self._sso_id: int | None = None
        self._user_data: dict[str, Any] = {}

    async def authenticate(self) -> bool:
        """Authenticate with the Orange Romania platform using OAuth flow.
        
        The authentication flow:
        1. GET /myaccount/ to get redirected to login page with 'ak' parameter
        2. POST credentials to the login URL
        3. Follow OAuth redirects automatically
        4. Session cookies are set automatically by aiohttp
        
        Returns:
            True if authentication successful, False otherwise.
            
        Raises:
            Exception: If network error occurs.
        """
        try:
            _LOGGER.debug("Starting Orange.ro authentication")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ro-RO,ro;q=0.9,en;q=0.8",
            }
            
            # Step 1: GET myaccount page to get redirected to login with 'ak' parameter
            async with self._session.get(
                LOGIN_PAGE_URL,
                headers=headers,
                allow_redirects=True,
            ) as response:
                if response.status != 200:
                    _LOGGER.error(f"Failed to load login page: {response.status}")
                    return False
                
                login_url = str(response.url)
                _LOGGER.debug(f"Login URL: {login_url}")
            
            # Step 2: POST credentials to login URL
            login_data = {
                "username": self._username,
                "password": self._password,
            }
            
            headers_post = {
                **headers,
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": BASE_URL,
                "Referer": login_url,
            }
            
            async with self._session.post(
                login_url,
                data=login_data,
                headers=headers_post,
                allow_redirects=True,  # Follow OAuth redirects
            ) as response:
                if response.status != 200:
                    _LOGGER.error(f"Login failed with status: {response.status}")
                    return False
                
                final_url = str(response.url)
                _LOGGER.debug(f"Final URL after login: {final_url}")
            
            # Step 3: Verify authentication by checking userData
            user_data = await self._fetch_user_data()
            
            if user_data and user_data.get("data", {}).get("isUserLogged"):
                self._authenticated = True
                current_user = user_data.get("data", {}).get("currentUser", {})
                self._sso_id = current_user.get("ssoId")
                self._user_data = current_user
                
                _LOGGER.info(
                    f"Successfully authenticated as {current_user.get('username')} "
                    f"(SSO ID: {self._sso_id})"
                )
                return True
            else:
                _LOGGER.error("Login appeared successful but user is not logged in")
                return False
                
        except aiohttp.ClientError as err:
            _LOGGER.error(f"Network error during authentication: {err}")
            raise
        except Exception as err:
            _LOGGER.error(f"Unexpected authentication error: {err}")
            raise

    async def _fetch_user_data(self) -> dict[str, Any]:
        """Fetch user data to verify authentication.
        
        Returns:
            User data dictionary.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": f"{BASE_URL}/myaccount/",
        }
        
        async with self._session.get(API_USER_DATA, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to fetch user data: {response.status}")

    async def get_data(self) -> dict[str, Any]:
        """Fetch all account data from Orange.ro.
        
        Returns data structure:
        {
            "user": {
                "sso_id": 12345,
                "username": "user",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "primary_msisdn": "0700123456"
            },
            "profiles": [
                {
                    "id": 123,
                    "name": "JOHN DOE",
                    "ocn": "0800123456",
                    "customer_type": "EXPLORER"
                }
            ],
            "subscribers": [
                {
                    "subscriber_id": 456,
                    "msisdn": "0700123456",
                    "status": "ACTIVE",
                    "subscription_name": "Smart S"
                }
            ],
            "summary": {
                "total_profiles": 1,
                "total_subscribers": 1,
                "total_loyalty_points": 4.38
            }
        }
        
        Returns:
            Dictionary with account data.
            
        Raises:
            Exception: If API request fails.
        """
        if not self._authenticated:
            await self.authenticate()
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "application/json",
                "Referer": f"{BASE_URL}/myaccount/",
            }
            
            # Fetch all data in parallel
            profiles_data = await self._fetch_profiles(headers)
            subscribers_data = await self._fetch_subscribers(headers)
            subscriptions_data = await self._fetch_subscriptions_summary(headers)
            
            # Fetch invoice data for each profile to get unpaid bills
            profiles_list = profiles_data.get("profiles", []) if profiles_data else []
            unpaid_bills_data = await self._fetch_unpaid_bills(headers, profiles_list)
            
            # Build summary
            total_loyalty_points = 0.0
            if subscriptions_data and subscriptions_data.get("data"):
                for profile in subscriptions_data["data"]:
                    total_loyalty_points += profile.get("totalPointsInOnlineShop", 0.0)
            
            return {
                "user": {
                    "sso_id": self._user_data.get("ssoId"),
                    "username": self._user_data.get("username"),
                    "email": self._user_data.get("email"),
                    "first_name": self._user_data.get("firstName"),
                    "last_name": self._user_data.get("lastName"),
                    "primary_msisdn": self._user_data.get("primaryMsisdn"),
                    "customer_type": self._user_data.get("customerType"),
                },
                "profiles": profiles_list,
                "subscribers": subscribers_data if subscribers_data else [],
                "subscriptions_summary": subscriptions_data.get("data", []) if subscriptions_data else [],
                "unpaid_bills": unpaid_bills_data,
                "summary": {
                    "total_profiles": len(profiles_list),
                    "total_subscribers": len(subscribers_data) if subscribers_data else 0,
                    "total_loyalty_points": total_loyalty_points,
                    "total_unpaid_amount": unpaid_bills_data.get("total_amount", 0.0),
                    "total_unpaid_count": unpaid_bills_data.get("total_count", 0),
                },
            }
            
        except Exception as err:
            _LOGGER.error(f"Error fetching data: {err}")
            raise

    async def _fetch_profiles(self, headers: dict[str, str]) -> dict[str, Any]:
        """Fetch user profiles."""
        async with self._session.get(API_PROFILES, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                _LOGGER.warning(f"Failed to fetch profiles: {response.status}")
                return {}

    async def _fetch_subscribers(self, headers: dict[str, str]) -> list[dict[str, Any]]:
        """Fetch subscribers list."""
        async with self._session.get(API_SUBSCRIBERS, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                _LOGGER.warning(f"Failed to fetch subscribers: {response.status}")
                return []

    async def _fetch_subscriptions_summary(self, headers: dict[str, str]) -> dict[str, Any]:
        """Fetch subscriptions summary."""
        async with self._session.get(API_SUBSCRIPTIONS_SUMMARY, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                _LOGGER.warning(f"Failed to fetch subscriptions summary: {response.status}")
                return {}

    async def _fetch_unpaid_bills(self, headers: dict[str, str], profiles: list[dict[str, Any]]) -> dict[str, Any]:
        """Fetch unpaid bills information for all profiles.
        
        Args:
            headers: HTTP headers for requests
            profiles: List of profile dictionaries
            
        Returns:
            Dictionary with unpaid bills data:
            {
                "total_amount": 129.41,
                "total_count": 2,
                "by_profile": {
                    "100000001": {
                        "amount": 129.41,
                        "services": 129.41,
                        "installments": 0.0,
                        "due_date": "2026-02-15",
                        "has_invoices": true,
                        "profile_name": "John Doe"
                    }
                }
            }
        """
        unpaid_bills = {
            "total_amount": 0.0,
            "total_count": 0,
            "by_profile": {}
        }
        
        for profile in profiles:
            profile_id = profile.get("id")
            if not profile_id:
                continue
            
            try:
                # Fetch invoice info for this profile
                url = API_PROFILE_INVOICE_INFO.format(profile_id=profile_id)
                async with self._session.get(url, headers=headers) as response:
                    if response.status == 200:
                        invoice_response = await response.json()
                        invoice_data = invoice_response.get("data")
                        
                        # Skip if no invoice data (e.g., prepaid profiles)
                        if not invoice_data:
                            continue
                        
                        # Extract unpaid bill information
                        total_balance = invoice_data.get("totalBalanceAmount", 0.0) or 0.0
                        
                        # Only include if there's an unpaid balance
                        if total_balance > 0:
                            # Convert timestamp to date string if due_date exists
                            due_date_ts = invoice_data.get("dueDate")
                            due_date_str = None
                            if due_date_ts:
                                from datetime import datetime
                                due_date_str = datetime.fromtimestamp(due_date_ts / 1000).strftime("%Y-%m-%d")
                            
                            unpaid_bills["by_profile"][str(profile_id)] = {
                                "amount": total_balance,
                                "services": invoice_data.get("totalBalanceServices", 0.0) or 0.0,
                                "installments": invoice_data.get("totalBalanceInstallments", 0.0) or 0.0,
                                "due_date": due_date_str,
                                "has_invoices": invoice_data.get("hasInvoicesOnProfile", False),
                                "profile_name": profile.get("name", "Unknown"),
                            }
                            
                            unpaid_bills["total_amount"] += total_balance
                            unpaid_bills["total_count"] += 1
                    else:
                        _LOGGER.warning(f"Failed to fetch invoice for profile {profile_id}: {response.status}")
                        
            except Exception as err:
                _LOGGER.warning(f"Error fetching invoice for profile {profile_id}: {err}")
                continue
        
        return unpaid_bills

    async def get_profile_invoices(self, profile_id: int) -> dict[str, Any]:
        """Get invoice information for a specific profile.
        
        Args:
            profile_id: Profile ID
            
        Returns:
            Invoice data dictionary.
        """
        if not self._authenticated:
            await self.authenticate()
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": f"{BASE_URL}/myaccount/",
        }
        
        url = API_PROFILE_INVOICE_INFO.format(profile_id=profile_id)
        
        async with self._session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to fetch invoice info: {response.status}")

    async def get_profile_transactions(self, profile_id: int) -> dict[str, Any]:
        """Get transaction history for a specific profile.
        
        Args:
            profile_id: Profile ID
            
        Returns:
            Transactions data dictionary.
        """
        if not self._authenticated:
            await self.authenticate()
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": f"{BASE_URL}/myaccount/",
        }
        
        url = API_PROFILE_TRANSACTIONS.format(profile_id=profile_id)
        
        async with self._session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to fetch transactions: {response.status}")
