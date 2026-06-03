import os
import stripe
from fastapi import APIRouter, HTTPException

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

if not stripe.api_key:
    raise Exception("STRIPE_SECRET_KEY is missing in environment")


@router.post("/create-checkout-session")
def create_checkout_session():

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",

            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": "Invoice SaaS Premium"
                        },
                        "unit_amount": 999,
                    },
                    "quantity": 1,
                }
            ],

            success_url="http://localhost:5173/success",
            cancel_url="http://localhost:5173/cancel",
        )

        return {"url": session.url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))