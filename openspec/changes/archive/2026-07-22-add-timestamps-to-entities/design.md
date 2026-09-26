## Context

As tabelas `chat`, `contact` e `deal` foram criadas na migration inicial (`0c6e3a5af8f8`) sem campos de rastreabilidade temporal. A base já possui dados em produção, portanto qualquer alteração de schema deve ser não-destrutiva e compatível com registros pré-existentes. O projeto usa SQLAlchemy com Alembic para gestão de schema e segue o padrão Ports & Adapters (Hexagonal Architecture) com DDD.

Stack relevante:
- **ORM**: SQLAlchemy (declarative models em `app/src/adapters/database/models.py`)
- **Migrations**: Alembic (diretório `migrations/`, `alembic.ini` na raiz)
- **Domínio**: Entidades puras em `app/src/domain/entities/` sem dependência de ORM

## Goals / Non-Goals

**Goals:**
- Adicionar `created_at` e `updated_at` (nullable) nas tabelas `chat`, `contact` e `deal` via nova migration Alembic.
- Atualizar os SQLAlchemy models para persistir automaticamente os timestamps (via `server_default` e `onupdate`).
- Expor os campos opcionais nas entidades de domínio (`Chat`, `Contact`, `Deal`).
- Garantir que dados existentes na base não sejam afetados (colunas nullable, sem backfill obrigatório agora).
- Manter 100% de cobertura de testes.

**Non-Goals:**
- Backfill dos dados existentes (será feito em change separado após validação).
- Tornar as colunas `NOT NULL` agora (será feito em change futuro após o backfill).
- Adicionar timestamps em outras entidades além de `chat`, `contact` e `deal`.
- Expor os timestamps via API/endpoints (pode ser feito futuramente).

## Decisions

### 1. Colunas nullable na migration inicial

**Decisão**: `created_at` e `updated_at` serão criadas com `nullable=True`.

**Rationale**: A base já possui dados sem esses valores. Criar as colunas como `NOT NULL` exigiria backfill atômico dentro da própria migration, o que pode ser lento e arriscado em produção. A abordagem em duas fases (nullable agora → NOT NULL após backfill) é padrão para deploys seguros em produção.

**Alternativa rejeitada**: `NOT NULL` com `server_default=func.now()` imediato. Rejeitada porque não reflete a data real de criação dos registros existentes, gerando dados incorretos.

### 2. Timezone-aware: `TIMESTAMP WITH TIME ZONE`

**Decisão**: Usar `DateTime(timezone=True)` no SQLAlchemy (mapeia para `TIMESTAMPTZ` no PostgreSQL).

**Rationale**: Evita ambiguidade de timezone em sistemas distribuídos e facilita comparações temporais corretas. Todos os timestamps novos devem ser armazenados em UTC.

**Alternativa rejeitada**: `DateTime` sem timezone. Rejeitada por gerar bugs difíceis de depurar em ambientes com configuração de timezone diferente do servidor de banco.

### 3. `server_default` e `onupdate` no model SQLAlchemy

**Decisão**: Usar `server_default=func.now()` para `created_at` e `onupdate=func.now()` para `updated_at`. Também adicionar `default=datetime.utcnow` para garantir valor em inserts via ORM que não passam pelo servidor.

**Rationale**: O `server_default` garante que novos registros inseridos diretamente no banco (fora do ORM) também recebam o timestamp. O `onupdate` no SQLAlchemy atualiza automaticamente `updated_at` em cada `session.flush()`.

### 4. Campos opcionais nas entidades de domínio

**Decisão**: Adicionar `created_at: datetime | None = None` e `updated_at: datetime | None = None` nas entidades `Chat`, `Contact` e `Deal`.

**Rationale**: Como os campos são nullable no banco e dados existentes terão `None`, as entidades devem refletir essa realidade sem quebrar código existente que instancia as entidades sem esses campos. Seguindo DDD, a entidade permanece agnóstica ao ORM.

## Risks / Trade-offs

- **[Risco] Dados existentes com `created_at = NULL`** → Mitigação: As colunas são explicitamente nullable; qualquer código que consuma `created_at` deve tratar `None`. Um change futuro fará o backfill e tornará as colunas `NOT NULL`.
- **[Risco] `updated_at` não atualizado em updates diretos via SQL (fora do ORM)** → Mitigação: O `server_default` e triggers no PostgreSQL podem ser adicionados no future change se necessário. Por ora, o fluxo da aplicação passa pelo ORM.
- **[Risco] Testes quebram ao instanciar entidades sem os novos campos** → Mitigação: Os campos têm `default=None`, então construtores existentes não precisam ser alterados.

## Migration Plan

1. Criar nova migration Alembic com `op.add_column` para cada tabela (`chat`, `contact`, `deal`).
2. `upgrade()`: adiciona `created_at` e `updated_at` (nullable=True) nas três tabelas.
3. `downgrade()`: remove as colunas com `op.drop_column`.
4. Atualizar os SQLAlchemy models (`ChatModel`, `ContactModel`, `DealModel`).
5. Atualizar entidades de domínio (`Chat`, `Contact`, `Deal`).
6. Atualizar adapters de repositório para mapear os novos campos ao hidratar entidades.
7. Atualizar testes afetados.

**Rollback**: Executar `alembic downgrade -1`. Colunas são removidas; dados de timestamp são perdidos (aceitável, pois ainda são nullable/temporários).

## Open Questions

- Nenhuma. A estratégia de backfill e remoção do nullable será tratada em change separado após validação em produção.
