## Context

Na alteração anterior, `agent.key` foi incluído no `templates.yaml`. Agora, evoluímos a arquitetura para armazenar caminhos do SSM Parameter Store (ex.: `/bwt/octadesk/keys/mendoza`) em vez de chaves estáticas em texto puro. O `OrchestratorService` resolverá dinamicamente a chave real consultando a AWS SSM via `ConfigPort`.

## Goals / Non-Goals

**Goals:**
- Declarar parâmetros `aws_ssm_parameter` com tipo `SecureString` no Terraform (`infra/ssm.tf`).
- Atualizar `templates.yaml` para usar caminhos SSM em `agent.key`.
- Adicionar o método `get_parameter(name: str) -> str` na porta `ConfigPort` e no adaptador `AWSParameterStoreAdapter`.
- Atualizar `OrchestratorService` para injetar `config_port` e resolver caminhos de SSM (iniciados por `/`), mantendo suporte a chaves diretas em texto plano quando o valor não começar com `/`.
- Atualizar `SynchronizerScheduler` para passar `self._config_adapter` ao instanciar `OrchestratorService`.

**Non-Goals:**
- Alterar o `OrchestratorReverseService` (focado na sincronização reverso de agentes BWT).

## Decisions

### Decisão 1: SecureString nos Parâmetros SSM no Terraform
- **Abordagem**: Definir `type = "SecureString"` para `/bwt/octadesk/keys/mendoza`, `/bwt/octadesk/keys/salta` e `/bwt/octadesk/keys/serra_gaucha` no `infra/ssm.tf` com `ignore_changes = [value]`.
- **Razão**: Garante criptografia de chave em repouso no KMS da AWS e permite atualização dinâmica dos valores de API Keys sem conflitos no Terraform.

### Decisão 2: Método Genérico `get_parameter` no `ConfigPort`
- **Abordagem**: Criar `get_parameter(self, name: str) -> str` em `ConfigPort` e implementar com `boto3.client("ssm").get_parameter(Name=name, WithDecryption=True)`.
- **Razão**: Fornece uma abstração reutilizável e desacoplada para buscar qualquer parâmetro individual no SSM pelo seu caminho.

### Decisão 3: Resolução Transparente com Confiança em Chaves Diretas
- **Abordagem**:
  ```python
  key_attr = configuration.agent.key
  if self._config_port and key_attr.startswith("/"):
      api_key = self._config_port.get_parameter(key_attr)
  else:
      api_key = key_attr
  self._octadesk.set_api_key(api_key)
  ```
- **Razão**: Se `agent.key` for um caminho SSM (começa com `/`), busca no SSM. Se for texto puro (ambientes locais/testes), usa o valor diretamente sem quebrar testes existentes.

## Risks / Trade-offs

- **Latência de chamada SSM por pipeline** → *Mitigação*: A resolução ocorre 1 vez por pipeline por ciclo de agendamento (que roda em intervalo configurado de minutos), garantindo impacto desprezível de latência.
