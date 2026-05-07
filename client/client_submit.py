import base64
import json
from pathlib import Path
import uuid

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


BASE_URL = "http://127.0.0.1:8000"

PRIVATE_KEY_PATH = Path("certs/client/client.key")
CERT_PATH = Path("certs/client/client.crt")


def canonical_json(data: dict) -> bytes:
    return json.dumps(data, separators=(",", ":"), sort_keys=True).encode()


def sign_payload(payload: dict) -> str:
    private_key = serialization.load_pem_private_key(
        PRIVATE_KEY_PATH.read_bytes(),
        password=None
    )

    signature = private_key.sign(
        canonical_json(payload),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    return base64.b64encode(signature).decode()


def load_certificate_b64() -> str:
    cert_pem = CERT_PATH.read_bytes()
    return base64.b64encode(cert_pem).decode()


def login(client_id: str, password: str) -> str:
    response = requests.post(
        f"{BASE_URL}/login",
        json={"client_id": client_id, "password": password}
    )

    response.raise_for_status()
    return response.json()["access_token"]


def submit(token: str, client_id: str, payload: dict, signature: str, certificate: str):

    headers = {"Authorization": f"Bearer {token}"}

    body = {
        "client_id": client_id,
        "payload": payload,
        "signature": signature,
        "certificate": certificate,
    }

    response = requests.post(
        f"{BASE_URL}/data/submit",
        json=body,
        headers=headers
    )

    print("Status:", response.status_code)
    print("Response:", response.text)


def main():
    print("Client started")

    client_id = "m"
    password = "123"

    payload = {
        "exam": "system_security",
        "score": 28,
        "nonce": str(uuid.uuid4()) #str(uuid.uuid4()) #"abc123" 
    }

    token = login(client_id, password)

    signature = sign_payload(payload)

    #payload["score"] = 31

    certificate = load_certificate_b64()

    submit(token, client_id, payload, signature, certificate)


if __name__ == "__main__":
    main()