# RD Station CRM Adapter Documentation

Documentação técnica do adaptador de saída do **RD Station CRM** (`RDStationAdapter`) no BWT Platform Hub.

---

## 1. Arquitetura

O adaptador RD Station implementa a porta abstrata `RDStationPort` localizada em [rdstation_port.py](file:///Users/mateus/projects/bwt/bwt-platform-hub/app/src/ports/rdstation_port.py).

- **Porta (`RDStationPort`)**: Interface que abstrai operações de negociações (Deals), contatos, pipelines, estágios do funil e campos customizados.
- **Adapter (`RDStationAdapter`)**: Localizado em [rdstation.py](file:///Users/mateus/projects/bwt/bwt-platform-hub/app/src/adapters/outbounds/rdstation.py). Consome a API v1 do RD Station CRM utilizando `httpx`.

---

## 2. Configurações e Credenciais

Configurado dinamicamente através do `Settings` (`app/src/config/settings.py`):
- `rdstation_token`: Token de autenticação da API RD Station CRM (armazenado no AWS Secrets Manager).
- `rdstation_url`: URL base da API (`https://crm.rdstation.com/api/v1`).

---

## 3. Principais Operações

| Método | Endpoint HTTP | Descrição |
|---|---|---|
| `get_deals` | `GET /deals?token=...` | Busca negociações filtrando por estágio, nome ou período |
| `get_deal` | `GET /deals/{deal_id}?token=...` | Obtém detalhes de uma negociação específica |
| `put_deal` | `PUT /deals/{deal_id}?token=...` | Atualiza estágio ou campos customizados do vendedor |
| `post_deal` | `POST /deals?token=...` | Cria nova negociação com contatos e campos customizados |
| `get_deal_pipelines` | `GET /deal_pipelines?token=...` | Retorna lista de pipelines e seus estágios (`Pipeline` domain entity) |
| `get_contacts` | `GET /contacts?token=...` | Consulta contatos no CRM por telefone ou período |

---

## 4. Tratamento de Erros e Logs

- Exceções HTTP e de comunicação lançam `IntegrationError`.
- Logs de sucesso e erro são registrados via `loguru` contendo contexto `adapter="rdstation"`.
- Testes usam `mock_rdstation_api` via `respx` para isolamento total.
