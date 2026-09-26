# Proposal: Refactor Orchestrator Reverse Service

## Intent
Refatorar a classe `OrchestratorReverseService` ([orchestrator_reverse.py](file:///Users/mateus/projects/bwt/bwt-platform-hub/app/src/services/orchestrator_reverse.py)), responsável pela sincronização no sentido Octadesk -> RD Station & Persistência Local, adequando-a rigorosamente aos princípios de Domain-Driven Design (DDD), Clean Architecture e SOLID estipulados no [AGENTS.md](file:///Users/mateus/projects/bwt/bwt-platform-hub/AGENTS.md).

## Problem Statement
A classe atual apresenta vários pontos críticos de arquitetura e bugs de execução:
1. **Violação do SRP / DDD**: A classe atua como "God Class", misturando leitura direta de YAML (`agents2seller.yaml`), chamadas diretas de APIs externas, normalização e controle de transições de estágio de negociação.
2. **Bug de Iteração**: Presença de um `return` precoce dentro dos loops internos (linha 165), fazendo com que apenas o primeiro chat/contato seja processado.
3. **Injeção Manual Exigida (`get_deal`)**: O método `RDStationPort.get_deal` não retorna contatos associados. O serviço atual realiza uma atribuição manual direta `deal_dict["contacts"] = [rd_contact]` antes de chamar `Deal.from_dict`. Isso precisa ser encapsulado de forma limpa e transparente.

## Proposed Solution
- Extrair a lógica do ciclo de sincronização por contato/chat para um **Workflow dedicado** (`ReverseSyncWorkflow`) na camada `app/src/services/workflows/`.
- Refatorar o `OrchestratorReverseService` para atuar puramente como orquestrador da camada de aplicação.
- Garantir a amarração correta entre o contato retornado da RD Station e a busca detalhada do negócio (`get_deal`).
- Corrigir bugs de digitação e controle de loop (`deal.rdstation_id`).
- Garantir 100% de cobertura de testes unitários com mocks.

## Non-Goals
- Alterar as APIs externas do Octadesk ou RD Station.
- Utilizar `ProcessSummaryTracker` na sincronização reversa (removido a pedido).
- Alterar as estruturas de tabelas do banco de dados (schema existente de Contact, Deal e Chat é mantido).
