from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=schemas.CustomerOut)
def create_customer(payload: schemas.CustomerCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_customer(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="customer name already exists")


@router.get("", response_model=list[schemas.CustomerOut])
def list_customers(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    country: str | None = None,
):
    return crud.list_customers(db, limit=limit, offset=offset, country=country)
