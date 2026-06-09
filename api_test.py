"""
End-to-end test: take REFRESH_TOKEN_<SHOP> from Secrets, get a fresh access_token,
call GET /me, and save the rotated refresh_token back to Secrets (Allegro rotates it).
Runs inside GitHub Actions. Prints no secret values.
"""
import os
import requests
from gh_secret import save_secret

SHOP = os.environ.get("SHOP", "IL")
CLIENT_ID     = os.environ[f"CLIENT_ID_{SHOP}"]
CLIENT_SECRET = os.environ[f"CLIENT_SECRET_{SHOP}"]
REFRESH_TOKEN = os.environ[f"REFRESH_TOKEN_{SHOP}"]
SECRET_NAME   = f"REFRESH_TOKEN_{SHOP}"

# 1. refresh_token -> access_token (+ a new refresh_token)
print("Обновляем access_token по refresh_token...")
r = requests.post(
    "https://allegro.pl/auth/oauth/token",
    auth=(CLIENT_ID, CLIENT_SECRET),
    data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
    timeout=30,
)
tok = r.json()
access_token = tok.get("access_token")
if not access_token:
    print(f"ОШИБКА обновления (HTTP {r.status_code}): {tok}")
    raise SystemExit(1)
print(f"✓ access_token получен, expires_in={tok.get('expires_in')}s")

# 2. Save the rotated refresh_token back so the stored one stays valid
new_rt = tok.get("refresh_token")
if new_rt and new_rt != REFRESH_TOKEN:
    save_secret(SECRET_NAME, new_rt)
    print(f"✓ {SECRET_NAME} обновлён (ротация refresh_token)")

# 3. Real API call: who am I?
me = requests.get(
    "https://api.allegro.pl/me",
    headers={"Authorization": f"Bearer {access_token}",
             "Accept": "application/vnd.allegro.public.v1+json"},
    timeout=30,
)
print(f"GET /me -> HTTP {me.status_code}")
if me.ok:
    d = me.json()
    print(f"  login: {d.get('login')} | id: {d.get('id')} | "
          f"marketplace: {(d.get('baseMarketplace') or {}).get('id')}")
    print("\n🎉 Связь с Allegro API работает!")
else:
    print(me.text[:300])
    raise SystemExit(1)
