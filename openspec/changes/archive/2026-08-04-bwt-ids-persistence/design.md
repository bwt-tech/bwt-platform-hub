# Design Document: Persistência dos IDs BWT

## Visão Geral da Arquitetura

Esta mudança segue rigorosamente os princípios de **Ports & Adapters (Hexagonal)** e **DDD** definidos no AGENTS.md. As alterações se distribuem pelas camadas:

```
Domain Layer  → entities/contact.py, entities/deal.py
               → value_objects/bwt_sync_result.py (NOVO)
               → repositories/contact_repository.py
               → repositories/deal_repository.py
Infrastructure → adapters/database/models.py
               → adapters/database/repositories/contact_repository_adapter.py
               → adapters/database/repositories/deal_repository_adapter.py
               → migrations/versions/<rev>_add_bwt_ids.py (NOVO)
Service Layer  → services/workflows/bwt_reverse_sync_service.py
               → services/workflows/reverse_sync_workflow.py
```

---

## 1. Domain Layer

### 1.1 Value Object: `BWTSyncResult`

**Arquivo:** `app/src/domain/entities/bwt_sync_result.py` *(NOVO)*

```python
@dataclass(frozen=True)
class BWTSyncResult:
    """Resultado imutável de uma sincronização com a BWT."""
    account_id: int
    contact_id: int
    deal_id: int
    responsible_id: int | None = None
```

Representa o resultado da sincronização BWT como Value Object imutável. Encapsula os IDs retornados pela API BWT sem expor detalhes de infraestrutura.

### 1.2 Entidade `Contact` — Evolução

**Arquivo:** `app/src/domain/entities/contact.py` *(MODIFICADO)*

Novos campos opcionais:
```python
bwt_account_id: int | None = None
bwt_contact_id: int | None = None
```

### 1.3 Entidade `Deal` — Evolução

**Arquivo:** `app/src/domain/entities/deal.py` *(MODIFICADO)*

Novos campos opcionais:
```python
bwt_deal_id: int | None = None
bwt_responsible_id: int | None = None
```

### 1.4 Port `ContactRepositoryPort` — Novos métodos

**Arquivo:** `app/src/domain/repositories/contact_repository.py` *(MODIFICADO)*

```python
@abstractmethod
def find_by_bwt_contact_id(self, bwt_contact_id: int) -> Contact | None:
    pass

@abstractmethod  
def find_by_bwt_account_id(self, bwt_account_id: int) -> Contact | None:
    pass
```

### 1.5 Port `DealRepositoryPort` — Novo método

**Arquivo:** `app/src/domain/repositories/deal_repository.py` *(MODIFICADO)*

```python
@abstractmethod
def find_by_bwt_deal_id(self, bwt_deal_id: int) -> Deal | None:
    pass
```

---

## 2. Infrastructure Layer

### 2.1 SQLAlchemy Models

**Arquivo:** `app/src/adapters/database/models.py` *(MODIFICADO)*

#### `ContactModel` — Novas colunas
```python
bwt_account_id = Column(Integer, unique=True, nullable=True)
bwt_contact_id = Column(Integer, unique=True, nullable=True)
```

#### `DealModel` — Novas colunas
```python
bwt_deal_id = Column(Integer, unique=True, nullable=True)
bwt_responsible_id = Column(Integer, nullable=True)
```

> **Decisão de design**: `bwt_responsible_id` é nullable e **não unique**, pois o mesmo responsável pode estar atribuído a múltiplos deals.

### 2.2 Migration Alembic

**Arquivo:** `migrations/versions/<rev>_add_bwt_ids_to_contact_and_deal.py` *(NOVO)*

```sql
-- upgrade
ALTER TABLE contact ADD COLUMN bwt_account_id INTEGER UNIQUE;
ALTER TABLE contact ADD COLUMN bwt_contact_id INTEGER UNIQUE;
ALTER TABLE deal    ADD COLUMN bwt_deal_id INTEGER UNIQUE;
ALTER TABLE deal    ADD COLUMN bwt_responsible_id INTEGER;
```

### 2.3 `ContactRepositoryAdapter` — Evolução

**Arquivo:** `app/src/adapters/database/repositories/contact_repository_adapter.py` *(MODIFICADO)*

- `_to_domain`: Mapeia `bwt_account_id` e `bwt_contact_id` do model para a entidade.
- `save`: Persiste `bwt_account_id` e `bwt_contact_id` quando fornecidos.
- `find_by_bwt_contact_id`: Query por `ContactModel.bwt_contact_id`.
- `find_by_bwt_account_id`: Query por `ContactModel.bwt_account_id`.

### 2.4 `DealRepositoryAdapter` — Evolução

**Arquivo:** `app/src/adapters/database/repositories/deal_repository_adapter.py` *(MODIFICADO)*

- `_to_domain`: Mapeia `bwt_deal_id` e `bwt_responsible_id` do model para a entidade.
- `save`: Persiste `bwt_deal_id` e `bwt_responsible_id` quando fornecidos.
- `find_by_bwt_deal_id`: Query por `DealModel.bwt_deal_id`.

---

## 3. Service Layer

### 3.1 `BWTReverseSyncService` — Retorno de IDs

**Arquivo:** `app/src/services/workflows/bwt_reverse_sync_service.py` *(MODIFICADO)*

O método `sync()` passa a retornar `BWTSyncResult` em vez de `None`:

```python
def sync(self, ...) -> BWTSyncResult:
    account, contact = self._resolve_or_create_account_and_contact(...)
    deal = self._resolve_or_create_active_deal(...)
    responsible = self._advance_deal_and_assign_seller(...)
    return BWTSyncResult(
        account_id=account.id,
        contact_id=contact.id,
        deal_id=deal.id,
        responsible_id=responsible.id if responsible else None,
    )
```

### 3.2 `ReverseSyncWorkflow` — Persistência dos IDs

**Arquivo:** `app/src/services/workflows/reverse_sync_workflow.py` *(MODIFICADO)*

Após a chamada ao `bwt_sync.sync()`, o workflow atualiza as entidades `Contact` e `Deal` com os IDs BWT e os persiste:

```python
bwt_result = self._bwt_sync.sync(bwt_port=bwt_port, ...)
if bwt_result and self._contact_repo and self._deal_repo:
    self._persist_bwt_ids(contact, deal, bwt_result)

def _persist_bwt_ids(self, contact, deal, bwt_result: BWTSyncResult) -> None:
    contact.bwt_account_id = bwt_result.account_id
    contact.bwt_contact_id = bwt_result.contact_id
    self._contact_repo.save(contact)
    deal.bwt_deal_id = bwt_result.deal_id
    deal.bwt_responsible_id = bwt_result.responsible_id
    self._deal_repo.save(deal)
```

---

## 4. Diagrama de Mapeamento

```
Octadesk (chat)
    ↓
ContactModel.octadesk_id     → Octadesk Contact ID
ContactModel.rdstation_id    → RD Station Contact ID
ContactModel.bwt_account_id  → BWT Account ID  ← NOVO
ContactModel.bwt_contact_id  → BWT Contact ID  ← NOVO

DealModel.rdstation_id       → RD Station Deal ID
DealModel.bwt_deal_id        → BWT Deal ID     ← NOVO
DealModel.bwt_responsible_id → BWT Responsible ← NOVO
```

---

## 5. Estratégia de Testes

- **Unit Tests** do `BWTReverseSyncService`: Verificar que `sync()` retorna `BWTSyncResult` com os IDs corretos nos cenários de criação, encontrar existente e assign de responsável.
- **Unit Tests** do `ReverseSyncWorkflow`: Verificar que `_persist_bwt_ids` é chamado e os repositórios recebem as entidades atualizadas.
- **Unit Tests** dos Repository Adapters: Verificar `save()` e `find_by_bwt_*` com mocks de sessão SQLAlchemy.
- **Cobertura**: 100% nas linhas adicionadas/modificadas.
