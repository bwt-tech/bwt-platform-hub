# BWT Platform Adapter Documentation

Documentação técnica do adaptador de saída da **Plataforma BWT** (`BWTAdapter`) no BWT Platform Hub.

---

## 1. Arquitetura

O adaptador da Plataforma BWT implementa a porta abstrata `BWTPort` localizada em [bwt_port.py](file:///Users/mateus/projects/bwt/bwt-platform-hub/app/src/ports/bwt_port.py).

- **Porta (`BWTPort`)**: Interface que declara os contratos de comunicação REST com a Plataforma BWT.
- **Adapter (`BWTAdapter`)**: Localizado em [bwt.py](file:///Users/mateus/projects/bwt/bwt-platform-hub/app/src/adapters/outbounds/bwt.py). Utiliza `httpx` para consumo com autenticação JWT Bearer.

---

## 2. Configurações e Credenciais

Configurado através do `Settings` (`app/src/config/settings.py`):
- `bwt_url`: URL base da API (padrão: `https://api.homolog.brasileiroswinetours.com.br`).
- `bwt_email`: E-mail de autenticação do usuário de integração.
- `bwt_password`: Senha do usuário de integração.
- `bwt_scope`: Escopo da conta (padrão: `"b2bit"`).

---

## 3. Autenticação e Cabeçalhos

Toda requisição para a Plataforma BWT inclui obrigatoriamente:
- Header: `Content-Type: application/json`
- Header: `Accept: application/json; version=v1_web`
- Header: `Authorization: Bearer <token_access>`

O adaptador realiza o login automático via `POST /auth/login/` ao instanciar ou antes de disparar chamadas que exijam autenticação, armazenando o token de acesso de forma transparente.

---

## 4. Principais Operações

| Método | Endpoint HTTP | Descrição |
|---|---|---|
| `login` | `POST /auth/login/` | Realiza login com e-mail/senha/escopo e obtém o token de acesso |
| `search_accounts` | `GET /sales/accounts?search={term}` | Pesquisa contas cadastradas por nome |
| `create_account` | `POST /sales/accounts/` | Cria nova conta na plataforma BWT (ex: tipo B2C) |
| `create_contact` | `POST /sales/accounts/{account_id}/contacts/` | Cadastra contato associado a uma conta existente |
| `create_deal` | `POST /sales/deals/` | Cria nova negociação vinculando conta, contato e origem |
| `update_deal_status` | `POST /sales/deals/{deal_id}/update-deal-status/` | Atualiza o estágio da negociação |
| `set_deal_responsible` | `POST /sales/deals/{deal_id}/set-responsible/` | Atribui um funcionário responsável pelo negócio |
| `get_company_users` | `GET /auth/company-users/` | Lista usuários/funcionários ativos da empresa |

---

## 5. Tratamento de Erros e Testes

- Falhas de conexão (`httpx.RequestError`) e respostas com erro HTTP (`httpx.HTTPStatusError`) são registradas via `loguru.logger` e disparam exceções do tipo `IntegrationError`.
- Suíte de testes em [test_bwt_adapter.py](file:///Users/mateus/projects/bwt/bwt-platform-hub/app/tests/unit/adapters/test_bwt_adapter.py) possui 100% de cobertura com mocks do `respx` via fixture `mock_bwt_api`.
