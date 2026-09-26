## Why

The database persistence layer is fully implemented and tested in isolation. However, in the background scheduler (`SyncronizerScheduler`), the `OrchestratorService` is instantiated without passing repository adapters. This means no contacts, deals, or chats are saved locally during background runs, violating core business requirements for local caching and transaction persistence.

## What Changes

- Modify `SyncronizerScheduler` to instantiate `OrchestratorService` with SQLAlchemy database repository adapters inside the execution loop.
- Scopes the database session lifecycle to the execution runs utilizing `get_session()` to guarantee transaction boundaries and resource clean up.
- Maintain compatibility with existing scheduler mock tests by properly assigning the service mock inside the execution block.
- Mock database session context in the scheduler unit tests to isolate execution from live database instances.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `deal-orchestration`: Integrate local database checking and persistence into the background deal synchronization loop.

## Impact

- `app/src/adapters/inbound/background/scheduler.py`: Wire database session context and repository adapters into `_execute()`.
- `app/tests/unit/adapters/background/test_scheduler_dynamic.py`: Mock `get_session` context and verify dynamic service instantiation and transaction boundaries.
