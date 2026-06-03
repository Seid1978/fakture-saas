import os
import stripe

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from auth.auth import get_current_user
from models.user import User

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


@router.post("/create-checkout-session")
def create_checkout_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",

            line_items=[
                {
                    "price_data": {
                        "currency": os.getenv("STRIPE_CURRENCY", "eur"),
                        "product_data": {
                            "name": os.getenv("STRIPE_PRODUCT_NAME", "Premium Plan")
                        },
                        "unit_amount": int(os.getenv("STRIPE_PRICE", 999)),
                    },
                    "quantity": 1,
                }
            ],

            success_url=f"{FRONTEND_URL}/success",
            cancel_url=f"{FRONTEND_URL}/cancel",

            metadata={
                "user_id": str(current_user.id)
            }
        )

        return {"url": session.url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))