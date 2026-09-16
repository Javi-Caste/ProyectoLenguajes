from AFND.NodoAFND import NodoAFND

class AFND:
    # Definir la quintupla
    def __init__(self, nombre = "AFND"):
        self.nombre = nombre
        self.nodos = {}  # Diccionario: {estado: NodoAFND}
        self.estado_inicial = None
        self.estados_finales = set()  # Conjunto de estados finales
        self.alfabeto = set()  # Conjunto de símbolos del alfabeto
        self.historial = []  # Lista para almacenar el historial de cadenas evaluadas 

# Define el alfabeto del autómata
    def definir_alfabeto(self, alfabeto):
        self.alfabeto = set(alfabeto)

# Agrega un nodo al autómata
    def agregar_nodo(self, estado, es_final=False, es_inicial=False):
        if estado not in self.nodos:
            nodo = NodoAFND(estado, es_final)
            self.nodos[estado] = nodo
            if es_inicial and self.estado_inicial is None:
                self.estado_inicial = nodo
        else:
            print(f"El nodo con estado '{estado}' ya existe.")

# Agrega una transición entre dos nodos
    def agregar_transicion(self, estado_origen, simbolo, estado_destino):
        # Validaciones 
        if simbolo not in self.alfabeto:
            raise ValueError(f"El símbolo '{simbolo}' no pertenece al alfabeto definido.")   
        
        if estado_origen not in self.nodos:
            raise ValueError(f"El estado de origen '{estado_origen}' no existe en el autómata.")
        
        if estado_destino not in self.nodos:
            raise ValueError(f"El estado de destino '{estado_destino}' no existe en el autómata.")
        
        # Agrega la transición al nodo de origen
        self.nodos[estado_origen].agregar_transicion(simbolo, self.nodos[estado_destino])
       
# Obtener estados alcanzables 
# Hace falta analisis estructural
# Hace falta metodo que muestre la quintupla del AFND

# Evalúa una cadena de entrada en el autómata
    def evaluar_cadena(self, cadena, mostrar_traza=True):

        if self.estado_inicial is None:
            raise ValueError("No se ha definido un estado inicial para el autómata.")

        estados_iniciales = {self.estado_inicial}

        def nombres_estados(estados):
            return ", ".join(sorted(estado.estado for estado in estados)) if estados else "-"
        
        # Inicializa el conjunto de estados actuales con el estado inicial
        estados_actuales = estados_iniciales

        if mostrar_traza:
            print(f"\nSimulación de la cadena: \"{cadena if cadena != '' else 'epsilon'}\"")
            print(f"Estados iniciales: {{{nombres_estados(estados_actuales)}}}")
            print("-" * 70)
            print(f"{'Paso':<6} | {'Estados actuales':<25} | {'Símbolo':<10} | {'Siguientes estados':<25}")
            print("-" * 70)
        
        # Procesa cada símbolo de la cadena
        for paso, simbolo in enumerate(cadena, 1):
            if simbolo not in self.alfabeto:
                if mostrar_traza:
                    print(f"{paso:<6} | {nombres_estados(estados_actuales):<25} | {simbolo:<10} | SIMBOLO INVALIDO")
                    print("-" * 70)
                self.historial.append({"cadena": cadena, "resultado": "Rechazada (Simbolo invalido)", "estados_finales": nombres_estados(estados_actuales)})
                raise ValueError(f"El símbolo '{simbolo}' no pertenece al alfabeto definido.")
            
            # Calcula los nuevos estados actuales a partir de las transiciones
            nuevos_estados = set()
            for estado in estados_actuales:
                nuevos_estados.update(estado.obtener_nodos(simbolo))

            if mostrar_traza:
                print(f"{paso:<6} | {nombres_estados(estados_actuales):<25} | {simbolo:<10} | {nombres_estados(nuevos_estados):<25}")
            estados_actuales = nuevos_estados
        
        # Verifica si alguno de los estados actuales es final
        aceptada = any(estado.es_final() for estado in estados_actuales)

        if mostrar_traza:
            print("-" * 70)
            print(f"Estados finales alcanzados: {{{nombres_estados(estados_actuales)}}}")
            print(f"Pertenece algún estado a F: {'SI' if aceptada else 'NO'}")
            print(f"Veredicto: {'[ACEPTADA]' if aceptada else '[RECHAZADA]'}\n")
        
        # Almacena la cadena evaluada y su resultado en el historial
        self.historial.append({
            "cadena": cadena if cadena != "" else "epsilon",
            "resultado": "Aceptada" if aceptada else "Rechazada",
            "estados_finales": nombres_estados(estados_actuales)
        })
        
        # Retorna el resultado de la evaluación
        return aceptada

