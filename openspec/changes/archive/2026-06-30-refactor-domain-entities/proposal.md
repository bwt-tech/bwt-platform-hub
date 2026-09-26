## Why

The current codebase represents several key domain concepts—such as Pipelines, DealStages, Chats, TemplateConfigurations, and SchedulerConfigs—as raw python dictionaries, which violates Domain-Driven Design (DDD) encapsulation and leads to fragile dictionary-indexing operations across the core logic. Additionally, agent contact details for notifications are hardcoded inside the Octadesk outbound adapter, violating the Clean Architecture/SOLID principle of decoupling infrastructure from business decisions.

## What Changes

- **Domain Entities**: Introduce explicit domain models (entities and value objects) for `Pipeline`, `DealStage`, `Chat`, `Agent`, `TemplateConfiguration`, and `SchedulerConfig`.
- **Adapter Refactoring**: Update outbound adapters (`RDStationAdapter`, `OctadeskAdapter`, `AWSParameterStoreAdapter`) to return these domain models rather than raw dictionaries/primitives.
- **Service & Workflow Refactoring**: Update `OrchestratorService` and its workflows (`NewContactWorkflow`, `ExistingContactWorkflow`, `RecurringNoAnswerChecker`) to operate strictly on the new domain entities.
- **Dynamic Agent Mentions**: Decouple agent notification logic by passing an `Agent` entity to `notify_agent()`, resolving the agent dynamically from configuration rather than hardcoding Vanessa's credentials in `octadesk.py`.
- **BREAKING (Configuration)**: Update `templates.yaml` to include agent metadata parameters (ID, name, email) per pipeline to drive dynamic notifications.

## Capabilities

### New Capabilities
*None*

### Modified Capabilities
- `deal-orchestration`: Update the orchestration process requirements to demand typed domain entities (`Pipeline`, `DealStage`, `Chat`, `Agent`, `TemplateConfiguration`) and dynamic agent configuration routing rather than dictionary indexing and hardcoded adapter values.

## Impact

- **Domain Layer**: New files under `app/src/domain/entities/`: `pipeline.py`, `deal_stage.py`, `chat.py`, `agent.py`, `template_configuration.py`, and `scheduler_config.py`.
- **Ports & Adapters**: Updated signatures and implementation for `RDStationPort`/`RDStationAdapter`, `OctadeskPort`/`OctadeskAdapter`, and `ConfigPort`/`AWSParameterStoreAdapter` to use the new typed objects.
- **Services & Workflows**: `OrchestratorService`, `NewContactWorkflow`, and `ExistingContactWorkflow` updated to use domain models.
- **Configuration**: Modifying `templates.yaml` to store agent assignment metadata.
- **Tests**: Mock adjustments in `conftest.py` and unit/functional tests to use typed models instead of dictionary payloads.
