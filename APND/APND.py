from collections import deque

from APND.NodoAPND import NodoAPND


class APND:
    # Automata de pila no determinista con aceptacion por estado final.

    EPS = "EPS"

    def __init__(self, nombre="APND", tipo="APND", limite_exploracion=10000):
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
            nodo = NodoAPND(nombre, es_final)
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
        if self.tipo != "APND":
            errores.append("Este módulo acepta únicamente TIPO=APND.")
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
            for (entrada, tope), alternativas in nodo.transiciones.items():
                if entrada != self.EPS and entrada not in self.alfabeto:
                    errores.append(f"delta({origen}, {entrada}, {tope}): entrada fuera de Sigma.")
                if tope not in self.alfabeto_pila:
                    errores.append(f"delta({origen}, {entrada}, {tope}): tope fuera de Gamma.")
                for destino, reemplazo in alternativas:
                    if destino not in self.nodos:
                        errores.append(f"delta({origen}, {entrada}, {tope}): destino '{destino}' no declarado.")
                    if any(simbolo not in self.alfabeto_pila for simbolo in reemplazo):
                        errores.append(f"delta({origen}, {entrada}, {tope}): reemplazo fuera de Gamma.")
        return not errores, errores

    def mostrar_definicion(self):
        print("\n" + "=" * 58)
        print(f"DEFINICION FORMAL DEL APND: {self.nombre}")
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
                    texto = ", ".join(
                        f"({destino}, {self._texto_reemplazo(reemplazo)})"
                        for destino, reemplazo in alternativas
                    ) or "-"
                    celdas.append(texto)
                filas.append((f"({estado}, {tope})", celdas))
        anchos = [max(18, len("(Estado, Tope)"), *(len(fila[0]) for fila in filas))]
        for indice, entrada in enumerate(columnas):
            anchos.append(max(len(entrada), *(len(fila[1][indice]) for fila in filas)))
        encabezado = " | ".join(
            texto.ljust(anchos[indice])
            for indice, texto in enumerate(["(Estado, Tope)"] + columnas)
        )
        print("\nTABLA DE TRANSICIONES - " + self.nombre)
        print("-" * len(encabezado))
        print(encabezado)
        print("-" * len(encabezado))
        for fila, celdas in filas:
            print(" | ".join(
                texto.ljust(anchos[indice])
                for indice, texto in enumerate([fila] + celdas)
            ))
        print("-" * len(encabezado))

    def _tokenizar_cadena(self, cadena):
        limpia = cadena.strip()
        if limpia.lower() in {"", "eps", "epsilon", "ε", "lambda", "λ"}:
            return []
        if "," in limpia:
            return [simbolo.strip() for simbolo in limpia.split(",") if simbolo.strip()]
        return list(limpia)

    def _registrar(self, cadena, resultado, estado="-", rama=None):
        registro = {
            "cadena": cadena if cadena else "epsilon",
            "resultado": resultado,
            "estado_final": estado,
        }
        if rama is not None:
            registro["rama_aceptante"] = rama
        self.historial.append(registro)

    def _imprimir_traza(self, rama):
        print(f"\nTRAZA DE RAMA {rama['id']}")
        print(
            f"{'Paso':<5} | {'Rama':<6} | {'Estado':<12} | {'Restante':<15} | "
            f"{'Pila antes':<20} | {'Entrada':<7} | {'Destino':<12} | "
            f"{'Reemplazo':<12} | Pila después"
        )
        print("-" * 145)
        for paso in rama["traza"]:
            print(
                f"{paso['numero']:<5} | {paso['rama']:<6} | {paso['estado']:<12} | "
                f"{paso['restante']:<15} | {paso['pila_antes']:<20} | "
                f"{paso['entrada']:<7} | {paso['destino']:<12} | "
                f"{paso['reemplazo']:<12} | {paso['pila_despues']}"
            )

    def evaluar_cadena(self, cadena, mostrar_traza=True):
        valido, errores = self.validar_estructura()
        if not valido:
            if mostrar_traza:
                print("[ERROR] APND inválido: " + "; ".join(errores))
            self._registrar(cadena, "No evaluada (APND inválido)")
            return None

        simbolos = self._tokenizar_cadena(cadena)
        ajenos = [simbolo for simbolo in simbolos if simbolo not in self.alfabeto]
        if ajenos:
            if mostrar_traza:
                print(f"[ERROR] Símbolos fuera de Sigma: {', '.join(ajenos)}.")
            self._registrar(cadena, "Rechazada (símbolo inválido)")
            return False

        rama_inicial = {
            "id": "R1",
            "estado": self.estadoInicial.estado,
            "posicion": 0,
            "pila": [self.simboloInicialPila],
            "traza": [],
        }
        pendientes = deque([rama_inicial])
        visitadas, exploradas, siguiente_rama = set(), 0, 2

        if mostrar_traza:
            print(f"\nSIMULACION APND - Cadena: {cadena if cadena else 'epsilon'}")

        while pendientes:
            if exploradas >= self.limite_exploracion:
                if mostrar_traza:
                    print("[DETENIDA] Simulación detenida: límite de exploración excedido.")
                self._registrar(cadena, "Detenida (límite de exploración)")
                return None

            rama = pendientes.popleft()
            estado, posicion, pila = rama["estado"], rama["posicion"], rama["pila"]
            configuracion = (estado, posicion, tuple(pila))
            if configuracion in visitadas:
                continue
            visitadas.add(configuracion)
            exploradas += 1

            if posicion == len(simbolos) and estado in self.estadosFinales:
                if mostrar_traza:
                    self._imprimir_traza(rama)
                    print(f"[ACEPTADA] Rama {rama['id']}: entrada consumida y estado final '{estado}'.")
                self._registrar(cadena, "Aceptada", estado, rama["id"])
                return True

            tope = pila[-1] if pila else None
            if tope is None:
                continue
            nodo = self.nodos[estado]
            alternativas = [(self.EPS, destino, reemplazo) for destino, reemplazo in nodo.obtener_transiciones(self.EPS, tope)]
            if posicion < len(simbolos):
                entrada_actual = simbolos[posicion]
                alternativas.extend(
                    (entrada_actual, destino, reemplazo)
                    for destino, reemplazo in nodo.obtener_transiciones(entrada_actual, tope)
                )
            if not alternativas:
                continue

            crear_ramas = len(alternativas) > 1
            nuevas_ramas = []
            for entrada, destino, reemplazo in alternativas:
                identificador = rama["id"]
                if crear_ramas:
                    identificador = f"R{siguiente_rama}"
                    siguiente_rama += 1
                nueva_pila = list(pila)
                antes = ";".join(nueva_pila) or "vacia"
                nueva_pila.pop()
                nueva_pila.extend(reversed(reemplazo))
                nueva_posicion = posicion + (entrada != self.EPS)
                paso = {
                    "numero": len(rama["traza"]) + 1,
                    "rama": identificador,
                    "estado": estado,
                    "restante": "".join(simbolos[posicion:]) or "epsilon",
                    "pila_antes": antes,
                    "entrada": entrada,
                    "destino": destino,
                    "reemplazo": self._texto_reemplazo(reemplazo),
                    "pila_despues": ";".join(nueva_pila) or "vacia",
                }
                nuevas_ramas.append({
                    "id": identificador,
                    "estado": destino,
                    "posicion": nueva_posicion,
                    "pila": nueva_pila,
                    "traza": rama["traza"] + [paso],
                })
            if crear_ramas and mostrar_traza:
                print(f"[RAMA {rama['id']}] Se generan: {', '.join(nueva['id'] for nueva in nuevas_ramas)}.")
            pendientes.extend(nuevas_ramas)

        if mostrar_traza:
            print("[RECHAZADA] Ninguna rama terminó con la entrada consumida en un estado final.")
        self._registrar(cadena, "Rechazada")
        return False
