from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
from pydantic import BaseModel

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# DB connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# FAKE USERS (RBAC)
# =========================
fake_users = {
    "admin": {"role": "admin", "base_id": None},
    "commander": {"role": "commander", "base_id": 1},
    "logistics": {"role": "logistics", "base_id": None}
}


@app.get("/login")
def login(username: str):
    return fake_users.get(username, {"error": "User not found"})


# RBAC check
def check_role(role, allowed_roles):
    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Access denied")


# Logging function
def create_log(db, action, details):
    log = models.Log(action=action, details=details)
    db.add(log)
    db.commit()


# Root
@app.get("/")
def root():
    return {"message": "Backend running"}


# =========================
# PURCHASE API
# =========================
class PurchaseRequest(BaseModel):
    base_id: int
    asset_id: int
    quantity: int


@app.post("/purchases")
def create_purchase(data: PurchaseRequest, role: str, db: Session = Depends(get_db)):
    check_role(role, ["admin", "logistics"])

    purchase = models.Purchase(
        base_id=data.base_id,
        asset_id=data.asset_id,
        quantity=data.quantity
    )
    db.add(purchase)
    db.commit()

    create_log(db, "PURCHASE", f"Added {data.quantity} items")

    return {"message": "Purchase added"}


# =========================
# TRANSFER API
# =========================
class TransferRequest(BaseModel):
    from_base: int
    to_base: int
    asset_id: int
    quantity: int


@app.post("/transfer")
def transfer_asset(data: TransferRequest, role: str, db: Session = Depends(get_db)):
    check_role(role, ["admin", "logistics"])

    transfer = models.Transfer(
        from_base=data.from_base,
        to_base=data.to_base,
        asset_id=data.asset_id,
        quantity=data.quantity
    )
    db.add(transfer)
    db.commit()

    create_log(db, "TRANSFER", f"{data.quantity} items transferred")

    return {"message": "Transfer successful"}


# =========================
# ASSIGNMENT API
# =========================
class AssignmentRequest(BaseModel):
    base_id: int
    asset_id: int
    assigned_to: str
    quantity: int


@app.post("/assign")
def assign_asset(data: AssignmentRequest, role: str, db: Session = Depends(get_db)):
    check_role(role, ["admin", "commander"])

    assignment = models.Assignment(
        base_id=data.base_id,
        asset_id=data.asset_id,
        assigned_to=data.assigned_to,
        quantity=data.quantity
    )
    db.add(assignment)
    db.commit()

    create_log(db, "ASSIGNMENT", f"{data.quantity} assigned to {data.assigned_to}")

    return {"message": "Asset assigned"}


# =========================
# EXPENDITURE API
# =========================
class ExpenditureRequest(BaseModel):
    base_id: int
    asset_id: int
    quantity: int


@app.post("/expend")
def expend_asset(data: ExpenditureRequest, role: str, db: Session = Depends(get_db)):
    check_role(role, ["admin", "commander"])

    expend = models.Expenditure(
        base_id=data.base_id,
        asset_id=data.asset_id,
        quantity=data.quantity
    )
    db.add(expend)
    db.commit()

    create_log(db, "EXPENDITURE", f"{data.quantity} items used")

    return {"message": "Asset expended"}


# =========================
# DASHBOARD API
# =========================
@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    purchases = db.query(models.Purchase).all()
    transfers = db.query(models.Transfer).all()
    assignments = db.query(models.Assignment).all()
    expenditures = db.query(models.Expenditure).all()

    total_purchases = sum(p.quantity for p in purchases)
    transfer_in = sum(t.quantity for t in transfers)
    transfer_out = sum(t.quantity for t in transfers)
    total_assigned = sum(a.quantity for a in assignments)
    total_expended = sum(e.quantity for e in expenditures)

    closing_balance = total_purchases + transfer_in - transfer_out - total_assigned - total_expended

    return {
        "purchases": total_purchases,
        "assigned": total_assigned,
        "expended": total_expended,
        "closing_balance": closing_balance
    }


# =========================
# VIEW LOGS (BONUS)
# =========================
@app.get("/logs")
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(models.Log).all()
    return logs