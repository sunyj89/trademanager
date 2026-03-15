from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=schemas.AgentOut)
def create_agent(payload: schemas.AgentCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_agent(db, payload)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="agent name already exists")


@router.get("", response_model=list[schemas.AgentOut])
def list_agents(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return crud.list_agents(db, limit=limit, offset=offset)
