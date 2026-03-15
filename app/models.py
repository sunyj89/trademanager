from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    country: Mapped[str] = mapped_column(String(128), nullable=False)
    customer_type: Mapped[str] = mapped_column(String(64), nullable=False, default="direct")
    source_channel: Mapped[str] = mapped_column(String(128), nullable=False)
    owner: Mapped[str] = mapped_column(String(128), nullable=False)
    level: Mapped[str] = mapped_column(String(32), nullable=False, default="B")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    tags: Mapped[str | None] = mapped_column(String(255), nullable=True)

    contacts: Mapped[list["Contact"]] = relationship(back_populates="customer")
    opportunities: Mapped[list["Opportunity"]] = relationship(back_populates="customer")
    contracts: Mapped[list["Contract"]] = relationship(back_populates="customer")
    followups: Mapped[list["FollowUp"]] = relationship(back_populates="customer")


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(128), nullable=False)
    product_interest: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="new")
    owner: Mapped[str] = mapped_column(String(128), nullable=False)
    recent_followup_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    followups: Mapped[list["FollowUp"]] = relationship(back_populates="lead")


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    country: Mapped[str] = mapped_column(String(128), nullable=False)
    contact: Mapped[str] = mapped_column(String(128), nullable=False)
    default_commission_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    opportunities: Mapped[list["Opportunity"]] = relationship(back_populates="agent")


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str | None] = mapped_column(String(128), nullable=True)
    mobile_whatsapp: Mapped[str | None] = mapped_column(String(64), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    wechat_skype: Mapped[str | None] = mapped_column(String(128), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)

    customer: Mapped[Customer] = relationship(back_populates="contacts")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    agent_id: Mapped[int | None] = mapped_column(ForeignKey("agents.id"), nullable=True)
    product: Mapped[str] = mapped_column(String(255), nullable=False)
    expected_amount: Mapped[float] = mapped_column(Float, nullable=False)
    expected_profit: Mapped[float | None] = mapped_column(Float, nullable=True)
    stage: Mapped[str] = mapped_column(String(64), nullable=False, default="qualification")
    expected_close_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    loss_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    customer: Mapped[Customer] = relationship(back_populates="opportunities")
    agent: Mapped[Agent | None] = relationship(back_populates="opportunities")
    contracts: Mapped[list["Contract"]] = relationship(back_populates="opportunity")
    followups: Mapped[list["FollowUp"]] = relationship(back_populates="opportunity")


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    contract_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    opportunity_id: Mapped[int | None] = mapped_column(ForeignKey("opportunities.id"), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(16), nullable=False, default="USD")
    delivery_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="signed")

    customer: Mapped[Customer] = relationship(back_populates="contracts")
    opportunity: Mapped[Opportunity | None] = relationship(back_populates="contracts")
    payments: Mapped[list["Payment"]] = relationship(back_populates="contract")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    exchange_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    settled_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    profit: Mapped[float | None] = mapped_column(Float, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    contract: Mapped[Contract] = relationship(back_populates="payments")


class FollowUp(Base):
    __tablename__ = "followups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    followup_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    method: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    next_followup_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    owner: Mapped[str] = mapped_column(String(128), nullable=False)
    lead_id: Mapped[int | None] = mapped_column(ForeignKey("leads.id"), nullable=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    opportunity_id: Mapped[int | None] = mapped_column(ForeignKey("opportunities.id"), nullable=True)

    lead: Mapped[Lead | None] = relationship(back_populates="followups")
    customer: Mapped[Customer | None] = relationship(back_populates="followups")
    opportunity: Mapped[Opportunity | None] = relationship(back_populates="followups")
