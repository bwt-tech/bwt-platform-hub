## Context

The current codebase handles domain concepts like Pipelines, DealStages, Chats, TemplateConfigurations, and SchedulerConfigs as raw python dictionaries. This increases the fragility of the application core since any external API schema changes require modifications throughout the services and workflows. Furthermore, agent contact details for notifications are hardcoded inside the Octadesk outbound adapter, violating Clean Architecture and SOLID separation of concerns.

## Goals / Non-Goals

**Goals:**
- Define domain models (`dataclasses`) for `Pipeline`, `DealStage`, `Chat`, `Agent`, `TemplateConfiguration`, and `SchedulerConfig`.
- Refactor Ports and Adapters (`RDStationPort`, `OctadeskPort`, `ConfigPort` and their implementations) to return these domain models rather than dictionaries.
- Decouple the agent information from the outbound `OctadeskAdapter`, passing it dynamically through port signatures.
- Update `templates.yaml` to include agent configurations per pipeline.
- Maintain 100% test coverage with updated mocks.

**Non-Goals:**
- Refactoring the application from synchronous to asynchronous execution.
- Modifying S3 reporting models or health endpoints.

## Decisions

### 1. Domain Entities Implementation
- **Choice**: Use standard Python `@dataclass` for the new domain entities.
- **Rationale**: Dataclasses are lightweight, built-in, and ensure that the domain layer has zero external framework dependencies (unlike Pydantic, which is heavily used in the API/contract layer but is tied to serialization concerns).
- **Alternative**: Using Pydantic `BaseModel`. Rejected to keep domain models clean and independent of serialization frameworks.

### 2. Port and Adapter Boundaries
- **Choice**: Map raw API responses to domain entities *inside the outbound adapters* before returning them through the ports.
- **Rationale**: Keeps the core application services and workflows completely isolated from third-party API payload details, upholding Hexagonal Architecture principles.
- **Alternative**: Return dicts from adapters and map them in `OrchestratorService`. Rejected because it leaks API payload details into the application services.

### 3. Agent Configuration Ingestion
- **Choice**: Store agent configuration metadata (ID, name, email) inside `templates.yaml` under each pipeline template entry.
- **Rationale**: Since `templates.yaml` is already the source of truth for pipeline template configurations, storing the target agent assignment details there is highly cohesive and keeps configuration unified.
- **Alternative**: Hardcoding them in a database or fetching dynamically from AWS Parameter Store. Rejected to avoid unnecessary complexity for a simple static mapping.

## Risks / Trade-offs

- **Risk**: Modifying all Port signatures will break existing mock configurations in unit tests.
  - **Mitigation**: Update all fixtures in `conftest.py` to return mock instances of the new domain entities rather than dictionaries.
- **Risk**: Missing configuration key in `templates.yaml` will cause runtime exceptions.
  - **Mitigation**: Implement robust default fallback values or descriptive validation errors inside the `TemplateConfiguration` parsing logic.
