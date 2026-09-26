from AFD.AFD import AFD

class Convertidor:
    # Metodo para convertir un AFND en un AFD equivalente (Construccion de Subconjuntos)
    def convertir(self, afnd):
        if afnd.estado_inicial is None:
            raise ValueError("No se ha definido un estado inicial para el AFND.")

        afd = AFD(f"{afnd.nombre}_AFD_Equivalente")
        alfabeto_lista = sorted(list(afnd.alfabeto))
        afd.definirAlfabeto(alfabeto_lista)

        mapeo_estados = {}        # frozenset(estados) -> letra (ej. 'A')
        tabla_equivalencias = []  # Lista de tuplas: (Macroestado, Representacion_Subconjunto, es_final)
        pendientes = []
        contador_letras = 0

        # Generador de identificadores para macroestados: A, B, C, ..., Z, A1, B1...
        def generar_nombre_macro(indice):
            abecedario = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            if indice < len(abecedario):
                return abecedario[indice]
            return f"{abecedario[indice % len(abecedario)]}{indice // len(abecedario)}"

        # Representacion en texto del subconjunto
        def texto_subconjunto(conjunto_estados):
            if not conjunto_estados:
                return "O"
            return "{" + ",".join(sorted(str(nodo.estado) for nodo in conjunto_estados)) + "}"

        # Determina si el subconjunto contiene al menos un estado de aceptacion
        def es_final(conjunto_estados):
            return any(nodo.es_final() for nodo in conjunto_estados)

        # Registra un macroestado en el AFD
        def registrar_macroestado(conjunto_estados, es_inicial=False):
            nonlocal contador_letras
            conjunto = frozenset(conjunto_estados)
            if conjunto not in mapeo_estados:
                nombre_macro = generar_nombre_macro(contador_letras)
                contador_letras += 1
                mapeo_estados[conjunto] = nombre_macro
                es_est_final = es_final(conjunto)
                
                afd.agregarEstado(nombre_macro, esInicial=es_inicial, esFinal=es_est_final)
                tabla_equivalencias.append((nombre_macro, texto_subconjunto(conjunto), es_est_final))
                pendientes.append(conjunto)
            elif es_inicial:
                afd.agregarEstado(mapeo_estados[conjunto], esInicial=True)
            return mapeo_estados[conjunto]

        # 1. Macroestado Inicial: {q0}
        conjunto_inicial = frozenset([afnd.estado_inicial])
        registrar_macroestado(conjunto_inicial, es_inicial=True)

        # 2. Iteracion de Construccion de Subconjuntos
        while pendientes:
            conjunto_actual = pendientes.pop(0)
            nombre_actual = mapeo_estados[conjunto_actual]

            for simbolo in alfabeto_lista:
                destinos = set()
                # Calculo de union de destinos: delta(S, a) = union de delta(q, a)
                for estado_nodo in conjunto_actual:
                    destinos.update(estado_nodo.obtener_nodos(simbolo))

                conjunto_destino = frozenset(destinos)
                nombre_destino = registrar_macroestado(conjunto_destino)
                afd.agregarTransicion(nombre_actual, simbolo, nombre_destino)

        # Asociar la tabla de equivalencias al objeto AFD resultante
        afd.tabla_equivalencias = tabla_equivalencias
        return afd, tabla_equivalencias