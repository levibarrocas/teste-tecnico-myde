from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.proposals.models import Proposal
from app.webhooks.dto import WebhookPayload

class WebhookService:
    @staticmethod
    async def process_callback(db: AsyncSession, payload: WebhookPayload) -> bool:
        # 1. Retrieve the proposal by the external protocol
        result = await db.execute(select(Proposal).where(Proposal.external_protocol == payload.protocol))
        proposal = result.scalars().first()

        if not proposal:
            return False  # Protocol not found

        # 2. IDEMPOTENCY CHECK
        # If the proposal is already in the state the webhook is trying to set,
        # we stop here and consider it a success. We do NOT raise an error.
        if proposal.status == payload.status:
            return True

        # 3. If not, apply the updates
        proposal.status = payload.status
        
        # Save the extra bank data if available
        if payload.data:
            proposal.bank_response = payload.model_dump()
            if payload.data.interest_rate:
                proposal.interest_rate = payload.data.interest_rate
            if payload.data.installment_value:
                proposal.installment_value = payload.data.installment_value

        await db.commit()
        return True