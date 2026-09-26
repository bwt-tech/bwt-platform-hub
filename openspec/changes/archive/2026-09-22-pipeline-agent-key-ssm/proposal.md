## Why

Para reforçar a segurança e evitar chaves de API estáticas no arquivo `templates.yaml`, a propriedade `key` do agente em cada pipeline passará a conter um caminho para o AWS SSM Parameter Store (ex.: `/bwt/octadesk/keys/mendoza`). O serviço de orquestração buscará e resolverá esse caminho via `ConfigPort` antes de configurar o `OctadeskAdapter`.

## What Changes

- Declaração dos recursos `aws_ssm_parameter` com tipo `SecureString` no arquivo de infraestrutura `infra/ssm.tf` para as chaves do Octadesk por pipeline.
- Atualização do arquivo `app/src/config/templates.yaml` para que a chave `key` de cada `agent` contenha o caminho SSM correspondente.
- Adição do método `get_parameter(self, name: str) -> str` na interface `ConfigPort` e implementação no `AWSParameterStoreAdapter`.
- Atualização do `OrchestratorService` para aceitar `config_port` e resolver caminhos de SSM (strings iniciadas com `/`), confiando em strings diretas caso não sejam caminhos.
- Atualização do `SynchronizerScheduler` para passar `self._config_adapter` como `config_port` ao instanciar o `OrchestratorService`.

## Capabilities

### New Capabilities

### Modified Capabilities

- `pipeline-agent-key`: Atualização dos requisitos de resolução da API Key do Octadesk para suporte a caminhos no AWS SSM Parameter Store.

## Impact

- **Infraestrutura**: `infra/ssm.tf` ganha definições dos parâmetros SSM SecureString.
- **Configuração**: `app/src/config/templates.yaml` passa a armazenar caminhos SSM em `agent.key`.
- **Portas e Adaptadores**: `ConfigPort` e `AWSParameterStoreAdapter` ganham suporte à busca de parâmetros individuais.
- **Serviço**: `OrchestratorService` resolve o caminho SSM via `ConfigPort`.
- **Testes**: Atualização da suíte de testes unitários para validar a busca SSM com fallback para chaves em texto plano.
