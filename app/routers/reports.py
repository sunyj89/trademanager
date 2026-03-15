from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/profit-summary", response_model=schemas.ProfitSummaryOut)
def profit_summary(db: Session = Depends(get_db)):
    return crud.summarize_profit(db)


@router.get("/pipeline-summary", response_model=schemas.PipelineSummaryOut)
def pipeline_summary(db: Session = Depends(get_db)):
    return crud.summarize_pipeline(db)


@router.get("/customer-value-summary", response_model=schemas.CustomerValueSummaryOut)
def customer_value_summary(db: Session = Depends(get_db)):
    return crud.summarize_customer_value(db)


@router.get("/agent-commission-summary", response_model=schemas.AgentCommissionSummaryOut)
def agent_commission_summary(db: Session = Depends(get_db)):
    return crud.summarize_agent_commission(db)


@router.get("/collection-progress-summary", response_model=schemas.CollectionProgressSummaryOut)
def collection_progress_summary(db: Session = Depends(get_db)):
    return crud.summarize_collection_progress(db)


@router.get("/contract-status-summary", response_model=schemas.ContractStatusSummaryOut)
def contract_status_summary(db: Session = Depends(get_db)):
    return crud.summarize_contract_status(db)
