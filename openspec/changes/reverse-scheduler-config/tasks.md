## 1. Contrato da Porta de Configuração (`ConfigPort`)

- [x] 1.1 Adicionar método abstrato `get_reverse_scheduler_config() -> SchedulerConfig` à interface `ConfigPort` em `app/src/ports/config_port.py`

## 2. Adapter de Configuração AWS (`AWSParameterStoreAdapter`)

- [x] 2.1 Declarar as constantes dos paths SSM do scheduler reverso em `AWSParameterStoreAdapter`: `/bwt/reverse_scheduler/enabled`, `/bwt/reverse_scheduler/cron`, `/bwt/reverse_scheduler/batch_size`
- [x] 2.2 Implementar o método `get_reverse_scheduler_config()` em `AWSParameterStoreAdapter`, replicando a lógica de `get_scheduler_config()` com os novos paths e os mesmos defaults (`enabled=True`, `cron="*/5 * * * *"`, `batch_size=10`)
- [x] 2.3 Escrever testes unitários para `get_reverse_scheduler_config()` cobrindo: parâmetros presentes, parâmetros ausentes (defaults), `batch_size` inválido (warning + fallback) e `ClientError` (log + defaults)

## 3. Suporte a `batch_size` no `OrchestratorReverseService`

- [x] 3.1 Adicionar `self.batch_size: int = 0` ao `__init__` de `OrchestratorReverseService` em `app/src/services/orchestrator_reverse.py`
- [x] 3.2 Aplicar truncamento de chats em `start_process`, antes do loop `for chat in chats`: `chats = chats[:self.batch_size] if self.batch_size > 0 else chats`, com log informativo quando o limite for aplicado
- [x] 3.3 Atualizar testes unitários de `OrchestratorReverseService` para cobrir: `batch_size=0` (sem limite), `batch_size=N` (truncamento aplicado) e log gerado quando o limite é ativado

## 4. Classe `ReverseSyncronizerScheduler`

- [x] 4.1 Criar a classe `ReverseSyncronizerScheduler` em `app/src/adapters/inbound/background/scheduler.py` com padrão Singleton (`_instance`, `_initialized`), job id `"reverse_sync_job"` e injeção de `OrchestratorReverseService`
- [x] 4.2 Implementar `__init__`: instanciar `AWSParameterStoreAdapter`, carregar configuração via `get_reverse_scheduler_config()`, instanciar `OctadeskAdapter`, `RDStationAdapter` e `OrchestratorReverseService`, e aplicar `batch_size` inicial
- [x] 4.3 Implementar `start()`: registrar job principal com `CronTrigger` do SSM e job de polling de configuração a cada 5 minutos, e iniciar o scheduler global
- [x] 4.4 Implementar `check_config()`: detectar mudanças de `cron` (reagendar job), `batch_size` (atualizar serviço) e capturar exceções sem propagar
- [x] 4.5 Implementar `_execute()`: verificar flag `enabled`; quando `False`, logar e retornar sem processar; quando `True`, abrir sessão com `get_session()`, instanciar `OrchestratorReverseService` com repositórios, aplicar `batch_size` e chamar `start_process()`
- [x] 4.6 Implementar `stop()`: chamar `scheduler.shutdown()` com log

## 5. Testes Unitários do `ReverseSyncronizerScheduler`

- [x] 5.1 Criar arquivo `app/tests/unit/adapters/background/test_reverse_scheduler.py` com fixture de setup análoga à do `test_scheduler_dynamic.py` (singleton reset, mocks de adapters e repositórios)
- [x] 5.2 Testar `_execute` com `enabled=False`: verificar que `start_process` não é chamado e log informativo é emitido
- [x] 5.3 Testar `_execute` com `enabled=True`: verificar que `start_process` é chamado
- [x] 5.4 Testar `check_config` com mudança de cron: verificar `reschedule_job` chamado com novo trigger e config atualizada
- [x] 5.5 Testar `check_config` com mudança de `batch_size`: verificar que `_service.batch_size` é atualizado e config atualizada
- [x] 5.6 Testar `check_config` com exceção: verificar que nenhuma exceção é propagada e scheduler continua
- [x] 5.7 Testar `start()`: verificar que `scheduler.add_job` é chamado para job principal e polling, e `scheduler.start()` é invocado
- [x] 5.8 Testar `stop()`: verificar que `scheduler.shutdown()` é chamado

## 6. Registro na Inicialização da Aplicação

- [x] 6.1 Importar `ReverseSyncronizerScheduler` em `app/main.py`
- [x] 6.2 Adicionar thread daemon para `ReverseSyncronizerScheduler().start` no bloco `lifespan`, após a thread do `SyncronizerScheduler`
- [x] 6.3 Atualizar o mock global de `conftest.py` para incluir o patch de `ReverseSyncronizerScheduler.start`, evitando execução real em testes

## 7. Verificação Final

- [x] 7.1 Executar a suíte completa de testes unitários com 100% de cobertura: `.venv/bin/pytest app/tests/unit/ --cov=app --cov-fail-under=100`
- [x] 7.2 Executar os testes funcionais: `.venv/bin/pytest app/tests/functional/`
- [x] 7.3 Atualizar o `README.md` para refletir a adição do scheduler reverso e os novos parâmetros SSM
