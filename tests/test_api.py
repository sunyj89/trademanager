from datetime import datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _uniq(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_customer_duplicate_name_returns_409():
    name = _uniq("ACME")
    payload = {
        "name": name,
        "country": "Germany",
        "customer_type": "direct",
        "source_channel": "Trade India",
        "owner": "grace",
    }
    assert client.post("/customers", json=payload).status_code == 200
    duplicate = client.post("/customers", json=payload)
    assert duplicate.status_code == 409


def test_contract_payment_flow():
    customer = client.post(
        "/customers",
        json={
            "name": _uniq("Delta Trading"),
            "country": "UAE",
            "customer_type": "direct",
            "source_channel": "Inquiry",
            "owner": "grace",
        },
    )
    assert customer.status_code == 200
    customer_id = customer.json()["id"]

    opportunity = client.post(
        "/opportunities",
        json={
            "customer_id": customer_id,
            "product": "Valve",
            "expected_amount": 50000,
            "stage": "proposal",
        },
    )
    assert opportunity.status_code == 200
    opportunity_id = opportunity.json()["id"]

    contract = client.post(
        "/contracts",
        json={
            "contract_no": _uniq("CT-2026"),
            "customer_id": customer_id,
            "opportunity_id": opportunity_id,
            "amount": 45000,
            "currency": "USD",
            "status": "signed",
        },
    )
    assert contract.status_code == 200
    contract_id = contract.json()["id"]

    payment = client.post(
        "/payments",
        json={
            "contract_id": contract_id,
            "received_at": datetime.utcnow().isoformat(),
            "amount": 20000,
            "exchange_rate": 7.1,
            "settled_amount": 142000,
            "cost": 120000,
            "profit": 22000,
        },
    )
    assert payment.status_code == 200

    payment_list = client.get("/payments", params={"contract_id": contract_id})
    assert payment_list.status_code == 200
    assert len(payment_list.json()) >= 1


def test_lead_conversion_to_customer_and_opportunity():
    lead = client.post(
        "/leads",
        json={
            "source": "Inquiry",
            "company": _uniq("Nordic Pumps"),
            "contact_name": "Luca",
            "product_interest": "Industrial Pump",
            "owner": "grace",
        },
    )
    assert lead.status_code == 200
    lead_id = lead.json()["id"]

    converted = client.post(
        f"/leads/{lead_id}/convert",
        json={"country": "Italy", "expected_amount": 32000, "create_opportunity": True},
    )
    assert converted.status_code == 200
    assert converted.json()["lead_id"] == lead_id
    assert converted.json()["customer_id"] is not None
    assert converted.json()["opportunity_id"] is not None


def test_mark_opportunity_won_creates_contract_and_summary():
    customer = client.post(
        "/customers",
        json={
            "name": _uniq("Sunrise Metals"),
            "country": "Egypt",
            "customer_type": "direct",
            "source_channel": "Trade India",
            "owner": "grace",
        },
    )
    customer_id = customer.json()["id"]

    opp = client.post(
        "/opportunities",
        json={
            "customer_id": customer_id,
            "product": "Steel Coil",
            "expected_amount": 80000,
            "stage": "proposal",
        },
    )
    opp_id = opp.json()["id"]

    won = client.post(
        f"/opportunities/{opp_id}/mark-won",
        json={"contract_no": _uniq("WON-CT"), "amount": 76000, "currency": "USD"},
    )
    assert won.status_code == 200
    assert won.json()["opportunity_id"] == opp_id

    report = client.get("/reports/profit-summary")
    assert report.status_code == 200
    payload = report.json()
    assert payload["contract_count"] >= 1
    assert payload["total_contract_amount"] >= 76000


def test_followup_requires_exactly_one_target():
    invalid = client.post(
        "/followups",
        json={
            "method": "email",
            "content": "hello",
            "owner": "grace",
            "customer_id": 1,
            "lead_id": 1,
        },
    )
    assert invalid.status_code == 422


def test_pagination_and_filtering():
    response = client.get("/customers", params={"limit": 1, "offset": 0, "country": "Germany"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_convert_lead_twice_returns_409():
    lead = client.post(
        "/leads",
        json={
            "source": "Inquiry",
            "company": _uniq("Twin Convert"),
            "contact_name": "Mia",
            "product_interest": "Pump",
            "owner": "grace",
        },
    )
    lead_id = lead.json()["id"]

    first = client.post(f"/leads/{lead_id}/convert", json={"country": "China"})
    assert first.status_code == 200

    second = client.post(f"/leads/{lead_id}/convert", json={"country": "China"})
    assert second.status_code == 409


def test_mark_won_twice_returns_409_and_pipeline_summary_available():
    customer = client.post(
        "/customers",
        json={
            "name": _uniq("Pipeline Co"),
            "country": "Brazil",
            "customer_type": "direct",
            "source_channel": "Inquiry",
            "owner": "grace",
        },
    )
    customer_id = customer.json()["id"]

    opp = client.post(
        "/opportunities",
        json={
            "customer_id": customer_id,
            "product": "Fitting",
            "expected_amount": 30000,
            "stage": "proposal",
        },
    )
    opp_id = opp.json()["id"]

    win1 = client.post(
        f"/opportunities/{opp_id}/mark-won",
        json={"contract_no": _uniq("WIN2"), "amount": 28000, "currency": "USD"},
    )
    assert win1.status_code == 200

    win2 = client.post(
        f"/opportunities/{opp_id}/mark-won",
        json={"contract_no": _uniq("WIN3"), "amount": 27000, "currency": "USD"},
    )
    assert win2.status_code == 409

    pipeline = client.get("/reports/pipeline-summary")
    assert pipeline.status_code == 200
    assert "items" in pipeline.json()


def test_contract_customer_opportunity_mismatch_returns_400():
    c1 = client.post(
        "/customers",
        json={
            "name": _uniq("Cust-A"),
            "country": "USA",
            "customer_type": "direct",
            "source_channel": "Inquiry",
            "owner": "grace",
        },
    )
    c2 = client.post(
        "/customers",
        json={
            "name": _uniq("Cust-B"),
            "country": "Canada",
            "customer_type": "direct",
            "source_channel": "Inquiry",
            "owner": "grace",
        },
    )
    c1_id = c1.json()["id"]
    c2_id = c2.json()["id"]

    opp = client.post(
        "/opportunities",
        json={
            "customer_id": c1_id,
            "product": "Seal",
            "expected_amount": 12000,
            "stage": "proposal",
        },
    )
    opp_id = opp.json()["id"]

    mismatch = client.post(
        "/contracts",
        json={
            "contract_no": _uniq("MISMATCH"),
            "customer_id": c2_id,
            "opportunity_id": opp_id,
            "amount": 11000,
            "currency": "USD",
        },
    )
    assert mismatch.status_code == 400


def test_customer_value_summary_endpoint():
    customer = client.post(
        "/customers",
        json={
            "name": _uniq("Value Co"),
            "country": "France",
            "customer_type": "direct",
            "source_channel": "Inquiry",
            "owner": "grace",
        },
    )
    customer_id = customer.json()["id"]

    contract = client.post(
        "/contracts",
        json={
            "contract_no": _uniq("VAL-CT"),
            "customer_id": customer_id,
            "amount": 25000,
            "currency": "USD",
            "status": "signed",
        },
    )
    assert contract.status_code == 200
    contract_id = contract.json()["id"]

    payment = client.post(
        "/payments",
        json={
            "contract_id": contract_id,
            "received_at": datetime.utcnow().isoformat(),
            "amount": 10000,
            "profit": 1800,
        },
    )
    assert payment.status_code == 200

    summary = client.get("/reports/customer-value-summary")
    assert summary.status_code == 200
    assert isinstance(summary.json().get("items"), list)


def test_cannot_add_payment_to_cancelled_contract():
    customer = client.post(
        "/customers",
        json={
            "name": _uniq("Cancelled Contract Co"),
            "country": "UK",
            "customer_type": "direct",
            "source_channel": "Inquiry",
            "owner": "grace",
        },
    )
    customer_id = customer.json()["id"]

    contract = client.post(
        "/contracts",
        json={
            "contract_no": _uniq("CANCEL-CT"),
            "customer_id": customer_id,
            "amount": 9000,
            "currency": "USD",
            "status": "cancelled",
        },
    )
    contract_id = contract.json()["id"]

    payment = client.post(
        "/payments",
        json={
            "contract_id": contract_id,
            "received_at": datetime.utcnow().isoformat(),
            "amount": 1000,
        },
    )
    assert payment.status_code == 400


def test_agent_commission_summary_endpoint():
    customer = client.post(
        "/customers",
        json={
            "name": _uniq("Commission Customer"),
            "country": "Japan",
            "customer_type": "direct",
            "source_channel": "Inquiry",
            "owner": "grace",
        },
    )
    customer_id = customer.json()["id"]

    agent = client.post(
        "/agents",
        json={
            "name": _uniq("Agent Commission"),
            "country": "Japan",
            "contact": "ac@example.com",
            "default_commission_rate": 0.1,
        },
    )
    agent_id = agent.json()["id"]

    opp = client.post(
        "/opportunities",
        json={
            "customer_id": customer_id,
            "agent_id": agent_id,
            "product": "Sensor",
            "expected_amount": 20000,
            "stage": "proposal",
        },
    )
    opp_id = opp.json()["id"]

    won = client.post(
        f"/opportunities/{opp_id}/mark-won",
        json={"contract_no": _uniq("AGENT-CM"), "amount": 18000, "currency": "USD"},
    )
    assert won.status_code == 200

    summary = client.get("/reports/agent-commission-summary")
    assert summary.status_code == 200
    assert isinstance(summary.json().get("items"), list)


def test_mark_opportunity_lost_sets_reason():
    customer = client.post(
        "/customers",
        json={
            "name": _uniq("Lost Opp Customer"),
            "country": "Spain",
            "customer_type": "direct",
            "source_channel": "Inquiry",
            "owner": "grace",
        },
    )
    customer_id = customer.json()["id"]

    opp = client.post(
        "/opportunities",
        json={
            "customer_id": customer_id,
            "product": "Pipe",
            "expected_amount": 15000,
            "stage": "proposal",
        },
    )
    opp_id = opp.json()["id"]

    lost = client.post(
        f"/opportunities/{opp_id}/mark-lost",
        json={"loss_reason": "price too high"},
    )
    assert lost.status_code == 200
    assert lost.json()["stage"] == "lost"
    assert lost.json()["loss_reason"] == "price too high"


def test_contract_status_transition_rules():
    customer = client.post(
        "/customers",
        json={
            "name": _uniq("Contract State"),
            "country": "India",
            "customer_type": "direct",
            "source_channel": "Inquiry",
            "owner": "grace",
        },
    )
    customer_id = customer.json()["id"]

    contract = client.post(
        "/contracts",
        json={
            "contract_no": _uniq("ST-CT"),
            "customer_id": customer_id,
            "amount": 14000,
            "currency": "USD",
            "status": "signed",
        },
    )
    contract_id = contract.json()["id"]

    complete = client.post(f"/contracts/{contract_id}/status", json={"status": "completed"})
    assert complete.status_code == 200

    rollback = client.post(f"/contracts/{contract_id}/status", json={"status": "signed"})
    assert rollback.status_code == 409


def test_collection_progress_summary_endpoint():
    customer = client.post(
        "/customers",
        json={
            "name": _uniq("Collection Co"),
            "country": "Korea",
            "customer_type": "direct",
            "source_channel": "Inquiry",
            "owner": "grace",
        },
    )
    customer_id = customer.json()["id"]

    contract = client.post(
        "/contracts",
        json={
            "contract_no": _uniq("COL-CT"),
            "customer_id": customer_id,
            "amount": 30000,
            "currency": "USD",
            "status": "signed",
        },
    )
    contract_id = contract.json()["id"]

    pay = client.post(
        "/payments",
        json={
            "contract_id": contract_id,
            "received_at": datetime.utcnow().isoformat(),
            "amount": 12000,
        },
    )
    assert pay.status_code == 200

    summary = client.get("/reports/collection-progress-summary")
    assert summary.status_code == 200
    assert isinstance(summary.json().get("items"), list)


def test_payment_cannot_exceed_contract_amount():
    customer = client.post(
        "/customers",
        json={
            "name": _uniq("Overpay Co"),
            "country": "USA",
            "customer_type": "direct",
            "source_channel": "Inquiry",
            "owner": "grace",
        },
    )
    customer_id = customer.json()["id"]

    contract = client.post(
        "/contracts",
        json={
            "contract_no": _uniq("OVER-CT"),
            "customer_id": customer_id,
            "amount": 10000,
            "currency": "USD",
            "status": "signed",
        },
    )
    contract_id = contract.json()["id"]

    p1 = client.post(
        "/payments",
        json={
            "contract_id": contract_id,
            "received_at": datetime.utcnow().isoformat(),
            "amount": 8000,
        },
    )
    assert p1.status_code == 200

    p2 = client.post(
        "/payments",
        json={
            "contract_id": contract_id,
            "received_at": datetime.utcnow().isoformat(),
            "amount": 3000,
        },
    )
    assert p2.status_code == 400


def test_contract_cannot_complete_before_full_payment_and_status_report():
    customer = client.post(
        "/customers",
        json={
            "name": _uniq("Status Report Co"),
            "country": "Germany",
            "customer_type": "direct",
            "source_channel": "Inquiry",
            "owner": "grace",
        },
    )
    customer_id = customer.json()["id"]

    contract = client.post(
        "/contracts",
        json={
            "contract_no": _uniq("STAT-CT"),
            "customer_id": customer_id,
            "amount": 20000,
            "currency": "USD",
            "status": "signed",
        },
    )
    contract_id = contract.json()["id"]

    early_complete = client.post(f"/contracts/{contract_id}/status", json={"status": "completed"})
    assert early_complete.status_code == 409

    pay = client.post(
        "/payments",
        json={
            "contract_id": contract_id,
            "received_at": datetime.utcnow().isoformat(),
            "amount": 20000,
        },
    )
    assert pay.status_code == 200

    complete = client.post(f"/contracts/{contract_id}/status", json={"status": "completed"})
    assert complete.status_code == 200

    status_report = client.get("/reports/contract-status-summary")
    assert status_report.status_code == 200
    assert isinstance(status_report.json().get("items"), list)
