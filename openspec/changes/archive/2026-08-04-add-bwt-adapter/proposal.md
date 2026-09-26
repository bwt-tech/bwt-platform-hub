# Proposal: Integração com a Plataforma BWT (Outbound Adapter & Port)

## Intent
Criar um novo adapter de saída (`BWTAdapter`) e a respectiva porta abstrata (`BWTPort`) para a integração com a API da Plataforma BWT (`https://api.homolog.brasileiroswinetours.com.br`), com base no script de referência [exemplo.py](file:///Users/mateus/projects/bwt/bwt-platform-hub/auxiliares/exemplo.py). A implementação deve respeitar os princípios de Domain-Driven Design (DDD), Clean Architecture (Ports & Adapters) e SOLID definidos no [AGENTS.md](file:///Users/mateus/projects/bwt/bwt-platform-hub/AGENTS.md).

## Problem Statement
Atualmente, a comunicação com a API da BWT existe apenas no formato de script experimental em [exemplo.py](file:///Users/mateus/projects/bwt/bwt-platform-hub/auxiliares/exemplo.py), com chamadas diretas via biblioteca `requests`, sem abstração por interfaces, sem gerenciamento unificado de erros, log estruturado ou integração com a suíte de testes.

Para padronizar e viabilizar futuras orquestrações de negócio, precisamos de um adapter robusto utilizando `httpx` e `loguru`, alinhado à estrutura de portas e adaptadores do projeto.

## Proposed Solution
1. **Configuração (`Settings`)**:
   - Adicionar variáveis de configuração para a API BWT em [settings.py](file:///Users/mateus/projects/bwt/bwt-platform-hub/app/src/config/settings.py) (`bwt_url`, `bwt_email`, `bwt_password`, `bwt_scope`).
2. **Porta (`BWTPort`)**:
   - Definir a interface abstrata em `app/src/ports/bwt_port.py` declarando os contratos para autenticação, busca/criação de contas, criação de contatos, criação/atualização de negociações (deals), atribuição de responsável e consulta de usuários da empresa.
3. **Adapter Outbound (`BWTAdapter`)**:
   - Implementar a classe `BWTAdapter` em `app/src/adapters/outbounds/bwt.py` (herdando de `BWTPort`).
   - Gerenciar o token JWT de acesso (`POST /auth/login/`) enviado no cabeçalho `Authorization: Bearer <token>` e utilizar os headers obrigatórios `Accept: application/json; version=v1_web`.
   - Utilizar `httpx` para chamadas HTTP resilientes e `loguru` para rastreabilidade de erros, lançando exceções de domínio do tipo `IntegrationError`.
4. **Testes Unitários**:
   - Escrever suíte de testes unitários com mocks completos (`pytest` / `unittest.mock` / `respx`) garantindo 100% de cobertura de código.

## Non-Goals
- Não incluir a nova integração BWT em nenhum fluxo de serviço/orquestrador existente nesta etapa (a inclusão em fluxos será feita em uma mudança posterior).
- Não alterar schemas ou tabelas do banco de dados relacional.
