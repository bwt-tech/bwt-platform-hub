# Design Document: Integração com a Plataforma BWT

## Architecture & DDD Compliance

### 1. Ports and Adapters (Hexagonal Architecture)
- **Port Interface (`app/src/ports/bwt_port.py`)**:
  Declara os métodos de contrato para interação com a BWT:
  - `login(email: str, password: str, scope: str)`: Autenticação e obtenção de token JWT.
  - `search_accounts(search_term: str)`: Pesquisa contas por nome (`GET /sales/accounts?search=...`).
  - `create_account(name: str, account_type: str = "B2C")`: Criação de conta (`POST /sales/accounts/`).
  - `create_contact(account_id: int | str, name: str, email: str, phone: dict | str, document: str | None = None)`: Criação de contato vinculado a uma conta (`POST /sales/accounts/{account_id}/contacts/`).
  - `create_deal(contact_id: int | str, account_id: int | str, origin: str = "WHATSAPP")`: Criação de negociação (`POST /sales/deals/`).
  - `update_deal_status(deal_id: int | str, stage: str)`: Atualização de estágio do negócio (`POST /sales/deals/{deal_id}/update-deal-status/`).
  - `get_company_users()`: Consulta de funcionários/usuários da empresa (`GET /auth/company-users/`).
  - `set_deal_responsible(deal_id: int | str, responsible_id: int)`: Atribuição de responsável pelo negócio (`POST /sales/deals/{deal_id}/set-responsible/`).

- **Adapter (`app/src/adapters/outbounds/bwt.py`)**:
  Implementa `BWTPort` utilizando `httpx` para consumo da API REST BWT.
  - Cabeçalhos padrão:
    ```json
    {
      "Content-Type": "application/json",
      "Accept": "application/json; version=v1_web"
    }
    ```
  - Autenticação via `Authorization: Bearer <token>`.
  - Tratamento de exceções: Captura `httpx.RequestError` e `httpx.HTTPStatusError`, registra logs via `loguru.logger` e lança `IntegrationError`.

### 2. Configuration & Credentials
Em [settings.py](file:///Users/mateus/projects/bwt/bwt-platform-hub/app/src/config/settings.py):
- `bwt_url`: `https://api.homolog.brasileiroswinetours.com.br`
- `bwt_email`: Configurado via env / secrets.
- `bwt_password`: Configurado via env / secrets.
- `bwt_scope`: `"b2bit"`

### 3. Isolation
Conforme solicitado pelo usuário, este adapter será criado em isolamento e não será acoplado a nenhum orquestrador ou fluxo nesta etapa.
