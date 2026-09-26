## 1. Setup and Preparation

- [x] 1.1 Import `get_session` and the repository adapters in `app/src/adapters/inbound/background/scheduler.py`
- [x] 1.2 Store `OctadeskAdapter` and `RDStationAdapter` instances as scheduler attributes (`self._octadesk`, `self._rdstation`) in `SyncronizerScheduler.__init__`

## 2. Core Implementation

- [x] 2.1 Refactor `SyncronizerScheduler._execute()` to wrap the execution inside the `get_session()` context manager block
- [x] 2.2 Inside the context manager, instantiate `SQLAlchemyContactRepositoryAdapter`, `SQLAlchemyDealRepositoryAdapter`, and `SQLAlchemyChatRepositoryAdapter` using the database session
- [x] 2.3 Re-assign `self._service` dynamically within `_execute()` using the active repository adapters and update it with the loaded batch size configuration

## 3. Testing and Validation

- [x] 3.1 Implement a mock database session context fixture in `app/tests/unit/adapters/background/test_scheduler_dynamic.py`
- [x] 3.2 Verify that the scheduler unit tests run and pass without attempting real database connections
- [x] 3.3 Implement a functional test in `app/tests/functional/` to run the scheduler loop and assert that contacts, deals, and chats are successfully persisted to the database
- [x] 3.4 Run the full test suite and confirm 100% test coverage is maintained (`pytest --cov=app --cov-fail-under=100`)

