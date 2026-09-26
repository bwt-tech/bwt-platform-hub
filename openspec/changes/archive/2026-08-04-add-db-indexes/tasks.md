# Tasks: Índices de Banco de Dados

## 1. Models SQLAlchemy

- [x] 1.1 Adicionar `__table_args__` em `DealModel` com `Index("ix_deal_contact_id", "contact_id")` e `Index("ix_deal_contact_id_rdstation_id", "contact_id", "rdstation_id")`
  - Arquivo: `app/src/adapters/database/models.py`
  - Importar `Index` de `sqlalchemy`

- [x] 1.2 Adicionar `__table_args__` em `ChatModel` com `Index("ix_chat_contact_id", "contact_id")`
  - Arquivo: `app/src/adapters/database/models.py`

## 2. Migration Alembic

- [x] 2.1 Criar arquivo de migration `migrations/versions/<rev>_add_indexes_to_deal_and_chat.py`
  - `upgrade`: `op.create_index("ix_deal_contact_id", "deal", ["contact_id"])`, `op.create_index("ix_deal_contact_id_rdstation_id", "deal", ["contact_id", "rdstation_id"])`, `op.create_index("ix_chat_contact_id", "chat", ["contact_id"])`
  - `downgrade`: `op.drop_index` na ordem inversa para os três índices

## 3. Testes

- [x] 3.1 Testes unitários de `DealModel` e `ChatModel`: verificar que `__table_args__` declara os índices esperados por nome
  - Arquivo: `app/tests/unit/adapters/database/test_models.py`

- [x] 3.2 Testes de integração dos repository adapters com db_session: verificar que `find_by_contact_id` (Deal e Chat) e `find_by_contact_id_and_rd_station_id` (Deal) retornam a entidade correta ou `None`
  - Arquivos: `app/tests/unit/adapters/database/repositories/test_deal_repository.py`, `app/tests/unit/adapters/database/repositories/test_chat_repository.py`
