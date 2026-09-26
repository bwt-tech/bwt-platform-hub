# BWT Contrib Integrator

Integration hub microservice for connecting third-party services (Meta, Google, RDStation, Octadesk, etc.) to the BWT ecosystem. Built using the Hexagonal Architecture pattern with Python 3.12+, FastAPI, and Pydantic.

## Prerequisites
- Python 3.12+ (3.14 via Docker)
- Docker (optional, but recommended for production)

## Rodando Localmente (Desenvolvimento)

A constituição do projeto (Princípio IX) dita que o ambiente de desenvolvimento local **deve ser obrigatoriamente** isolado usando um Virtual Environment (venv).

1. **Crie e ative o ambiente virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

    2. **Instale as dependências:**
    O pacote será instalado no modo editável (`-e`) com as dependências de desenvolvimento.
    ```bash
    pip install -e ".[dev]"
    ```

3. **Inicie o servidor localmente:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
   ```

4. A aplicação estará rodando em `http://localhost:8080`.
   Teste o endpoint de health check:
   ```bash
   curl -i http://localhost:8080/health
   ```

## Parametrização e AWS (LocalStack)

Esta aplicação utiliza **AWS Secrets Manager** para credenciais e **AWS SSM Parameter Store** para configurações dinâmicas (frequência de agendamento, limite de batch, enablement).

### Simulação Local com LocalStack

Para desenvolver localmente, utilize o Docker Compose para subir o LocalStack:

1. **Suba o LocalStack:**
   ```bash
   docker compose up -d
   ```

2. O script `localstack-init.sh` provisionará automaticamente os segredos e parâmetros iniciais em `http://localhost:4566`.

3. **Configuração da Aplicação:**
   Certifique-se de que as variáveis de ambiente apontam para o LocalStack e para o banco de dados:
   ```env
   APP_AWS_ENDPOINT_URL=http://localhost:4566
   APP_AWS_REGION=us-east-1
   DATABASE_URL=postgresql://postgres:postgrespassword@localhost:5432/bwt_platform
   ```

### Alteração Dinâmica de Configuração

Você pode alterar o comportamento dos agendadores em tempo de execução sem reiniciar a aplicação:

```bash
# Scheduler Direto (OrchestratorService)
aws --endpoint-url=http://localhost:4566 ssm put-parameter --name "/bwt/scheduler/enabled" --value "false" --overwrite
aws --endpoint-url=http://localhost:4566 ssm put-parameter --name "/bwt/scheduler/cron" --value "*/10 * * * *" --overwrite
aws --endpoint-url=http://localhost:4566 ssm put-parameter --name "/bwt/scheduler/batch_size" --value "100" --overwrite

# Scheduler Reverso (OrchestratorReverseService)
aws --endpoint-url=http://localhost:4566 ssm put-parameter --name "/bwt/reverse_scheduler/enabled" --value "false" --overwrite
aws --endpoint-url=http://localhost:4566 ssm put-parameter --name "/bwt/reverse_scheduler/cron" --value "0 */2 * * *" --overwrite
aws --endpoint-url=http://localhost:4566 ssm put-parameter --name "/bwt/reverse_scheduler/batch_size" --value "50" --overwrite
```

A aplicação consulta as alterações a cada 5 minutos. Cada scheduler opera de forma independente.

#### Parâmetros SSM

| Parâmetro | Descrição | Padrão |
|---|---|---|
| `/bwt/scheduler/enabled` | Habilita/desabilita o scheduler direto | `true` |
| `/bwt/scheduler/cron` | Frequência do scheduler direto (expressão cron) | `*/5 * * * *` |
| `/bwt/scheduler/batch_size` | Máximo de deals por ciclo direto (`0` = sem limite) | `10` |
| `/bwt/reverse_scheduler/enabled` | Habilita/desabilita o scheduler reverso | `true` |
| `/bwt/reverse_scheduler/cron` | Frequência do scheduler reverso (expressão cron) | `*/5 * * * *` |
| `/bwt/reverse_scheduler/batch_size` | Máximo de chats por ciclo reverso (`0` = sem limite) | `10` |


## Banco de Dados e Migrações (Alembic)

Esta aplicação utiliza um banco de dados PostgreSQL para persistir entidades de domínio sincronizadas (Contacts, Deals, Chats), otimizando o processamento através de caches locais e garantindo a unicidade de contatos.

### Executando Migrações do Banco de Dados

Para criar as tabelas e aplicar as migrações mais recentes ao banco local ou de produção:

```bash
alembic upgrade head
```

Para gerar uma nova migração automaticamente após alterar as definições de esquema em `app/src/adapters/database/models.py`:

```bash
alembic revision --autogenerate -m "descricao_da_migracao"
```



## Rodando com Docker

1. **Faça o build da imagem:**
   ```bash
   docker build -t bwt-contrib-integrator:latest ./app
   ```

2. **Inicie o container:**
   ```bash
   docker run --rm -p 8080:8080 bwt-contrib-integrator:latest
   ```

## Testes

Os testes são mandatórios (100% de cobertura de unidade).

**Testes Unitários:**
```bash
pytest app/tests/unit/ --cov=app --cov-fail-under=100 -v
```

**Testes Funcionais:**
```bash
pytest app/tests/functional/ -v
```

### Isolamento de Ambiente em Testes

Para atender à obrigatoriedade de isolamento completo e evitar conexões externas/buscas de credenciais reais:
- O arquivo `app/tests/conftest.py` intercepta a importação de `app.main` aplicando mocks globais via `unittest.mock.patch` para `sentry_sdk.init` e `AWSSecretsManagerAdapter`.
- Desta forma, no momento em que `init_configs()` é disparado no nível do módulo ao importar `app.main`, as conexões externas de inicialização do Sentry e consulta do AWS Secrets Manager já estão devidamente mockadas.
- Após a importação inicial sob isolamento de mocks, os patchers são parados para que as implementações reais continuem totalmente disponíveis para os demais testes unitários (como testes específicos dos adapters usando o `moto`).



## Arquitetura

O código-fonte em `app/` segue o modelo port-and-adapters (Hexagonal) estrito:
- `app/api/` — Controllers / Roteadores FastAPI
- `app/core/` — Regras de domínio e negócio (sem frameworks)
- `app/services/` — Casos de uso
- `app/contracts/` — Contratos JSON (Pydantic models strict)
- `app/adapters/` — Implementação das ferramentas/APIs de terceiros (Infraestrutura: Octadesk, RDStation, BWT Platform, AWS S3/Secrets/SSM)
- `app/ports/` — Interfaces abstratas de portas de entrada e saída (`OctadeskPort`, `RDStationPort`, `BWTPort`, `S3Port`, etc.)

## Modelagem do Domínio (DDD)

A aplicação utiliza entidades de domínio tipadas e imutáveis (`@dataclass`) para representar os principais conceitos de negócio, desacoplando o núcleo de frameworks de serialização ou dicionários brutos:
- `Pipeline` & `DealStage` — Representam o funil do CRM e suas etapas
- `Contact`, `Deal` & `Chat` — Entidades imutáveis com rastreabilidade temporal (`created_at`, `updated_at`) para auditorias e sincronização

As transformações de payload bruto (JSON de APIs externas) para as entidades de domínio ocorrem exclusivamente nos adaptadores (Adapters) de saída, mantendo as portas (Ports) e serviços 100% independentes de contratos externos.

### Parametrização de Pipelines e Agentes (`templates.yaml`)

O arquivo `templates.yaml` mapeia as configurações de cada pipeline da RD Station para seus respectivos templates e credenciais no Octadesk. Cada agente possui uma chave `key` de API individual para autorização por pipeline:

```yaml
templates:
  Brasileiros em Mendoza:
    phone: "+5512991344987"
    template: "698b79c0ef5524949f9ae3cc"
    write_enabled: false
    agent:
      id: "bc6b081e-46f1-43b2-b580-df9c53fd393e"
      name: "Vanessa - Comercial"
      email: "vanessa.brasileirosemmendoza@gmail.com"
      key: "/bwt/octadesk/keys/mendoza"
```

### Adaptação de APIs Externas (Outbound Adapters)
- **OctadeskAdapter**: Integração com API de chat e contatos da Octadesk (suporta alternância dinâmica de API Keys por pipeline via `set_api_key`).
- **RDStationAdapter**: Integração com CRM RD Station (deals, pipelines, contatos).
- **BWTAdapter**: Integração REST com a Plataforma BWT (autenticação JWT, contas, contatos, negociações e usuários da empresa).


## Fluxograma de Processamento (OrchestratorService)

O fluxo abaixo descreve a lógica do método `start_process` na classe `OrchestratorService`.

```mermaid
flowchart TD
    Start([Início]) --> GetPipelines[Buscar Configuração de Pipelines]
    GetPipelines --> LoopPipelines{Para cada<br/>Pipeline}
    
    LoopPipelines -- "Fim" --> End([Fim / Retornar Sumários])
    LoopPipelines -- "Próxima" --> InitTracker[Inicializar ProcessSummaryTracker]
    InitTracker --> GetDeals[Buscar Negociações em 'Sem Contato']
    
    GetDeals --> LoopDeals{Para cada<br/>Negociação}
    LoopDeals -- "Fim" --> CollectSummary[Armazenar Sumário]
    CollectSummary --> LoopPipelines
    
    LoopDeals -- "Próxima" --> Validate{"Contém telefone<br/>e email válidos?"}
    
    Validate -- "Não / Erro" --> LogError1[Registrar Falha]
    LogError1 --> LoopDeals
    
    Validate -- "Sim" --> Normalize[Extrair Entidades: Deal e Contact]
    Normalize --> CheckRecurring{Contato recorrente<br/>sem resposta?}
    
    CheckRecurring -- "Sim" --> UpdateDealNoAnswer[Manter Negociação no RD]
    UpdateDealNoAnswer --> LoopDeals
    
    CheckRecurring -- "Não" --> GetOctadesk[Verificar contato no Octadesk]
    
    GetOctadesk --> CheckOctadesk{Contato já<br/>existe?}
    
    CheckOctadesk -- "Não" --> NewContact[Executar: NewContactWorkflow]
    NewContact --> CreateContact[Criar contato no Octadesk]
    CreateContact --> StartChat1[Iniciar Chat via Template]
    StartChat1 --> NotifyNew[Notificar Atendente]
    NotifyNew --> UpdateDeal1[Avançar Negociação BD]
    UpdateDeal1 --> LoopDeals
    
    CheckOctadesk -- "Sim" --> ExistingContact[Executar: ExistingContactWorkflow]
    ExistingContact --> CheckChats{Possui chat<br/>ativo?}
    
    CheckChats -- "Não" --> RecordNoChat[Apenas Registrar e Ignorar]
    RecordNoChat --> LoopDeals
    
    CheckChats -- "Sim" --> NotifyExisting[Notificar Atendente]
    NotifyExisting --> UpdateDeal2[Avançar Negociação BD]
    UpdateDeal2 --> LoopDeals
```

## Exemplo de Uso (Orchestrator)

```python
from app.src.services.orchestrator import OrchestratorService
from app.src.adapters.outbounds.octadesk import OctadeskAdapter
from app.src.adapters.outbounds.rdstation import RDStationAdapter

# Inicialização dos adaptadores (ports)
octadesk = OctadeskAdapter(api_key="...", base_url="...")
rdstation = RDStationAdapter(token="...")

# Injeção de dependência no serviço
service = OrchestratorService(
    octadesk_port=octadesk, 
    rdstation_port=rdstation
)

# Execução do processo de integração e obtenção do sumário
summaries = service.start_process()
```

## Fluxograma de Processamento Reverso (OrchestratorReverseService)

O fluxo abaixo descreve a sincronização no sentido **Octadesk → RD Station → BWT & Persistência Local**, orquestrada por `OrchestratorReverseService` e delegada a serviços especializados.

### Componentes da arquitetura

| Componente | Responsabilidade |
|---|---|
| `OrchestratorReverseService` | Itera agentes/chats, resolve escopo e delega ao workflow |
| `AgentSellerConfigLoader` | Carrega `agents2seller.yaml` como `AgentSellerConfiguration` |
| `PipelineScopeResolver` | Resolve pipeline RD + escopo BWT (fixo ou por tag do chat) |
| `BWTPortFactory` | Cria instância isolada de `BWTPort` por chat/escopo |
| `ReverseSyncWorkflow` | Coordena persistência local, RD e BWT |
| `RDStationReverseSyncService` | Regras de negociação na RD Station |
| `BWTReverseSyncService` | Conta, contato, deal e vendedor na BWT |
| `DealStatusPolicy` | Regras de transição de status (EPV, SC, NR, etc.) |

### Exemplo de uso

```python
from app.src.services.orchestrator_reverse import OrchestratorReverseService
from app.src.adapters.outbounds.octadesk import OctadeskAdapter
from app.src.adapters.outbounds.rdstation import RDStationAdapter

octadesk = OctadeskAdapter(api_key="...", base_url="...")
rdstation = RDStationAdapter(token="...")

service = OrchestratorReverseService(
    octadesk_port=octadesk,
    rdstation_port=rdstation,
)

service.start_process()
```

> O `BWTPort` é construído automaticamente via `BWTPortFactory` a cada chat, com o escopo definido em `agents2seller.yaml` (ex.: `SBM`, `SBS`, `SG`).

```mermaid
flowchart TD
    Start([Início: start_process]) --> LoadConfig[AgentSellerConfigLoader]
    LoadConfig --> FetchPipelines[Buscar Pipelines na RD Station]
    FetchPipelines --> LoopAgent{Para cada Agente}

    LoopAgent -->|Fim| End([Fim do Processamento])
    LoopAgent -->|Próximo| FetchChats[Buscar chats em andamento no Octadesk]

    FetchChats --> LoopChat{Para cada Chat}
    LoopChat -->|Fim Chats| LoopAgent
    LoopChat -->|Próximo| ResolveScope[PipelineScopeResolver: pipeline + escopo BWT]
    ResolveScope -->|Sem match| LoopChat
    ResolveScope -->|Match| CreateBWT[BWTPortFactory.create escopo]
    CreateBWT --> ExecuteWorkflow[ReverseSyncWorkflow.execute]

    ExecuteWorkflow --> PersistLocal[Persistir Contact e Chat local]
    PersistLocal --> RDSync[RDStationReverseSyncService]
    RDSync --> BWTSync[BWTReverseSyncService]

    RDSync --> RDLoop{Status da Deal RD}
    RDLoop -->|SC, CF| UpdateRD[Atualizar para WITH_SELLER / EPV]
    RDLoop -->|EPV, PE| SkipCreate[Não criar nova deal]
    RDLoop -->|NR, SI, IF, PR, VF| MarkCreate[Criar nova deal]
    UpdateRD --> RDCreate{create_new_deal?}
    SkipCreate --> RDCreate
    MarkCreate --> RDCreate
    RDCreate -->|Sim| PostRD[Criar negociação no RD]
    RDCreate -->|Não| BWTSync

    BWTSync --> FindAccount[Buscar/criar conta e contato BWT]
    FindAccount --> FindDeal[Buscar/criar deal ativa BWT]
    FindDeal --> AssignSeller[Avançar stage e atribuir vendedor]
    AssignSeller --> LoopChat
    PostRD --> BWTSync
```

---

## 📜 Histórico de Mudanças
Para detalhes sobre versões, novos recursos e correções, consulte o arquivo [RELEASE_NOTES.md](file:///home/mateus/bwt/bwt-platform-hub/RELEASE_NOTES.md).




EAAVxi18v4dsBR7ZCPID6z01ywkqEqOtMDdamQ56aAwfgd7ZANNavCeqjxKD29VEPjZCsUqHCxAB8KUSre6cqU21rVzc6802ZAqymS5k3NTyrwSJZBlN7c5vVy4LAJHgnpHZAvvarf7SWjXnRJanGKxDy6WmMSguSwZC8Tr09neohARfgzEuSGZAYb7KNyrFIm1OIrQZDZD