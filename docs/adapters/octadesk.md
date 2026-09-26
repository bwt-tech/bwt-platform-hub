# Octadesk Adapter Documentation

Documentação técnica do adaptador de saída da **Octadesk** (`OctadeskAdapter`) no BWT Platform Hub.

---

## 1. Arquitetura

O adaptador Octadesk implementa a porta abstrata `OctadeskPort` localizada em [octadesk_port.py](file:///Users/mateus/projects/bwt/bwt-platform-hub/app/src/ports/octadesk_port.py).

- **Porta (`OctadeskPort`)**: Define contratos para consulta de chats em andamento, mensagens, contatos por telefone e criação de novos atendimentos.
- **Adapter (`OctadeskAdapter`)**: Localizado em [octadesk.py](file:///Users/mateus/projects/bwt/bwt-platform-hub/app/src/adapters/outbounds/octadesk.py). Utiliza `httpx` para consumo das APIs REST da Octadesk.

---

## 2. Configurações e Credenciais

Configurado dinamicamente através do `Settings` (`app/src/config/settings.py`):
- `octadesk_api_key`: Chave de API da Octadesk (obtida via AWS Secrets Manager ou variável `APP_OCTADESK_API_KEY`).
- `octadesk_base_url`: URL base da API Octadesk.
- `octadesk_subdomain`: Subdomínio da organização na Octadesk.

---

## 3. Principais Operações

| Método | Endpoint HTTP | Descrição |
|---|---|---|
| `get_chats_in_progress` | `GET /chats?status=in_progress` | Lista atendimentos ativos atribuídos a um agente |
| `get_contacts_by_phone` | `GET /contacts?phone={phone}` | Pesquisa contatos pelo número de telefone |
| `post_contacts` | `POST /contacts` | Cadastra novo contato na plataforma Octadesk |
| `start_chat` | `POST /chats` | Inicia atendimento automatizado via template |
| `notify_agent` | `POST /chats/{chat_id}/messages` | Envia notificação interna para o atendente |

---

## 4. Tratamento de Erros e Logs

- Erros HTTP (`4xx` / `5xx`) ou falhas de conexão são capturados, registrados via `loguru.logger` com context de `adapter="octadesk"` e relançados como `IntegrationError`.
- Em ambiente de testes, chamadas são 100% isoladas utilizando a fixture `mock_octadesk_api` com `respx`.
