"""Constants for the Orange Romania integration.

Copyright (c) 2026 Emanuel Besliu
Licensed under the MIT License

DISCLAIMER: This integration is developed independently through reverse engineering
for personal and educational use only. It is NOT affiliated with, endorsed by, or
supported by Orange Romania. Orange Romania has no responsibility or liability for
this integration. Use at your own risk.
"""

DOMAIN = "orange"

# Base URLs
BASE_URL = "https://www.orange.ro"
MYACCOUNT_URL = f"{BASE_URL}/myaccount/"
API_BASE = f"{BASE_URL}/myaccount/api/v4"

# Authentication endpoints
LOGIN_PAGE_URL = f"{MYACCOUNT_URL}"
# Login endpoint is dynamic (includes 'ak' parameter from redirect)

# API endpoints
API_USER_DATA = f"{API_BASE}/userData"
API_PROFILES = f"{API_BASE}/profiles"
API_SUBSCRIBERS = f"{API_BASE}/subscribers"
API_SUBSCRIPTIONS_SUMMARY = f"{API_BASE}/packages-and-options/subscriptionsSummary"
API_PROFILE_CUSTOMER_INFO = f"{API_BASE}/profile/{{profile_id}}/customerInfo"
API_PROFILE_INVOICE_INFO = f"{API_BASE}/profile/{{profile_id}}/invoiceInfo"
API_PROFILE_TRANSACTIONS = f"{API_BASE}/profiles/{{profile_id}}/transactions"
API_PROFILE_INSTALLMENTS = f"{API_BASE}/profiles/{{profile_id}}/installmentsNew"
API_SUBSCRIBER_INFO = f"{API_BASE}/subscribers/{{subscriber_id}}"
API_ACTIVE_OPTIONS = f"{API_BASE}/activeOptions/{{subscriber_id}}"
API_MSISDN_EXTRA_INFO = f"{API_BASE}/msisdnExtraInfo/{{msisdn}}"

# Update interval
DEFAULT_SCAN_INTERVAL = 3600  # 1 hour in seconds
