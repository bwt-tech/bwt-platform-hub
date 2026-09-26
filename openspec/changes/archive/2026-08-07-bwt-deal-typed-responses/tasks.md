## 1. Contratos de Response (responses.py)

- [x] 1.1 Adicionar model `ContactInfoResponse` com campos `id: int`, `name: str`, `email: str`, `document: Optional[str]`, `phone: Optional[PhoneContact]`, `is_foreign: bool`
- [x] 1.2 Adicionar model `CreateDealResponse` com `contact: AccountContactResponse`, `account: AccountResponse`, `contact_info: Optional[ContactInfoResponse]`, `responsible: Optional[SimplifiedUserResponse]`, `stage: Optional[DealStage]`, `origin: Optional[DealOrigin]`, e demais campos opcionais do payload (`description`, `categories`, `lost_reason`, `lost_reason_notes`, `finished_at`, `created`, `modified`)
- [x] 1.3 Remover o model `DealResponse` genérico de `responses.py`

## 2. Exportações do Pacote (contracts/bwt/__init__.py)

- [x] 2.1 Remover `DealResponse` das importações e da lista `__all__`
- [x] 2.2 Adicionar `ContactInfoResponse` e `CreateDealResponse` às importações e à lista `__all__`

## 3. Port (bwt_port.py)

- [x] 3.1 Substituir importação de `DealResponse` por `CreateDealResponse`
- [x] 3.2 Atualizar assinatura de `create_deal` para retornar `CreateDealResponse`

## 4. Adapter (bwt.py)

- [x] 4.1 Substituir importação de `DealResponse` por `CreateDealResponse`
- [x] 4.2 Atualizar tipo de retorno de `create_deal` para `CreateDealResponse`
- [x] 4.3 Verificar que `DealResponse.model_validate(raw)` em `create_deal` foi substituído por `CreateDealResponse.model_validate(raw)`

## 5. Serviço de Domínio (bwt_reverse_sync_service.py)

- [x] 5.1 Substituir importação de `DealResponse` por `CreateDealResponse`
- [x] 5.2 Atualizar tipo de retorno de `_resolve_or_create_active_deal` para `CreateDealResponse | DealQueryResponse`
- [x] 5.3 Atualizar anotações de tipo de `_advance_deal_and_assign_seller` onde usa `DealResponse`

## 6. Testes (test_bwt_adapter.py)

- [x] 6.1 Substituir importação de `DealResponse` por `CreateDealResponse`
- [x] 6.2 Atualizar `assert isinstance(res, DealResponse)` para `isinstance(res, CreateDealResponse)` no teste `test_bwt_create_deal`
- [x] 6.3 Atualizar o fixture JSON do mock em `test_bwt_create_deal` para refletir o payload expandido real da API (com `contact` e `account` como objetos e `contact_info` como objeto)
