
class NodoAFD:
    # Constructor de la clase NodoAFD
    def __init__(self, estado, esFinal=False):
        self.estado = estado
        self.transiciones = {}  
        self.Final = esFinal  # Indica si el nodo es un estado final
    
    # Método para agregar una transición desde el nodo actual a otro nodo
    def agregarTransicion(self,valor, nodo):
        if valor not in self.transiciones:
            self.transiciones[valor] = nodo
        else:
            raise ValueError(f"Ya existe una transición para el valor '{valor}' desde el estado '{self.estado}'.")

    # Metodo para obtener un nodo por medio de un valor
    def obtenerNodo(self, valor):
        if valor in self.transiciones:
            # Retorna el nodo en indice valor del diccionario
            return self.transiciones[valor]
        else:
            raise ValueError(f"No existe una transición para el valor '{valor}' desde el estado '{self.estado}'.")
    
    # Método para establecer si el nodo es un estado final
    def esFinal(self):
        return self.Final
    
    # Metodo para mostrar las transiciones del nodo
    def mostrarTransiciones(self):
        print(f"Transiciones del estado '{self.estado}':")
        for valor, nodo in self.transiciones.items():
            print(f"  Valor: '{valor}' -> Estado: '{nodo.estado}'")