## 1. Domain Entities

- [x] 1.1 Create `app/src/domain/entities/contact.py` with a `Contact` dataclass (name, phone, email, deal_id, optional chat_response)
- [x] 1.2 Create `app/src/domain/entities/deal.py` with a `Deal` dataclass and factory method to build from RD Station deal dict
- [x] 1.3 Add phone normalization and prerequisite validation as methods on `Deal` (replacing `_get_phone`, `_get_email`, `_validate_pre_requisites`)
- [x] 1.4 Create `app/src/domain/entities/__init__.py` exporting public entities

## 2. Process Summary Tracker

- [x] 2.1 Create `app/src/domain/process_summary_tracker.py` with `ProcessSummaryTracker` class
- [x] 2.2 Implement zeroed counter initialization matching current summary dict fields (pipeline, deals_processed, contacts_created, etc.)
- [x] 2.3 Implement record methods for each outcome (record_contact_created, record_contact_existing, record_chat_started, record_chat_not_started, record_chat_existing, record_recurring_no_answer, record_deal_failed, record_deal_moved, record_deal_processed)
- [x] 2.4 Implement `to_dict()` method that produces the same summary structure currently returned by `start_process`

## 3. Workflow Handlers

- [x] 3.1 Create `app/src/services/workflows/new_contact_workflow.py` with handler that creates contact, starts chat, notifies agent, and moves deal
- [x] 3.2 Create `app/src/services/workflows/existing_contact_workflow.py` with handler that branches on chat existence (notify + move deal, or record no chat)
- [x] 3.3 Create `app/src/services/workflows/recurring_no_answer_checker.py` extracting `_is_recurring_no_answer` logic
- [x] 3.4 Create `app/src/services/workflows/__init__.py` exporting workflow handlers

## 4. Orchestrator Refactor

- [x] 4.1 Slim down `OrchestratorService.start_process` to orchestrate pipeline iteration, template resolution, and workflow delegation
- [x] 4.2 Replace inline summary dict mutation with `ProcessSummaryTracker` calls in the main loop
- [x] 4.3 Replace `_process_new_contact` and `_process_existing_contact` inline logic with dedicated workflow handler calls
- [x] 4.4 Keep adapter lookup helpers (`_has_contact`, `_has_chat`, `_get_existing_chat_id`, `_all_phones`) in orchestrator or extract to a shared lookup helper if needed by workflows
- [x] 4.5 Preserve existing behavior for batch_size limiting, PROCESSED phone deduplication, and pipeline stage constants (NO_CONTACT, NO_ANSWER, CONTACTED)

## 5. Test Updates

- [x] 5.1 Add unit tests for `Contact` and `Deal` entity factories and validation
- [x] 5.2 Add unit tests for `ProcessSummaryTracker` counter and detail recording
- [x] 5.3 Add unit tests for new-contact and existing-contact workflow handlers in isolation
- [x] 5.4 Verify all existing tests in `test_orchestrator_service.py` pass without behavior changes
- [x] 5.5 Run full test suite and confirm no regressions
