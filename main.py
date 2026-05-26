from fastapi import FastAPI, HTTPException, Depends, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.pdfgen import canvas

app = FastAPI()

# -------------------
# CORS
# -------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------
# JWT CONFIG
# -------------------
SECRET_KEY = "supersecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# -------------------
# FAKE DATABASE
# -------------------
invoices = []
invoice_id_counter = 1

# -------------------
# MODELS
# -------------------
class Invoice(BaseModel):
    client: str
    amount: float

class LoginData(BaseModel):
    username: str
    password: str


# -------------------
# JWT CREATE
# -------------------
def create_token(data: dict):
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# -------------------
# AUTH CHECK
# -------------------
def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="No token")

    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user = payload.get("sub")
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalid or expired")


# -------------------
# LOGIN
# -------------------
@app.post("/login")
def login(data: LoginData):
    if data.username == "Marko" and data.password == "1234":
        token = create_token({"sub": data.username})
        return {"access_token": token, "token_type": "bearer"}

    raise HTTPException(status_code=401, detail="Invalid login")


# -------------------
# GET INVOICES (SAAS)
# -------------------
@app.get("/invoices")
def get_invoices(user: str = Depends(get_current_user)):
    return [inv for inv in invoices if inv["owner"] == user]


# -------------------
# CREATE INVOICE (SAAS)
# -------------------
@app.post("/invoices")
def create_invoice(invoice: Invoice, user: str = Depends(get_current_user)):
    global invoice_id_counter

    new_invoice = {
        "id": invoice_id_counter,
        "client": invoice.client,
        "amount": invoice.amount,
        "owner": user
    }

    invoices.append(new_invoice)
    invoice_id_counter += 1

    return new_invoice


# -------------------
# DELETE INVOICE (SAAS)
# -------------------
@app.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: int, user: str = Depends(get_current_user)):
    global invoices

    invoices = [
        inv for inv in invoices
        if not (inv["id"] == invoice_id and inv["owner"] == user)
    ]

    return {"message": "Deleted"}


# -------------------
# PDF DOWNLOAD (SAAS)
# -------------------
@app.get("/invoices/{invoice_id}/pdf")
def generate_pdf(invoice_id: int, user: str = Depends(get_current_user)):
    invoice = next(
        (i for i in invoices if i["id"] == invoice_id and i["owner"] == user),
        None
    )

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("Helvetica-Bold", 18)
    p.drawString(100, 800, "INVOICE")

    p.setFont("Helvetica", 12)
    p.drawString(100, 760, f"Invoice ID: {invoice['id']}")
    p.drawString(100, 740, f"Client: {invoice['client']}")
    p.drawString(100, 720, f"Amount: {invoice['amount']} €")
    p.drawString(100, 700, f"Owner: {user}")

    p.showPage()
    p.save()

    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{invoice_id}.pdf"
        }
    )


# -------------------
# STATS (SAAS DASHBOARD)
# -------------------
@app.get("/stats")
def get_stats(user: str = Depends(get_current_user)):
    user_invoices = [inv for inv in invoices if inv["owner"] == user]

    total_invoices = len(user_invoices)
    total_revenue = sum(inv["amount"] for inv in user_invoices)
    avg_invoice = total_revenue / total_invoices if total_invoices > 0 else 0

    return {
        "total_invoices": total_invoices,
        "total_revenue": total_revenue,
        "avg_invoice": avg_invoice
    }