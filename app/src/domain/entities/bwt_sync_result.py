from dataclasses import dataclass


@dataclass(frozen=True)
class BWTSyncResult:
    """Resultado imutável de uma sincronização com a plataforma BWT.

    Encapsula os IDs retornados pela API BWT após a criação ou localização
    de um account, contact, deal e responsável, sem expor detalhes de infra.
    """

    account_id: int
    contact_id: int
    deal_id: int
    responsible_id: int | None = None
