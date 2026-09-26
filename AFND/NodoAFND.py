class NodoAFND:
    # Constructor de la clase NodoAFND
    def __init__(self, estado, es_final=False):
        self.estado = estado
        self.transiciones = {}  # Diccionario: {simbolo: [NodoAFND]}
        self._es_final = es_final

    # Metodo para agregar transiciones desde el nodo actual hacia otros nodos
    def agregar_transicion(self, simbolo, nodo_destino):
        if simbolo not in self.transiciones:
            self.transiciones[simbolo] = []
        if nodo_destino not in self.transiciones[simbolo]:
            self.transiciones[simbolo].append(nodo_destino)

    # Metodo para obtener la lista de nodos destino para un simbolo
    def obtener_nodos(self, simbolo):
        return self.transiciones.get(simbolo, [])

    # Metodo para establecer si el nodo es estado final
    def set_final(self, es_final):
        self._es_final = es_final

    # Metodo para comprobar si es estado final
    def es_final(self):
        return self._es_final

    # Metodo para mostrar las transiciones del nodo
    def mostrar_transiciones(self):
        if not self.transiciones:
            print(f"  Estado '{self.estado}': Sin transiciones definidas.")
            return
        for simbolo, nodos in self.transiciones.items():
            destinos = ", ".join(sorted(str(nodo.estado) for nodo in nodos))
            print(f"  delta({self.estado}, '{simbolo}') -> {{{destinos}}}")