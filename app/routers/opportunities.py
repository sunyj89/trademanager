from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.post("", response_model=schemas.OpportunityOut)
def create_opportunity(payload: schemas.OpportunityCreate, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == payload.customer_id).first()
    if customer is None:
        raise HTTPException(status_code=400, detail="customer_id does not exist")

    if payload.agent_id is not None:
        agent = db.query(models.Agent).filter(models.Agent.id == payload.agent_id).first()
        if agent is None:
            raise HTTPException(status_code=400, detail="agent_id does not exist")

    return crud.create_opportunity(db, payload)


@router.get("", response_model=list[schemas.OpportunityOut])
def list_opportunities(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    stage: str | None = None,
):
    return crud.list_opportunities(db, limit=limit, offset=offset, stage=stage)


@router.post("/{opportunity_id}/mark-won", response_model=schemas.ContractOut)
def mark_opportunity_won(opportunity_id: int, payload: schemas.OpportunityWinRequest, db: Session = Depends(get_db)):
    opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if opportunity is None:
        raise HTTPException(status_code=404, detail="opportunity not found")
    if opportunity.stage == "won":
        raise HTTPException(status_code=409, detail="opportunity already won")

    existing_contract = db.query(models.Contract).filter(models.Contract.opportunity_id == opportunity.id).first()
    if existing_contract is not None:
        raise HTTPException(status_code=409, detail="contract already exists for this opportunity")

    contract = models.Contract(
        contract_no=payload.contract_no,
        customer_id=opportunity.customer_id,
        opportunity_id=opportunity.id,
        amount=payload.amount,
        currency=payload.currency,
        delivery_plan=payload.delivery_plan,
        status="signed",
    )
    db.add(contract)
    opportunity.stage = "won"

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="contract_no already exists")

    db.refresh(contract)
    return contract


@router.post("/{opportunity_id}/mark-lost", response_model=schemas.OpportunityOut)
def mark_opportunity_lost(opportunity_id: int, payload: schemas.OpportunityLostRequest, db: Session = Depends(get_db)):
    opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if opportunity is None:
        raise HTTPException(status_code=404, detail="opportunity not found")
    if opportunity.stage == "won":
        raise HTTPException(status_code=409, detail="won opportunity cannot be marked lost")
    if opportunity.stage == "lost":
        raise HTTPException(status_code=409, detail="opportunity already lost")

    opportunity.stage = "lost"
    opportunity.loss_reason = payload.loss_reason
    db.commit()
    db.refresh(opportunity)
    return opportunity
