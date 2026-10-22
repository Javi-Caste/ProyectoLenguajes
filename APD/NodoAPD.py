class NodoAPD:
    # Representa un estado de un automata de pila.

    # Las transiciones se agrupan por (simbolo de entrada, tope de pila). Cada
    # valor es una lista para conservar la misma representacion para APD y una
    # futura extension APND.
    # 

    def __init__(self, estado, es_final=False):
        self.estado = estado
        self.final = es_final
        self.transiciones = {}

    def agregar_transicion(self, entrada, tope, destino, reemplazo):
        clave = (entrada, tope)
        self.transiciones.setdefault(clave, []).append((destino, tuple(reemplazo)))

    def obtener_transiciones(self, entrada, tope):
        return self.transiciones.get((entrada, tope), [])

    def es_final(self):
        return self.final
