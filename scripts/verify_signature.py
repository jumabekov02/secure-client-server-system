import base64
import json
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


PRIVATE_PATH = Path("keys/client_private_key.pem")
PUBLIC_PATH = Path("keys/client_public_key.pem")


def canonical_json(data: dict) -> bytes:
    s = json.dumps(data, separators=(",", ":"), sort_keys=True)
    return s.encode("utf-8")


def main():
    payload = {"exam": "system_security", "score": 28}

    # load keys
    private_key = serialization.load_pem_private_key(PRIVATE_PATH.read_bytes(), password=None)
    public_key = serialization.load_pem_public_key(PUBLIC_PATH.read_bytes())

    # sign
    signature = private_key.sign(canonical_json(payload), ec.ECDSA(hashes.SHA256()))
    signature_b64 = base64.b64encode(signature).decode("utf-8")

    # verify OK
    try:
        public_key.verify(base64.b64decode(signature_b64), canonical_json(payload), ec.ECDSA(hashes.SHA256()))
        print("Verification OK (original payload)")
    except InvalidSignature:
        print("Verification FAILED (original payload)")

    # tamper payload
    tampered = {"exam": "system_security", "score": 29}

    # verify FAIL
    try:
        public_key.verify(base64.b64decode(signature_b64), canonical_json(tampered), ec.ECDSA(hashes.SHA256()))
        print("Verification OK (tampered payload)  <-- SHOULD NOT HAPPEN")
    except InvalidSignature:
        print("Verification FAILED (tampered payload)  <-- EXPECTED")


if __name__ == "__main__":
    main()
