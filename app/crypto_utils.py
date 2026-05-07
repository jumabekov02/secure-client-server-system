import base64
import json
from pathlib import Path

from fastapi import HTTPException
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

CA_CERT_PATH = Path("certs/ca/ca.crt")
CA_CERT = x509.load_pem_x509_certificate(CA_CERT_PATH.read_bytes())

USED_NONCES = set()


def canonical_json(data: dict) -> bytes:
    s = json.dumps(data, separators=(",", ":"), sort_keys=True)
    return s.encode("utf-8")


def load_and_verify_client_cert(cert_b64: str):
    cert_pem = base64.b64decode(cert_b64)
    client_cert = x509.load_pem_x509_certificate(cert_pem)

    try:
        CA_CERT.public_key().verify(
            client_cert.signature,
            client_cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            client_cert.signature_hash_algorithm,
        )
        print("Certificate is trusted")
    except InvalidSignature:
        print("Invalid certificate!")
        raise HTTPException(status_code=401, detail="Invalid client certificate")
    
    print("Public key extracted from certificate")

    return client_cert.public_key()


def verify_payload_signature(public_key, payload: dict, signature_b64: str):
    signature = base64.b64decode(signature_b64)

    try:
        public_key.verify(
            signature,
            canonical_json(payload),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        print("Signature is valid")
    except InvalidSignature:
        print("Invalid payload signature detected!")
        raise HTTPException(status_code=401, detail="Invalid payload signature")


def check_nonce(nonce: str):
    if nonce in USED_NONCES:
        print("Replay attack detected!")
        raise HTTPException(status_code=401, detail="Replay attack detected")

    USED_NONCES.add(nonce)
    print("Nonce accepted")