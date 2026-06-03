import os
import stripe

from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.user import User

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


# =========================
# STRIPE WEBHOOK
# =========================
@router.post("/")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret missing")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            WEBHOOK_SECRET
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")


    # =========================
    # PAYMENT SUCCESS EVENT
    # =========================
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        user_id = session["metadata"].get("user_id")

        if not user_id:
            return {"status": "missing user_id"}

        # DB session
        db: Session = next(get_db())

        user = db.query(User).filter(User.id == int(user_id)).first()

        if user:
            user.is_premium = True
            db.commit()

    return {"status": "success"}