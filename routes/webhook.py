import os
import hmac
import hashlib
import json

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models.user import User

router = APIRouter(prefix="/webhook", tags=["Webhook"])

# =========================
# ENV
# =========================
WEBHOOK_SECRET = os.getenv("LEMON_WEBHOOK_SECRET")


# =========================
# DB SESSION (LOCAL SAFE)
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# VERIFY SIGNATURE
# =========================
def verify_signature(raw_body: bytes, signature: str):
    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret missing")

    if not signature:
        return False

    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


# =========================
# LEMON SQUEEZY WEBHOOK
# =========================
@router.post("/lemon-squeezy")
async def lemon_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    raw_body = await request.body()

    signature = (
        request.headers.get("X-Signature")
        or request.headers.get("X-Signature-256")
    )

    # =========================
    # SECURITY CHECK
    # =========================
    if not verify_signature(raw_body, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    # parse JSON safely
    try:
        event = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # =========================
    # EVENT TYPE
    # =========================
    event_name = event.get("meta", {}).get("event_name")

    if event_name in ["order_created", "subscription_payment_success"]:

        data = event.get("data", {})
        attributes = data.get("attributes", {})

        user_id = (
            attributes.get("custom_data", {}).get("user_id")
            or attributes.get("user_id")
        )

        if not user_id:
            return {"status": "missing user_id"}

        user = db.query(User).filter(User.id == int(user_id)).first()

        if user and not user.is_premium:
            user.is_premium = True
            db.commit()

    return {"status": "success"}