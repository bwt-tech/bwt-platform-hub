from app.src.adapters.outbounds.bwt import BWTAdapter
from app.src.ports.bwt_port import BWTPort


class BWTPortFactory:
    """Cria instâncias isoladas de BWTPort com escopo pré-configurado."""

    def create(self, scope: str) -> BWTPort:
        return BWTAdapter(scope=scope)
