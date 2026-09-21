
class NodoAFND:
    def __init__(self, estado, es_final=False):
        self.estado = estado
        self.transiciones = {} # Diccionario: {simbolo: [NodoAFND]}
        self._es_final = es_final
# Agrega transiciones desde el nodo actual a otros nodos
    def agregar_transicion(self, simbolo, nodo_destino):
        if simbolo not in self.transiciones:
            self.transiciones[simbolo] = []
        if nodo_destino not in self.transiciones[simbolo]:
            self.transiciones[simbolo].append(nodo_destino)
    
    def obtener_nodos(self, simbolo):
        return self.transiciones.get(simbolo, [])
    
    def set_final(self, es_final):
        self._es_final = es_final

    def es_final(self):
        return self._es_final
    
    # Muestra las transiciones del nodo
    def mostrar_transiciones(self):
        if not self.transiciones:
            print(f"  Estado '{self.estado}': Sin transiciones definidas.")
            return
        for simbolo, nodos in self.transiciones.items():
            destinos = ', '.join(str(nodo.estado) for nodo in nodos)
            print(f"  delta({self.estado}, '{simbolo}') -> {destinos}")
