# Tasks: Persistência dos IDs BWT

## Fase 1 — Domain Layer

- [x] **T1** Criar Value Object `BWTSyncResult`
  - Arquivo: `app/src/domain/entities/bwt_sync_result.py`
  - Dataclass frozen com campos: `account_id: int`, `contact_id: int`, `deal_id: int`, `responsible_id: int | None`

- [x] **T2** Evoluir entidade `Contact` com campos BWT
  - Arquivo: `app/src/domain/entities/contact.py`
  - Adicionar: `bwt_account_id: int | None = None`, `bwt_contact_id: int | None = None`

- [x] **T3** Evoluir entidade `Deal` com campos BWT
  - Arquivo: `app/src/domain/entities/deal.py`
  - Adicionar: `bwt_deal_id: int | None = None`, `bwt_responsible_id: int | None = None`

- [x] **T4** Evoluir Port `ContactRepositoryPort` com métodos BWT
  - Arquivo: `app/src/domain/repositories/contact_repository.py`
  - Adicionar métodos abstratos: `find_by_bwt_contact_id`, `find_by_bwt_account_id`

- [x] **T5** Evoluir Port `DealRepositoryPort` com método BWT
  - Arquivo: `app/src/domain/repositories/deal_repository.py`
  - Adicionar método abstrato: `find_by_bwt_deal_id`

## Fase 2 — Infrastructure Layer

- [x] **T6** Adicionar colunas BWT ao `ContactModel` e `DealModel`
  - Arquivo: `app/src/adapters/database/models.py`
  - `ContactModel`: `bwt_account_id = Column(Integer, unique=True, nullable=True)`, `bwt_contact_id = Column(Integer, unique=True, nullable=True)`
  - `DealModel`: `bwt_deal_id = Column(Integer, unique=True, nullable=True)`, `bwt_responsible_id = Column(Integer, nullable=True)`

- [x] **T7** Criar migration Alembic para adicionar colunas BWT
  - Arquivo: `migrations/versions/<rev>_add_bwt_ids_to_contact_and_deal.py`
  - `upgrade`: `op.add_column` para as 4 novas colunas com UniqueConstraint onde aplicável
  - `downgrade`: `op.drop_column` / `op.drop_constraint` para reversão

- [x] **T8** Evoluir `SQLAlchemyContactRepositoryAdapter`
  - Arquivo: `app/src/adapters/database/repositories/contact_repository_adapter.py`
  - Atualizar `_to_domain` para mapear `bwt_account_id` e `bwt_contact_id`
  - Atualizar `save` para persistir `bwt_account_id` e `bwt_contact_id`
  - Implementar `find_by_bwt_contact_id` e `find_by_bwt_account_id`

- [x] **T9** Evoluir `SQLAlchemyDealRepositoryAdapter`
  - Arquivo: `app/src/adapters/database/repositories/deal_repository_adapter.py`
  - Atualizar `_to_domain` para mapear `bwt_deal_id` e `bwt_responsible_id`
  - Atualizar `save` para persistir `bwt_deal_id` e `bwt_responsible_id`
  - Implementar `find_by_bwt_deal_id`

## Fase 3 — Service Layer

- [x] **T10** Alterar `BWTReverseSyncService.sync()` para retornar `BWTSyncResult`
  - Arquivo: `app/src/services/workflows/bwt_reverse_sync_service.py`
  - Coletar `account`, `contact`, `deal`, `responsible` ao longo do fluxo
  - Retornar `BWTSyncResult(account_id=..., contact_id=..., deal_id=..., responsible_id=...)`

- [x] **T11** Alterar `ReverseSyncWorkflow` para persistir IDs BWT
  - Arquivo: `app/src/services/workflows/reverse_sync_workflow.py`
  - Capturar retorno de `bwt_sync.sync()` como `BWTSyncResult`
  - Implementar `_persist_bwt_ids(contact, deal, bwt_result)` para atualizar e salvar entidades

## Fase 4 — Testes

- [x] **T12** Testes unitários de `BWTReverseSyncService`
  - Verificar que `sync()` retorna `BWTSyncResult` com os IDs corretos
  - Cenários: criação de novos recursos, reuso de existentes, com e sem responsável

- [x] **T13** Testes unitários de `ReverseSyncWorkflow`
  - Verificar que `_persist_bwt_ids` é chamado após `bwt_sync.sync()`
  - Verificar que `contact_repo.save` e `deal_repo.save` são chamados com campos BWT atualizados

- [x] **T14** Testes unitários dos Repository Adapters
  - `SQLAlchemyContactRepositoryAdapter`: `save()` persiste `bwt_account_id`/`bwt_contact_id`; `find_by_bwt_contact_id`/`find_by_bwt_account_id` retornam entidade ou None
  - `SQLAlchemyDealRepositoryAdapter`: `save()` persiste `bwt_deal_id`/`bwt_responsible_id`; `find_by_bwt_deal_id` retorna entidade ou None
