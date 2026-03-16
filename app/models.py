from pydantic import BaseModel


class LoginRequest(BaseModel):
    client_id: str
    password: str


class SubmitRequest(BaseModel):
    client_id: str
    payload: dict
    signature: str
    certificate: str