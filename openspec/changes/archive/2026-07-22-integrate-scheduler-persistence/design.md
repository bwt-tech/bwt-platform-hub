## Context

The system has a fully configured database persistence layer with Alembic migrations, database models, and repository adapters (`SQLAlchemyContactRepositoryAdapter`, `SQLAlchemyDealRepositoryAdapter`, and `SQLAlchemyChatRepositoryAdapter`).

Currently, the scheduler (`SyncronizerScheduler`) instantiates `OrchestratorService` without these repository adapters, meaning background periodic runs completely bypass database operations. This design details how to bridge this gap safely and securely.

## Goals / Non-Goals

**Goals:**
- Wire the database session lifecycle and repository adapters to the background scheduler's periodic synchronization runs.
- Guarantee transaction integrity (commit/rollback/close) per execution loop run.
- Prevent stale connections, pool exhaustion, and resource leaks.
- Keep unit and functional tests 100% passing and compliant with the 100% coverage target.

**Non-Goals:**
- Re-architecting database models, entities, or ports.
- Refactoring the core execution logic of `OrchestratorService` or workflows.

## Decisions

### Decision 1: Scoped Database Session per Run Loop
- **Approach**: Wrap the synchronization loop execution in `_execute()` inside a `get_session()` context manager block.
- **Alternatives considered**:
  - Keep a single database session for the scheduler lifetime. Rejected because SQLAlchemy sessions are not thread-safe and long-lived sessions suffer from stale connection errors and database pool exhaustion.
- **Rationale**: The context manager ensures that for each cron/interval run, a fresh database connection is established, commits/rollbacks are cleanly isolated to that run, and resources are closed immediately when finished.

### Decision 2: Re-assign `self._service` inside `_execute()`
- **Approach**: Assign the newly created `OrchestratorService` (which receives the repo adapters) to `self._service` within the `_execute()` function.
- **Alternatives considered**:
  - Use a separate local variable `service` and do not touch `self._service`. Rejected because existing unit tests check calls and attributes on `self._service`.
- **Rationale**: Preserves maximum compatibility with existing tests by ensuring the active service instance (or its mock during tests) is always pointed to by `self._service`.

## Risks / Trade-offs

- **[Risk]**: Database connections could be attempted during scheduler unit tests if `get_session` is called.
  - **Mitigation**: Globally patch `get_session` in `test_scheduler_dynamic.py` using a mock context manager.
- **[Risk]**: Concurrent runs of the scheduler could cause race conditions if the cron trigger is configured too frequently.
  - **Mitigation**: Standard APScheduler configuration blocks concurrent execution of the same job, and database transactional locks isolate queries.
