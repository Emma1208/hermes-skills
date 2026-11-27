import requests, json

with open("/data/data/com.termux/files/home/.fb_page_token.txt") as f:
    USER_TOKEN=f.read...=== TEST: Récupération page token pour 'L'absolu et moi' ===")
r = requests.get(f"https://graph.facebook.com/v25.0/me/accounts?access_token={USER_TOKEN}", timeout=15)
pages = r.json().get("data", [])

PAGE_TOKEN = None
PAGE_ID = "555987340922131"
for p in pages:
    if p["id"] == PAGE_ID:
        PAGE_TOKEN = p["access_token"]
        print(f"Page token récupéré: {PAGE_TOKEN[:40]}... (len={len(PAGE_TOKEN)})")
        break

if not PAGE_TOKEN:
    # Try to get from page endpoint
    r2 = requests.get(f"https://graph.facebook.com/v25.0/{PAGE_ID}?access_token={USER_TOKEN}&fields=access_token", timeout=15)
    PAGE_TOKEN = r2.json().get("access_token")
    print(f"Page token (fallback): {PAGE_TOKEN[:40] if PAGE_TOKEN else 'FAIL'}...")

print()

if PAGE_TOKEN:
    # Sauvegarder le page token
    with open("/data/data/com.termux/files/home/.fb_page_token.txt", "w") as f:
        f.write(PAGE_TOKEN)
    print("✅ Page token sauvegardé dans .fb_page_token.txt")

    # TEST PUBLICATION
    print()
    print("=== TEST: Publication sur 'L'absolu et moi' ===")
    msg = "🧪 Test de publication automatique — Hermes Agent • 30 juin 2026"
    r3 = requests.post(
        f"https://graph.facebook.com/v25.0/{PAGE_ID}/feed",
        data={"message": msg, "access_token": PAGE_TOKEN},
        timeout=20
    )
    print(f"HTTP {r3.status_code}")
    result = r3.json()
    print(json.dumps(result, indent=2))
    
    if "id" in result:
        post_id = result["id"]
        print(f"\n🎉 PUBLIÉ ! Post ID: {post_id}")
        print(f"🔗 https://facebook.com/{post_id}")
    else:
        print(f"\n❌ ÉCHEC: {result}")
else:
    print("❌ Impossible de récupérer le page token")
