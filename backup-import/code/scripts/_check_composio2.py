import requests, json, sys

API_KEY = "ak_L...BASE = "https://backend.composio.dev"
CA_ID = "ca_fBpRB-AgyUng"
USER_ID = "pg-test-50870525-657b-4048-ba4a-cf30768f7be5"
HEADERS = {"x-api-key": API_KEY}

def check(label, r):
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"  HTTP {r.status_code}")
    text = r.text[:3000]
    # Hide any actual tokens
    if 'access_token' in text and '***' not in text:
        print("  ⚠️ TOKEN VISIBLE dans la réponse!")
    print(text)
    return r.json() if r.ok else None

# 1) Get specific connected account
print("=== 1) GET /connected_accounts/{id} ===")
r = requests.get(f"{BASE}/api/v3/connected_accounts/{CA_ID}", 
                 params={"user_id": USER_ID}, headers=HEADERS, timeout=20)
data = check("Account spécifique", r)

# 2) Initiate reconnect
print("\n=== 2) POST /connected_accounts/{id}/reconnect ===")
r = requests.post(f"{BASE}/api/v3/connected_accounts/{CA_ID}/reconnect",
                  params={"user_id": USER_ID}, headers=HEADERS, timeout=20)
check("Reconnect", r)

# 3) Try MCP tools/list (just to confirm 401)
print("\n=== 3) MCP tools/list ===")
MCP_URL = f"https://backend.composio.dev/v3/mcp/fa3e8ea0-2ee4-44c5-a008-02bbef38efdc?connected_account_id={CA_ID}&user_id={USER_ID}"
mcp_headers = {
    "x-api-key": API_KEY,
    "Accept": "application/json, text/event-stream;q=0.9",
    "Content-Type": "application/json"
}
r = requests.post(MCP_URL, json={
    "jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}
}, headers=mcp_headers, timeout=20)
check("MCP tools/list", r)

# 4) Try to get token via /api/v1/auth (maybe)
print("\n=== 4) GET /connected_accounts (avec fields) ===")
r = requests.get(f"{BASE}/api/v3/connected_accounts/{CA_ID}",
                 params={"user_id": USER_ID, "include_token": "true"},
                 headers=HEADERS, timeout=20)
check("Avec include_token=true", r)

print("\n=== RÉSUMÉ ===")
print("Si tous les tokens sont REDACTED → le Dashboard Composio a changé de politique.")
print("Solution: Reconnecter le compte Facebook via dashboard Composio.")
