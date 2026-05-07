import time
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = "a8F2kLm9QwEr7TyUiOp3ZxCvBnM5rStY8pL1hG6dJ"
ALGORITHM = "HS256"
TOKEN_TTL_SECONDS = 60 * 15

auth_scheme = HTTPBearer()


def create_access_token(client_id: str) -> str:
    now = int(time.time())
    payload = {
        "sub": client_id,
        "iat": now,
        "exp": now + TOKEN_TTL_SECONDS
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    