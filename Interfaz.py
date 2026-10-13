from AFD.AFD import AFD
from AFND.AFND import AFND
from AFND.Convertidor import Convertidor
from GestionAutomatas.GestorAutomatas import GestorAutomatas
from ManejoArchivos.AFD.leerAFD import cargarAFDDesdeArchivo
from ManejoArchivos.AFD.leerCadenas import evaluarArchivoCadenas
from ManejoArchivos.AFND.leerAFND import cargarAFNDDesdeArchivo
from ManejoArchivos.AFND.leerCadenasAFND import evaluarArchivoCadenasAFND


def _datos_basicos(tipo):
    nombre = input("Ingrese el nombre del automata: ").strip() or f"{tipo}_Manual"
    estados = [e.strip() for e in input("Ingrese los estados separados por comas: ").split(",") if e.strip()]
    alfabeto = [s.strip() for s in input("Ingrese el alfabeto separado por comas: ").split(",") if s.strip()]
    if not estados or not alfabeto or len(set(estados)) != len(estados) or len(set(alfabeto)) != len(alfabeto):
        print("[ERROR] Estados y alfabeto deben ser no vacios y sin duplicados.")
        return None
    inicial = input(f"Ingrese el estado inicial ({estados}): ").strip()
    finales = [f.strip() for f in input("Ingrese los estados finales separados por comas: ").split(",") if f.strip()]
    if inicial not in estados or any(final not in estados for final in finales):
        print("[ERROR] El inicial y todos los finales deben pertenecer a los estados declarados.")
        return None
    return nombre, estados, alfabeto, inicial, finales


def crearAFDManual():
    print("\n--- CREACION MANUAL DE UN AFD ---")
    datos = _datos_basicos("AFD")
    if not datos:
        return None
    nombre, estados, alfabeto, inicial, finales = datos
    afd = AFD(nombre)
    afd.definirAlfabeto(alfabeto)
    for estado in estados:
        afd.agregarEstado(estado, esInicial=estado == inicial, esFinal=estado in finales)
    for estado in estados:
        for simbolo in alfabeto:
            destino = input(f"  delta({estado}, '{simbolo}') -> ").strip()
            while destino not in estados:
                print(f"  [ADVERTENCIA] Debe pertenecer a {estados}")
                destino = input(f"  delta({estado}, '{simbolo}') -> ").strip()
            afd.agregarTransicion(estado, simbolo, destino)
    return afd


def crearAFNDManual():
    print("\n--- CREACION MANUAL DE UN AFND ---")
    datos = _datos_basicos("AFND")
    if not datos:
        return None
    nombre, estados, alfabeto, inicial, finales = datos
    afnd = AFND(nombre)
    afnd.definir_alfabeto(alfabeto)
    for estado in estados:
        afnd.agregar_nodo(estado, es_final=estado in finales, es_inicial=estado == inicial)
    print("Use destinos separados por espacios u 'O' para transicion vacia.")
    for estado in estados:
        for simbolo in alfabeto:
            destinos = input(f"  delta({estado}, '{simbolo}') -> ").strip()
            while destinos not in {"O", "Ø", ""} and any(destino not in estados for destino in destinos.split()):
                print(f"  [ERROR] Los destinos deben pertenecer a {estados}.")
                destinos = input(f"  delta({estado}, '{simbolo}') -> ").strip()
            if destinos not in {"O", "Ø", ""}:
                for destino in destinos.split():
                    afnd.agregar_transicion(estado, simbolo, destino)
    return afnd


def mostrarMenu():
    print("\n" + "=" * 65)
    print("   SISTEMA DE AUTOMATAS FINITOS - FASES 1 Y 2")
    print("=" * 65)
    opciones = [
        "Crear un AFD manualmente", "Cargar un AFD desde un archivo .txt",
        "Crear un AFND manualmente", "Cargar un AFND desde un archivo .txt",
        "Mostrar la definicion formal y la tabla del automata activo", "Validar la estructura del automata activo",
        "Convertir el AFND activo en un AFD equivalente", "Mostrar la tabla de equivalencias del AFD activo",
        "Mostrar la tabla de transicion del AFD activo", "Evaluar una cadena en el automata activo",
        "Evaluar un archivo de cadenas en el automata activo", "Consultar el historial del automata activo",
        "Realizar el analisis estructural del automata activo", "Completar AFD activo con estado de trampa",
        "Seleccionar automata cargado", "Salir",
    ]
    for indice, texto in enumerate(opciones, 1):
        print(f" {indice:>2}. {texto}")
    print("=" * 65)


def _mostrar_resultado_carga(resultado, gestor, tipo, origen):
    if not resultado.exitoso:
        print("[ERROR] No se cargo el automata:")
        for error in resultado.errores:
            print(f"  - {error}")
        return
    registro = gestor.registrar(resultado.instancia, tipo, origen)
    print(f"[OK] {tipo} '{registro.nombre}' registrado como {registro.id} y establecido como activo.")
    for advertencia in resultado.advertencias:
        print(f"[ADVERTENCIA] {advertencia}")


def _activo(gestor):
    registro = gestor.obtener_activo()
    if not registro:
        print("[ADVERTENCIA] No hay automata activo. Cree, cargue o seleccione uno.")
    return registro


def seleccionarAutomata(gestor):
    registros = gestor.listar()
    if not registros:
        print("[INFO] No hay automatas registrados.")
        return
    print("\nAUTOMATAS DISPONIBLES")
    for indice, registro in enumerate(registros, 1):
        activo = " | ACTIVO" if gestor.obtener_activo() and gestor.obtener_activo().id == registro.id else ""
        relacion = f" | de {registro.padre_id}" if registro.padre_id else ""
        print(f"[{indice}] {registro.id} | {registro.tipo:<4} | {registro.nombre} | {registro.origen}{relacion}{activo}")
    seleccion = input("Seleccione numero, ID o 0 para cancelar: ").strip()
    if seleccion == "0":
        return
    registro = None
    if seleccion.isdigit() and 1 <= int(seleccion) <= len(registros):
        registro = gestor.seleccionar(registros[int(seleccion) - 1].id)
    else:
        registro = gestor.seleccionar(seleccion)
    if registro:
        print(f"[OK] Automata activo: {registro.id} | {registro.nombre} ({registro.tipo}).")
    else:
        print("[ERROR] Seleccion invalida. El automata activo no cambio.")


def iniciar():
    gestor = GestorAutomatas()
    convertidor = Convertidor()
    while True:
        mostrarMenu()
        opcion = input("Seleccione una opcion (1-16): ").strip()
        if opcion == "1":
            automata = crearAFDManual()
            if automata:
                registro = gestor.registrar(automata, "AFD", "manual")
                print(f"[OK] AFD registrado como {registro.id}.")
        elif opcion == "2":
            _mostrar_resultado_carga(cargarAFDDesdeArchivo(input("Ruta del AFD: ").strip()), gestor, "AFD", "archivo")
        elif opcion == "3":
            automata = crearAFNDManual()
            if automata:
                registro = gestor.registrar(automata, "AFND", "manual")
                print(f"[OK] AFND registrado como {registro.id}.")
        elif opcion == "4":
            _mostrar_resultado_carga(cargarAFNDDesdeArchivo(input("Ruta del AFND: ").strip()), gestor, "AFND", "archivo")
        elif opcion == "5":
            registro = _activo(gestor)
            if registro:
                if registro.tipo == "AFD":
                    registro.instancia.mostrarDefinicion(); registro.instancia.mostrarTablaTransiciones()
                else:
                    registro.instancia.mostrar_quintupla(); registro.instancia.mostrar_tabla_transiciones()
        elif opcion == "6":
            registro = _activo(gestor)
            if registro:
                validacion = registro.instancia.validarEstructura() if registro.tipo == "AFD" else registro.instancia.validar_estructura()
                valido, errores = validacion[0], validacion[1]
                faltantes = validacion[2] if registro.tipo == "AFD" else []
                print("[OK] Estructura valida." if valido else "[ADVERTENCIA] Estructura incompleta o invalida.")
                for error in errores: print(f"  - {error}")
                if faltantes: print(f"  - Transiciones faltantes: {len(faltantes)}")
        elif opcion == "7":
            registro = _activo(gestor)
            if not registro or registro.tipo != "AFND":
                print("[ADVERTENCIA] Debe seleccionar un AFND activo.")
            else:
                valido, errores = registro.instancia.validar_estructura()
                if not valido:
                    print("[ERROR] AFND invalido: " + "; ".join(errores))
                else:
                    afd, equivalencias = convertidor.convertir(registro.instancia)
                    nuevo = gestor.registrar(afd, "AFD", "conversion", registro.id, equivalencias)
                    print(f"[OK] AFD equivalente registrado como {nuevo.id} y establecido como activo.")
        elif opcion == "8":
            registro = _activo(gestor)
            if not registro or not registro.equivalencias:
                print("[ADVERTENCIA] Seleccione un AFD generado por conversion.")
            else:
                print("\nTABLA DE EQUIVALENCIAS")
                for macro, conjunto, final in registro.equivalencias:
                    print(f"{'*' if final else ' '} {macro:<12} -> {conjunto}")
        elif opcion == "9":
            registro = _activo(gestor)
            if registro and registro.tipo == "AFD": registro.instancia.mostrarTablaTransiciones()
            elif registro: print("[ADVERTENCIA] El automata activo no es un AFD.")
        elif opcion == "10":
            registro = _activo(gestor)
            if registro:
                cadena = input("Cadena (Enter o 'eps' para vacia): ")
                if registro.tipo == "AFD": registro.instancia.validarCadena(cadena, mostrarTraza=True)
                else: registro.instancia.evaluar_cadena(cadena, mostrar_traza=True)
        elif opcion == "11":
            registro = _activo(gestor)
            if registro:
                ruta = input("Ruta del archivo de cadenas: ").strip()
                if registro.tipo == "AFD": evaluarArchivoCadenas(registro.instancia, ruta)
                else: evaluarArchivoCadenasAFND(registro.instancia, ruta)
        elif opcion == "12":
            registro = _activo(gestor)
            if registro:
                print(f"\n--- HISTORIAL ({registro.id}: {registro.nombre}) ---")
                for indice, entrada in enumerate(registro.instancia.historial, 1):
                    final = entrada.get('estado_final', entrada.get('estados_finales', '-'))
                    print(f"{indice}. {entrada['cadena']} -> {entrada['resultado']} | Final: {final}")
                if not registro.instancia.historial: print("No hay evaluaciones.")
        elif opcion == "13":
            registro = _activo(gestor)
            if registro:
                if registro.tipo == "AFD": registro.instancia.analisisEstructural()
                else: registro.instancia.analisis_estructural()
        elif opcion == "14":
            registro = _activo(gestor)
            if registro and registro.tipo == "AFD": registro.instancia.completarConEstadoTrampa()
            elif registro: print("[ADVERTENCIA] El estado de trampa solo aplica a AFD.")
        elif opcion == "15":
            seleccionarAutomata(gestor)
        elif opcion == "16":
            print("\nFinalizando ejecucion del programa.")
            break
        else:
            print("[ERROR] Opcion no valida.")
