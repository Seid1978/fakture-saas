from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# 🔐 AUTH ROUTES
from auth.auth import router as auth_router

# 📄 INVOICE ROUTES
from routes.invoices import router as invoice_router

# 💳 STRIPE ROUTES
from routes.payment import router as stripe_router


app = FastAPI(title="Invoice SaaS API")


# 🌍 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 🔐 AUTH
app.include_router(auth_router, prefix="/auth", tags=["Auth"])


# 📄 INVOICES
app.include_router(invoice_router, prefix="/invoices", tags=["Invoices"])


# 💳 STRIPE
app.include_router(stripe_router, prefix="/stripe", tags=["Stripe"])


# 🧪 HEALTH CHECK
@app.get("/")
def root():
    return {"message": "Invoice SaaS API running 🚀"}