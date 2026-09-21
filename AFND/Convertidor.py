from AFD.AFD import AFD


class Convertidor:
    def convertir(self, afnd):
        if afnd.estado_inicial is None:
            raise ValueError("No se ha definido un estado inicial para el AFND.")

        afd = AFD(f"{afnd.nombre}_convertido")
        afd.definirAlfabeto(afnd.alfabeto)

        mapeo_estados = {}
        pendientes = []

        def nombre_estado(conjunto_estados):
            if not conjunto_estados:
                return "VACIO"
            return "{" + ",".join(sorted(str(nodo.estado) for nodo in conjunto_estados)) + "}"

        def es_estado_final(conjunto_estados):
            return any(nodo.es_final() for nodo in conjunto_estados)

        def agregar_estado_afd(conjunto_estados, es_inicial=False):
            conjunto = frozenset(conjunto_estados)
            if conjunto not in mapeo_estados:
                nombre = nombre_estado(conjunto)
                mapeo_estados[conjunto] = nombre
                afd.agregarEstado(nombre, esInicial=es_inicial, esFinal=es_estado_final(conjunto))
                pendientes.append(conjunto)
            elif es_inicial:
                afd.agregarEstado(mapeo_estados[conjunto], esInicial=True)
            return mapeo_estados[conjunto]

        conjunto_inicial = frozenset([afnd.estado_inicial])
        agregar_estado_afd(conjunto_inicial, es_inicial=True)

        while pendientes:
            conjunto_actual = pendientes.pop(0)
            nombre_actual = mapeo_estados[conjunto_actual]

            for simbolo in afd.alfabeto:
                destinos = set()
                for estado in conjunto_actual:
                    destinos.update(estado.obtener_nodos(simbolo))

                conjunto_destino = frozenset(destinos)
                nombre_destino = agregar_estado_afd(conjunto_destino)
                afd.agregarTransicion(nombre_actual, simbolo, nombre_destino)

        return afd
