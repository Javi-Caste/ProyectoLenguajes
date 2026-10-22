class NodoAPND:
    # Representa un estado de un automata de pila no determinista.

    def __init__(self, estado, es_final=False):
        self.estado = estado
        self.final = es_final
        # Cada clave puede conservar varias alternativas validas para APND.
        self.transiciones = {}

    def agregar_transicion(self, entrada, tope, destino, reemplazo):
        clave = (entrada, tope)
        self.transiciones.setdefault(clave, []).append((destino, tuple(reemplazo)))

    def obtener_transiciones(self, entrada, tope):
        return self.transiciones.get((entrada, tope), [])

    def es_final(self):
        return self.final
