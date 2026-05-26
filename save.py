from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from jose import jwt, JWTError
from datetime import datetime, timedelta

from pydantic import BaseModel
import hashlib

# -------------------
# APP
# -------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------
# DB
# -------------------
DATABASE_URL = "sqlite:///./invoices.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# -------------------
# SECURITY
# -------------------
SECRET_KEY = "secret123"
ALGORITHM = "HS256"

security = HTTPBearer()

# -------------------
# MODELS
# -------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    client = Column(String)
    amount = Column(Float)
    owner = Column(String)

Base.metadata.create_all(bind=engine)

# -------------------
# SCHEMAS
# -------------------
class UserAuth(BaseModel):
    username: str
    password: str

class InvoiceCreate(BaseModel):
    client: str
    amount: float

# -------------------
# DB SESSION
# -------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------
# PASSWORD (SHA256 SAFE)
# -------------------
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain: str, hashed: str):
    return hashlib.sha256(plain.encode()).hexdigest() == hashed

# -------------------
# JWT
# -------------------
def create_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

        return username

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# -------------------
# REGISTER
# -------------------
@app.post("/register")
def register(data: UserAuth, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        username=data.username,
        password=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "user created"}

# -------------------
# LOGIN
# -------------------
@app.post("/login")
def login(data: UserAuth, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.username == data.username).first()

    if not user:
        raise HTTPException(status_code=401, detail="invalid credentials")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="invalid credentials")

    token = create_token(user.username)

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# -------------------
# INVOICES (PROTECTED)
# -------------------
@app.get("/invoices")
def get_invoices(
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    return db.query(Invoice).filter(Invoice.owner == user).all()

@app.post("/invoices")
def create_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    inv = Invoice(
        client=data.client,
        amount=data.amount,
        owner=user
    )

    db.add(inv)
    db.commit()
    db.refresh(inv)

    return inv

# -------------------
# STATS
# -------------------
@app.get("/stats")
def stats(
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    invoices = db.query(Invoice).filter(Invoice.owner == user).all()

    return {
        "total_invoices": len(invoices),
        "total_revenue": sum(i.amount for i in invoices)
    }