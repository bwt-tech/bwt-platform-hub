## 1. Domain Entities Implementation

- [x] 1.1 Create `Pipeline` and `DealStage` entities in `app/src/domain/entities/`
- [x] 1.2 Create `Chat` and `Agent` entities in `app/src/domain/entities/`
- [x] 1.3 Create `TemplateConfiguration` and `SchedulerConfig` domain entities

## 2. Ports and Adapters Update

- [x] 2.1 Update `RDStationPort` and `RDStationAdapter` to return typed `Pipeline` and stage models
- [x] 2.2 Update `OctadeskPort` and `OctadeskAdapter` to return typed `Chat` and handle dynamic `Agent` notification
- [x] 2.3 Update `ConfigPort` and `AWSParameterStoreAdapter` to return `SchedulerConfig` objects

## 3. Configuration & Services Refactoring

- [x] 3.1 Update `templates.yaml` to include agent ID, name, and email per pipeline entry
- [x] 3.2 Update `OrchestratorService` to parse configurations and process pipelines using the new domain models
- [x] 3.3 Update `NewContactWorkflow`, `ExistingContactWorkflow`, and `RecurringNoAnswerChecker` to use typed domain entities and dynamic agent notification parameters

## 4. Tests and Verification

- [x] 4.1 Update all unit test fixtures in `conftest.py` to return mock domain entities
- [x] 4.2 Refactor unit and functional tests to comply with the updated port contracts and assert dynamic agent notification parameters
- [x] 4.3 Run test suite via `pytest --cov=app --cov-fail-under=100` to verify full correctness and 100% test coverage compliance
