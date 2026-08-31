from AFD.AFD import AFD
from ManejoArchivos.leerAFD import cargarAFDDesdeArchivo
from ManejoArchivos.leerCadenas import evaluarArchivoCadenas

# Funcion para la creacion interactiva de un AFD
def crearAFDManual():
    print("\n--- CREACION MANUAL DE UN AFD ---")
    nombre = input("Ingrese el nombre del automata: ").strip() or "AFD_Manual"

    estadosInput = input("Ingrese los estados separados por comas (ej. q0,q1,q2): ")
    estados = [e.strip() for e in estadosInput.split(",") if e.strip()]

    alfabetoInput = input("Ingrese el alfabeto separado por comas (ej. a,b): ")
    alfabeto = [s.strip() for s in alfabetoInput.split(",") if s.strip()]

    inicial = input(f"Ingrese el estado inicial ({estados}): ").strip()
    while inicial not in estados:
        print(f"[ADVERTENCIA] El estado inicial debe ser uno de los estados definidos: {estados}")
        inicial = input(f"Ingrese el estado inicial ({estados}): ").strip()

    finalesInput = input("Ingrese los estados finales separados por comas: ")
    finales = [f.strip() for f in finalesInput.split(",") if f.strip()]

    afd = AFD(nombre)
    afd.definirAlfabeto(alfabeto)

    for e in estados:
        afd.agregarEstado(e, esInicial=(e == inicial), esFinal=(e in finales))

    print("\nDefinicion de transiciones delta(q, sigma) -> q':")
    for e in estados:
        for s in alfabeto:
            destino = input(f"  delta({e}, '{s}') -> ").strip()
            while destino not in estados:
                print(f"  [ADVERTENCIA] Estado destino invalido. Debe pertenecer a {estados}")
                destino = input(f"  delta({e}, '{s}') -> ").strip()
            afd.agregarTransicion(e, s, destino)

    print("\n[OK] AFD creado exitosamente.")
    return afd

# Funcion para desplegar el menu de opciones
def mostrarMenu():
    print("\n" + "-" * 55)
    print("      SISTEMA SIMULADOR Y VALIDADOR DE AFD")
    print("-" * 55)
    print(" 1. Crear un AFD manualmente")
    print(" 2. Cargar un AFD desde un archivo .txt")
    print(" 3. Mostrar la definicion formal del AFD")
    print(" 4. Mostrar la tabla de transicion")
    print(" 5. Validar la estructura del automata")
    print(" 6. Evaluar una cadena")
    print(" 7. Evaluar un archivo de cadenas")
    print(" 8. Consultar el historial de evaluaciones")
    print(" 9. Cargar o crear otro automata")
    print(" 10. Salir")
    print("-" * 55)

# Funcion controladora del flujo de la interfaz
def iniciar():
    afdActual = None

    while True:
        mostrarMenu()
        opcion = input("Seleccione una opcion (1-10): ").strip()

        if opcion == "1":
            afdActual = crearAFDManual()

        elif opcion == "2":
            ruta = input("Ingrese la ruta del archivo .txt del AFD: ").strip()
            afdCargado = cargarAFDDesdeArchivo(ruta)
            if afdCargado:
                afdActual = afdCargado

        elif opcion == "3":
            if afdActual:
                afdActual.mostrarDefinicion()
            else:
                print("[ADVERTENCIA] Primero debe cargar o crear un automata.")

        elif opcion == "4":
            if afdActual:
                afdActual.mostrarTablaTransiciones()
            else:
                print("[ADVERTENCIA] Primero debe cargar o crear un automata.")

        elif opcion == "5":
            if afdActual:
                valido, errores, faltantes = afdActual.validarEstructura()
                if valido:
                    print("\n[OK] El automata es estructuralmente VALIDO, determinista y completo.")
                else:
                    print("\n[ADVERTENCIA] El automata presenta observaciones estructurales:")
                    for err in errores:
                        print(f"  - {err}")
                    if faltantes:
                        print(f"  - Transiciones faltantes: {len(faltantes)} pares (estado, simbolo) sin definir.")
                        opcTrampa = input("¿Desea agregar un estado trampa para completarlo? (s/n): ").strip().lower()
                        if opcTrampa == 's':
                            afdActual.completarConEstadoTrampa()

                afdActual.analisisEstructural()
            else:
                print("[ADVERTENCIA] Primero debe cargar o crear un automata.")

        elif opcion == "6":
            if afdActual:
                cadena = input("Ingrese la cadena a evaluar (presione Enter o escriba 'eps' para cadena vacia): ")
                afdActual.validarCadena(cadena, mostrarTraza=True)
            else:
                print("[ADVERTENCIA] Primero debe cargar o crear un automata.")

        elif opcion == "7":
            if afdActual:
                ruta = input("Ingrese la ruta del archivo de cadenas (.txt): ").strip()
                evaluarArchivoCadenas(afdActual, ruta)
            else:
                print("[ADVERTENCIA] Primero debe cargar o crear un automata.")

        elif opcion == "8":
            if afdActual:
                print(f"\n--- HISTORIAL DE EVALUACIONES ({len(afdActual.historial)} registros) ---")
                if not afdActual.historial:
                    print("  No hay evaluaciones registradas.")
                else:
                    for i, h in enumerate(afdActual.historial, 1):
                        print(f"  {i}. Cadena: \"{h['cadena']}\" -> Resultado: {h['resultado']} | Estado Final: {h['estado_final']}")
            else:
                print("[ADVERTENCIA] Primero debe cargar o crear un automata.")

        elif opcion == "9":
            afdActual = None
            print("[INFO] Memoria del automata liberada. Puede crear o cargar uno nuevo.")

        elif opcion == "10":
            print("\nFinalizando ejecucion del programa.")
            break
        else:
            print("[ERROR] Opcion no valida. Ingrese un numero del 1 al 10.")