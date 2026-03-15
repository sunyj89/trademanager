from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", response_model=schemas.PaymentOut)
def create_payment(payload: schemas.PaymentCreate, db: Session = Depends(get_db)):
    contract = db.query(models.Contract).filter(models.Contract.id == payload.contract_id).first()
    if contract is None:
        raise HTTPException(status_code=400, detail="contract_id does not exist")
    if contract.status == "cancelled":
        raise HTTPException(status_code=400, detail="cannot add payment to cancelled contract")

    paid_amount = crud.get_contract_paid_amount(db, contract.id)
    if paid_amount + payload.amount > contract.amount:
        raise HTTPException(status_code=400, detail="payment exceeds contract amount")

    return crud.create_payment(db, payload)


@router.get("", response_model=list[schemas.PaymentOut])
def list_payments(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    contract_id: int | None = None,
):
    return crud.list_payments(db, limit=limit, offset=offset, contract_id=contract_id)
