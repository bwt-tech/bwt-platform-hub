# 🚀 BWT Platform Hub - Release Notes

Bem-vindo ao registro oficial de mudanças do **BWT Platform Hub**. Este documento detalha a evolução do microserviço de integração, focando em confiabilidade, escalabilidade e conformidade com a Arquitetura Hexagonal.

---

## [1.2.0] - 2026-06-22
### 🏛️ Arquitetura & Core
- **Workflows & Orchestration**: Refatorada a lógica principal do `OrchestratorService` para utilizar o padrão *Workflow* (`NewContactWorkflow` e `ExistingContactWorkflow`), garantindo separação de preocupações.
- **Process Tracking**: Implementado `ProcessSummaryTracker` para coletar métricas granulares durante a execução do batch.
- **DDD Refinement**: Melhoria nas entidades de domínio e isolamento total das regras de negócio em relação aos adaptadores externos.

### 📝 Documentação
- **Architecture Synchronization**: Atualização do `README.md` com novos fluxogramas Mermaid detalhando o processo de orquestração e novos rituais de entrega.

---

## [1.1.0] - 2026-06-15 a 2026-06-21
### ⚙️ Funcionalidades & Lógica de Negócio
- **Horário Comercial**: Adicionada trava operacional para garantir que o processamento de leads ocorra apenas em janelas de tempo permitidas.
- **Mecanismo de Retentativa**: Otimização do fluxo de retentativa para prevenir duplicação de mensagens e lidar com instabilidades em APIs de terceiros.
- **Busca de Contatos Híbrida**: Nova lógica de busca que suporta formatos dinâmicos de telefone (8 e 9 dígitos, com e sem DDI).
- **Dual-Delivery Logs**: Implementação de entrega dual de logs via FireLens para integração transparente com Datadog.

### 🛡️ Qualidade & Testes
- **Port Isolation**: Refatoração completa da suíte de testes unitários para garantir 100% de cobertura, utilizando mocks estritos para as portas do RDStation e Octadesk.
- **Normalization**: Sanetização automática de strings e telefones para evitar inconsistências no banco de dados.

---

## [1.0.0] - 2026-06-01 a 2026-06-14
### ☁️ Infraestrutura & Persistência
- **S3 Integration**: Adicionada porta de saída e adaptador para AWS S3, permitindo o upload automático de sumários de processamento para auditoria.
- **Observabilidade**: Integração inicial com Sentry para rastreamento de erros e Datadog para métricas de performance.
- **Dockerization**: Otimização do `Dockerfile` multi-stage para redução de footprint e segurança.

### 🚀 Inicialização
- **Bootstrap do Projeto**: Configuração inicial seguindo os princípios SOLID e Hexagonal.
- **Parameter Store & Secrets**: Integração com AWS SSM e Secrets Manager para configuração dinâmica em tempo de execução.

---

> [!NOTE]
> Este projeto segue rigorosamente o guia de governança definido em [AGENTS.md](file:///home/mateus/bwt/bwt-platform-hub/AGENTS.md).
