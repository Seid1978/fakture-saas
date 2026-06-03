from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.models import User

from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from datetime import datetime, timedelta

# 🔐 CONFIG
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()

# 🔐 HASHING (stable)
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

security = HTTPBearer()


# 📦 SCHEMAS
class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


# 🔑 CREATE TOKEN (WITH EXPIRY)
def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# 🔓 DECODE TOKEN (STRICT)
def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token expired or invalid"
        )


# 🚀 REGISTER
@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_password = pwd_context.hash(data.password)

    new_user = User(
        email=data.email,
        password=hashed_password,
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created"}


# 🔐 LOGIN
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not pwd_context.verify(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "id": user.id,
        "sub": user.email,
        "role": user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# 👤 CURRENT USER (SECURE)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    payload = decode_token(token)

    user = db.query(User).filter(User.id == payload["id"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# 👤 /ME
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }


# 🔐 ROLE SYSTEM (SaaS READY)
def require_role(role: str):
    def checker(current_user: User = Depends(get_current_user)):

        # admin always has access (SaaS pattern)
        if current_user.role != "admin" and current_user.role != role:
            raise HTTPException(status_code=403, detail="Forbidden")

        return current_user

    return checker


# 🧪 ADMIN TEST ROUTE
@router.get("/admin")
def admin_only(user: User = Depends(require_role("admin"))):
    return {"message": f"Welcome admin {user.email}"}