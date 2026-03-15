from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=schemas.LeadOut)
def create_lead(payload: schemas.LeadCreate, db: Session = Depends(get_db)):
    return crud.create_lead(db, payload)


@router.get("", response_model=list[schemas.LeadOut])
def list_leads(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    source: str | None = None,
):
    return crud.list_leads(db, limit=limit, offset=offset, source=source)


@router.post("/{lead_id}/convert", response_model=schemas.LeadConvertResult)
def convert_lead(lead_id: int, payload: schemas.LeadConvertRequest, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if lead is None:
        raise HTTPException(status_code=404, detail="lead not found")
    if lead.status == "converted":
        raise HTTPException(status_code=409, detail="lead already converted")

    customer_name = payload.customer_name or lead.company
    customer = models.Customer(
        name=customer_name,
        country=payload.country,
        customer_type=payload.customer_type,
        source_channel=lead.source,
        owner=lead.owner,
    )
    db.add(customer)

    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="customer name already exists")

    opportunity = None
    if payload.create_opportunity:
        opportunity = models.Opportunity(
            customer_id=customer.id,
            product=lead.product_interest,
            expected_amount=payload.expected_amount,
            stage="qualification",
        )
        db.add(opportunity)

    lead.status = "converted"
    db.commit()

    return schemas.LeadConvertResult(
        lead_id=lead.id,
        customer_id=customer.id,
        opportunity_id=opportunity.id if opportunity else None,
    )
