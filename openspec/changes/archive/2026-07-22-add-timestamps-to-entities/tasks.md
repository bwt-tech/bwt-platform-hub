## 1. Migration Alembic

- [x] 1.1 Criar nova migration Alembic `add_timestamps_to_entities` com `op.add_column` para adicionar `created_at` e `updated_at` (TIMESTAMPTZ, nullable=True) nas tabelas `chat`, `contact` e `deal`
- [x] 1.2 Implementar `downgrade()` na migration com `op.drop_column` para reverter as colunas nas três tabelas

## 2. SQLAlchemy Models

- [x] 2.1 Adicionar colunas `created_at` e `updated_at` (DateTime timezone=True, nullable=True, server_default e onupdate) em `ChatModel`
- [x] 2.2 Adicionar colunas `created_at` e `updated_at` (DateTime timezone=True, nullable=True, server_default e onupdate) em `ContactModel`
- [x] 2.3 Adicionar colunas `created_at` e `updated_at` (DateTime timezone=True, nullable=True, server_default e onupdate) em `DealModel`

## 3. Entidades de Domínio

- [x] 3.1 Adicionar campos opcionais `created_at: datetime | None = None` e `updated_at: datetime | None = None` na entidade `Chat` e atualizar `from_dict`
- [x] 3.2 Adicionar campos opcionais `created_at: datetime | None = None` e `updated_at: datetime | None = None` na entidade `Contact`
- [x] 3.3 Adicionar campos opcionais `created_at: datetime | None = None` e `updated_at: datetime | None = None` na entidade `Deal`

## 4. Adapters de Repositório

- [x] 4.1 Atualizar os adapters de repositório (`ChatRepository`, `ContactRepository`, `DealRepository`) para mapear `created_at` e `updated_at` ao converter model → entidade de domínio

## 5. Testes

- [x] 5.1 Atualizar/criar testes unitários para `ChatModel` cobrindo persistência de `created_at` e `updated_at`
- [x] 5.2 Atualizar/criar testes unitários para `ContactModel` cobrindo persistência de `created_at` e `updated_at`
- [x] 5.3 Atualizar/criar testes unitários para `DealModel` cobrindo persistência de `created_at` e `updated_at`
- [x] 5.4 Atualizar testes das entidades de domínio `Chat`, `Contact` e `Deal` para cobrir os novos campos opcionais
- [x] 5.5 Atualizar testes dos adapters de repositório para cobrir o mapeamento dos campos de timestamp
