## Why

The current `OrchestratorService` has become bloated, accumulating multiple responsibilities such as API request orchestration, business logic differentiation for new vs. existing contacts, error handling, and payload counting. Refactoring it is essential to align with the project's architectural principles (SOLID, DDD, Ports and Adapters) mapping clear boundaries for maintainability and testability.

## What Changes

- Extract core business entities out of the service into their proper domain structures.
- Separate the handling of brand new contacts vs. existing contacts into isolated workflows or use cases.
- Repurpose the counting logic (`summary["chats_started"]`, `chats_not_started`, etc.) into a cohesive summary/statistics tracker component rather than inline dictionary mutation.
- Enhance error handling by relying on specialized component boundaries, rather than a monolithic loop.

## Capabilities

### New Capabilities
- `deal-orchestration`: Extracted capability governing how deals are converted into contacts and chats, establishing clear pathways for new and existing contacts.
- `orchestration-statistics`: A new metric-capturing capability that isolates how processed items are tracked.

### Modified Capabilities

## Impact

- `app/src/services/orchestrator.py`: Major structural changes breaking it down into smaller components.
- `app/tests/unit/services/test_orchestrator_service.py`: Will require test restructuring to align with the new isolated workflows and components.
- Domain models and entities will be introduced, shifting dictionary-based data passing to typed entity objects.
