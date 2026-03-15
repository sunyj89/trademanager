from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.database import Base, engine
from app.routers import agents, contacts, contracts, customers, demo, followups, leads, opportunities, payments, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TradeManager CRM MVP", version="0.5.0")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def mvp_dashboard():
    return FileResponse(Path(__file__).with_name("static_index.html"))


app.include_router(leads.router)
app.include_router(customers.router)
app.include_router(agents.router)
app.include_router(contacts.router)
app.include_router(opportunities.router)
app.include_router(contracts.router)
app.include_router(payments.router)
app.include_router(followups.router)
app.include_router(reports.router)
app.include_router(demo.router)
