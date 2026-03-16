import base64
import json
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


PRIVATE_PATH = Path("keys/client_private_key.pem")


def canonical_json(data: dict) -> bytes:
    s = json.dumps(data, separators=(",", ":"), sort_keys=True)
    return s.encode("utf-8")


def main():
    payload = {"exam": "system_security", "score": 28}

    private_pem = PRIVATE_PATH.read_bytes()
    private_key = serialization.load_pem_private_key(private_pem, password=None)

    signature = private_key.sign(
        canonical_json(payload),
        ec.ECDSA(hashes.SHA256())
    )

    signature_b64 = base64.b64encode(signature).decode("utf-8")

    print("Payload:", payload)
    print("Signature (base64):", signature_b64)


if __name__ == "__main__":
    main()
