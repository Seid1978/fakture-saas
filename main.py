import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine

# =========================
# ENV
# =========================
load_dotenv()

# =========================
# MODELS (ENSURE TABLES EXIST)
# =========================
from models.user import User
from models.invoice import Invoice

# =========================
# ROUTES
# =========================
from auth.auth import router as auth_router
from routes.invoices import router as invoices_router
from routes.payment import router as payment_router
from routes.webhook import router as webhook_router
from routes.user_routes import router as user_router


# =========================
# LIFESPAN
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Invoice SaaS API...")

    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database init error: {e}")

    yield

    print("🛑 Shutting down API...")


# =========================
# APP
# =========================
app = FastAPI(
    title="Invoice SaaS API 🚀",
    version="1.0.0",
    lifespan=lifespan
)


# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# ROUTES
# =========================
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(invoices_router, prefix="/invoices", tags=["Invoices"])
app.include_router(payment_router, prefix="/payments", tags=["Payments"])
app.include_router(webhook_router, prefix="/webhook", tags=["Webhook"])
app.include_router(user_router, prefix="/user", tags=["User"])


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def root():
    return {
        "message": "Invoice SaaS API running 🚀",
        "status": "ok",
        "docs": "/docs"
    }