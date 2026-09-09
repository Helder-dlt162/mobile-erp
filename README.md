# Atelier ERP MVP

MVP operacional para indústria de móveis, com front-end React/Vite e API desacoplada em FastAPI.

## Executar com Docker

```bash
docker compose up -d --build
npm run dev
```

Acesse `http://localhost:5173/`.

- Front-end: `http://localhost:5173`
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health`

## Credenciais demo

- E-mail: `admin@atelier.com`
- Senha: `atelier123`

## O que está funcional

- Login JWT e proteção de rotas.
- Middleware de request-id, tempo de resposta e auditoria.
- PostgreSQL 16 via Docker Compose.
- Seed automático com OPs, materiais e usuário administrador.
- Dashboard, ordens de produção, inventário e simulador de preço.
- CRUD completo de materiais.
- Registro e recebimento de NFs de entrada com atualização transacional do estoque.
- CRUD de fornecedores e clientes com busca por nome/documento.
- Autocomplete de fornecedor no lançamento de NF, com vínculo por ID.
- Dropdown fiscal com NF de entrada funcional e NF de venda marcada como WIP.
- NF de entrada com múltiplos itens no mesmo documento.
- Ao confirmar a NF de entrada, o estoque é atualizado e uma conta a pagar é criada automaticamente com vencimento e forma de pagamento.
- Financeiro inicial com contas a pagar, vencimento, pagamento e baixa.
- Configurações persistentes separadas por módulo, com preparação de parâmetros SEFAZ.
- Gestão de usuários com permissões por módulo e Funcionários marcado como WIP.
- Testes automatizados de saúde, autenticação, autorização, dashboard e precificação.

## Desenvolvimento local da API

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/pytest backend/tests -q
.venv/bin/uvicorn app.main:app --app-dir backend --reload --port 8000
```

Sem `DATABASE_URL`, a API usa SQLite local para desenvolvimento rápido. Com Docker, usa PostgreSQL.

## Pendência de negócio

O briefing mistura Lucro Real e Simples Nacional. O simulador marca o regime fiscal como pendente de confirmação; não deve ser usado como cálculo fiscal oficial até essa decisão.
