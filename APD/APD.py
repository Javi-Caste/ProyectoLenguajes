from APD.NodoAPD import NodoAPD


class APD:
    # Autómata de pila determinista con aceptación por estado final.

    EPS = "EPS"

    def __init__(self, nombre="APD", tipo="APD", limite_exploracion=10000):
        self.nombre = nombre
        self.tipo = tipo.upper()
        self.alfabeto = []
        self.alfabeto_pila = []
        self.nodos = {}
        self.estadoInicial = None
        self.simboloInicialPila = None
        self.estadosFinales = []
        self.historial = []
        self.limite_exploracion = limite_exploracion

    def definir_alfabeto(self, alfabeto):
        self.alfabeto = list(dict.fromkeys(alfabeto))

    def definir_alfabeto_pila(self, alfabeto):
        self.alfabeto_pila = list(dict.fromkeys(alfabeto))

    def agregar_estado(self, nombre, es_inicial=False, es_final=False):
        nodo = self.nodos.get(nombre)
        if nodo is None:
            nodo = NodoAPD(nombre, es_final)
            self.nodos[nombre] = nodo
        elif es_final:
            nodo.final = True
        if es_inicial:
            self.estadoInicial = nodo
        if es_final and nombre not in self.estadosFinales:
            self.estadosFinales.append(nombre)
        return nodo

    def definir_simbolo_inicial_pila(self, simbolo):
        self.simboloInicialPila = simbolo

    def agregar_transicion(self, origen, entrada, tope, destino, reemplazo):
        if origen not in self.nodos:
            raise ValueError(f"El estado origen '{origen}' no existe.")
        self.nodos[origen].agregar_transicion(entrada, tope, destino, reemplazo)

    def validar_estructura(self):
        errores = []
        if self.tipo != "APD":
            errores.append("Este módulo acepta únicamente TIPO=APD.")
        if not self.nodos:
            errores.append("El conjunto de estados Q está vacío.")
        if not self.alfabeto:
            errores.append("El alfabeto de entrada Sigma está vacío.")
        if not self.alfabeto_pila:
            errores.append("El alfabeto de pila Gamma está vacío.")
        if self.EPS in self.alfabeto or self.EPS in self.alfabeto_pila:
            errores.append("EPS no puede pertenecer a los alfabetos.")
        if self.estadoInicial is None or self.estadoInicial.estado not in self.nodos:
            errores.append("El estado inicial q0 no pertenece a Q.")
        if self.simboloInicialPila not in self.alfabeto_pila:
            errores.append("El símbolo inicial de pila Z0 debe pertenecer a Gamma.")
        for final in self.estadosFinales:
            if final not in self.nodos:
                errores.append(f"El estado final '{final}' no pertenece a Q.")

        for origen, nodo in self.nodos.items():
            por_estado_tope = {}
            for (entrada, tope), alternativas in nodo.transiciones.items():
                if entrada != self.EPS and entrada not in self.alfabeto:
                    errores.append(f"delta({origen}, {entrada}, {tope}): entrada fuera de Sigma.")
                if tope not in self.alfabeto_pila:
                    errores.append(f"delta({origen}, {entrada}, {tope}): tope fuera de Gamma.")
                if len(alternativas) > 1:
                    errores.append(f"delta({origen}, {entrada}, {tope}) tiene más de una alternativa.")
                por_estado_tope.setdefault(tope, set()).add(entrada)
                for destino, reemplazo in alternativas:
                    if destino not in self.nodos:
                        errores.append(f"delta({origen}, {entrada}, {tope}): destino '{destino}' no declarado.")
                    if any(simbolo not in self.alfabeto_pila for simbolo in reemplazo):
                        errores.append(f"delta({origen}, {entrada}, {tope}): reemplazo fuera de Gamma.")
            for tope, entradas in por_estado_tope.items():
                if self.EPS in entradas and len(entradas) > 1:
                    errores.append(f"Conflicto APD en ({origen}, {tope}): no se puede mezclar EPS con entrada consumida.")
        return not errores, errores

    def mostrar_definicion(self):
        print("\n" + "=" * 58)
        print(f"DEFINICION FORMAL DEL APD: {self.nombre}")
        print("=" * 58)
        print(f"TIPO:                  {self.tipo}")
        print(f"Q (Estados):           {{{', '.join(sorted(self.nodos))}}}")
        print(f"Sigma (Entrada):       {{{', '.join(self.alfabeto)}}}")
        print(f"Gamma (Pila):          {{{', '.join(self.alfabeto_pila)}}}")
        print(f"q0 (Inicial):          {self.estadoInicial.estado if self.estadoInicial else 'No definido'}")
        print(f"Z0 (Pila inicial):     {self.simboloInicialPila or 'No definido'}")
        print(f"F (Finales):           {{{', '.join(sorted(self.estadosFinales))}}}")
        print("=" * 58)

    @staticmethod
    def _texto_reemplazo(reemplazo):
        return "EPS" if not reemplazo else ";".join(reemplazo)

    def mostrar_tabla_transiciones(self):
        columnas = list(self.alfabeto)
        if any(entrada == self.EPS for nodo in self.nodos.values() for entrada, _ in nodo.transiciones):
            columnas.append(self.EPS)
        if not self.nodos or not self.alfabeto_pila:
            print("[ADVERTENCIA] No hay datos suficientes para mostrar la tabla.")
            return
        filas = []
        for estado in sorted(self.nodos):
            for tope in self.alfabeto_pila:
                celdas = []
                for entrada in columnas:
                    alternativas = self.nodos[estado].obtener_transiciones(entrada, tope)
                    texto = ", ".join(f"({destino}, {self._texto_reemplazo(rep)})" for destino, rep in alternativas) or "-"
                    celdas.append(texto)
                filas.append((f"({estado}, {tope})", celdas))
        anchos = [max(18, len("(Estado, Tope)"), *(len(f[0]) for f in filas))]
        for indice, entrada in enumerate(columnas):
            anchos.append(max(len(entrada), *(len(f[1][indice]) for f in filas)))
        encabezado = " | ".join(texto.ljust(anchos[i]) for i, texto in enumerate(["(Estado, Tope)"] + columnas))
        print("\nTABLA DE TRANSICIONES - " + self.nombre)
        print("-" * len(encabezado))
        print(encabezado)
        print("-" * len(encabezado))
        for fila, celdas in filas:
            print(" | ".join(texto.ljust(anchos[i]) for i, texto in enumerate([fila] + celdas)))
        print("-" * len(encabezado))

    def _tokenizar_cadena(self, cadena):
        limpia = cadena.strip()
        if limpia.lower() in {"", "eps", "epsilon", "ε", "lambda", "λ"}:
            return []
        if "," in limpia:
            return [simbolo.strip() for simbolo in limpia.split(",") if simbolo.strip()]
        return list(limpia)

    def _registrar(self, cadena, resultado, estado="-"):
        self.historial.append({"cadena": cadena if cadena else "epsilon", "resultado": resultado, "estado_final": estado})

    def evaluar_cadena(self, cadena, mostrar_traza=True):
        valido, errores = self.validar_estructura()
        if not valido:
            if mostrar_traza:
                print("[ERROR] APD inválido: " + "; ".join(errores))
            self._registrar(cadena, "No evaluada (APD inválido)")
            return None
        simbolos = self._tokenizar_cadena(cadena)
        ajenos = [simbolo for simbolo in simbolos if simbolo not in self.alfabeto]
        if ajenos:
            if mostrar_traza:
                print(f"[ERROR] Símbolos fuera de Sigma: {', '.join(ajenos)}.")
            self._registrar(cadena, "Rechazada (símbolo inválido)")
            return False

        estado, posicion, pila = self.estadoInicial.estado, 0, [self.simboloInicialPila]
        visitadas, pasos = set(), 0
        if mostrar_traza:
            print(f"\nSIMULACION APD - Cadena: {cadena if cadena else 'epsilon'}")
            print(f"{'Paso':<5} | {'Estado':<12} | {'Restante':<15} | {'Pila antes':<20} | {'Entrada':<7} | {'Destino':<12} | {'Reemplazo':<12} | Pila después")
            print("-" * 130)
        while pasos < self.limite_exploracion:
            configuracion = (estado, posicion, tuple(pila))
            if configuracion in visitadas:
                if mostrar_traza:
                    print("[RECHAZADA] Se detectó una configuración repetida.")
                self._registrar(cadena, "Rechazada (ciclo)", estado)
                return False
            visitadas.add(configuracion)
            if posicion == len(simbolos) and estado in self.estadosFinales:
                if mostrar_traza:
                    print(f"[ACEPTADA] Entrada consumida y estado final '{estado}'.")
                self._registrar(cadena, "Aceptada", estado)
                return True
            tope = pila[-1] if pila else None
            entrada = self.EPS
            alternativas = self.nodos[estado].obtener_transiciones(self.EPS, tope) if tope else []
            if not alternativas and posicion < len(simbolos):
                entrada = simbolos[posicion]
                alternativas = self.nodos[estado].obtener_transiciones(entrada, tope) if tope else []
            if not alternativas:
                if mostrar_traza:
                    print(f"[RECHAZADA] No hay transición aplicable desde '{estado}'.")
                self._registrar(cadena, "Rechazada (bloqueo)", estado)
                return False
            destino, reemplazo = alternativas[0]
            antes = list(pila)
            pila.pop()
            pila.extend(reversed(reemplazo))
            restante = "".join(simbolos[posicion:]) or "epsilon"
            if mostrar_traza:
                print(f"{pasos + 1:<5} | {estado:<12} | {restante:<15} | {';'.join(antes):<20} | {entrada:<7} | {destino:<12} | {self._texto_reemplazo(reemplazo):<12} | {';'.join(pila) or 'vacia'}")
            estado = destino
            if entrada != self.EPS:
                posicion += 1
            pasos += 1
        if mostrar_traza:
            print("[DETENIDA] Límite de exploración excedido; no se clasifica como rechazada.")
        self._registrar(cadena, "Detenida (límite de exploración)", estado)
        return None
