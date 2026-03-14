from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.webhooks.dto import WebhookPayload
from app.webhooks.service import WebhookService

router = APIRouter()

@router.post("/bank-callback", status_code=status.HTTP_200_OK)
async def bank_callback(
    payload: WebhookPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Receive asynchronous callbacks from the Mock Bank.
    """
    found = await WebhookService.process_callback(db, payload)
    if not found:
        # We return 404 if the protocol doesn't match any proposal
        raise HTTPException(status_code=404, detail="Proposal not found for this protocol")
    
    return {"message": "Callback processed successfully"}
