## 1. Infraestrutura e Configuração

- [x] 1.1 Declarar os parâmetros SSM `SecureString` no arquivo `infra/ssm.tf`
- [x] 1.2 Atualizar `app/src/config/templates.yaml` para definir `agent.key` como caminhos SSM (`/bwt/octadesk/keys/...`)

## 2. Porta e Adaptador de Configuração (SSM)

- [x] 2.1 Adicionar os testes unitários para `get_parameter` em `app/tests/unit/adapters/test_aws_config_adapter.py`
- [x] 2.2 Adicionar método abstrato `get_parameter` em `app/src/ports/config_port.py` e sua implementação em `app/src/adapters/outbounds/aws_config_adapter.py`

## 3. Orquestração e Agendador

- [x] 3.1 Escrever testes unitários em `app/tests/unit/services/test_orchestrator.py` validando a resolução de caminho SSM via `config_port` e o fallback para chave direta
- [x] 3.2 Atualizar `OrchestratorService` (`app/src/services/orchestrator.py`) para receber `config_port` e resolver caminhos iniciados por `/`
- [x] 3.3 Atualizar `SynchronizerScheduler._execute()` em `app/src/adapters/inbound/background/scheduler.py` para passar `self._config_adapter` para o `OrchestratorService`

## 4. Validação e Qualidade

- [x] 4.1 Executar a suíte de testes unitários com 100% de cobertura (`.venv/bin/pytest app/tests/unit/ --cov=app/src --cov-fail-under=100`)
