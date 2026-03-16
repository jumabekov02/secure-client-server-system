from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from pathlib import Path

KEY_DIR = Path("keys")
PRIVATE_PATH = KEY_DIR / "client_private_key.pem"
PUBLIC_PATH = KEY_DIR / "client_public_key.pem"

def main():
    KEY_DIR.mkdir(exist_ok=True)

    # ECDSA P-256 private key
    private_key = ec.generate_private_key(ec.SECP256R1())

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),  # позже можно пароль
    )

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    PRIVATE_PATH.write_bytes(private_pem)
    PUBLIC_PATH.write_bytes(public_pem)

    print("Saved:")
    print(" -", PRIVATE_PATH)
    print(" -", PUBLIC_PATH)

if __name__ == "__main__":
    main()
