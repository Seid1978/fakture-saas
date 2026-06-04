import os
from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from auth.auth import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])

# =========================
# ENV
# =========================
LEMON_CHECKOUT_URL = os.getenv("LEMON_CHECKOUT_URL")


# =========================
# CREATE CHECKOUT SESSION (LEMON SQUEEZY)
# =========================
@router.post("/create-checkout-session")
def create_checkout_session(
    current_user: User = Depends(get_current_user)
):

    if not LEMON_CHECKOUT_URL:
        raise HTTPException(
            status_code=500,
            detail="LEMON_CHECKOUT_URL is not set in .env"
        )

    # 🔥 optional: attach user id for webhook tracking
    checkout_url = f"{LEMON_CHECKOUT_URL}?checkout[custom][user_id]={current_user.id}"

    return {
        "url": checkout_url
    }