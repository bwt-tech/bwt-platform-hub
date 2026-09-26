## Context

O projeto já possui um scheduler direto (`SyncronizerScheduler`) que:
- Carrega configuração (`enabled`, `cron`, `batch_size`) via `AWSParameterStoreAdapter.get_scheduler_config()` dos paths `/bwt/scheduler/*`.
- Aplica `batch_size` diretamente ao `OrchestratorService`.
- Faz polling de reconfiguração a cada 5 minutos via APScheduler.
- Segue o padrão Singleton para garantir uma única instância em runtime.

O `OrchestratorReverseService` existe mas não possui controles operacionais equivalentes. A interface `ConfigPort` hoje declara apenas `get_scheduler_config()`. O `AWSParameterStoreAdapter` implementa exclusivamente os paths do scheduler direto.

Ver `proposal.md` para motivação completa.

## Goals / Non-Goals

**Goals:**
- Criar `ReverseSyncronizerScheduler` espelhando estruturalmente `SyncronizerScheduler`, reaproveitando o mesmo `AWSParameterStoreAdapter` instanciado separadamente com paths SSM distintos.
- Estender `ConfigPort` com `get_reverse_scheduler_config()` mantendo backward compatibility total com implementações existentes.
- Adicionar `batch_size` ao `OrchestratorReverseService` com a mesma semântica do `OrchestratorService` (truncar a lista de chats antes do loop de processamento).
- Manter cobertura de testes unitários em 100%.

**Non-Goals:**
- Unificar os dois schedulers em uma única classe genérica (prematura generalização).
- Alterar a lógica de negócio do `OrchestratorReverseService` além do suporte a `batch_size`.
- Modificar a infraestrutura de SSM (criação dos parâmetros no Parameter Store é responsabilidade de infra/Terraform, fora do escopo desta mudança de código).
- Compartilhar instância do `AWSParameterStoreAdapter` entre os dois schedulers.

## Decisions

### D1 — Classe dedicada `ReverseSyncronizerScheduler` em vez de scheduler genérico parametrizável

**Decisão**: Criar `ReverseSyncronizerScheduler` como classe separada e independente dentro do mesmo módulo `scheduler.py`.

**Rationale**: O padrão Singleton já usado por `SyncronizerScheduler` não é trivialmente genérico sem introduzir complexidade desnecessária (chaves de instância por tipo). A duplicação estrutural é aceitável dado o número limitado de schedulers e a ausência de lógica de negócio na classe — ela é essencialmente cola de infraestrutura. Qualquer generalização futura pode ser feita quando um terceiro scheduler surgir.

**Alternativa considerada**: Extrair uma classe base `BaseScheduler` abstrata com Template Method. Rejeitado por adicionar indireção sem reduzir duplicação significativamente no cenário de dois schedulers.

---

### D2 — Paths SSM separados para o scheduler reverso (`/bwt/reverse_scheduler/*`)

**Decisão**: Usar o prefixo `/bwt/reverse_scheduler/` para as três chaves (enabled, cron, batch_size), separado do prefixo `/bwt/scheduler/` do scheduler direto.

**Rationale**: Permite controle operacional independente entre os dois fluxos — é o caso de uso central desta mudança. Compartilhar os mesmos parâmetros eliminaria o controle granular.

**Alternativa considerada**: Reutilizar os mesmos parâmetros SSM do scheduler direto. Rejeitado pois impede controlar os dois fluxos de forma independente.

---

### D3 — `get_reverse_scheduler_config()` como novo método em `ConfigPort` (não quebra backward compatibility)

**Decisão**: Adicionar `get_reverse_scheduler_config()` como método abstrato em `ConfigPort`. A única implementação concreta existente (`AWSParameterStoreAdapter`) será atualizada simultaneamente.

**Rationale**: A interface já tem um único implementador, portanto não há risco de quebra em runtime. Adicionar ao contrato da porta mantém o princípio DIP — o scheduler depende da abstração, não do adapter concreto.

**Alternativa considerada**: Criar uma porta separada `ReverseConfigPort`. Rejeitado por over-engineering — a responsabilidade de "ler configuração de schedulers" é coesa e não justifica duas interfaces.

---

### D4 — `batch_size` aplicado em `OrchestratorReverseService` via atributo público

**Decisão**: Adicionar `self.batch_size = 0` (sem limite por padrão) ao `__init__` do `OrchestratorReverseService`, e aplicar o truncamento `chats[:self.batch_size] if self.batch_size > 0 else chats` dentro de `start_process`, antes do loop `for chat in chats`.

**Rationale**: Espelha exatamente o padrão do `OrchestratorService`, reduzindo a curva cognitiva. O atributo público permite que o scheduler o sobreponha após instanciação, sem acoplamento à construção.

**Alternativa considerada**: Passar `batch_size` como parâmetro do construtor. Rejeitado porque o scheduler re-instancia o serviço a cada execução (padrão já estabelecido no `SyncronizerScheduler._execute`), e o `batch_size` precisa ser ajustável dinamicamente via polling sem recriar o scheduler.

---

### D5 — Re-instanciação do `OrchestratorReverseService` a cada `_execute`

**Decisão**: Seguir o mesmo padrão do `SyncronizerScheduler._execute`: instanciar `OrchestratorReverseService` dentro do `with get_session()`, injetando os repositórios de sessão, e aplicar `batch_size` imediatamente após.

**Rationale**: Garante que cada ciclo opere com uma sessão de banco de dados fresca, evitando sessões stale ou conexões abertas entre execuções. É o padrão estabelecido e testado do scheduler direto.

## Risks / Trade-offs

**[Risco] Duplicação estrutural entre `SyncronizerScheduler` e `ReverseSyncronizerScheduler`**
→ Mitigação: Documentada como decisão consciente (D1). Se um terceiro scheduler surgir, extrai-se a base comum naquele momento com evidência real de necessidade.

**[Risco] Parâmetros SSM ausentes em ambiente de produção no momento do deploy**
→ Mitigação: O `AWSParameterStoreAdapter` já possui lógica de fallback com valores padrão (`enabled=False`, `cron="*/5 * * * *"`, `batch_size=10`). O serviço sobe e opera com os defaults até que os parâmetros sejam criados.

**[Risco] `ConfigPort` passa a ter dois métodos abstratos — implementações de teste podem não implementar o novo**
→ Mitigação: Todos os mocks existentes que implementam `ConfigPort` usam `MagicMock` ou `unittest.mock`, que criam métodos automaticamente. Nenhuma implementação concreta adicional existe além do `AWSParameterStoreAdapter`.

**[Trade-off] `_execute` re-instancia o serviço a cada ciclo (D5)**
→ Custo de criação de objetos a cada execução. Aceitável pelo benefício de sessões de banco limpas e pelo precedente estabelecido no scheduler direto.

## Migration Plan

1. Criar os parâmetros SSM no ambiente alvo (responsabilidade de Infra/Terraform, fora do escopo do código):
   - `/bwt/reverse_scheduler/enabled` → `"true"`
   - `/bwt/reverse_scheduler/cron` → expressão cron desejada
   - `/bwt/reverse_scheduler/batch_size` → `"50"` (ou valor operacional)
2. Fazer deploy da aplicação com as alterações de código.
3. O `ReverseSyncronizerScheduler` inicia automaticamente via o ponto de entrada já existente (lifespan/startup do FastAPI).
4. **Rollback**: Reverter o deploy para a versão anterior. Os parâmetros SSM exclusivos do scheduler reverso podem permanecer sem efeito colateral.
