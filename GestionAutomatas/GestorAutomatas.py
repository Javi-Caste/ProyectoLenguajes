from dataclasses import dataclass
from typing import Any


@dataclass
class RegistroAutomata:
    id: str
    nombre: str
    tipo: str
    instancia: Any
    origen: str
    padre_id: str | None = None
    equivalencias: list | None = None



# Mantiene las instancias de automatas durante la ejecucion actual.
class GestorAutomatas:

    def __init__(self):
        self._registros: dict[str, RegistroAutomata] = {}
        self._activo_id: str | None = None
        self._contador = 0
    
    def registrar(self, instancia, tipo: str, origen: str, padre_id: str | None = None, equivalencias: list | None = None) -> RegistroAutomata:
        self._contador += 1
        identificador = f"AUT-{self._contador:03d}"
        registro = RegistroAutomata(
            id=identificador,
            nombre=instancia.nombre,
            tipo=tipo,
            instancia=instancia,
            origen=origen,
            padre_id=padre_id,
            equivalencias=equivalencias,
        )
        self._registros[identificador] = registro
        self._activo_id = identificador
        return registro

    def listar(self) -> list[RegistroAutomata]:
        return list(self._registros.values())

    def obtener(self, identificador: str) -> RegistroAutomata | None:
        return self._registros.get(identificador.upper())

    def seleccionar(self, identificador: str) -> RegistroAutomata | None:
        registro = self.obtener(identificador)
        if registro:
            self._activo_id = registro.id
        return registro

    def obtener_activo(self) -> RegistroAutomata | None:
        if self._activo_id is None:
            return None
        return self._registros[self._activo_id]

    def esta_vacio(self) -> bool:
        return not self._registros
