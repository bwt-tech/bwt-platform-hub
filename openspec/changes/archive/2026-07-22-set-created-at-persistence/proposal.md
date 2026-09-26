## Why

Atualmente, ao persistir entidades de Chat, Contact e Deal no banco de dados, o campo `created_at` depende do default do ORM ou do banco caso não seja especificado na entidade de domínio. Para garantir consistência e auditabilidade em relatórios e sincronizações entre sistemas, o valor de `created_at` deve ser explicitamente capturado da entidade ou preenchido com a data/hora atual do processamento (UTC) quando não informado.

## What Changes

- Atualizar os adaptadores de repositório (`SQLAlchemyChatRepositoryAdapter`, `SQLAlchemyContactRepositoryAdapter`, `SQLAlchemyDealRepositoryAdapter`) para garantirem que `created_at` seja definido na criação do modelo no banco.
- Se o objeto de domínio possuir `created_at`, utilizar esse valor; caso contrário, utilizar a data/hora atual do processamento (`datetime.now()`).
- Garantir que a transferência do campo `created_at` entre a entidade de domínio e o modelo ORM ocorra corretamente na criação e seja preservada na atualização.
- Atualizar a criação das instâncias de modelos no banco e os construtores/fábricas das entidades se necessário.

## Capabilities

### New Capabilities

- `model-created-at-persistence`: Garantia de persistência e fallback automático da data de criação (`created_at`) para os modelos Chat, Contact e Deal.

### Modified Capabilities

None.

## Impact

- `app/src/adapters/database/repositories/chat_repository_adapter.py`
- `app/src/adapters/database/repositories/contact_repository_adapter.py`
- `app/src/adapters/database/repositories/deal_repository_adapter.py`
- `app/src/adapters/database/models.py` (se ajuste fino no schema for necessário)
- Suíte de testes automatizados dos repositórios e entidades de domínio.
