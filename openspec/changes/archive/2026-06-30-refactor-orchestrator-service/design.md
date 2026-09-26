## Context

The `OrchestratorService` has accumulated multiple responsibilities. The user requested identifying new contacts versus existing contacts, moving tracking counters to a different entity, and separating the extraction of domain entities. This refactor aligns the codebase with our Hexagonal Architecture/DDD principles by ensuring that domain rules (what a contact is, what a chat is) and use-case workflows (how to process a deal into a chat) are separated from external API handlers and payload aggregations.

## Goals / Non-Goals

**Goals:**
- Extract tracking data structure (statistics of processed deals).
- Extract entities (`Deal`, `Contact`, `Chat`) to avoid pure dictionary manipulation.
- Separate "deal for **new** contact" handling from "deal for **existing** contact" handling workflows.

**Non-Goals:**
- Do not rewrite the external Adapters (`OctadeskAdapter`, `RDStationAdapter`).
- Do not alter the overarching pipeline configuration keys (`NO_CONTACT`, `NO_ANSWER`, `CONTACTED`) beyond what is necessary to satisfy the refactor.

## Decisions

- **Domain Entities**: Create `Contact`, `Deal`, and process summary entities (e.g. `ProcessSummary`) structurally. Reason: Stops deeply nested loops and dict indexing (e.g., `deal["contacts"][0]["phones"][0]["phone"]`) scattering across the service layer.
- **Orchestration Breakdown**: Break `OrchestratorService` logic into workflow handlers (`_process_new_contact`, `_process_existing_contact`). Reason: Improves readability, reduces cognitive complexity of the main `start_process` block.
- **Summary Tracker**: Introduce a class `ProcessSummaryTracker` that manages counts (`chats_started`, `chats_not_started` etc). Reason: Centralizes accounting instead of massive inline dictionary mutations.

## Risks / Trade-offs

- **Risk**: Test suites are tightly coupled to current internal looping logic. → **Mitigation**: Refactor step-by-step; the existing `test_orchestrator_service.py` with the robust mock setups will be an anchor point.
- **Risk**: Losing track of a step in the deal transition. → **Mitigation**: Validating test scenarios ensuring that `put_deal` happens precisely at the end of both existing and new flow conditions.
