## Context

A API BWT retorna payloads distintos para cada endpoint de Deal:

- `POST /sales/deals/` → objetos `contact` e `account` expandidos (dicts completos), campo `contact_info` como dict
- `POST /sales/deals/{id}/update-deal-status/` → apenas `{id, stage}` — o adapter já ignora a resposta (`None`)
- `POST /sales/deals/{id}/set-responsible/` → apenas `{id, responsible}` — o adapter já ignora a resposta (`None`)
- `GET /sales/deals/?account=...` → paginado com `DealQueryResponse` (já correto)

O model `DealResponse` atual tentava cobrir todos os cenários com `Optional[int|Dict]` após tentativa de patch — abordagem frágil e não-semântica.

## Goals / Non-Goals

**Goals:**
- Criar `ContactInfoResponse` como sub-model para o campo `contact_info` do POST de criação
- Criar `CreateDealResponse` mapeando fielmente o payload de `POST /sales/deals/`
- Remover `DealResponse` genérico e ajustar todas as referências
- Manter `DealQueryResponse` e `DealsQueryResponse` intactos (já corretos)

**Non-Goals:**
- Não criar models para os payloads de `update-deal-status` e `set-responsible` — o adapter já retorna `None` nestes casos, o que é correto
- Não alterar a lógica de negócio em `bwt_reverse_sync_service.py` além de ajuste de tipos

## Decisions

### D1: `CreateDealResponse` com sub-models tipados ao invés de `Dict`

**Decisão**: usar `AccountContactResponse` e `AccountResponse` existentes como tipos de `contact` e `account` no `CreateDealResponse`, e criar `ContactInfoResponse` para `contact_info`.

**Alternativas consideradas**:
- `Optional[int | Dict]`: funciona, mas perde semântica e obriga verificações de tipo nos consumidores
- `Any`: aceita tudo, derrota o propósito do Pydantic
- `model_validator` que extrai só o `id`: mantém `int`, mas esconde informação disponível

**Rationale**: Sub-models tipados são a abordagem correta em DDD e Clean Code. O domínio que usa apenas `deal.id` e `deal.stage` não é afetado — esses campos continuam presentes.

### D2: Remoção de `DealResponse` sem deprecation gradual

**Decisão**: remover diretamente — não manter alias.

**Rationale**: `DealResponse` nunca funcionou corretamente com o payload real (`ValidationError` em produção). Não há valor em manter uma abstração quebrada. O impacto é controlado: apenas 3 arquivos de produção e 1 de testes precisam ser ajustados.

### D3: `bwt_reverse_sync_service` usa `CreateDealResponse`

**Decisão**: o método `_resolve_or_create_active_deal` retorna `CreateDealResponse | DealQueryResponse`. Como ambos têm `.id` e `.stage`, o duck typing via `Union` é suficiente — não há necessidade de Protocol separado.

**Alternativas consideradas**:
- Criar Protocol `DealLike` com `id: int` e `stage: DealStage`: correto em teoria, mas overengineering para 2 campos em 1 serviço
- Retornar só `DealQueryResponse` de ambos: exigiria wrapper desnecessário no adapter

## Risks / Trade-offs

- **Risco**: Outros serviços futuros que importem `DealResponse` quebrarão em runtime → **Mitigação**: busca por `DealResponse` em todo o codebase antes de remover garante que não há consumidores ocultos
- **Trade-off**: `CreateDealResponse` carrega mais dados do que o domínio precisa (objetos expandidos de `contact` e `account`). Aceitável — o custo é só memória, e os dados extras ficam disponíveis para uso futuro sem retrabalho

## Migration Plan

1. Adicionar `ContactInfoResponse` e `CreateDealResponse` em `responses.py`
2. Remover `DealResponse` de `responses.py`
3. Atualizar `__init__.py` do pacote `contracts.bwt`
4. Atualizar `BWTPort.create_deal` → retorna `CreateDealResponse`
5. Atualizar `BWTAdapter.create_deal` → retorna `CreateDealResponse`
6. Atualizar `bwt_reverse_sync_service._resolve_or_create_active_deal` → tipagem `CreateDealResponse`
7. Atualizar testes

Rollback: reverter os 5 arquivos modificados. Não há migrações de banco ou mudanças de API externa.
