# Design Document: Refactor Orchestrator Reverse Service

## Architecture & DDD Compliance

### 1. Application Service vs Workflow vs Sub-Services

- `OrchestratorReverseService` atua como orquestrador fino: carrega configuração, itera agentes/chats, resolve escopo e delega.
- `ReverseSyncWorkflow` coordena os três passos por chat: persistência local → RD Station → BWT.
- `RDStationReverseSyncService` encapsula regras de negociação na RD Station.
- `BWTReverseSyncService` encapsula conta, contato, deal e atribuição de vendedor na BWT.

### 2. Escopo BWT por Chat (Regra de Negócio)

- Cada entrada em `agents2seller.yaml` associa um escopo BWT (`SBM`, `SBS`, `SG`) ao pipeline.
- Agentes com `pipelines_by_tag` resolvem escopo dinamicamente pelas tags do chat.
- **`BWTPortFactory`** cria uma instância isolada de `BWTPort` a cada chat — não reutiliza adapter compartilhado com `configure_scope`.
- `PipelineScopeResolver` (domínio) centraliza a resolução pipeline + escopo.

### 3. RD Station `get_deal` Contact Context Injection

- `DealFactory.from_rd_deal_with_contact` encapsula a injeção `deal_dict["contacts"] = [rd_contact]` antes de `Deal.from_dict`.

### 4. State Management & Flow Decisions

- Regras centralizadas em `DealStatusPolicy`:
  - `WITH_SELLER = "EPV"`
  - `IN_PROGRESS = {"EPV", "PE"}`
  - `UPDATE_PROGRESS = {"SC", "CF"}`
  - `FINAL_STATUS = {"NR", "SI", "IF", "PR", "VF"}`

### 5. Estrutura de Arquivos

```
app/src/
├── domain/
│   ├── entities/agent_seller_configuration.py
│   ├── factories/deal_factory.py
│   ├── policies/deal_status_policy.py
│   └── services/pipeline_scope_resolver.py
├── services/
│   ├── agent_seller_config_loader.py
│   ├── factories/bwt_port_factory.py
│   ├── orchestrator_reverse.py
│   └── workflows/
│       ├── reverse_sync_workflow.py
│       ├── rd_station_reverse_sync_service.py
│       └── bwt_reverse_sync_service.py
```
