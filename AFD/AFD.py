from AFD.NodoAFD import NodoAFD

class AFD:
    # Constructor de la clase AFD
    def __init__(self, nombre="AFD"):
        self.nombre = nombre              # Nombre o identificador del AFD
        self.alfabeto = []                # Simbolos que conforman el alfabeto (Sigma)
        self.nodos = {}                   # Diccionario para almacenar los nodos: {nombre: NodoAFD}
        self.estadoInicial = None         # NodoAFD que representa el estado inicial (q0)
        self.estadosFinales = []          # Lista de nombres de los estados finales (F)
        self.historial = []               # Lista para registrar las evaluaciones realizadas

    # Metodo para definir el alfabeto del AFD
    def definirAlfabeto(self, alfabeto):
        self.alfabeto = sorted(list(set(alfabeto)))

    # Metodo para agregar un estado al AFD
    def agregarEstado(self, nombre, esInicial=False, esFinal=False):
        if nombre not in self.nodos:
            nodo = NodoAFD(nombre, esFinal)
            self.nodos[nombre] = nodo
        else:
            nodo = self.nodos[nombre]
            if esFinal:
                nodo.setFinal(True)

        if esInicial:
            self.estadoInicial = nodo
        if esFinal and nombre not in self.estadosFinales:
            self.estadosFinales.append(nombre)
        return nodo

    # Metodo para agregar una transicion entre estados
    def agregarTransicion(self, origen, simbolo, destino):
        if origen not in self.nodos or destino not in self.nodos:
            raise ValueError(f"Error: Los estados '{origen}' o '{destino}' no existen en el conjunto Q.")
        if simbolo not in self.alfabeto:
            raise ValueError(f"Error: El simbolo '{simbolo}' no pertenece al alfabeto {self.alfabeto}.")
        self.nodos[origen].agregarTransicion(simbolo, self.nodos[destino])

    # Metodo para validar la estructura formal de la quintupla
    def validarEstructura(self):
        errores = []
        if not self.nodos:
            errores.append("El conjunto de estados Q esta vacio.")
        if not self.alfabeto:
            errores.append("El alfabeto Sigma no ha sido definido.")
        if not self.estadoInicial:
            errores.append("No se ha definido un estado inicial q0.")
        elif self.estadoInicial.estado not in self.nodos:
            errores.append("El estado inicial q0 no pertenece al conjunto Q.")

        for f in self.estadosFinales:
            if f not in self.nodos:
                errores.append(f"El estado final '{f}' no pertenece al conjunto Q.")

        # Verificar si faltan transiciones para que el AFD sea completo
        transicionesFaltantes = []
        for nombre, nodo in self.nodos.items():
            for simbolo in self.alfabeto:
                if simbolo not in nodo.transiciones:
                    transicionesFaltantes.append((nombre, simbolo))

        esValido = len(errores) == 0 and len(transicionesFaltantes) == 0
        return esValido, errores, transicionesFaltantes

    # Metodo para completar el AFD agregando un estado de trampa
    def completarConEstadoTrampa(self):
        _, _, faltantes = self.validarEstructura()
        if not faltantes:
            print("[INFO] El automata ya se encuentra completo. No requiere estado trampa.")
            return

        nombreTrampa = "q_dead"
        contador = 0
        while nombreTrampa in self.nodos:
            contador += 1
            nombreTrampa = f"q_dead{contador}"

        nodoTrampa = self.agregarEstado(nombreTrampa, esInicial=False, esFinal=False)
        for s in self.alfabeto:
            nodoTrampa.agregarTransicion(s, nodoTrampa)

        for estadoOrigen, simbolo in faltantes:
            self.nodos[estadoOrigen].agregarTransicion(simbolo, nodoTrampa)

        print(f"[OK] Se agrego el estado trampa '{nombreTrampa}' y se completaron {len(faltantes)} transiciones.")

    # Metodo para calcular los estados alcanzables desde el estado inicial
    def obtenerEstadosAlcanzables(self):
        if not self.estadoInicial:
            return set()
        visitados = set()
        cola = [self.estadoInicial]
        visitados.add(self.estadoInicial.estado)

        while cola:
            actual = cola.pop(0)
            for _, destino in actual.transiciones.items():
                if destino.estado not in visitados:
                    visitados.add(destino.estado)
                    cola.append(destino)
        return visitados

    # Metodo para realizar el analisis estructural de accesibilidad y lenguaje vacio
    def analisisEstructural(self):
        alcanzables = self.obtenerEstadosAlcanzables()
        todos = set(self.nodos.keys())
        inaccesibles = todos - alcanzables
        finalesAlcanzables = set(self.estadosFinales).intersection(alcanzables)
        esVacio = len(finalesAlcanzables) == 0

        print("\n--- ANALISIS ESTRUCTURAL DEL AFD ---")
        print(f"Estados alcanzables: {', '.join(sorted(alcanzables)) if alcanzables else 'Ninguno'}")
        print(f"Estados inaccesibles: {', '.join(sorted(inaccesibles)) if inaccesibles else 'Ninguno'}")
        print(f"Estados finales alcanzables: {', '.join(sorted(finalesAlcanzables)) if finalesAlcanzables else 'Ninguno'}")
        print(f"Lenguaje reconocido vacio (L(M) = vacio): {'SI (No alcanza ningun estado final)' if esVacio else 'NO'}")

    # Metodo para validar y simular una cadena paso a paso
    def validarCadena(self, cadena, mostrarTraza=True):
        if not self.estadoInicial:
            print("[ERROR] El automata no tiene un estado inicial definido.")
            return False

        # Reconocimiento de cadena vacia
        cadenaLimpia = "" if cadena in ["ε", "E", "eps", "lambda", "λ"] else cadena

        # Validacion de simbolos respecto al alfabeto
        for simbolo in cadenaLimpia:
            if simbolo not in self.alfabeto:
                if mostrarTraza:
                    print(f"[ERROR] El simbolo '{simbolo}' no pertenece al alfabeto {self.alfabeto}.")
                self.historial.append({"cadena": cadena, "resultado": "Rechazada (Simbolo Invalido)", "estado_final": "-"})
                return False

        if mostrarTraza:
            print(f"\nSimulacion de la cadena: \"{cadena if cadena != '' else 'epsilon'}\"")
            print(f"Estado inicial: {self.estadoInicial.estado}")
            print("-" * 55)
            print(f"{'Paso':<6} | {'Estado Actual':<15} | {'Simbolo':<10} | {'Siguiente Estado':<15}")
            print("-" * 55)

        nodoActual = self.estadoInicial
        paso = 1

        for simbolo in cadenaLimpia:
            nodoSiguiente = nodoActual.obtenerNodo(simbolo)
            if nodoSiguiente is None:
                if mostrarTraza:
                    print(f"{paso:<6} | {nodoActual.estado:<15} | {simbolo:<10} | TRANSICION NO DEFINIDA")
                    print("-" * 55)
                    print(f"[RECHAZADA] Bloqueo en el estado '{nodoActual.estado}' con el simbolo '{simbolo}'.")
                self.historial.append({"cadena": cadena, "resultado": "Rechazada (Bloqueo)", "estado_final": nodoActual.estado})
                return False

            if mostrarTraza:
                print(f"{paso:<6} | {nodoActual.estado:<15} | {simbolo:<10} | {nodoSiguiente.estado:<15}")
            nodoActual = nodoSiguiente
            paso += 1

        esAceptada = nodoActual.esFinal()
        if mostrarTraza:
            print("-" * 55)
            print(f"Estado final alcanzado: {nodoActual.estado}")
            print(f"Pertenece al conjunto de aceptacion F: {'SI' if esAceptada else 'NO'}")
            print(f"Veredicto: {'[ACEPTADA]' if esAceptada else '[RECHAZADA]'}\n")

        self.historial.append({
            "cadena": cadena if cadena != "" else "epsilon",
            "resultado": "Aceptada" if esAceptada else "Rechazada",
            "estado_final": nodoActual.estado
        })
        return esAceptada

    # Metodo para mostrar la definicion formal de la quintupla
    def mostrarDefinicion(self):
        print("\n" + "=" * 50)
        print(f"DEFINICION FORMAL DEL AFD: {self.nombre}")
        print("=" * 50)
        print(f"Q  (Estados):         {{{', '.join(sorted(self.nodos.keys()))}}}")
        print(f"Sigma (Alfabeto):     {{{', '.join(self.alfabeto)}}}")
        print(f"q0 (Estado Inicial):  {self.estadoInicial.estado if self.estadoInicial else 'No definido'}")
        print(f"F  (Estados Finales): {{{', '.join(sorted(self.estadosFinales))}}}")
        print("=" * 50)

    # Metodo para mostrar la tabla de transiciones
    def mostrarTablaTransiciones(self):
        print(f"\nTABLA DE TRANSICION - {self.nombre}")
        if not self.nodos or not self.alfabeto:
            print("[ADVERTENCIA] No hay estados o alfabeto definidos para mostrar la tabla.")
            return

        header = f"{'Estado (Q)':<15}" + "".join([f"| {s:<10}" for s in self.alfabeto])
        print("-" * len(header))
        print(header)
        print("-" * len(header))

        for nombreEstado, nodo in sorted(self.nodos.items()):
            prefijo = ""
            if self.estadoInicial and self.estadoInicial.estado == nombreEstado:
                prefijo += "->"
            if nodo.esFinal():
                prefijo += "*"
            estadoStr = f"{prefijo}{nombreEstado}"

            fila = f"{estadoStr:<15}"
            for s in self.alfabeto:
                destino = nodo.obtenerNodo(s)
                destStr = destino.estado if destino else "-"
                fila += f"| {destStr:<10}"
            print(fila)
        print("-" * len(header))
        print("Leyenda: -> Estado Inicial | * Estado Final\n")