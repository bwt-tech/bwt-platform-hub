## Why

O contrato `DealResponse` é genérico e não reflete os payloads reais retornados pela API BWT em cada endpoint. Isso causou erros de validação em produção (`ValidationError` para `contact`, `account` e `contact_info`) porque o POST `/sales/deals/` retorna objetos expandidos (dicts), enquanto o model esperava `int` e `str`. A correção correta é criar response models específicos por cenário, respeitando o contrato real de cada endpoint.

## What Changes

- **BREAKING** — Remove `DealResponse` genérico de `responses.py`
- Novo model `ContactInfoResponse`: sub-objeto retornado no campo `contact_info` do `POST /sales/deals/`
- Novo model `CreateDealResponse`: payload completo retornado por `POST /sales/deals/`, com `contact` e `account` como objetos expandidos (`AccountContactResponse` e `AccountResponse`)
- Atualiza `BWTAdapter.create_deal` para retornar `CreateDealResponse`
- Atualiza `BWTPort.create_deal` para retornar `CreateDealResponse`
- Atualiza `bwt_reverse_sync_service` para usar `CreateDealResponse` onde aplicável
- Atualiza `__init__.py` do pacote `contracts.bwt` para exportar os novos tipos
- Atualiza testes do adapter (`test_bwt_adapter.py`) para usar `CreateDealResponse`

## Capabilities

### New Capabilities

- `bwt-deal-typed-responses`: Response models específicos e tipados para cada endpoint de Deal da API BWT, eliminando o model genérico `DealResponse` que não representava fielmente nenhum payload real.

### Modified Capabilities

_(sem mudanças em specs existentes — `openspec/specs/` não contém spec de deals)_

## Impact

- **`app/src/contracts/bwt/responses.py`**: remoção de `DealResponse`, adição de `ContactInfoResponse` e `CreateDealResponse`
- **`app/src/contracts/bwt/__init__.py`**: exportações atualizadas
- **`app/src/adapters/outbounds/bwt.py`**: tipo de retorno de `create_deal`
- **`app/src/ports/bwt_port.py`**: assinatura de `create_deal`
- **`app/src/services/workflows/bwt_reverse_sync_service.py`**: tipagem de `_resolve_or_create_active_deal`
- **`app/tests/unit/adapters/test_bwt_adapter.py`**: assert de `isinstance(res, CreateDealResponse)`
