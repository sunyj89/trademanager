from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.post("", response_model=schemas.ContractOut)
def create_contract(payload: schemas.ContractCreate, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == payload.customer_id).first()
    if customer is None:
        raise HTTPException(status_code=400, detail="customer_id does not exist")

    if payload.opportunity_id is not None:
        opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == payload.opportunity_id).first()
        if opportunity is None:
            raise HTTPException(status_code=400, detail="opportunity_id does not exist")
        if opportunity.customer_id != payload.customer_id:
            raise HTTPException(status_code=400, detail="opportunity does not belong to customer")

    try:
        return crud.create_contract(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="contract_no already exists")


@router.get("", response_model=list[schemas.ContractOut])
def list_contracts(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: str | None = None,
):
    return crud.list_contracts(db, limit=limit, offset=offset, status=status)


@router.post("/{contract_id}/status", response_model=schemas.ContractOut)
def update_contract_status(contract_id: int, payload: schemas.ContractStatusUpdateRequest, db: Session = Depends(get_db)):
    contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
    if contract is None:
        raise HTTPException(status_code=404, detail="contract not found")

    if contract.status == payload.status:
        return contract

    if contract.status == "completed" and payload.status != "completed":
        raise HTTPException(status_code=409, detail="completed contract status cannot be changed")

    if payload.status == "cancelled":
        has_payment = db.query(models.Payment).filter(models.Payment.contract_id == contract.id).first() is not None
        if has_payment:
            raise HTTPException(status_code=409, detail="cannot cancel contract with payments")

    if payload.status == "completed":
        paid_amount = crud.get_contract_paid_amount(db, contract.id)
        if paid_amount < contract.amount:
            raise HTTPException(status_code=409, detail="cannot complete contract before full payment")

    contract.status = payload.status
    db.commit()
    db.refresh(contract)
    return contract
