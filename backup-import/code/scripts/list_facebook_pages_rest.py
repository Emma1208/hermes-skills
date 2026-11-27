#!/usr/bin/env python3
import requests, json, re
from pathlib import Path

p = Path('/data/data/com.termux/files/home/.hermes/config.yaml')
api_key = re.search(r"x-api-key: \"([^\"]+)\"", p.read_text()).group(1)
CA_ID = "ca_fBpRB-AgyUng"
USER_ID = "pg-test-50870525-657b-4048-ba4a-cf30768f7be5"
BASE_URL = "https://backend.composio.dev/api/v3"
session = requests.Session()
session.headers.update({"x-api-key": api_key, "Accept": "application/json", "Content-Type": "application/json"})
r = session.get(f"{BASE_URL}/connected_accounts", params={"user_id": USER_ID, "toolkit": "facebook"}, timeout=30)
r.raise_for_status()
accounts = r.json().get("items", [])
account = next((a for a in accounts if a.get("id") == CA_ID), None)
if not account:
    raise SystemExit(f"Account {CA_ID} not found.")
print("account_status:", account.get("status"))
print("account_id:", account.get("id"))
print("toolkit:", account.get("toolkit", {}).get("slug"))

tool_payload = {
    "toolkit_slug": "facebook",
    "connected_account_id": CA_ID,
    "user_id": USER_ID,
    "name": "FACEBOOK_LIST_MANAGED_PAGES",
    "arguments": {}
}
r2 = session.post(f"{BASE_URL}/tools/call", json=tool_payload, timeout=30)
print("list_pages_status:", r2.status_code)
print(r2.text[:1000])
