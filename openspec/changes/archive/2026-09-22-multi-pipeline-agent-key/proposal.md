## Why

Cada pipeline de atendimento no Octadesk necessita operar com sua própria API Key correspondente ao agente/conta responsável por aquele pipeline. Atualmente, o `OctadeskAdapter` opera com uma chave estática global, o que não reflete a separação de credenciais e agentes por pipeline durante a orquestração de contatos e negócios.

## What Changes

- Adição da propriedade `key` ao bloco `agent` de cada pipeline no arquivo de configuração `app/src/config/templates.yaml`.
- Atualização da entidade de domínio `Agent` para incluir o atributo `key`.
- Atualização do `OrchestratorService` para definir a API Key no `OctadeskAdapter` via `set_api_key` dinamicamente no início do processamento de cada pipeline.

## Capabilities

### New Capabilities

- `pipeline-agent-key`: Suporte ao gerenciamento e atribuição dinâmica de API Keys do Octadesk por agente/pipeline na orquestração.

### Modified Capabilities

## Impact

- **Configuração**: `app/src/config/templates.yaml` passa a conter o atributo `key` em cada `agent`.
- **Domínio**: `app/src/domain/entities/agent.py` ganha o campo `key`.
- **Serviço de Orquestração**: `app/src/services/orchestrator.py` altera a chave do adapter `OctadeskAdapter` via `set_api_key` para cada pipeline processado.
- **Suíte de Testes**: Atualização das fixtures e unit/functional tests para incluir o atributo `key` no `agent`.
