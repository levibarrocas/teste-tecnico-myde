import httpx
from app.core.config import settings

class BankClient:
    def __init__(self):
        self.base_url = settings.MOCK_BANK_URL

    async def simulate(self, cpf: str, amount: float, installments: int):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/simular",
                json={"cpf": cpf, "amount": amount, "installments": installments}
            )
            response.raise_for_status()
            return response.json()

    async def submit(self, protocol: str, name: str):
        async with httpx.AsyncClient() as client:
            # Based on requirements, we send protocol and client name as data
            payload = {"protocol": protocol, "client_data": {"name": name}}
            response = await client.post(
                f"{self.base_url}/api/incluir",
                json=payload
            )
            response.raise_for_status()
            return response.json()
