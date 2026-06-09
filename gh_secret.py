"""Helper: encrypt a value with the repo's public key and store it as a GitHub Actions secret."""
import os
import base64
import requests
from nacl import encoding, public

GH_REPO = os.environ.get("GH_REPO", "sellerup-biz/il_allegro")


def save_secret(name: str, value: str, gh_token: str | None = None) -> int:
    """Create/update an Actions secret. Returns the HTTP status (201 created / 204 updated)."""
    gh_token = gh_token or os.environ["GH_TOKEN"]
    headers = {"Authorization": f"token {gh_token}", "Accept": "application/vnd.github+json"}

    pk = requests.get(
        f"https://api.github.com/repos/{GH_REPO}/actions/secrets/public-key",
        headers=headers, timeout=30,
    ).json()

    sealed = public.SealedBox(public.PublicKey(pk["key"].encode(), encoding.Base64Encoder()))
    encrypted = base64.b64encode(sealed.encrypt(value.encode())).decode()

    r = requests.put(
        f"https://api.github.com/repos/{GH_REPO}/actions/secrets/{name}",
        headers=headers,
        json={"encrypted_value": encrypted, "key_id": pk["key_id"]},
        timeout=30,
    )
    r.raise_for_status()
    return r.status_code
