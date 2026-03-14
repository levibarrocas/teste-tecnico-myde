import asyncio
import json
import logging
import os
import sys
from sqlalchemy import select

# Ensure we can import from the app directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal
from app.proposals.models import Proposal, ProposalStatus
from app.clients.models import Client
from app.tenants.models import Tenant
from app.users.models import User # Import the User model
from app.core.sqs import get_sqs_client
from app.core.config import settings
from app.core.bank import BankClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_proposal(proposal_id: str):
    async with AsyncSessionLocal() as db:
        # 1. Fetch proposal
        result = await db.execute(select(Proposal).where(Proposal.id == proposal_id))
        proposal = result.scalars().first()
        
        if not proposal:
            logger.error(f"Proposal {proposal_id} not found")
            return

        # 2. Fetch Client
        client_result = await db.execute(select(Client).where(Client.id == proposal.client_id))
        client = client_result.scalars().first()
        
        if not client:
             logger.error(f"Client for proposal {proposal_id} not found")
             return

        bank = BankClient()

        try:
            # CASE A: Processing a Simulation Request
            if proposal.status == ProposalStatus.PENDING and proposal.type == "simulacao":
                logger.info(f"Simulating proposal {proposal_id} for {client.cpf}")
                response = await bank.simulate(
                    cpf=client.cpf,
                    amount=float(proposal.amount),
                    installments=proposal.installments
                )
                protocol = response.get("protocol")
                
                # Update Proposal waiting for Webhook
                proposal.external_protocol = protocol
                proposal.status = ProposalStatus.PROCESSING
                db.add(proposal)
                await db.commit()
                logger.info(f"Proposal {proposal_id} simulated. Protocol: {protocol}")

            # CASE B: Processing a Submission Request
            elif proposal.status == ProposalStatus.PROCESSING and proposal.type == "proposta":
                logger.info(f"Submitting proposal {proposal_id} to bank. Protocol: {proposal.external_protocol}")
                await bank.submit(
                    protocol=proposal.external_protocol,
                    name=client.name
                )
                # Status remains PROCESSING until Webhook
                logger.info(f"Proposal {proposal_id} submitted.")
            
            else:
                logger.info(f"Proposal {proposal_id} in status {proposal.status}/{proposal.type}, skipping.")

        except Exception as e:
            logger.error(f"Error processing proposal {proposal_id}: {e}")
            # Raising error here allows SQS to retry (depending on visibility timeout configuration)
            raise e

async def run_worker():
    logger.info("Starting SQS Worker...")
    async with get_sqs_client() as client:
        # Create the queue if it doesn't exist (idempotent)
        queue_url = (await client.create_queue(QueueName=settings.SQS_QUEUE_NAME))["QueueUrl"]
        
        while True:
            # Long polling for messages
            response = await client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=10)
            
            if "Messages" in response:
                for msg in response["Messages"]:
                    await process_proposal(json.loads(msg["Body"])["proposal_id"])
                    await client.delete_message(QueueUrl=queue_url, ReceiptHandle=msg["ReceiptHandle"])

if __name__ == "__main__":
    asyncio.run(run_worker())
