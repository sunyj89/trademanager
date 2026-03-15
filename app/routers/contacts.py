from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.post("", response_model=schemas.ContactOut)
def create_contact(payload: schemas.ContactCreate, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == payload.customer_id).first()
    if customer is None:
        raise HTTPException(status_code=400, detail="customer_id does not exist")
    return crud.create_contact(db, payload)


@router.get("", response_model=list[schemas.ContactOut])
def list_contacts(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    customer_id: int | None = None,
):
    return crud.list_contacts(db, limit=limit, offset=offset, customer_id=customer_id)
