# Proposal: Índices de Banco de Dados para Consultas de Lookup

## Why

As tabelas `deal` e `chat` possuem FKs `contact_id` utilizadas em consultas frequentes sem índice explícito, forçando o PostgreSQL a realizar sequential scans à medida que o volume de dados cresce. As colunas únicas já possuem índices implícitos gerados pelo `UNIQUE` constraint, mas as FKs e colunas de lookup compostas ainda estão descobertas.

## What Changes

- **Índice em `deal.contact_id`**: FK usada em `find_by_contact_id` e `find_by_contact_id_and_rd_station_id` — sem índice hoje.
- **Índice composto em `(deal.contact_id, deal.rdstation_id)`**: suporte à query combinada `find_by_contact_id_and_rd_station_id`.
- **Índice em `chat.contact_id`**: FK usada em `find_by_contact_id` — sem índice hoje.
- **Migration Alembic** adicionando os três índices com `downgrade` que os remove.
- **Atualização dos modelos SQLAlchemy** declarando os índices via `Index` para manter models e banco em sincronia.

## Capabilities

### New Capabilities

- `db-indexes`: Criação de índices explícitos nas colunas de FK (`deal.contact_id`, `chat.contact_id`) e índice composto `(deal.contact_id, deal.rdstation_id)` para suportar as queries de lookup dos repository adapters com desempenho previsível.

### Modified Capabilities

*(nenhuma — nenhum comportamento de domínio ou requisito de aplicação muda)*

## Impact

- **`app/src/adapters/database/models.py`**: declaração dos índices nos models `DealModel` e `ChatModel` via `__table_args__`.
- **`migrations/versions/<rev>_add_indexes_to_deal_and_chat.py`**: nova migration Alembic com `upgrade` e `downgrade`.
- Sem impacto em APIs, domínio, contratos ou lógica de negócio.
- Sem breaking changes.
