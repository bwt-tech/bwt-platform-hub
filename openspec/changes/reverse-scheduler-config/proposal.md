## Why

O fluxo de sincronização reversa (`OrchestratorReverseService`) não possui controles operacionais equivalentes ao fluxo direto (`OrchestratorService`). Atualmente, não é possível habilitar/desabilitar a execução reversa nem controlar sua frequência ou volume de processamento sem redeploy. A paridade operacional entre os dois fluxos é necessária para permitir operação segura e controlada em produção.

## What Changes

- Adição de três novas chaves no AWS SSM Parameter Store exclusivas para o scheduler reverso: `enabled`, `cron` e `batch_size`.
- Criação da classe `ReverseSyncronizerScheduler` no módulo `app/src/adapters/inbound/background/scheduler.py`, espelhando o padrão já estabelecido pela `SyncronizerScheduler`.
- Adição do atributo `batch_size` na classe `OrchestratorReverseService` para respeitar o limite de chats processados por execução.
- Extensão do `AWSParameterStoreAdapter` para carregar separadamente a configuração do scheduler reverso via `get_reverse_scheduler_config()`.
- Extensão da interface `ConfigPort` com o método abstrato `get_reverse_scheduler_config()`.
- Registro do `ReverseSyncronizerScheduler` na inicialização da aplicação (FastAPI lifespan ou entrypoint existente).
- Cobertura de testes unitários 100% para todos os novos comportamentos.

## Capabilities

### New Capabilities

- `reverse-scheduler-config`: Configuração dinâmica do scheduler reverso via AWS SSM Parameter Store, permitindo controlar habilitação, frequência (cron) e tamanho de lote (`batch_size`) do `OrchestratorReverseService` sem redeploy.

### Modified Capabilities

- `scheduler-config`: A interface `ConfigPort` e o `AWSParameterStoreAdapter` são estendidos para suportar a leitura das configurações do scheduler reverso, adicionando o método `get_reverse_scheduler_config()`.

## Impact

- `app/src/adapters/inbound/background/scheduler.py` — nova classe `ReverseSyncronizerScheduler`.
- `app/src/adapters/outbounds/aws_config_adapter.py` — novo método `get_reverse_scheduler_config()` com paths SSM dedicados (`/bwt/reverse_scheduler/*`).
- `app/src/ports/config_port.py` — novo método abstrato `get_reverse_scheduler_config()`.
- `app/src/services/orchestrator_reverse.py` — adição do atributo `batch_size` e respeito ao limite no loop de chats.
- `app/tests/unit/adapters/background/test_scheduler_dynamic.py` — novos casos de teste para `ReverseSyncronizerScheduler`.
- `app/tests/unit/adapters/outbounds/test_aws_config_adapter.py` — cobertura do novo método.
- `app/tests/unit/services/test_orchestrator_reverse_service.py` — cobertura do `batch_size`.
- Nenhuma API pública HTTP é afetada. Sem breaking changes em contratos externos.
