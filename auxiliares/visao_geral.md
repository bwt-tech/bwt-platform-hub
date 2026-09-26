# Visão Geral — Consumo da API BR Wine Tours Backend

## Sumário
Este documento apresenta um guia passo a passo para aplicações consumidoras da API BR Wine Tours Backend. Inclui como obter credenciais, realizar autenticação via JWT e consumir endpoints protegidos.

## Informações Gerais

**Base URL (ambiente de homologação)**: `https://api-homologacao.brwinetours.com.br`  
**Base URL (ambiente de produção)**: `https://api.brwinetours.com.br`

**Protocolo de Autenticação**: JWT (JSON Web Token) via `djangorestframework-simplejwt`  
**Algoritmo de assinatura**: HS256  
**Formato do token**: Bearer Token no header `Authorization`

**Versionamento da API**: Header `Accept` obrigatório com versão aceita (ex: `application/json; version=v1_web`)

**Tipos de usuário suportados**:
- `CompanyUser` — usuário de empresa (escopo multi-tenant via `{company_id}:{email}`)
- `CompanyDriver` — motorista
- `ManagementUser` — usuário interno da plataforma
- `AffiliateUser` — afiliado
- `ClientUser` — cliente final

---

## Passo a Passo: Autenticação e Consumo

### 1. Obtenção de Credenciais

Antes de consumir a API, você precisa de credenciais válidas:
- **Email** do usuário
- **Senha** do usuário
- **Scope** (company_id) — obrigatório para `CompanyUser` e `CompanyDriver`

**Cenário 1: CompanyUser (usuário de empresa)**
- Email é prefixado internamente com `{company_id}:{email}`
- Você deve fornecer o `scope` no body do login

**Cenário 2: ClientUser ou CompanyDriver (apps mobile)**
- Email deve estar verificado (`email_verified = true`)
- Se não estiver verificado, complete o fluxo de verificação via código TOTP primeiro

**Cenário 3: ManagementUser ou AffiliateUser**
- Login direto sem scope ou verificação prévia

**Como obter as credenciais:**
- Entre em contato com o administrador do sistema para criação de usuário
- Ou use o fluxo de cadastro público (se disponível para o seu tipo de usuário)

---

### 2. Login (Obtenção dos Tokens JWT)

**Endpoint**: `POST /auth/login/`

**Headers obrigatórios**:
```
Content-Type: application/json
Accept: application/json; version=v1_web
```

**Body (CompanyUser com scope)**:
```json
{
  "email": "usuario@empresa.com",
  "password": "SuaSenhaSegura123!",
  "scope": "5"
}
```

**Body (ManagementUser sem scope)**:
```json
{
  "email": "admin@brwinetours.com.br",
  "password": "SenhaAdmin123!"
}
```

**Exemplo de requisição cURL**:
```bash
curl -X POST "https://api-homologacao.brwinetours.com.br/auth/login/" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json; version=v1_web" \
  -d '{
    "email": "usuario@empresa.com",
    "password": "SuaSenhaSegura123!",
    "scope": "5"
  }'
```

**Resposta de sucesso (200 OK)**:
```json
{
  "user": {
    "id": 42,
    "email": "5:usuario@empresa.com",
    "name": "João Silva",
    "polymorphic_ctype": 15,
    "company": 5,
    "is_active": true,
    "language": "pt-br",
    "rocket_chat_id": "abc123xyz"
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM3NTg1NjAwLCJpYXQiOjE3Mzc0OTkyMDAsImp0aSI6ImFiYzEyMyIsInVzZXJfaWQiOjQyfQ.signature",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2OTAzNTIwMCwiaWF0IjoxNzM3NDk5MjAwLCJqdGkiOiJ4eXo3ODkiLCJ1c2VyX2lkIjo0Mn0.signature"
  }
}
```

**Validade dos tokens**:
- **Access token**: 1 dia (86400 segundos)
- **Refresh token**: 365 dias

**Erros comuns**:
- `401 Unauthorized` → credenciais inválidas
- `403 Forbidden` → email não verificado (CompanyDriver ou ClientUser)
- `400 Bad Request` → scope ausente ou inválido
- `406 Not Acceptable` → versão da API não suportada (header `Accept` incorreto)

---

### 3. Renovação do Access Token

Quando o access token expirar, use o refresh token para obter um novo access token sem precisar fazer login novamente.

**Endpoint**: `POST /auth/refresh/`

**Headers obrigatórios**:
```
Content-Type: application/json
Accept: application/json; version=v1_web
```

**Body**:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Exemplo de requisição cURL**:
```bash
curl -X POST "https://api-homologacao.brwinetours.com.br/auth/refresh/" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json; version=v1_web" \
  -d '{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Resposta de sucesso (200 OK)**:
```json
{
  "user": {
    "id": 42,
    "email": "5:usuario@empresa.com",
    "name": "João Silva",
    ...
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...(novo token)",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...(mesmo token)"
  }
}
```

**Nota**: O refresh token **não rotaciona automaticamente** (`ROTATE_REFRESH_TOKENS: False`). O mesmo refresh token pode ser reutilizado até expirar.

---

### 4. Consumo de Endpoint Protegido (Exemplo: GET /sales/contacts/)

Uma vez autenticado, você pode consumir endpoints protegidos usando o access token.

**Endpoint**: `GET /sales/contacts/`

**Descrição**: Lista todos os contatos da empresa do usuário autenticado (filtro automático por `company_id`).

**Permissões requeridas**:
- Tipo de usuário: `CompanyUser`
- Permissão customizada: `view` no model `Contact` (app `sales`)

**Headers obrigatórios**:
```
Authorization: Bearer <access_token>
Accept: application/json; version=v1_web
```

**Query params opcionais**:
- `?search=<termo>` — busca por nome ou documento do contato
- `?page=<número>` — paginação (20 itens por página)
- `?page_size=<tamanho>` — altera o tamanho da página

**Exemplo de requisição cURL**:
```bash
curl -X GET "https://api-homologacao.brwinetours.com.br/sales/contacts/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM3NTg1NjAwLCJpYXQiOjE3Mzc0OTkyMDAsImp0aSI6ImFiYzEyMyIsInVzZXJfaWQiOjQyfQ.signature" \
  -H "Accept: application/json; version=v1_web"
```

**Resposta de sucesso (200 OK)**:
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 101,
      "name": "Maria Santos",
      "email": "maria.santos@example.com",
      "document": "12345678901",
      "phone": {
        "id": 201,
        "number": "+55 11 98765-4321",
        "country_code": "BR"
      },
      "address": {
        "id": 301,
        "street": "Rua das Flores",
        "number": "123",
        "neighborhood": "Centro",
        "city": "São Paulo",
        "state": "SP",
        "zip_code": "01000-000",
        "country": "BR"
      },
      "zip_code": "01000-000",
      "is_foreign": false,
      "account": {
        "id": 50,
        "name": "Empresa XYZ Ltda",
        "document": "12345678000199",
        "type": "LEGAL"
      }
    },
    {
      "id": 102,
      "name": "João Oliveira",
      "email": "joao.oliveira@example.com",
      "document": "98765432100",
      "phone": {
        "id": 202,
        "number": "+55 21 91234-5678",
        "country_code": "BR"
      },
      "address": null,
      "zip_code": null,
      "is_foreign": false,
      "account": null
    }
  ]
}
```

**Campos retornados**:
- `id` — identificador único do contato
- `name` — nome completo
- `email` — endereço de email (único por empresa)
- `document` — CPF ou documento equivalente
- `phone` — objeto aninhado com número, código do país
- `address` — objeto aninhado com endereço completo (pode ser `null`)
- `zip_code` — CEP ou código postal
- `is_foreign` — indica se é contato estrangeiro
- `account` — conta (empresa/pessoa) associada ao contato (pode ser `null`)

**Paginação**: A resposta inclui `count` (total de registros), `next` (URL da próxima página) e `previous` (URL da página anterior).

**Erros comuns**:
- `401 Unauthorized` → token ausente, inválido ou expirado
- `403 Forbidden` → usuário sem permissão `view` no model `Contact`, ou empresa inativa
- `406 Not Acceptable` → versão da API não suportada

---

### 5. Criação de um Contato (Exemplo: POST /sales/contacts/)

**Endpoint**: `POST /sales/contacts/`

**Descrição**: Cria um novo contato para a empresa do usuário autenticado.

**Permissões requeridas**:
- Tipo de usuário: `CompanyUser` (ou `IsAnonymous` com `CanCreate` para cadastro público)
- Permissão customizada: `add` no model `Contact` (app `sales`)

**Headers obrigatórios**:
```
Authorization: Bearer <access_token>
Accept: application/json; version=v1_web
Content-Type: application/json
```

**Body**:
```json
{
  "name": "Ana Costa",
  "email": "ana.costa@example.com",
  "document": "11122233344",
  "phone": {
    "number": "+55 11 99999-8888",
    "country_code": "BR"
  },
  "address": {
    "street": "Av. Paulista",
    "number": "1000",
    "neighborhood": "Bela Vista",
    "city": "São Paulo",
    "state": "SP",
    "zip_code": "01310-100",
    "country": "BR"
  },
  "zip_code": "01310-100",
  "is_foreign": false,
  "account": 50
}
```

**Campos opcionais**: `address`, `zip_code`, `is_foreign`, `account`

**Exemplo de requisição cURL**:
```bash
curl -X POST "https://api-homologacao.brwinetours.com.br/sales/contacts/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Accept: application/json; version=v1_web" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ana Costa",
    "email": "ana.costa@example.com",
    "document": "11122233344",
    "phone": {
      "number": "+55 11 99999-8888",
      "country_code": "BR"
    },
    "is_foreign": false
  }'
```

**Resposta de sucesso (201 Created)**:
```json
{
  "id": 103,
  "name": "Ana Costa",
  "email": "ana.costa@example.com",
  "document": "11122233344",
  "phone": {
    "id": 203,
    "number": "+55 11 99999-8888",
    "country_code": "BR"
  },
  "address": null,
  "zip_code": null,
  "is_foreign": false,
  "account": null
}
```

**Validações aplicadas**:
- Email deve ser único por empresa (não pode haver dois contatos com o mesmo email na mesma company)
- Documento (CPF) deve ser válido

**Erros comuns**:
- `400 Bad Request` → email já existe, documento inválido, campos obrigatórios ausentes
- `403 Forbidden` → usuário sem permissão `add`

---

### 6. Logout (Invalidação do Refresh Token)

**Endpoint**: `POST /auth/logout/`

**Descrição**: Blacklista o refresh token, impedindo renovação futura do access token. O access token atual continua válido até expirar.

**Headers obrigatórios**:
```
Authorization: Bearer <access_token>
Accept: application/json; version=v1_web
Content-Type: application/json
```

**Body**:
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Exemplo de requisição cURL**:
```bash
curl -X POST "https://api-homologacao.brwinetours.com.br/auth/logout/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Accept: application/json; version=v1_web" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Resposta de sucesso (204 No Content)**: Body vazio

**Erros comuns**:
- `401 Unauthorized` → token de autenticação ausente ou inválido
- `400 Bad Request` → refresh token ausente ou já blacklistado

---

## Fluxo Completo em Shell Script

```bash
#!/bin/bash

# Configuração
BASE_URL="https://api-homologacao.brwinetours.com.br"
EMAIL="usuario@empresa.com"
PASSWORD="SuaSenhaSegura123!"
SCOPE="5"

# 1. Login
echo "=== 1. Realizando login ==="
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json; version=v1_web" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"scope\":\"$SCOPE\"}")

echo "$LOGIN_RESPONSE" | jq '.'

# Extrai o access token da resposta
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.tokens.access')
REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.tokens.refresh')

echo ""
echo "Access Token: $ACCESS_TOKEN"
echo ""

# 2. Listar contatos
echo "=== 2. Listando contatos ==="
CONTACTS_RESPONSE=$(curl -s -X GET "$BASE_URL/sales/contacts/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Accept: application/json; version=v1_web")

echo "$CONTACTS_RESPONSE" | jq '.'

# 3. Criar novo contato
echo ""
echo "=== 3. Criando novo contato ==="
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/sales/contacts/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Accept: application/json; version=v1_web" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Teste API",
    "email": "teste.api@example.com",
    "document": "11111111111",
    "phone": {
      "number": "+55 11 91111-1111",
      "country_code": "BR"
    },
    "is_foreign": false
  }')

echo "$CREATE_RESPONSE" | jq '.'

# 4. Renovar token (simulação após 23 horas)
echo ""
echo "=== 4. Renovando access token ==="
REFRESH_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/refresh/" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json; version=v1_web" \
  -d "{\"refresh\":\"$REFRESH_TOKEN\"}")

echo "$REFRESH_RESPONSE" | jq '.'

NEW_ACCESS_TOKEN=$(echo "$REFRESH_RESPONSE" | jq -r '.tokens.access')
echo ""
echo "Novo Access Token: $NEW_ACCESS_TOKEN"

# 5. Logout
echo ""
echo "=== 5. Realizando logout ==="
LOGOUT_RESPONSE=$(curl -s -w "\nHTTP Status: %{http_code}" -X POST "$BASE_URL/auth/logout/" \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN" \
  -H "Accept: application/json; version=v1_web" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\":\"$REFRESH_TOKEN\"}")

echo "$LOGOUT_RESPONSE"
echo ""
echo "=== Fluxo completo finalizado ==="
```

**Para executar**:
```bash
chmod +x api_flow.sh
./api_flow.sh
```

**Requisito**: `jq` instalado para parsing do JSON (`sudo apt install jq` ou `brew install jq`)

---

## Observações de Segurança

1. **HTTPS obrigatório**: Todas as requisições devem usar HTTPS em produção
2. **Armazenamento seguro**: Access e refresh tokens devem ser armazenados de forma segura (keychain, encrypted storage)
3. **Não compartilhar tokens**: Tokens são pessoais e não devem ser compartilhados entre usuários
4. **Renovação proativa**: Renove o access token antes de expirar (ex: aos 23h de vida útil)
5. **Logout ao sair**: Sempre blackliste o refresh token ao fazer logout da aplicação
6. **Multi-tenancy**: Email com scope garante isolamento entre empresas (automático na camada de serializer/queryset)
7. **Empresa inativa**: Se a empresa do usuário for desativada, a autenticação falhará silenciosamente (retorna 401)
8. **Versionamento**: Sempre envie o header `Accept` com a versão correta; versões desatualizadas são rejeitadas

---

## Referências Técnicas

- **Autenticação**: `src/authentication/views.py` → `LoginView`, `RefreshTokenView`, `LogoutView`
- **JWT Config**: `src/wine_tour/settings/base.py` → `SIMPLE_JWT`
- **Autenticador customizado**: `src/authentication/authenticators.py` → `JWTAuthentication`
- **Endpoint de contatos**: `src/sales/views.py` → `ContactViewSet`
- **Serializer de contatos**: `src/sales/serializers.py` → `ContactSerializer`
- **Permissões**: `src/authentication/permissions/classes.py` → `UserHasCustomPermission`, `IsCompanyUser`
- **Versionamento**: `src/core/versionings.py` → `ConstanceHeaderVersioning`

---

**Última atualização**: 2026-07-22  
**Versão do documento**: 1.0.0
