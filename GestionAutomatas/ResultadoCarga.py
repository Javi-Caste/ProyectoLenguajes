from dataclasses import dataclass, field
from typing import Any


# Resultado sin efectos de consola de una carga de automata.
@dataclass
class ResultadoCarga:
    instancia: Any | None = None
    errores: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)

    @property
    def exitoso(self) -> bool:
        return self.instancia is not None and not self.errores
