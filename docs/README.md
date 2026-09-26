# Documentação Técnica e Decisões Arquiteturais (ADRs)

Este repositório armazena a documentação técnica, especificações de adaptadores de infraestrutura e o registro de decisões de arquitetura do **BWT Platform Hub**.

---

## 📚 Índice de Documentação

### 1. Adaptadores e Infraestrutura (`docs/adapters/`)
Documentação técnica detalhada de cada integração e componente de persistência:
- [Database & Persistência (PostgreSQL + Alembic)](./adapters/database.md): Modelagem relacional, repositórios DDD e ciclo de vida de conexões SQLAlchemy.
- [Parametrização AWS (SSM & Secrets Manager)](./adapters/aws_parameterization.md): Integração com AWS SSM Parameter Store e AWS Secrets Manager.
- [Adaptador Octadesk](./adapters/octadesk.md): Abstração de API de chats, mensagens, contatos e webhooks da Octadesk.
- [Adaptador RD Station](./adapters/rdstation.md): Integração de CRM para deals, funis de vendas (pipelines) e contatos.
- [Adaptador Plataforma BWT](./adapters/bwt.md): Integração REST nativa com a Plataforma BWT (autenticação JWT, contas, contatos, negociações e usuários).

---

## 🏛️ Decisões Arquiteturais Relevantes (ADR Summary)

1. **ADR-001: Padrão Ports & Adapters (Hexagonal Architecture)**
   - **Decisão**: Isolar totalmente o domínio de negócio de frameworks e bibliotecas externas.
   - **Status**: Aceito e Implementado.

2. **ADR-002: Observabilidade Estruturada com Loguru**
   - **Decisão**: Substituir a biblioteca padrão `logging` pelo `loguru` emitindo JSON estruturado com `correlation_id` e identificador do adapter.
   - **Status**: Aceito e Implementado.

3. **ADR-003: Validação de Contratos Strict com Pydantic v2**
   - **Decisão**: Garantir validação estrita em todas as bordas da aplicação (`app/src/contracts/`).
   - **Status**: Aceito e Implementado.

4. **ADR-004: Cobertura de 100% de Testes Unitários com Mocks de Rede**
   - **Decisão**: Bloqueio total de chamadas HTTP/AWS reais em ambiente de testes utilizando `respx` e `moto`.
   - **Status**: Aceito e Implementado.

5. **ADR-005: Clean Code como Prática Inegociável**
   - **Decisão**: Adotar rigorosamente os princípios de Clean Code (Robert C. Martin) em toda implementação — nomenclatura reveladora de intenção, funções pequenas e focadas (máximo ~20 linhas), eliminação de strings e números mágicos, e proibição de código morto ou imports não utilizados.
   - **Rationale**: Readability e manutenibilidade são requisitos de primeira classe para um integration hub de longa vida que cresce com cada nova integração onboarded.
   - **Status**: Aceito e Implementado.

6. **ADR-006: Design Patterns — Factories, Builders, Strategy**
   - **Decisão**: Aplicação mandatória de Design Patterns sempre que aplicável: Factories/Builders para criação de objetos complexos (ex: `Deal.from_dict`, `Contact.from_dict`), Strategy e Template Method para encapsular algoritmos e fluxos variantes em workflows.
   - **Rationale**: Padrões de projeto garantem extensibilidade sem modificação do núcleo, seguindo OCP do SOLID. Factories eliminam acoplamento de construção em múltiplos pontos do codebase.
   - **Status**: Aceito e Implementado.

---

## 🔗 Governança e Links Úteis
- [AGENTS.md (Governança e Padrões do Projeto)](../AGENTS.md)
- [Constituição do Projeto (.specify/memory/constitution.md)](../.specify/memory/constitution.md)
- [Diretrizes Completas de Arquitetura, SOLID, Clean Code e Design Patterns](../.agent/rules/diretrizes.md)
- [Estratégia de Testes e TDD](../.agent/rules/testes.md)
- [Checklist de Finalização](../.agent/rules/finalizacao.md)
