from AFND.NodoAFND import NodoAFND

class AFND:
    # Constructor de la clase AFND
    def __init__(self, nombre="AFND"):
        self.nombre = nombre
        self.nodos = {}           # Diccionario: {nombre_estado: NodoAFND}
        self.estado_inicial = None
        self.estados_finales = set()
        self.alfabeto = set()
        self.historial = []

    # Metodo para definir el alfabeto
    def definir_alfabeto(self, alfabeto):
        self.alfabeto = set(alfabeto)

    # Metodo para agregar un nodo al AFND
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
        return nodo

    # Metodo para agregar una transicion
    def agregar_transicion(self, estado_origen, simbolo, estado_destino):
        if simbolo not in self.alfabeto:
            raise ValueError(f"El simbolo '{simbolo}' no pertenece al alfabeto definido.")
        if estado_origen not in self.nodos:
            raise ValueError(f"El estado origen '{estado_origen}' no existe.")
        if estado_destino not in self.nodos:
            raise ValueError(f"El estado destino '{estado_destino}' no existe.")
        self.nodos[estado_origen].agregar_transicion(simbolo, self.nodos[estado_destino])

    # Metodo para validar la estructura del AFND
    def validar_estructura(self):
        errores = []
        if not self.nodos:
            errores.append("El conjunto de estados Q esta vacio.")
        if not self.alfabeto:
            errores.append("El alfabeto Sigma no ha sido definido.")
        if not self.estado_inicial:
            errores.append("No se ha definido un estado inicial q0.")
        elif self.estado_inicial.estado not in self.nodos:
            errores.append("El estado inicial q0 no pertenece a Q.")

        for f in self.estados_finales:
            if f.estado not in self.nodos:
                errores.append(f"El estado final '{f.estado}' no pertenece a Q.")

        es_valido = len(errores) == 0
        return es_valido, errores

    # Metodo para obtener estados alcanzables mediante BFS
    def obtener_estados_alcanzables(self):
        if self.estado_inicial is None:
            return set()
        estados_alcanzables = set()
        cola = [self.estado_inicial]
        estados_alcanzables.add(self.estado_inicial)

        while cola:
            nodo_actual = cola.pop(0)
            for simbolo in self.alfabeto:
                for nodo_destino in nodo_actual.obtener_nodos(simbolo):
                    if nodo_destino not in estados_alcanzables:
                        estados_alcanzables.add(nodo_destino)
                        cola.append(nodo_destino)
        return estados_alcanzables

    # Metodo para analisis estructural de accesibilidad
    def analisis_estructural(self):
        alcanzables_nodos = self.obtener_estados_alcanzables()
        alcanzables = {nodo.estado for nodo in alcanzables_nodos}
        todos = set(self.nodos.keys())
        inaccesibles = todos - alcanzables
        finales_alcanzables = {f.estado for f in self.estados_finales if f.estado in alcanzables}
        es_vacio = len(finales_alcanzables) == 0

        print("\n--- ANALISIS ESTRUCTURAL DEL AFND ---")
        print(f"Estados alcanzables: {', '.join(sorted(alcanzables)) if alcanzables else 'Ninguno'}")
        print(f"Estados inaccesibles: {', '.join(sorted(inaccesibles)) if inaccesibles else 'Ninguno'}")
        print(f"Estados finales alcanzables: {', '.join(sorted(finales_alcanzables)) if finales_alcanzables else 'Ninguno'}")
        print(f"Lenguaje reconocido vacio (L(M) = vacio): {'SI (No alcanza estados finales)' if es_vacio else 'NO'}")

    # Metodo para mostrar la definicion formal de la quintupla
    def mostrar_quintupla(self):
        print("\n" + "=" * 55)
        print(f"DEFINICION FORMAL DEL AFND: {self.nombre}")
        print("=" * 55)
        print(f"Q  (Estados):         {{{', '.join(sorted(self.nodos.keys()))}}}")
        print(f"Sigma (Alfabeto):     {{{', '.join(sorted(self.alfabeto))}}}")
        print(f"q0 (Estado Inicial):  {self.estado_inicial.estado if self.estado_inicial else 'No definido'}")
        finales = sorted(list({f.estado for f in self.estados_finales}))
        print(f"F  (Estados Finales): {{{', '.join(finales)}}}")
        print("=" * 55)

    # Metodo para mostrar la tabla de transiciones del AFND
    def mostrar_tabla_transiciones(self):
        print(f"\nTABLA DE TRANSICION - AFND: {self.nombre}")
        if not self.nodos or not self.alfabeto:
            print("[ADVERTENCIA] No hay estados o alfabeto definidos.")
            return

        alfabeto_ordenado = sorted(list(self.alfabeto))
        header = f"{'Estado (Q)':<15}" + "".join([f"| {s:<18}" for s in alfabeto_ordenado])
        print("-" * len(header))
        print(header)
        print("-" * len(header))

        for nombre_estado, nodo in sorted(self.nodos.items()):
            prefijo = ""
            if self.estado_inicial and self.estado_inicial.estado == nombre_estado:
                prefijo += "->"
            if nodo.es_final():
                prefijo += "*"
            estado_str = f"{prefijo}{nombre_estado}"

            fila = f"{estado_str:<15}"
            for s in alfabeto_ordenado:
                destinos = nodo.obtener_nodos(s)
                if destinos:
                    dest_str = "{" + ",".join(sorted(d.estado for d in destinos)) + "}"
                else:
                    dest_str = "O"  # Representacion de conjunto vacio
                fila += f"| {dest_str:<18}"
            print(fila)
        print("-" * len(header))
        print("Leyenda: -> Estado Inicial | * Estado Final | O Transicion vacia\n")

    # Metodo para evaluar una cadena paso a paso en el AFND
    def evaluar_cadena(self, cadena, mostrar_traza=True):
        if self.estado_inicial is None:
            raise ValueError("No se ha definido un estado inicial para el automata.")

        cadena_limpia = "" if cadena in ["ε", "eps", "lambda", "λ"] else cadena

        def nombres_estados(estados):
            return "{" + ",".join(sorted(str(e.estado) for e in estados)) + "}" if estados else "O"

        estados_actuales = {self.estado_inicial}

        if mostrar_traza:
            print(f"\nSimulacion en AFND de la cadena: \"{cadena if cadena != '' else 'epsilon'}\"")
            print(f"Estado inicial: {{{self.estado_inicial.estado}}}")
            print("-" * 70)
            print(f"{'Paso':<6} | {'Estados Actuales':<25} | {'Simbolo':<10} | {'Siguientes Estados':<25}")
            print("-" * 70)

        for paso, simbolo in enumerate(cadena_limpia, 1):
            if simbolo not in self.alfabeto:
                if mostrar_traza:
                    print(f"{paso:<6} | {nombres_estados(estados_actuales):<25} | {simbolo:<10} | SIMBOLO INVALIDO")
                    print("-" * 70)
                self.historial.append({"cadena": cadena, "resultado": "Rechazada (Simbolo Invalido)", "estado_final": nombres_estados(estados_actuales)})
                return False

            nuevos_estados = set()
            for estado in estados_actuales:
                nuevos_estados.update(estado.obtener_nodos(simbolo))

            if mostrar_traza:
                print(f"{paso:<6} | {nombres_estados(estados_actuales):<25} | {simbolo:<10} | {nombres_estados(nuevos_estados):<25}")
            estados_actuales = nuevos_estados

            if not estados_actuales:
                break

        aceptada = any(estado.es_final() for estado in estados_actuales)

        if mostrar_traza:
            print("-" * 70)
            print(f"Estados finales alcanzados: {nombres_estados(estados_actuales)}")
            print(f"Contiene al menos un estado de F: {'SI' if aceptada else 'NO'}")
            print(f"Veredicto: {'[ACEPTADA]' if aceptada else '[RECHAZADA]'}\n")

        self.historial.append({
            "cadena": cadena if cadena != "" else "epsilon",
            "resultado": "Aceptada" if aceptada else "Rechazada",
            "estado_final": nombres_estados(estados_actuales)
        })
        return aceptada