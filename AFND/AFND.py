from AFND.NodoAFND import NodoAFND

# Hace falta analisis estructural
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
            if es_final:
                self.estados_finales.add(nodo)
            if es_inicial and self.estado_inicial is None:
                self.estado_inicial = nodo
        else:
            nodo = self.nodos[estado]
            if es_final:
                nodo.set_final(True)
                self.estados_finales.add(nodo)
            if es_inicial and self.estado_inicial is None:
                self.estado_inicial = nodo
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
    def obtener_estados_alcanzables(self):
        # Primero se revisa si hay un estado inicial definido
        if self.estado_inicial is None:
            raise ValueError("No se ha definido un estado inicial para el autómata.")
        
        # Ahora que se tiene el estado inicial
        # Se puede revisar en base al estado inicial y las transiciones definidas, qué estados son alcanzables
        estados_alcanzables = set()
        cola = [self.estado_inicial]
        estados_alcanzables.add(self.estado_inicial)
        
        # Se revisa cada nodo en la cola y se agregan sus transiciones a la cola si no han sido visitadas
        while cola:
            nodo_actual = cola.pop(0)
            for simbolo in self.alfabeto:
                for nodo_destino in nodo_actual.obtener_nodos(simbolo):
                    if nodo_destino not in estados_alcanzables:
                        estados_alcanzables.add(nodo_destino)
                        cola.append(nodo_destino)
        return estados_alcanzables


# Evalúa una cadena de entrada en el autómata
    def evaluar_cadena(self, cadena, mostrar_traza=True):

        if self.estado_inicial is None:
            raise ValueError("No se ha definido un estado inicial para el autómata.")

        estados_iniciales = {self.estado_inicial}

        def nombres_estados(estados):
            return ", ".join(sorted(str(estado.estado) for estado in estados)) if estados else "-"
        
        # Inicializa el conjunto de estados actuales con el estado inicial
        estados_actuales = estados_iniciales

        if mostrar_traza:
            print(f"\nSimulación de la cadena: \"{cadena if cadena != '' else 'cadena vacia'}\"")
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
            "cadena": cadena if cadena != "" else "cadena vacia",
            "resultado": "Aceptada" if aceptada else "Rechazada",
            "estados_finales": nombres_estados(estados_actuales)
        })
        
        # Retorna el resultado de la evaluación
        return aceptada
    
# Hace falta metodo que muestre la quintupla del AFND
    def mostrar_quintupla(self):
        print(f"Nombre del autómata: {self.nombre}")
        print(f"Estados (Q): {', '.join(sorted(str(estado) for estado in self.nodos.keys()))}")
        print(f"Alfabeto (Σ): {', '.join(sorted(str(simbolo) for simbolo in self.alfabeto))}")
        print(f"Estado inicial (q0): {self.estado_inicial.estado if self.estado_inicial else 'No definido'}")
        print(f"Estados finales (F): {', '.join(sorted(str(estado.estado) for estado in self.estados_finales)) if self.estados_finales else 'No definidos'}")
        transiciones = []
        for origen in self.nodos.values():
            for simbolo, destinos in origen.transiciones.items():
                for destino in destinos:
                    transiciones.append(f"{origen.estado} --({simbolo})--> {destino.estado}")
        print(f"Transiciones: {', '.join(sorted(transiciones)) if transiciones else 'No definidas'}")
