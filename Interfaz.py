from AFD.AFD import AFD
from AFND.AFND import AFND
from AFND.Convertidor import Convertidor
from ManejoArchivos.AFD.leerAFD import cargarAFDDesdeArchivo
from ManejoArchivos.AFD.leerCadenas import evaluarArchivoCadenas
from ManejoArchivos.AFND.leerAFND import cargarAFNDDesdeArchivo
from ManejoArchivos.AFND.leerCadenasAFND import evaluarArchivoCadenasAFND
# Creacion interactiva de un AFD manual
def crearAFDManual():
    print("\n--- CREACION MANUAL DE UN AFD ---")
    nombre = input("Ingrese el nombre del automata: ").strip() or "AFD_Manual"
    estados = [e.strip() for e in input("Ingrese los estados separados por comas (ej. q0,q1): ").split(",") if e.strip()]
    alfabeto = [s.strip() for s in input("Ingrese el alfabeto separado por comas (ej. a,b): ").split(",") if s.strip()]
    
    inicial = input(f"Ingrese el estado inicial ({estados}): ").strip()
    while inicial not in estados:
        print(f"[ADVERTENCIA] Debe pertenecer a {estados}")
        inicial = input(f"Ingrese el estado inicial ({estados}): ").strip()

    finales = [f.strip() for f in input("Ingrese los estados finales separados por comas: ").split(",") if f.strip()]

    afd = AFD(nombre)
    afd.definirAlfabeto(alfabeto)
    for e in estados:
        afd.agregarEstado(e, esInicial=(e == inicial), esFinal=(e in finales))

    print("\nDefinicion de transiciones delta(q, sigma) -> q':")
    for e in estados:
        for s in alfabeto:
            dest = input(f"  delta({e}, '{s}') -> ").strip()
            while dest not in estados:
                print(f"  [ADVERTENCIA] Estado invalido. Debe pertenecer a {estados}")
                dest = input(f"  delta({e}, '{s}') -> ").strip()
            afd.agregarTransicion(e, s, dest)

    print("[OK] AFD creado exitosamente.")
    return afd

# Creacion interactiva de un AFND manual
def crearAFNDManual():
    print("\n--- CREACION MANUAL DE UN AFND ---")
    nombre = input("Ingrese el nombre del automata: ").strip() or "AFND_Manual"
    estados = [e.strip() for e in input("Ingrese los estados separados por comas (ej. q0,q1): ").split(",") if e.strip()]
    alfabeto = [s.strip() for s in input("Ingrese el alfabeto separado por comas (ej. a,b): ").split(",") if s.strip()]

    inicial = input(f"Ingrese el estado inicial ({estados}): ").strip()
    while inicial not in estados:
        print(f"[ADVERTENCIA] Debe pertenecer a {estados}")
        inicial = input(f"Ingrese el estado inicial ({estados}): ").strip()

    finales = [f.strip() for f in input("Ingrese los estados finales separados por comas: ").split(",") if f.strip()]

    afnd = AFND(nombre)
    afnd.definir_alfabeto(alfabeto)
    for e in estados:
        afnd.agregar_nodo(e, es_final=(e in finales), es_inicial=(e == inicial))

    print("\nDefinicion de transiciones delta(q, sigma) -> {destinos} (Separar destinos con espacios, o escribir 'O' para vacio):")
    for e in estados:
        for s in alfabeto:
            dests_input = input(f"  delta({e}, '{s}') -> ").strip()
            if dests_input not in ["O", "Ø", ""]:
                for d in dests_input.split():
                    if d in estados:
                        afnd.agregar_transicion(e, s, d)
                    else:
                        print(f"  [ADVERTENCIA] Estado destino '{d}' ignorado por no existir en Q.")

    print("[OK] AFND creado exitosamente.")
    return afnd

# Despliegue del menu principal
def mostrarMenu():
    print("\n" + "=" * 65)
    print("   SISTEMA DE CONVERSION DE AFND A AFD Y SIMULACION - FASE 2")
    print("=" * 65)
    print(" 1.  Crear un AFD manualmente")
    print(" 2.  Cargar un AFD desde un archivo .txt")
    print(" 3.  Crear un AFND manualmente")
    print(" 4.  Cargar un AFND desde un archivo .txt")
    print(" 5.  Mostrar la definicion formal y la tabla del automata cargado")
    print(" 6.  Validar la estructura del automata")
    print(" 7.  Convertir el AFND cargado en un AFD equivalente")
    print(" 8.  Mostrar la tabla de equivalencias de macroestados")
    print(" 9.  Mostrar la tabla de transicion del AFD generado")
    print(" 10. Evaluar una cadena")
    print(" 11. Evaluar un archivo de cadenas")
    print(" 12. Consultar el historial de evaluaciones")
    print(" 13. Realizar el analisis estructural")
    print(" 14. Cargar o crear otro automata")
    print(" 15. Salir")
    print("=" * 65)

# Bucle principal de control
def iniciar():
    automata_cargado = None
    tipo_cargado = None       # "AFD" o "AFND"
    afd_generado = None
    tabla_equivalencias = []
    convertidor = Convertidor()

    while True:
        mostrarMenu()
        opcion = input("Seleccione una opcion (1-15): ").strip()

        if opcion == "1":
            automata_cargado = crearAFDManual()
            tipo_cargado = "AFD"
            afd_generado = None
            tabla_equivalencias = []

        elif opcion == "2":
            ruta = input("Ingrese la ruta del archivo .txt del AFD: ").strip()
            cargado = cargarAFDDesdeArchivo(ruta)
            if cargado:
                automata_cargado = cargado
                tipo_cargado = "AFD"
                afd_generado = None
                tabla_equivalencias = []

        elif opcion == "3":
            automata_cargado = crearAFNDManual()
            tipo_cargado = "AFND"
            afd_generado = None
            tabla_equivalencias = []

        elif opcion == "4":
            ruta = input("Ingrese la ruta del archivo .txt del AFND: ").strip()
            cargado = cargarAFNDDesdeArchivo(ruta)
            if cargado:
                automata_cargado = cargado
                tipo_cargado = "AFND"
                afd_generado = None
                tabla_equivalencias = []

        elif opcion == "5":
            if automata_cargado:
                if tipo_cargado == "AFD":
                    automata_cargado.mostrarDefinicion()
                    automata_cargado.mostrarTablaTransiciones()
                else:
                    automata_cargado.mostrar_quintupla()
                    automata_cargado.mostrar_tabla_transiciones()
            else:
                print("[ADVERTENCIA] No hay ningun automata cargado en memoria.")

        elif opcion == "6":
            if automata_cargado:
                if tipo_cargado == "AFD":
                    valido, errores, faltantes = automata_cargado.validarEstructura()
                    if valido:
                        print("[OK] El AFD es estructuralmente VALIDO, determinista y completo.")
                    else:
                        print("[ADVERTENCIA] Observaciones del AFD:")
                        for err in errores:
                            print(f"  - {err}")
                        if faltantes:
                            print(f"  - Transiciones faltantes: {len(faltantes)}")
                else:
                    valido, errores = automata_cargado.validar_estructura()
                    if valido:
                        print("[OK] El AFND es estructuralmente VALIDO.")
                    else:
                        print("[ADVERTENCIA] Observaciones del AFND:")
                        for err in errores:
                            print(f"  - {err}")
            else:
                print("[ADVERTENCIA] Primero debe cargar un automata.")

        elif opcion == "7":
            if tipo_cargado == "AFND" and automata_cargado:
                try:
                    afd_generado, tabla_equivalencias = convertidor.convertir(automata_cargado)
                    print(f"\n[OK] Conversion exitosa mediante Construccion de Subconjuntos.")
                    print(f"Se genero el AFD equivalente '{afd_generado.nombre}' con {len(afd_generado.nodos)} macroestados.")
                except Exception as e:
                    print(f"[ERROR en conversion]: {e}")
            else:
                print("[ADVERTENCIA] Debe cargar un AFND valido para ejecutar la conversion.")

        elif opcion == "8":
            if tabla_equivalencias:
                print("\n" + "=" * 50)
                print("TABLA DE EQUIVALENCIAS DE MACROESTADOS")
                print("=" * 50)
                print(f"{'Macroestado AFD':<18} | {'Conjunto de Estados AFND':<25}")
                print("-" * 50)
                for macro, conj_str, es_fin in tabla_equivalencias:
                    marca_final = "*" if es_fin else " "
                    print(f"  {marca_final} {macro:<14} | {conj_str:<25}")
                print("-" * 50)
                print("Leyenda: * Contiene al menos un estado final del AFND\n")
            else:
                print("[ADVERTENCIA] No se ha generado la tabla de equivalencias. Convierta un AFND primero (Opcion 7).")

        elif opcion == "9":
            if afd_generado:
                afd_generado.mostrarTablaTransiciones()
            else:
                print("[ADVERTENCIA] No existe un AFD generado. Convierta un AFND primero (Opcion 7).")

        elif opcion == "10":
            # Permite evaluar en el AFD generado si existe, o en el automata cargado
            target = afd_generado if afd_generado else automata_cargado
            if target:
                cadena = input("Ingrese la cadena a evaluar (presione Enter o 'eps' para vacia): ")
                if hasattr(target, "validarCadena"):
                    target.validarCadena(cadena, mostrarTraza=True)
                else:
                    target.evaluar_cadena(cadena, mostrar_traza=True)
            else:
                print("[ADVERTENCIA] Primero debe cargar un automata o convertir un AFND.")

        elif opcion == "11":
            target = afd_generado if afd_generado else automata_cargado
            if target:
                ruta = input("Ingrese la ruta del archivo de cadenas (.txt): ").strip()
                if hasattr(target, "validarCadena"):
                    evaluarArchivoCadenas(target, ruta)
                else:
                    evaluarArchivoCadenasAFND(target, ruta)
            else:
                print("[ADVERTENCIA] Primero debe cargar un automata o convertir un AFND.")

        elif opcion == "12":
            target = afd_generado if afd_generado else automata_cargado
            if target:
                print(f"\n--- HISTORIAL DE EVALUACIONES ({len(target.historial)} registros) ---")
                if not target.historial:
                    print("  No hay registros de evaluaciones previas.")
                else:
                    for i, h in enumerate(target.historial, 1):
                        fin = h.get('estado_final', h.get('estados_finales', '-'))
                        print(f"  {i}. Cadena: \"{h['cadena']}\" -> {h['resultado']} | Final: {fin}")
            else:
                print("[ADVERTENCIA] No hay automata activo.")

        elif opcion == "13":
            target = afd_generado if afd_generado else automata_cargado
            if target:
                if hasattr(target, "analisisEstructural"):
                    target.analisisEstructural()
                else:
                    target.analisis_estructural()
            else:
                print("[ADVERTENCIA] Primero cargue un automata.")

        elif opcion == "14":
            automata_cargado = None
            tipo_cargado = None
            afd_generado = None
            tabla_equivalencias = []
            print("[INFO] Memoria liberada. Listo para cargar o crear un nuevo automata.")

        elif opcion == "15":
            print("\nFinalizando ejecucion del programa.")
            break
        else:
            print("[ERROR] Opcion no valida. Ingrese un numero del 1 al 15.")