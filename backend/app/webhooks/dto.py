from pydantic import BaseModel, ConfigDict

class WebhookData(BaseModel):
    interest_rate: float | None = None
    installment_value: float | None = None
    total_amount: float | None = None
    approved_amount: float | None = None

    model_config = ConfigDict(from_attributes=True)

class WebhookPayload(BaseModel):
    protocol: str
    event: str
    status: str
    data: WebhookData | None = None
