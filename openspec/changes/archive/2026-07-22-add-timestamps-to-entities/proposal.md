## Why

As entidades `Chat`, `Contact` e `Deal` persistidas no banco de dados não possuem rastreabilidade temporal, impossibilitando auditorias, depuração de problemas e análise histórica de dados. Adicionar `created_at` e `updated_at` resolve essa lacuna e habilita features futuras baseadas em tempo (ex: relatórios, SLAs, expiração de registros).

## What Changes

- Adição das colunas `created_at` e `updated_at` (tipo `TIMESTAMP WITH TIME ZONE`) nas tabelas `chat`, `contact` e `deal`.
- As colunas são inicialmente `nullable=True` para compatibilidade com dados existentes na base.
- Nova migration Alembic (`add_timestamps_to_entities`) que aplica os `ALTER TABLE` em cada tabela.
- Atualização dos SQLAlchemy models (`ChatModel`, `ContactModel`, `DealModel`) para incluir as novas colunas com `server_default` e `onupdate`.
- Atualização das entidades de domínio (`Chat`, `Contact`, `Deal`) para expor os campos opcionais `created_at` e `updated_at`.
- Atualização dos métodos `from_dict` / `to_dict` das entidades para mapear os novos campos.
- Atualização dos adapters de repositório para propagar os timestamps ao hidratar entidades de domínio a partir dos models.

## Capabilities

### New Capabilities

- `entity-timestamps`: Rastreabilidade temporal (criação e atualização) para as entidades `Chat`, `Contact` e `Deal` persistidas em banco de dados.

### Modified Capabilities

- `deal-orchestration`: O fluxo de orquestração de deals escreve e lê a entidade `Deal`; o contrato de domínio agora inclui campos opcionais de timestamp.
- `orchestration-statistics`: Estatísticas de orquestração consomem entidades `Deal` e `Contact`; os campos de timestamp ficam disponíveis para cálculos temporais futuros.

## Impact

- **Schema do banco de dados**: `ALTER TABLE` nas tabelas `chat`, `contact` e `deal` — impacto mínimo com colunas nullable.
- **SQLAlchemy models** (`app/src/adapters/database/models.py`): inclusão de `Column(DateTime(timezone=True), ...)` nos três models afetados.
- **Entidades de domínio** (`app/src/domain/entities/chat.py`, `contact.py`, `deal.py`): novos campos opcionais `created_at` e `updated_at`.
- **Adapters de repositório**: leitura dos timestamps ao converter model → entidade.
- **Testes unitários**: mocks e fixtures precisam ser atualizados para os novos campos (opcionais, sem quebrar testes existentes).
- **Sem breaking changes na API pública**: os campos são opcionais e podem retornar `None` para registros migrados ainda não preenchidos.
