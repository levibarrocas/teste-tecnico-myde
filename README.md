# Solução do Teste Técnico Backend

Este documento descreve como executar a solução implementada e lista os requisitos atendidos.

## 🚀 Como Executar o Projeto

O projeto utiliza **Docker Compose** para orquestrar a API, o Worker, o Banco de Dados e os serviços auxiliares (LocalStack, Mock Bank).

### 1. Iniciar os Serviços
Execute o comando abaixo na raiz do projeto:

```bash
docker-compose up --build
```

Aguarde até que todos os serviços estejam rodando. A API estará disponível em `http://localhost:8000`.

### 2. Popular o Banco de Dados (Seed)
Para criar os tenants e usuários de teste iniciais, execute em outro terminal:

```bash
docker-compose exec backend-api python seed.py
```

Isso criará o usuário:
- **Email:** `admin@acme.com`
- **Senha:** `password123`

### 3. Rodar os Testes
Para executar a suíte de testes (unitários e integração):

```bash
docker-compose exec backend-api pytest
```

---

## ✅ Checklist de Entrega

### Obrigatório
- [x] Código fonte em repositório Git
- [x] `README.md` (e `INSTRUCTIONS.md`) com instruções claras
- [x] Migrations com Alembic funcionando
- [x] Seed com dados iniciais (tenants + usuários)
- [x] Todos os endpoints funcionando
- [x] Fluxo assíncrono via fila (SQS/LocalStack)
- [x] Webhook recebendo e processando callbacks
- [x] Multi-tenancy funcionando (tenant A não vê dados do tenant B)
- [x] Autenticação JWT
- [x] Testes unitários e de integração

### Diferenciais
- [x] Testes de integração
- [x] Dockerfile para a API
- [ ] Logs estruturados
- [ ] Documentação Swagger/OpenAPI customizada
- [x] Tratamento de idempotência no webhook
- [x] Rate limiting
- [x] Validação de CPF