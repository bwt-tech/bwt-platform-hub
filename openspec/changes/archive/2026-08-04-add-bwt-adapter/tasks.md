# Implementation Tasks: Integração com a Plataforma BWT

- [x] 1. Adicionar Configurações da BWT em Settings
  - Adicionar `bwt_url`, `bwt_email`, `bwt_password`, `bwt_scope` em `app/src/config/settings.py`.

- [x] 2. Criar a Porta Abstrata `BWTPort`
  - Criar `app/src/ports/bwt_port.py` com métodos abstratos para login, contas, contatos, negociações e usuários da empresa.

- [x] 3. Criar o Outbound Adapter `BWTAdapter`
  - Criar `app/src/adapters/outbounds/bwt.py` implementando `BWTPort`.
  - Configurar headers (`Accept: application/json; version=v1_web`), autenticação JWT Bearer e tratamento de erro via `IntegrationError`.

- [x] 4. Criar Testes Unitários com Mocks
  - Escrever testes em `app/tests/unit/adapters/test_bwt_adapter.py`.
  - Garantir 100% de cobertura nos métodos do `BWTAdapter`.

- [x] 5. Atualizar Documentação
  - Atualizar o `README.md` registrando a adição do novo adapter BWT conforme o ritual de finalização.
