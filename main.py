import time
import jwt
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()
SECRET_KEY = "CHANGE_ME_LATER"
ALGORITHM = "HS256"
TOKEN_TTL_SECONDS = 60 * 15 

class LoginRequest(BaseModel):
    client_id: str
    password: str

def create_access_token(client_id: str) -> str:
    now = int(time.time())
    payload = {
        "sub": client_id,
        "iat": now, 
        "exp": now + TOKEN_TTL_SECONDS
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@app.get("/")
def root():
    return {"message": "Server is running"}

@app.post("/login")
def login(data: LoginRequest): 
    if not (data.client_id == "m" and data.password == "123"):
        raise HTTPException(status_code=401, details="invalid credentials")
    
    token = create_access_token(data.client_id)
    return{"access_token": token, "token_type": "bearer"}

auth_scheme = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected")
def protected_route(client_id: str = Depends(verify_token)):
    return {"message": "Access granted", "client_id": client_id}
