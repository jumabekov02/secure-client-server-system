from fastapi import FastAPI, HTTPException, Depends

from app.models import LoginRequest, SubmitRequest
from app.auth import create_access_token, verify_token
from app.crypto_utils import (
    load_and_verify_client_cert,
    verify_payload_signature,
    check_nonce,
)

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Server is running"}


@app.post("/login")
def login(data: LoginRequest):
    print(f"\n=== Login Attempt ===")
    print(f"Client ID: {data.client_id}")

    if not (data.client_id == "m" and data.password == "123"):
        print("Login failed: invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    print("Login successful: JWT token issued")

    token = create_access_token(data.client_id)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/protected")
def protected_route(client_id: str = Depends(verify_token)):
    return {"message": "Access granted", "client_id": client_id}


@app.post("/data/submit")
def submit_data(req: SubmitRequest, client_id: str = Depends(verify_token)):

    print("\n=== New Secure Request ===")
    print(f"Authenticated client: {client_id}")

    print("Step 1: Checking client_id match...")

    if client_id != req.client_id:
        print("client_id mismatch detected")
        raise HTTPException(status_code=401, detail="Token client_id mismatch")
    
    print("Step 2: Validating client certificate...")
    public_key = load_and_verify_client_cert(req.certificate)

    print("Step 3: Verifying digital signature...")
    verify_payload_signature(public_key, req.payload, req.signature)

    print("Step 4: Checking nonce (replay protection)...")
    check_nonce(req.payload["nonce"])

    print("Request accepted successfully\n")
    
    return {
        "status": "accepted",
        "from": client_id,
        "payload": req.payload,
    }