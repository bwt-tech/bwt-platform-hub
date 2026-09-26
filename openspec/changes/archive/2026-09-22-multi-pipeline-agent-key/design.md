## Context

A orquestração do sistema consome o arquivo `app/src/config/templates.yaml` para mapear pipelines da RDStation a templates e agentes do Octadesk. Para dar suporte a múltiplas chaves de API do Octadesk (uma por agente/pipeline), o valor da chave de API precisa estar contido na configuração do agente e ser repassado ao `OctadeskAdapter` via o setter `set_api_key`.

## Goals / Non-Goals

**Goals:**
- Incluir o campo `key` dentro do objeto `agent` em cada pipeline do `templates.yaml`.
- Atualizar a entidade de domínio `Agent` para gerenciar a propriedade `key`.
- Atualizar o `OrchestratorService` para invocar `self._octadesk.set_api_key(configuration.agent.key)` no início do ciclo de cada pipeline.
- Garantir que a suíte de testes mantenha 100% de cobertura.

**Non-Goals:**
- Alterar o comportamento interno dos endpoints HTTP do `OctadeskAdapter` (o método `set_api_key` já existe e altera `self.api_key`).
- Alterar a estrutura do `RDStationPort` ou da integração RDStation.

## Decisions

### Decisão 1: Propriedade `key` aninhada em `agent` no `templates.yaml`
- **Abordagem**: Colocar a propriedade `key` dentro do dicionário `agent` de cada template (`agent.key`).
- **Razão**: Alinha-se diretamente com o requisito do negócio onde a API Key pertence ao agente responsável por aquele pipeline no Octadesk.

### Decisão 2: Atualização do `Agent` no Domínio Puro
- **Abordagem**: Adicionar o campo `key: str` na classe `@dataclass class Agent` e atualizar `Agent.from_dict`.
- **Razão**: Mantém a camada de domínio consistente e auto-validável.

### Decisão 3: Atribuição dinâmica via setter no `OrchestratorService`
- **Abordagem**: No loop de pipelines em `OrchestratorService.start_process()`, após carregar a `TemplateConfiguration` correspondente, chamar `self._octadesk.set_api_key(configuration.agent.key)`.
- **Razão**: Garante que todas as chamadas subseqüentes efetuadas pelo `OctadeskAdapter` e pelas workflows associadas durante a execução daquele pipeline utilizarão os cabeçalhos HTTP com a API Key do agente correto.

## Risks / Trade-offs

- **Formato do `templates.yaml` em testes existentes** → *Mitigação*: Atualizar as fixtures de teste em `conftest.py` e testes unitários/funcionais que simulam o `templates.yaml` para incluir o campo `key` no dicionário `agent`.
