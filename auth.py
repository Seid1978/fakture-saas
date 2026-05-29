from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from database import SessionLocal
import models

# --------------------
# CONFIG
# --------------------
SECRET_KEY = "supersecretkey123"  # kasnije prebaci u .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# --------------------
# PASSWORD HASHING
# --------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# --------------------
# JWT CREATE
# --------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --------------------
# DECODE TOKEN
# --------------------
def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

# --------------------
# OAUTH2 SCHEME
# --------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --------------------
# GET CURRENT USER (PRO VERSION)
# --------------------
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")

    if email is None:
        raise HTTPException(status_code=401, detail="Token missing subject")

    db = SessionLocal()
    user = db.query(models.User).filter(models.User.email == email).first()
    db.close()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user