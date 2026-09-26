# Proposal: Persistência dos IDs BWT nos Modelos de Banco de Dados

## Intent

Evoluir as tabelas e modelos de domínio para armazenar os identificadores coletados durante a sincronização com a plataforma BWT. Após o processo de sincronização reversa (Octadesk → RD Station → BWT), o sistema já obtém IDs críticos da BWT — `account_id`, `contact_id`, `deal_id` e `responsible_id` — mas não os persiste em banco de dados, impossibilitando rastreabilidade, deduplicação e reaproveitamento em execuções futuras.

## Problem Statement

Atualmente, o `BWTReverseSyncService` cria ou localiza recursos na BWT (account, contact, deal, responsible) em cada execução de sincronização reversa, mas **descarta os IDs retornados**. Isso implica:

1. **Ausência de rastreabilidade**: Não é possível auditar qual account/contact/deal da BWT está associado a qual contact/deal interno.
2. **Re-consultas desnecessárias**: A cada ciclo de sincronização, o sistema precisa re-buscar na BWT o que poderia ser resolvido localmente via lookup de ID.
3. **Risco de duplicatas**: Sem persistência do `bwt_contact_id` e `bwt_account_id` no `ContactModel`, múltiplas sincronizações podem criar recursos duplicados na BWT.
4. **Impossibilidade de rastrear responsável**: O `responsible_id` atribuído a um deal na BWT não é armazenado, impossibilitando auditorias de atribuição de vendedor.

## Proposed Solution

Adicionar colunas de IDs BWT nas tabelas `contact` e `deal`, com as respectivas evoluções nos modelos SQLAlchemy, entidades de domínio, repositórios e uma migration Alembic:

### 1. Tabela `contact` — Novos campos BWT
| Campo | Tipo | Descrição |
|---|---|---|
| `bwt_account_id` | `INTEGER`, nullable, unique | ID do Account na BWT associado a este contato |
| `bwt_contact_id` | `INTEGER`, nullable, unique | ID do Contact na BWT associado a este contato |

### 2. Tabela `deal` — Novos campos BWT
| Campo | Tipo | Descrição |
|---|---|---|
| `bwt_deal_id` | `INTEGER`, nullable, unique | ID do Deal na BWT associado a esta negociação |
| `bwt_responsible_id` | `INTEGER`, nullable | ID do Company User (responsável) atribuído ao deal na BWT |

### 3. Fluxo de persistência no `BWTReverseSyncService`
- O método `sync()` passa a retornar um `BWTSyncResult` com os IDs coletados.
- O `ReverseSyncWorkflow` persiste os IDs no `contact` e `deal` após a sincronização BWT bem-sucedida.

### 4. Lookup por IDs BWT
- Novos métodos `find_by_bwt_contact_id` e `find_by_bwt_deal_id` nos repositórios para evitar re-criação de recursos.

## Non-Goals
- Não alterará a lógica de negócio do `BWTReverseSyncService` além do retorno dos IDs.
- Não sincronizará retroativamente contatos/deals existentes com IDs BWT.
- Não criará endpoints HTTP para exposição desses IDs.
