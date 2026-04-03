from fastapi import APIRouter, HTTPException
from jose import jwt
from datetime import datetime, timedelta
from app.models.schemas import Token, TokenRequest
from app.config import settings

router = APIRouter()

# Fake user for demo purposes (in real apps, this comes from a database)
FAKE_USER = {
    "username": "admin",
    "password": "admin123"
}


def create_access_token(data: dict) -> str:
    """
    Creates a JWT token that expires after set minutes.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


@router.post("/token", response_model=Token)
def login(request: TokenRequest):
    """
    User sends username + password → gets back a JWT token.
    """
    if request.username != FAKE_USER["username"] or request.password != FAKE_USER["password"]:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": request.username})
    return {"access_token": token, "token_type": "bearer"}