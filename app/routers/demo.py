from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.database import get_db

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/reset")
def reset_demo_data(db: Session = Depends(get_db)):
    db.query(models.Payment).delete()
    db.query(models.Contract).delete()
    db.query(models.FollowUp).delete()
    db.query(models.Opportunity).delete()
    db.query(models.Contact).delete()
    db.query(models.Lead).delete()
    db.query(models.Customer).delete()
    db.query(models.Agent).delete()
    db.commit()
    return {"status": "ok"}


@router.post("/seed")
def seed_demo_data(db: Session = Depends(get_db)):
    if db.query(models.Customer).count() > 0:
        return {"status": "skipped", "reason": "data already exists"}

    agent = models.Agent(
        name="MENA Distributor",
        country="UAE",
        contact="mena@example.com",
        default_commission_rate=0.08,
        status="active",
    )
    db.add(agent)
    db.flush()

    customer_a = models.Customer(
        name="Atlas Trading",
        country="Egypt",
        customer_type="direct",
        source_channel="Inquiry",
        owner="grace",
        level="A",
        status="active",
    )
    customer_b = models.Customer(
        name="Nordic Pumps AB",
        country="Sweden",
        customer_type="direct",
        source_channel="Trade India",
        owner="grace",
        level="B",
        status="active",
    )
    db.add_all([customer_a, customer_b])
    db.flush()

    db.add_all(
        [
            models.Contact(customer_id=customer_a.id, name="Ahmed", title="Manager", email="ahmed@atlas.com"),
            models.Contact(customer_id=customer_b.id, name="Luca", title="Buyer", email="luca@nordic.com"),
        ]
    )

    db.add(
        models.Lead(
            source="Trade India",
            company="Valves Pro Ltd",
            contact_name="Nina",
            product_interest="Industrial Valve",
            status="new",
            owner="grace",
        )
    )

    opp_a = models.Opportunity(
        customer_id=customer_a.id,
        agent_id=agent.id,
        product="Valve",
        expected_amount=50000,
        stage="proposal",
    )
    opp_b = models.Opportunity(
        customer_id=customer_b.id,
        product="Pump",
        expected_amount=32000,
        stage="qualification",
    )
    db.add_all([opp_a, opp_b])
    db.flush()

    contract = models.Contract(
        contract_no="CT-DEMO-001",
        customer_id=customer_a.id,
        opportunity_id=opp_a.id,
        amount=42000,
        currency="USD",
        status="signed",
    )
    db.add(contract)
    db.flush()

    db.add(
        models.Payment(
            contract_id=contract.id,
            received_at=datetime.utcnow() - timedelta(days=2),
            amount=18000,
            profit=3600,
        )
    )

    db.add(
        models.FollowUp(
            followup_at=datetime.utcnow(),
            method="email",
            content="Sent updated quotation",
            owner="grace",
            opportunity_id=opp_a.id,
        )
    )

    db.commit()
    return {"status": "ok"}


@router.post("/bootstrap")
def bootstrap_demo_data(db: Session = Depends(get_db)):
    """Reset and seed demo data in one call for fast local preview."""
    db.query(models.Payment).delete()
    db.query(models.Contract).delete()
    db.query(models.FollowUp).delete()
    db.query(models.Opportunity).delete()
    db.query(models.Contact).delete()
    db.query(models.Lead).delete()
    db.query(models.Customer).delete()
    db.query(models.Agent).delete()
    db.commit()

    agent = models.Agent(
        name="MENA Distributor",
        country="UAE",
        contact="mena@example.com",
        default_commission_rate=0.08,
        status="active",
    )
    db.add(agent)
    db.flush()

    customer_a = models.Customer(
        name="Atlas Trading",
        country="Egypt",
        customer_type="direct",
        source_channel="Inquiry",
        owner="grace",
        level="A",
        status="active",
    )
    customer_b = models.Customer(
        name="Nordic Pumps AB",
        country="Sweden",
        customer_type="direct",
        source_channel="Trade India",
        owner="grace",
        level="B",
        status="active",
    )
    db.add_all([customer_a, customer_b])
    db.flush()

    db.add_all(
        [
            models.Contact(customer_id=customer_a.id, name="Ahmed", title="Manager", email="ahmed@atlas.com"),
            models.Contact(customer_id=customer_b.id, name="Luca", title="Buyer", email="luca@nordic.com"),
        ]
    )

    db.add(
        models.Lead(
            source="Trade India",
            company="Valves Pro Ltd",
            contact_name="Nina",
            product_interest="Industrial Valve",
            status="new",
            owner="grace",
        )
    )

    opp_a = models.Opportunity(
        customer_id=customer_a.id,
        agent_id=agent.id,
        product="Valve",
        expected_amount=50000,
        stage="proposal",
    )
    opp_b = models.Opportunity(
        customer_id=customer_b.id,
        product="Pump",
        expected_amount=32000,
        stage="qualification",
    )
    db.add_all([opp_a, opp_b])
    db.flush()

    contract = models.Contract(
        contract_no="CT-DEMO-001",
        customer_id=customer_a.id,
        opportunity_id=opp_a.id,
        amount=42000,
        currency="USD",
        status="signed",
    )
    db.add(contract)
    db.flush()

    db.add(
        models.Payment(
            contract_id=contract.id,
            received_at=datetime.utcnow() - timedelta(days=2),
            amount=18000,
            profit=3600,
        )
    )

    db.add(
        models.FollowUp(
            followup_at=datetime.utcnow(),
            method="email",
            content="Sent updated quotation",
            owner="grace",
            opportunity_id=opp_a.id,
        )
    )

    db.commit()
    return {"status": "ok"}
