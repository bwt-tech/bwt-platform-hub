## Context

As entidades de domínio `Chat`, `Contact` e `Deal` possuem o campo opcional `created_at: datetime | None`. Nos adaptadores SQLAlchemy (`SQLAlchemyChatRepositoryAdapter`, `SQLAlchemyContactRepositoryAdapter`, `SQLAlchemyDealRepositoryAdapter`), na criação de novos registros no banco, se a entidade não possuir `created_at` preenchido (ou se for `None`), o valor deve ser explicitamente definido como a data/hora atual da execução (`datetime.now()`). Caso a entidade já traga um `created_at` preenchido, esse valor deve ser mantido ao instanciar o modelo SQLAlchemy.

## Goals / Non-Goals

**Goals:**
- Garantir a atribuição explícita de `created_at` nos adaptadores de repositório para `ChatModel`, `ContactModel` e `DealModel`.
- Utilizar `datetime.now()` como fallback quando `entity.created_at` estiver ausente / for `None`.
- Manter o valor existente de `created_at` durante atualizações (`update`) de registros já existentes no banco.
- Atualizar os testes de integração e testes unitários dos repositórios para validar a atribuição de `created_at`.

**Non-Goals:**
- Alterar schemas de banco de dados ou criar novas migrations caso os campos de tabela já suportem `DateTime(timezone=True)`.
- Alterar regras de negócio não relacionadas a timestamps de criação de `Chat`, `Contact` ou `Deal`.

## Decisions

### 1. Tratamento no Nível do Repositório (Adapter) vs ORM Default
- **Decisão**: Definir o `created_at` explicitamente nos adaptadores de repositório (`save` method) antes de salvar o modelo SQLAlchemy:
  `created_at = entity.created_at or datetime.now()`
- **Razão**: Garante que o objeto persistido no banco e retornado pelo método `save()` possua uma data válida em tempo de execução na camada da aplicação, sem depender exclusivamente da execução diferida do `server_default` do banco ou do `default` do SQLAlchemy no commit.

### 2. Uso de Fuso Horário UTC (``)
- **Decisão**: Utilizar `datetime.now()` em vez de `datetime.utcnow()` (que está descontinuado/deprecated no Python 3.12+).
- **Razão**: Garante conformidade com Python 3.12+ e timezone awareness.

### 3. Preservação em Updates
- **Decisão**: Durante atualizações de modelos existentes, se `model.created_at` já estiver preenchido no banco e `entity.created_at` não for fornecido, manter o `model.created_at` original.
- **Razão**: Evita sobrescrever a data de criação original de um registro durante uma atualização parcial de dados.

## Risks / Trade-offs

- **Diferenças de Timezone** → Garantir uso consistente de UTC (``) para evitar discrepâncias em ambientes locais e servidores.
- **Testes com Mocks** → Testes de repositório que comparam timestamps devem permitir pequenas variações de tempo (ou usar congelamento de relógio / assertis com `assertIsNotNone`).
