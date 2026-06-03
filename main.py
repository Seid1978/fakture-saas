import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import Base, engine

load_dotenv()


# =========================
# MODELS
# =========================
from models.user import User
from models.invoice import Invoice


# =========================
# ROUTES
# =========================
from auth.auth import router as auth_router
from routes.invoices import router as invoices_router
from routes.payment import router as stripe_router
from routes.stripe_webhook import router as stripe_webhook_router
from routes.user import router as user_router


# =========================
# LIFESPAN (NEW WAY)
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


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
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:5173"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# ROUTES
# =========================
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(invoices_router, prefix="/invoices", tags=["Invoices"])
app.include_router(stripe_router, prefix="/stripe", tags=["Stripe"])

app.include_router(
    stripe_webhook_router,
    prefix="/stripe/webhook",
    tags=["Stripe Webhook"]
)

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