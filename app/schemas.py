from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CustomerBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    country: str
    customer_type: str = "direct"
    source_channel: str
    owner: str
    level: str = "B"
    status: str = "active"
    tags: str | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerOut(CustomerBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class LeadBase(BaseModel):
    source: str
    company: str
    contact_name: str
    product_interest: str
    status: str = "new"
    owner: str
    recent_followup_at: datetime | None = None


class LeadCreate(LeadBase):
    pass


class LeadOut(LeadBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class LeadConvertRequest(BaseModel):
    customer_name: str | None = None
    country: str = "Unknown"
    customer_type: str = "direct"
    create_opportunity: bool = True
    expected_amount: float = Field(default=0, ge=0)


class LeadConvertResult(BaseModel):
    lead_id: int
    customer_id: int
    opportunity_id: int | None = None


class AgentBase(BaseModel):
    name: str
    country: str
    contact: str
    default_commission_rate: float = Field(default=0.0, ge=0, le=1)
    status: str = "active"


class AgentCreate(AgentBase):
    pass


class AgentOut(AgentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ContactBase(BaseModel):
    customer_id: int
    name: str
    title: str | None = None
    mobile_whatsapp: str | None = None
    email: str | None = None
    wechat_skype: str | None = None
    remark: str | None = None


class ContactCreate(ContactBase):
    pass


class ContactOut(ContactBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class OpportunityBase(BaseModel):
    customer_id: int
    agent_id: int | None = None
    product: str
    expected_amount: float = Field(gt=0)
    expected_profit: float | None = None
    stage: str = "qualification"
    expected_close_at: datetime | None = None
    loss_reason: str | None = None


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityOut(OpportunityBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class OpportunityWinRequest(BaseModel):
    contract_no: str = Field(min_length=1, max_length=64)
    amount: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=16)
    delivery_plan: str | None = None


class OpportunityLostRequest(BaseModel):
    loss_reason: str = Field(min_length=2)


class ContractBase(BaseModel):
    contract_no: str = Field(min_length=1, max_length=64)
    customer_id: int
    opportunity_id: int | None = None
    amount: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=16)
    delivery_plan: str | None = None
    status: str = "signed"


class ContractCreate(ContractBase):
    pass


class ContractOut(ContractBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ContractStatusUpdateRequest(BaseModel):
    status: str = Field(pattern="^(signed|completed|cancelled)$")


class PaymentBase(BaseModel):
    contract_id: int
    received_at: datetime
    amount: float = Field(gt=0)
    exchange_rate: float | None = Field(default=None, gt=0)
    settled_amount: float | None = None
    cost: float | None = None
    profit: float | None = None
    note: str | None = None


class PaymentCreate(PaymentBase):
    pass


class PaymentOut(PaymentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProfitSummaryOut(BaseModel):
    contract_count: int
    payment_count: int
    total_contract_amount: float
    total_payment_amount: float
    total_profit: float


class PipelineStageOut(BaseModel):
    stage: str
    count: int
    total_expected_amount: float


class PipelineSummaryOut(BaseModel):
    items: list[PipelineStageOut]


class CustomerValueItemOut(BaseModel):
    customer_id: int
    customer_name: str
    contract_amount: float
    payment_amount: float
    profit_amount: float


class CustomerValueSummaryOut(BaseModel):
    items: list[CustomerValueItemOut]


class AgentCommissionItemOut(BaseModel):
    agent_id: int
    agent_name: str
    contract_count: int
    contract_amount: float
    estimated_commission: float


class AgentCommissionSummaryOut(BaseModel):
    items: list[AgentCommissionItemOut]


class CollectionProgressItemOut(BaseModel):
    contract_id: int
    contract_no: str
    contract_amount: float
    paid_amount: float
    outstanding_amount: float
    progress_ratio: float


class CollectionProgressSummaryOut(BaseModel):
    items: list[CollectionProgressItemOut]


class ContractStatusSummaryItemOut(BaseModel):
    status: str
    contract_count: int
    contract_amount: float


class ContractStatusSummaryOut(BaseModel):
    items: list[ContractStatusSummaryItemOut]


class FollowUpBase(BaseModel):
    followup_at: datetime | None = None
    method: str
    content: str
    next_followup_at: datetime | None = None
    owner: str
    lead_id: int | None = None
    customer_id: int | None = None
    opportunity_id: int | None = None

    @model_validator(mode="after")
    def validate_target(self):
        linked = [self.lead_id, self.customer_id, self.opportunity_id]
        if sum(item is not None for item in linked) != 1:
            raise ValueError("exactly one target id must be provided")
        return self


class FollowUpCreate(FollowUpBase):
    pass


class FollowUpOut(FollowUpBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
