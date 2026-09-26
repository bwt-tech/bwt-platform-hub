# Tasks: Refactor Orchestrator Reverse Service

- [x] 1. Criar camada de domínio
  - `DealStatusPolicy`, `AgentSellerConfiguration`, `PipelineScopeResolver`, `DealFactory`
- [x] 2. Criar factories e loaders
  - `BWTPortFactory`, `AgentSellerConfigLoader`
- [x] 3. Extrair sub-serviços de sync
  - `RDStationReverseSyncService`, `BWTReverseSyncService`
- [x] 4. Refatorar `ReverseSyncWorkflow` como coordenador
  - Recebe `bwt_port` por chat via `execute()`
- [x] 5. Refatorar `OrchestratorReverseService`
  - Orquestrador fino; `BWTPortFactory.create(scope)` a cada chat
- [x] 6. Testes unitários
  - Cobertura para resolver, policy, factory e workflows
- [x] 7. Documentação
  - Atualizar `README.md` e `design.md`
