from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models, schemas


def create_customer(db: Session, payload: schemas.CustomerCreate) -> models.Customer:
    obj = models.Customer(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_customers(db: Session, limit: int, offset: int, country: str | None) -> list[models.Customer]:
    stmt = select(models.Customer).order_by(models.Customer.id.desc()).limit(limit).offset(offset)
    if country:
        stmt = stmt.where(models.Customer.country == country)
    return list(db.scalars(stmt).all())


def create_lead(db: Session, payload: schemas.LeadCreate) -> models.Lead:
    obj = models.Lead(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_leads(db: Session, limit: int, offset: int, source: str | None) -> list[models.Lead]:
    stmt = select(models.Lead).order_by(models.Lead.id.desc()).limit(limit).offset(offset)
    if source:
        stmt = stmt.where(models.Lead.source == source)
    return list(db.scalars(stmt).all())


def create_agent(db: Session, payload: schemas.AgentCreate) -> models.Agent:
    obj = models.Agent(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_agents(db: Session, limit: int, offset: int) -> list[models.Agent]:
    stmt = select(models.Agent).order_by(models.Agent.id.desc()).limit(limit).offset(offset)
    return list(db.scalars(stmt).all())


def create_contact(db: Session, payload: schemas.ContactCreate) -> models.Contact:
    obj = models.Contact(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_contacts(db: Session, limit: int, offset: int, customer_id: int | None) -> list[models.Contact]:
    stmt = select(models.Contact).order_by(models.Contact.id.desc()).limit(limit).offset(offset)
    if customer_id is not None:
        stmt = stmt.where(models.Contact.customer_id == customer_id)
    return list(db.scalars(stmt).all())


def create_opportunity(db: Session, payload: schemas.OpportunityCreate) -> models.Opportunity:
    obj = models.Opportunity(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_opportunities(db: Session, limit: int, offset: int, stage: str | None) -> list[models.Opportunity]:
    stmt = select(models.Opportunity).order_by(models.Opportunity.id.desc()).limit(limit).offset(offset)
    if stage:
        stmt = stmt.where(models.Opportunity.stage == stage)
    return list(db.scalars(stmt).all())


def create_contract(db: Session, payload: schemas.ContractCreate) -> models.Contract:
    obj = models.Contract(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_contracts(db: Session, limit: int, offset: int, status: str | None) -> list[models.Contract]:
    stmt = select(models.Contract).order_by(models.Contract.id.desc()).limit(limit).offset(offset)
    if status:
        stmt = stmt.where(models.Contract.status == status)
    return list(db.scalars(stmt).all())




def get_contract_paid_amount(db: Session, contract_id: int) -> float:
    amount = db.scalar(
        select(func.coalesce(func.sum(models.Payment.amount), 0.0)).where(models.Payment.contract_id == contract_id)
    )
    return float(amount or 0.0)

def create_payment(db: Session, payload: schemas.PaymentCreate) -> models.Payment:
    obj = models.Payment(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_payments(db: Session, limit: int, offset: int, contract_id: int | None) -> list[models.Payment]:
    stmt = select(models.Payment).order_by(models.Payment.id.desc()).limit(limit).offset(offset)
    if contract_id is not None:
        stmt = stmt.where(models.Payment.contract_id == contract_id)
    return list(db.scalars(stmt).all())


def create_followup(db: Session, payload: schemas.FollowUpCreate) -> models.FollowUp:
    values = payload.model_dump(exclude_none=True)
    obj = models.FollowUp(**values)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_followups(db: Session, limit: int, offset: int, owner: str | None) -> list[models.FollowUp]:
    stmt = select(models.FollowUp).order_by(models.FollowUp.id.desc()).limit(limit).offset(offset)
    if owner:
        stmt = stmt.where(models.FollowUp.owner == owner)
    return list(db.scalars(stmt).all())


def summarize_profit(db: Session) -> schemas.ProfitSummaryOut:
    contract_count = db.scalar(select(func.count(models.Contract.id))) or 0
    payment_count = db.scalar(select(func.count(models.Payment.id))) or 0
    total_contract_amount = db.scalar(select(func.coalesce(func.sum(models.Contract.amount), 0.0))) or 0.0
    total_payment_amount = db.scalar(select(func.coalesce(func.sum(models.Payment.amount), 0.0))) or 0.0
    total_profit = db.scalar(select(func.coalesce(func.sum(models.Payment.profit), 0.0))) or 0.0
    return schemas.ProfitSummaryOut(
        contract_count=int(contract_count),
        payment_count=int(payment_count),
        total_contract_amount=float(total_contract_amount),
        total_payment_amount=float(total_payment_amount),
        total_profit=float(total_profit),
    )


def summarize_pipeline(db: Session) -> schemas.PipelineSummaryOut:
    stmt = (
        select(
            models.Opportunity.stage,
            func.count(models.Opportunity.id),
            func.coalesce(func.sum(models.Opportunity.expected_amount), 0.0),
        )
        .group_by(models.Opportunity.stage)
        .order_by(models.Opportunity.stage.asc())
    )
    rows = db.execute(stmt).all()
    items = [
        schemas.PipelineStageOut(
            stage=str(stage),
            count=int(count),
            total_expected_amount=float(total_amount),
        )
        for stage, count, total_amount in rows
    ]
    return schemas.PipelineSummaryOut(items=items)


def summarize_customer_value(db: Session) -> schemas.CustomerValueSummaryOut:
    contract_sum_sq = (
        select(
            models.Contract.customer_id.label("customer_id"),
            func.coalesce(func.sum(models.Contract.amount), 0.0).label("contract_amount"),
        )
        .group_by(models.Contract.customer_id)
        .subquery()
    )

    payment_sum_sq = (
        select(
            models.Contract.customer_id.label("customer_id"),
            func.coalesce(func.sum(models.Payment.amount), 0.0).label("payment_amount"),
            func.coalesce(func.sum(models.Payment.profit), 0.0).label("profit_amount"),
        )
        .select_from(models.Contract)
        .join(models.Payment, models.Payment.contract_id == models.Contract.id, isouter=True)
        .group_by(models.Contract.customer_id)
        .subquery()
    )

    stmt = (
        select(
            models.Customer.id,
            models.Customer.name,
            func.coalesce(contract_sum_sq.c.contract_amount, 0.0),
            func.coalesce(payment_sum_sq.c.payment_amount, 0.0),
            func.coalesce(payment_sum_sq.c.profit_amount, 0.0),
        )
        .select_from(models.Customer)
        .join(contract_sum_sq, contract_sum_sq.c.customer_id == models.Customer.id, isouter=True)
        .join(payment_sum_sq, payment_sum_sq.c.customer_id == models.Customer.id, isouter=True)
        .order_by(models.Customer.id.asc())
    )

    rows = db.execute(stmt).all()
    items = [
        schemas.CustomerValueItemOut(
            customer_id=int(customer_id),
            customer_name=str(customer_name),
            contract_amount=float(contract_amount),
            payment_amount=float(payment_amount),
            profit_amount=float(profit_amount),
        )
        for customer_id, customer_name, contract_amount, payment_amount, profit_amount in rows
    ]
    return schemas.CustomerValueSummaryOut(items=items)


def summarize_agent_commission(db: Session) -> schemas.AgentCommissionSummaryOut:
    stmt = (
        select(
            models.Agent.id,
            models.Agent.name,
            func.count(models.Contract.id),
            func.coalesce(func.sum(models.Contract.amount), 0.0),
            func.coalesce(
                func.sum(models.Contract.amount * models.Agent.default_commission_rate),
                0.0,
            ),
        )
        .select_from(models.Agent)
        .join(models.Opportunity, models.Opportunity.agent_id == models.Agent.id, isouter=True)
        .join(models.Contract, models.Contract.opportunity_id == models.Opportunity.id, isouter=True)
        .group_by(models.Agent.id, models.Agent.name)
        .order_by(models.Agent.id.asc())
    )
    rows = db.execute(stmt).all()
    items = [
        schemas.AgentCommissionItemOut(
            agent_id=int(agent_id),
            agent_name=str(agent_name),
            contract_count=int(contract_count),
            contract_amount=float(contract_amount),
            estimated_commission=float(estimated_commission),
        )
        for agent_id, agent_name, contract_count, contract_amount, estimated_commission in rows
    ]
    return schemas.AgentCommissionSummaryOut(items=items)


def summarize_collection_progress(db: Session) -> schemas.CollectionProgressSummaryOut:
    paid_sq = (
        select(
            models.Payment.contract_id.label("contract_id"),
            func.coalesce(func.sum(models.Payment.amount), 0.0).label("paid_amount"),
        )
        .group_by(models.Payment.contract_id)
        .subquery()
    )

    stmt = (
        select(
            models.Contract.id,
            models.Contract.contract_no,
            models.Contract.amount,
            func.coalesce(paid_sq.c.paid_amount, 0.0),
        )
        .select_from(models.Contract)
        .join(paid_sq, paid_sq.c.contract_id == models.Contract.id, isouter=True)
        .order_by(models.Contract.id.asc())
    )
    rows = db.execute(stmt).all()
    items = []
    for contract_id, contract_no, contract_amount, paid_amount in rows:
        contract_amount = float(contract_amount)
        paid_amount = float(paid_amount)
        outstanding = contract_amount - paid_amount
        ratio = 0.0 if contract_amount <= 0 else min(max(paid_amount / contract_amount, 0.0), 1.0)
        items.append(
            schemas.CollectionProgressItemOut(
                contract_id=int(contract_id),
                contract_no=str(contract_no),
                contract_amount=contract_amount,
                paid_amount=paid_amount,
                outstanding_amount=outstanding,
                progress_ratio=ratio,
            )
        )
    return schemas.CollectionProgressSummaryOut(items=items)


def summarize_contract_status(db: Session) -> schemas.ContractStatusSummaryOut:
    stmt = (
        select(
            models.Contract.status,
            func.count(models.Contract.id),
            func.coalesce(func.sum(models.Contract.amount), 0.0),
        )
        .group_by(models.Contract.status)
        .order_by(models.Contract.status.asc())
    )
    rows = db.execute(stmt).all()
    items = [
        schemas.ContractStatusSummaryItemOut(
            status=str(status),
            contract_count=int(contract_count),
            contract_amount=float(contract_amount),
        )
        for status, contract_count, contract_amount in rows
    ]
    return schemas.ContractStatusSummaryOut(items=items)
