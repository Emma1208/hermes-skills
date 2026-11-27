import requests, json

with open("/data/data/com.termux/files/home/.fb_page_token.txt") as f:
    TOKEN = f.read().strip()

print(f"Token length: {len(TOKEN)}")
print(f"Token start: {TOKEN[:30]}...")
print()

# Test 1: /me
print("=== TEST 1: /me ===")
r = requests.get(f"https://graph.facebook.com/v25.0/me?access_token={TOKEN}&fields=id,name", timeout=15)
print(f"HTTP {r.status_code}: {r.text[:400]}")
print()

# Test 2: /me/accounts
print("=== TEST 2: /me/accounts ===")
r2 = requests.get(f"https://graph.facebook.com/v25.0/me/accounts?access_token={TOKEN}", timeout=15)
print(f"HTTP {r2.status_code}")
data = r2.json()
pages = data.get("data", [])
for p in pages:
    print(f"  Page: {p['name']} (ID: {p['id']})")
    pt = p.get('access_token', '')
    print(f"  Page token: {pt[:40] if pt else 'N/A'}...")
print()

# Test 3: Page spécifique
print("=== TEST 3: Page 555987340922131 ===")
r3 = requests.get(f"https://graph.facebook.com/v25.0/555987340922131?access_token={TOKEN}&fields=id,name,access_token", timeout=15)
print(f"HTTP {r3.status_code}: {r3.text[:400]}")
print()

# Test 4: Publication test (just fields, no actual post)
print("=== TEST 4: Page feed ===")
r4 = requests.get(f"https://graph.facebook.com/v25.0/555987340922131/feed?access_token={TOKEN}&limit=2&fields=id,message,created_time", timeout=15)
print(f"HTTP {r4.status_code}")
if r4.ok:
    for post in r4.json().get("data", []):
        msg = (post.get('message', '')[:80])
        print(f"  Post {post['id']}: {msg}...")
else:
    print(r4.text[:400])
