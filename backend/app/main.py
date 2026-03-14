from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.limiter import limiter
from app.auth.endpoints import router as auth_router
from app.clients.endpoints import router as clients_router
from app.proposals.endpoints import router as proposals_router
from app.webhooks.endpoints import router as webhooks_router

# Import models to ensure they are registered with SQLAlchemy
from app.tenants.models import Tenant
from app.proposals.models import Proposal

description = """
API desenvolvida para o teste técnico, responsável pelo gerenciamento de propostas de crédito. 🚀

## Funcionalidades
* **Autenticação**: Controle de acesso via tokens JWT e isolamento de Multi-Tenancy.
* **Clientes**: Cadastro e listagem com validação estrita de CPF.
* **Propostas**: Simulação, integração assíncrona via filas SQS e envio de propostas.
* **Webhooks**: Recepção de callbacks do banco com processamento seguro e idempotente.
"""

app = FastAPI(
    title="Credit Proposal API",
    description=description,
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(clients_router, prefix="/api/clients", tags=["clients"])
app.include_router(proposals_router, prefix="/api/proposals", tags=["proposals"])
app.include_router(webhooks_router, prefix="/api/webhooks", tags=["webhooks"])

@app.get("/")
async def root():
    return {"message": "API is running"}
