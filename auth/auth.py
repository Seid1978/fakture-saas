from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import hashlib
import os

from database import SessionLocal
from models.user import User
from jose import jwt

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# =========================
# DB
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# SCHEMA
# =========================
class UserAuth(BaseModel):
    email: str
    password: str

# =========================
# PASSWORD
# =========================
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain, hashed):
    return hash_password(plain) == hashed

# =========================
# TOKEN
# =========================
def create_token(user_id: int, email: str):
    payload = {
        "user_id": user_id,
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# =========================
# REGISTER
# =========================
@router.post("/register")
def register(data: UserAuth, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        email=data.email,
        hashed_password=hash_password(data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}

# =========================
# LOGIN
# =========================
@router.post("/login")
def login(data: UserAuth, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user.id, user.email)

    return {
        "access_token": token,
        "token_type": "bearer"
    }