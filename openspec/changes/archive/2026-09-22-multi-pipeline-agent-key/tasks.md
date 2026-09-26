## 1. Configuração e Entidades de Domínio

- [x] 1.1 Adicionar propriedade `key` ao bloco `agent` em cada pipeline no `app/src/config/templates.yaml`
- [x] 1.2 Escrever testes unitários para a entidade `Agent` em `app/tests/unit/domain/entities/test_agent.py` testando o carregamento do campo `key`
- [x] 1.3 Atualizar a entidade de domínio `Agent` (`app/src/domain/entities/agent.py`) para incluir o campo `key` e suporte no `from_dict`

## 2. Orquestração e Adapters

- [x] 2.1 Escrever testes unitários em `app/tests/unit/services/test_orchestrator.py` verificando a chamada a `set_api_key` no `OctadeskAdapter` a cada pipeline
- [x] 2.2 Atualizar `OrchestratorService` (`app/src/services/orchestrator.py`) para invocar `self._octadesk.set_api_key(configuration.agent.key)` no loop de pipelines

## 3. Garantia de Qualidade e Cobertura 100%

- [x] 3.1 Atualizar fixtures e mocks de teste existentes em `app/tests/` para refletir o novo campo `key` em `agent`
- [x] 3.2 Validar a suíte completa de testes unitários com 100% de cobertura (`.venv/bin/pytest app/tests/unit/ --cov=app --cov-fail-under=100`)
