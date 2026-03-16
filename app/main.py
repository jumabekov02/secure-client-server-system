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
    if not (data.client_id == "m" and data.password == "123"):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data.client_id)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/protected")
def protected_route(client_id: str = Depends(verify_token)):
    return {"message": "Access granted", "client_id": client_id}


@app.post("/data/submit")
def submit_data(req: SubmitRequest, client_id: str = Depends(verify_token)):
    if client_id != req.client_id:
        raise HTTPException(status_code=401, detail="Token client_id mismatch")

    public_key = load_and_verify_client_cert(req.certificate)
    verify_payload_signature(public_key, req.payload, req.signature)
    check_nonce(req.payload["nonce"])

    return {
        "status": "accepted",
        "from": client_id,
        "payload": req.payload,
    }