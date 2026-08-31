class NodoAFD:
    # Constructor de la clase NodoAFD
    def __init__(self, estado, esFinal=False):
        self.estado = estado
        self.transiciones = {}  # Diccionario: {simbolo: NodoAFD}
        self.Final = esFinal    # Indica si el nodo es un estado final

    # Metodo para agregar una transicion desde el nodo actual a otro nodo
    def agregarTransicion(self, valor, nodo):
        if valor not in self.transiciones:
            self.transiciones[valor] = nodo
        else:
            raise ValueError(f"Ya existe una transicion para el valor '{valor}' desde el estado '{self.estado}'.")

    # Metodo para obtener un nodo por medio de un valor
    def obtenerNodo(self, valor):
        if valor in self.transiciones:
            return self.transiciones[valor]
        return None

    # Metodo para verificar si el nodo es un estado final
    def esFinal(self):
        return self.Final

    # Metodo para establecer si el nodo es final
    def setFinal(self, esFinal):
        self.Final = esFinal

    # Metodo para mostrar las transiciones del nodo
    def mostrarTransiciones(self):
        if not self.transiciones:
            print(f"  Estado '{self.estado}': Sin transiciones definidas.")
            return
        for valor, nodo in self.transiciones.items():
            print(f"  delta({self.estado}, '{valor}') -> {nodo.estado}")