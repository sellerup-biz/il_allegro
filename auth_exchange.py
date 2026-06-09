"""
Exchanges an Allegro authorization_code for a refresh_token and stores it
in GitHub Secrets as REFRESH_TOKEN_<SHOP>. Runs inside GitHub Actions.
"""
import os
import requests
from gh_secret import save_secret

REDIRECT_URI = "https://sellerup-biz.github.io/il_allegro/callback.html"
SHOP = os.environ["SHOP"]   # IL
CODE = os.environ["CODE"]

CLIENT_ID     = os.environ[f"CLIENT_ID_{SHOP}"]
CLIENT_SECRET = os.environ[f"CLIENT_SECRET_{SHOP}"]
SECRET_NAME   = f"REFRESH_TOKEN_{SHOP}"

SHOP_NAMES = {"IL": "IL_read"}
print(f"Магазин: {SHOP_NAMES.get(SHOP, SHOP)}")

# 1. authorization_code -> access_token + refresh_token
print("Обмениваем code -> tokens...")
r = requests.post(
    "https://allegro.pl/auth/oauth/token",
    auth=(CLIENT_ID, CLIENT_SECRET),
    data={
        "grant_type": "authorization_code",
        "code": CODE,
        "redirect_uri": REDIRECT_URI,
    },
    timeout=30,
)
data = r.json()
if "refresh_token" not in data:
    print(f"ОШИБКА Allegro (HTTP {r.status_code}): {data}")
    raise SystemExit(1)

print("Получен access_token + refresh_token")

# 2. Сохраняем refresh_token в GitHub Secrets (зашифровано)
print(f"Сохраняем {SECRET_NAME} в GitHub Secrets...")
status = save_secret(SECRET_NAME, data["refresh_token"])
print(f"✅ {SECRET_NAME} сохранён (HTTP {status})")
print(f"\n🎉 Авторизация {SHOP_NAMES.get(SHOP, SHOP)} завершена!")
