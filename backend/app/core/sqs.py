import json
from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from app.core.config import settings

@asynccontextmanager
async def get_sqs_client():
    session = get_session()
    async with session.create_client(
        "sqs",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.SQS_ENDPOINT_URL,
    ) as client:
        yield client

async def enqueue_proposal(proposal_id: str):
    """Sends the proposal ID to the SQS queue for processing."""
    async with get_sqs_client() as client:
        try:
            # In a real app, you might cache the Queue URL
            response = await client.get_queue_url(QueueName=settings.SQS_QUEUE_NAME)
            queue_url = response["QueueUrl"]
            
            message_body = json.dumps({"proposal_id": proposal_id})
            
            await client.send_message(QueueUrl=queue_url, MessageBody=message_body)
        except Exception as e:
            print(f"Failed to enqueue proposal {proposal_id}: {e}")
            # In production, we should raise this or handle dead-letter queues
