## 1. Chat Persistence

- [x] 1.1 Update `SQLAlchemyChatRepositoryAdapter` to set `created_at` from `chat.created_at` or default to `datetime.now()` when creating new records
- [x] 1.2 Write/update unit and integration tests for `SQLAlchemyChatRepositoryAdapter` to verify `created_at` persistence and fallback behavior

## 2. Contact Persistence

- [x] 2.1 Update `SQLAlchemyContactRepositoryAdapter` to set `created_at` from `contact.created_at` or default to `datetime.now()` when creating new records
- [x] 2.2 Write/update unit and integration tests for `SQLAlchemyContactRepositoryAdapter` to verify `created_at` persistence and fallback behavior

## 3. Deal Persistence

- [x] 3.1 Update `SQLAlchemyDealRepositoryAdapter` to set `created_at` from `deal.created_at` or default to `datetime.now()` when creating new records
- [x] 3.2 Write/update unit and integration tests for `SQLAlchemyDealRepositoryAdapter` to verify `created_at` persistence and fallback behavior

## 4. Verification

- [x] 4.1 Run complete test suite (`pytest`) and ensure all tests pass cleanly with full coverage
