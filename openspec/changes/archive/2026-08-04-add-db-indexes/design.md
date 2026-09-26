# Design: Índices de Banco de Dados

## Context

Ver `proposal.md — Why` para a motivação. Resumo técnico do estado atual:

| Tabela | Coluna | Índice existente | Usado em |
|--------|--------|-----------------|----------|
| `contact` | `octadesk_id` | UNIQUE (implícito) | `find_by_octadesk_id` |
| `contact` | `rdstation_id` | UNIQUE (implícito) | lookup no `save` |
| `contact` | `bwt_account_id` | UNIQUE (implícito) | `find_by_bwt_account_id` |
| `contact` | `bwt_contact_id` | UNIQUE (implícito) | `find_by_bwt_contact_id` |
| `contact_info` | `phone` | UNIQUE (implícito) | `find_by_phone` |
| `contact_info` | `email` | UNIQUE (implícito) | `find_by_email` |
| `deal` | `rdstation_id` | UNIQUE (implícito) | `find_by_rdstation_id` |
| `deal` | `bwt_deal_id` | UNIQUE (implícito) | `find_by_bwt_deal_id` |
| `deal` | `contact_id` | **nenhum** ❌ | `find_by_contact_id`, query composta |
| `chat` | `octadesk_id` | UNIQUE (implícito) | `find_by_octadesk_id` |
| `chat` | `contact_id` | **nenhum** ❌ | `find_by_contact_id` |

No PostgreSQL, `UNIQUE` constraints criam automaticamente um B-tree index. FKs, por outro lado, **não** criam índices automaticamente — responsabilidade do schema explicitá-los.

## Goals / Non-Goals

**Goals:**
- Criar índice em `deal.contact_id`
- Criar índice composto em `(deal.contact_id, deal.rdstation_id)`
- Criar índice em `chat.contact_id`
- Declarar os índices nos models SQLAlchemy via `__table_args__`
- Fornecer migration Alembic com `upgrade` e `downgrade` corretos

**Non-Goals:**
- Índices em colunas sem uso como critério de lookup (`deal_status`, `channel`, `bwt_responsible_id`)
- Índices parciais (partial indexes) ou índices de expressão — sem evidência de necessidade agora
- Refatoração dos repository adapters ou da lógica de domínio
- Monitoramento de query plans (responsabilidade de infra/observabilidade)

## Decisions

### D1 — Índice simples vs. composto para `deal.contact_id`

**Decisão**: criar **ambos** — índice simples em `contact_id` e índice composto `(contact_id, rdstation_id)`.

**Rationale**: `find_by_contact_id` usa apenas `contact_id`; o índice simples o cobre. `find_by_contact_id_and_rd_station_id` usa os dois campos; o índice composto o cobre (e também cobre `find_by_contact_id` pela regra do prefixo de índice). A criação de ambos evita dependência da ordem dos campos e é explícita na intenção.

**Alternativa descartada**: índice composto apenas — funcionaria para `find_by_contact_id` por prefixo, mas seria implícito e menos legível. A criação do índice simples também é mais semântica.

### D2 — Declaração nos models SQLAlchemy

**Decisão**: usar `__table_args__` com `Index` do SQLAlchemy em `DealModel` e `ChatModel`.

**Rationale**: mantém models e schema em sincronia, permite que Alembic autogenerate detecte divergências futuramente, e documenta os índices no código-fonte da camada de infraestrutura.

**Alternativa descartada**: apenas na migration, sem alterar os models — cria divergência entre `Base.metadata` e o banco real, o que pode confundir futuras gerações automáticas de migration.

### D3 — Nomenclatura dos índices

**Padrão adotado**: `ix_<tabela>_<coluna(s)>`

- `ix_deal_contact_id`
- `ix_deal_contact_id_rdstation_id`
- `ix_chat_contact_id`

**Rationale**: segue a convenção do SQLAlchemy para `Index` sem nome explícito (`ix_` prefix) e é consistente com nomes de constraints existentes no projeto (`uq_contact_bwt_account_id`, etc.).

## Risks / Trade-offs

- **[Risco] Lock na criação do índice em produção** → Mitigação: o PostgreSQL cria índices com `ACCESS SHARE` lock por padrão para `CREATE INDEX CONCURRENT` — se o volume de dados justificar zero-downtime, usar `postgresql_concurrently=True` no Alembic. Para volumes atuais (startup), lock padrão é aceitável.
- **[Trade-off] Overhead de escrita** → Índices adicionam custo em `INSERT`/`UPDATE`/`DELETE`. Para `contact_id` em `deal` e `chat`, o custo é mínimo dado o padrão de escrita esporádico (1 deal e 1 chat por sincronização).
- **[Risco] Migration com `downgrade` incorreto** → Mitigação: implementar `downgrade` com `op.drop_index` explícito e testar localmente com `alembic downgrade -1`.

## Migration Plan

1. Gerar revisão Alembic: `alembic revision -m "add_indexes_to_deal_and_chat"`
2. Preencher `upgrade` com `op.create_index` para os três índices
3. Preencher `downgrade` com `op.drop_index` na ordem inversa
4. Aplicar localmente: `alembic upgrade head`
5. Verificar com `\d deal` e `\d chat` no psql
6. Em produção: executar via pipeline de migration existente (`.github/workflows/migrate.yml`)

**Rollback**: `alembic downgrade -1` remove os três índices sem impacto em dados.
