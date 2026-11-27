import requests, json, os

API_KEY = "ak_LdvFn7cpbdYn-HrpUwaY"
BASE = "https://backend.composio.dev"
USER_ID = "pg-test-50870525-657b-4048-ba4a-cf30768f7be5"

def get_accounts(toolkit=None):
    url = f"{BASE}/api/v3/connected_accounts"
    params = {"user_id": USER_ID}
    if toolkit:
        params["toolkit"] = toolkit
    headers = {"x-api-key": API_KEY}
    r = requests.get(url, params=params, headers=headers, timeout=20)
    return r.status_code, r.json()

# Tous les comptes
print("=== TOUS LES COMPTES CONNECTÉS ===")
status, data = get_accounts()
print(f"Status: {status}")
items = data.get("items", [])
for item in items:
    tk = item.get("toolkit", {}).get("slug", "?")
    aid = item.get("id", "?")
    st = item.get("status", "?")
    print(f"  [{st}] {tk}: {aid}")

# Facebook spécifique
print("\n=== FACEBOOK uniquement ===")
status, data = get_accounts("facebook")
print(f"Status: {status}")
items = data.get("items", [])
print(f"Comptes Facebook: {len(items)}")
for item in items:
    print(json.dumps(item, indent=2)[:2000])
