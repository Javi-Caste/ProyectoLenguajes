import NodoAFD
# Deberia apuntar al estado inicial del AFD
# Deberia contener el alfabeto del AFD

class AFD:
    # Constructor de la clase AFD
    def __init__(self, estadoInicial, alfabeto):
        self.estadoInicial = estadoInicial  # NodoAFD que representa el estado inicial del AFD
        self.alfabeto = alfabeto  # Lista de símbolos que conforman el alfabeto del AFD
        self.nodos = []  # Lista para almacenar los nodos del AFD
    
    # Método para agregar un nodo al AFD
    def agregarNodo(self, nodo):
        if isinstance(nodo, NodoAFD.NodoAFD):
            self.nodos.append(nodo)
        else:
            raise ValueError("El nodo debe ser una instancia de la clase NodoAFD.")
    
    # Método para procesar una cadena
    def validarCadena(self, cadena):
        nodoActual = self.estadoInicial
        for simbolo in cadena:
            if simbolo not in self.alfabeto:
                raise ValueError(f"El símbolo '{simbolo}' no pertenece al alfabeto del AFD.")
            try:
                nodoActual = nodoActual.obtenerNodo(simbolo)
            except ValueError as e:
                return False  # No existe una transición para el símbolo actual
        return nodoActual.esFinal()  # Retorna True si el estado final es alcanzado, de lo contrario False
    
    # Metodo para mostrar los nodos del AFD
    def mostrarNodos(self):
        for nodo in self.nodos:
            print(f"Estado: {nodo.estado}, Final: {nodo.esFinal()}, Transiciones: {list(nodo.transiciones.keys())}")