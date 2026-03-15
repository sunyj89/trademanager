from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(prefix="/followups", tags=["followups"])


def _check_target_exists(db: Session, payload: schemas.FollowUpCreate):
    if payload.lead_id is not None:
        if db.query(models.Lead).filter(models.Lead.id == payload.lead_id).first() is None:
            raise HTTPException(status_code=400, detail="lead_id does not exist")
    if payload.customer_id is not None:
        if db.query(models.Customer).filter(models.Customer.id == payload.customer_id).first() is None:
            raise HTTPException(status_code=400, detail="customer_id does not exist")
    if payload.opportunity_id is not None:
        if db.query(models.Opportunity).filter(models.Opportunity.id == payload.opportunity_id).first() is None:
            raise HTTPException(status_code=400, detail="opportunity_id does not exist")


@router.post("", response_model=schemas.FollowUpOut)
def create_followup(payload: schemas.FollowUpCreate, db: Session = Depends(get_db)):
    _check_target_exists(db, payload)
    return crud.create_followup(db, payload)


@router.get("", response_model=list[schemas.FollowUpOut])
def list_followups(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    owner: str | None = None,
):
    return crud.list_followups(db, limit=limit, offset=offset, owner=owner)
