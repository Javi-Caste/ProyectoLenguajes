from AFD.AFD import AFD
from AFND.AFND import AFND, es_simbolo_epsilon
from AFND.Convertidor import Convertidor
from APD.APD import APD
from APND.APND import APND
from GestionAutomatas.GestorAutomatas import GestorAutomatas
from ManejoArchivos.cargarAutomata import cargar_automata_desde_archivo
import os

gestor = GestorAutomatas()
convertidor_afnd = Convertidor()

def crearAFDManual():
    print("\n--- CREACION MANUAL DE UN AFD ---")
    nombre = input("Ingrese el nombre del automata: ").strip() or "AFD_Manual"
    estados = [e.strip() for e in input("Estados Q separados por comas (ej. q0,q1): ").split(",") if e.strip()]
    alfabeto = [s.strip() for s in input("Alfabeto Sigma separado por comas (ej. a,b): ").split(",") if s.strip()]
    
    if any(es_simbolo_epsilon(s) for s in alfabeto):
        print("[ERROR] Un AFD no admite simbolos epsilon en su alfabeto.")
        return

    inicial = input(f"Estado inicial q0 ({estados}): ").strip()
    if inicial not in estados:
        print("[ERROR] El estado inicial debe pertenecer a Q. Creacion cancelada.")
        return
        
    finales = [f.strip() for f in input("Estados finales F separados por comas: ").split(",") if f.strip()]
    for f in finales:
        if f not in estados:
            print(f"[ERROR] El estado final '{f}' no pertenece a Q. Creacion cancelada.")
            return

    afd = AFD(nombre)
    afd.definirAlfabeto(alfabeto)
    for e in estados:
        afd.agregarEstado(e, esInicial=(e == inicial), esFinal=(e in finales))

    print("\nDefinicion de transiciones delta(q, sigma) -> destino:")
    for e in estados:
        for s in alfabeto:
            dest = input(f"  delta({e}, '{s}') -> ").strip()
            if dest not in estados:
                print(f"  [ERROR] Destino '{dest}' no pertenece a Q. Creacion cancelada.")
                return
            afd.agregarTransicion(e, s, dest)

    valido, errores, faltantes = afd.validarEstructura()
    if not valido and errores:
        print("[ERROR] El AFD contiene errores estructurales y NO fue registrado:")
        for err in errores:
            print(f"  - {err}")
        return

    reg = gestor.registrar(afd, "AFD", "Manual")
    print(f"\n[OK] AFD valido creado exitosamente con ID: {reg.id}")


def crearAFNDManual():
    print("\n--- CREACION MANUAL DE UN AFND ---")
    nombre = input("Ingrese el nombre del automata: ").strip() or "AFND_Manual"
    estados = [e.strip() for e in input("Estados Q separados por comas (ej. q0,q1): ").split(",") if e.strip()]
    alfabeto = [s.strip() for s in input("Alfabeto Sigma separado por comas (ej. a,b): ").split(",") if s.strip()]
    
    # Retroalimentacion: rechazar transiciones/simbolos epsilon manuales en AFND
    if any(es_simbolo_epsilon(s) for s in alfabeto):
        print("[ERROR] AFND no permite epsilon en el alfabeto. Creacion cancelada.")
        return

    inicial = input(f"Estado inicial q0 ({estados}): ").strip()
    if inicial not in estados:
        print("[ERROR] El estado inicial debe pertenecer a Q. Creacion cancelada.")
        return
        
    finales = [f.strip() for f in input("Estados finales F separados por comas: ").split(",") if f.strip()]
    for f in finales:
        if f not in estados:
            print(f"[ERROR] El estado final '{f}' no pertenece a Q. Creacion cancelada.")
            return

    afnd = AFND(nombre)
    afnd.definir_alfabeto(alfabeto)
    for e in estados:
        afnd.agregar_nodo(e, es_final=(e in finales), es_inicial=(e == inicial))

    print("\nDefinicion de transiciones delta(q, sigma) -> {destinos} (separar por espacios o 'O' para vacio):")
    for e in estados:
        for s in alfabeto:
            dests_input = input(f"  delta({e}, '{s}') -> ").strip()
            if es_simbolo_epsilon(dests_input):
                print("[ERROR] Transiciones epsilon no permitidas en AFND. Creacion cancelada.")
                return
            if dests_input not in ["O", "Ø", "vacio", ""]:
                for d in dests_input.split():
                    if d not in estados:
                        print(f"[ERROR] Destino '{d}' no existe en Q. Creacion cancelada.")
                        return
                    afnd.agregar_transicion(e, s, d)

    valido, errores = afnd.validar_estructura()
    if not valido:
        print("[ERROR] El AFND contiene errores estructurales y NO fue registrado:")
        for err in errores:
            print(f"  - {err}")
        return

    reg = gestor.registrar(afnd, "AFND", "Manual")
    print(f"\n[OK] AFND valido creado exitosamente con ID: {reg.id}")


def crearPilaManual():
    print("\n--- CREACION MANUAL DE AUTOMATA DE PILA (APD / APND) ---")
    tipo = input("Tipo de automata (APD o APND): ").strip().upper()
    if tipo not in ["APD", "APND"]:
        print("[ERROR] Tipo invalido. Debe ser APD o APND.")
        return

    nombre = input("Nombre del automata: ").strip() or f"{tipo}_Manual"
    estados = [e.strip() for e in input("Estados Q separados por comas (ej. q0,q1,q2): ").split(",") if e.strip()]
    alfabeto = [s.strip() for s in input("Alfabeto de entrada Sigma (ej. a,b): ").split(",") if s.strip()]
    gamma = [g.strip() for g in input("Alfabeto de pila Gamma (ej. Z0,A): ").split(",") if g.strip()]

    # Validacion formal de EPS en alfabetos
    if "EPS" in alfabeto or any(es_simbolo_epsilon(s) for s in alfabeto):
        print("[ERROR] EPS no puede pertenecer a Sigma. Creacion cancelada.")
        return
    if "EPS" in gamma or any(es_simbolo_epsilon(g) for g in gamma):
        print("[ERROR] EPS no puede pertenecer a Gamma. Creacion cancelada.")
        return

    inicial = input(f"Estado inicial q0 ({estados}): ").strip()
    if inicial not in estados:
        print("[ERROR] q0 debe pertenecer a Q. Creacion cancelada.")
        return

    inicial_pila = input(f"Simbolo inicial de pila Z0 ({gamma}): ").strip()
    if inicial_pila not in gamma:
        print("[ERROR] Z0 debe pertenecer a Gamma. Creacion cancelada.")
        return

    finales = [f.strip() for f in input("Estados finales F separados por comas: ").split(",") if f.strip()]
    for f in finales:
        if f not in estados:
            print(f"[ERROR] Estado final '{f}' no pertenece a Q. Creacion cancelada.")
            return

    clase = APD if tipo == "APD" else APND
    automata = clase(nombre, tipo)
    automata.definir_alfabeto(alfabeto)
    automata.definir_alfabeto_pila(gamma)
    automata.definir_simbolo_inicial_pila(inicial_pila)

    for e in estados:
        automata.agregar_estado(e, es_inicial=(e == inicial), es_final=(e in finales))

    print("\n--- INGRESO DE TRANSICIONES ---")
    print("Formato APD:  origen, entrada, tope, destino, reemplazo (ej. q0, a, Z0, q0, A;Z0)")
    print("Formato APND: origen, entrada, tope, dest1, reemp1 | dest2, reemp2")
    print("Escriba 'FIN' para finalizar el ingreso.")

    transiciones_ingresadas = False
    while True:
        linea = input("Transicion: ").strip()
        if linea.upper() == "FIN":
            break
        if not linea:
            continue

        try:
            if tipo == "APD":
                if "|" in linea:
                    print("  [ERROR] Alternativas '|' no estan permitidas en APD. Transicion rechazada.")
                    continue
                partes = [p.strip() for p in linea.split(",")]
                if len(partes) != 5:
                    print("  [ERROR] Se requieren exactamente 5 componentes separados por coma.")
                    continue
                q_origen, entrada, tope, q_destino, reemp_raw = partes
                
                # Validacion de formato de reemplazo
                if reemp_raw.upper() == "EPS":
                    reemplazo = ()
                else:
                    reemplazo = tuple(reemp_raw.split(";"))
                    if "EPS" in reemplazo or not reemplazo:
                        print("  [ERROR] EPS solo puede aparecer como reemplazo completo unico. Rechazada.")
                        continue

                automata.agregar_transicion(q_origen, entrada, tope, q_destino, reemplazo)
                transiciones_ingresadas = True
                print("  [OK] Transicion APD registrada.")
            else:
                partes_principales = [p.strip() for p in linea.split(",", 3)]
                if len(partes_principales) != 4:
                    print("  [ERROR] Use: origen, entrada, tope, alternativas")
                    continue
                q_origen, entrada, tope, texto_alternativas = partes_principales
                for alt in texto_alternativas.split("|"):
                    subpartes = [s.strip() for s in alt.split(",")]
                    if len(subpartes) != 2:
                        print(f"  [ERROR] Alternativa invalida: '{alt}'")
                        continue
                    q_destino, reemp_raw = subpartes
                    if reemp_raw.upper() == "EPS":
                        reemplazo = ()
                    else:
                        reemplazo = tuple(reemp_raw.split(";"))
                        if "EPS" in reemplazo or not reemplazo:
                            print(f"  [ERROR] EPS invalido en reemplazo '{alt}'.")
                            continue
                    automata.agregar_transicion(q_origen, entrada, tope, q_destino, reemplazo)
                    transiciones_ingresadas = True
                print("  [OK] Alternativa(s) APND registrada(s).")
        except Exception as e:
            print(f"  [ERROR al procesar transicion]: {e}")

    # Validacion estricta final antes de guardar
    valido, errores = automata.validar_estructura()
    if not valido:
        print("\n[ERROR CRITICO] El automata presenta inconsistencias y NO sera registrado:")
        for err in errores:
            print(f"  - {err}")
        return

    reg = gestor.registrar(automata, tipo, "Manual")
    print(f"\n[OK] {tipo} '{nombre}' validado y registrado con ID: {reg.id}")


def cargarArchivo():
    ruta = input("Ingrese la ruta del archivo .txt: ").strip()
    resultado = cargar_automata_desde_archivo(ruta)
    if resultado.errores:
        print("\n[ERROR] Bloqueo de modelo invalido. No se acepto en memoria:")
        for err in resultado.errores:
            print(f"  - {err}")
        return

    if resultado.advertencias:
        print("\n[ADVERTENCIA] Observaciones detectadas durante la carga:")
        for adv in resultado.advertencias:
            print(f"  - {adv}")

    if resultado.instancia:
        reg = gestor.registrar(resultado.instancia, resultado.tipo, f"Archivo: {ruta}")
        print(f"\n[OK] Automata '{resultado.instancia.nombre}' ({resultado.tipo}) cargado con ID: {reg.id}")


def listarYSeleccionar():
    if gestor.esta_vacio():
        print("[ADVERTENCIA] No hay automatas en memoria.")
        return

    print("\n--- AUTOMATAS REGISTRADOS EN SESION ---")
    activo = gestor.obtener_activo()
    for reg in gestor.listar():
        marca = "--> [ACTIVO] " if (activo and activo.id == reg.id) else "    "
        print(f"{marca}ID: {reg.id} | Tipo: {reg.tipo:<4} | Nombre: {reg.nombre:<20} | Origen: {reg.origen}")

    cambiar = input("\n¿Desea cambiar el automata activo? (s/n): ").strip().lower()
    if cambiar == 's':
        target_id = input("Ingrese el ID del automata (ej. AUT-001): ").strip()
        reg_sel = gestor.seleccionar(target_id)
        if reg_sel:
            print(f"[OK] Automata activo cambiado a: {reg_sel.id} ({reg_sel.nombre})")
        else:
            print("[ERROR] ID no encontrado.")


def mostrarDefinicionYTabla():
    reg = gestor.obtener_activo()
    if not reg:
        print("[ADVERTENCIA] No hay automata activo.")
        return

    auto = reg.instancia
    if reg.tipo == "AFD":
        auto.mostrarDefinicion()
        auto.mostrarTablaTransiciones()
    elif reg.tipo == "AFND":
        auto.mostrar_quintupla()
        auto.mostrar_tabla_transiciones()
    elif reg.tipo in ["APD", "APND"]:
        auto.mostrar_definicion()
        auto.mostrar_tabla_transiciones()


def validarEstructuraActivo():
    reg = gestor.obtener_activo()
    if not reg:
        print("[ADVERTENCIA] No hay automata activo.")
        return

    auto = reg.instancia
    if reg.tipo == "AFD":
        valido, errores, faltantes = auto.validarEstructura()
        if valido:
            print(f"[OK] El AFD '{auto.nombre}' es estructuralmente VALIDO y completo.")
        else:
            print(f"[ADVERTENCIA] Observaciones del AFD:")
            for e in errores:
                print(f"  - {e}")
            if faltantes:
                print(f"  - Transiciones faltantes: {len(faltantes)}")
                opc = input("¿Desea agregar un estado trampa para completarlo? (s/n): ").strip().lower()
                if opc == 's':
                    if hasattr(auto, "completarConEstadoTrampa"):
                        auto.completarConEstadoTrampa()
                    elif hasattr(auto, "completar_con_trampa"):
                        auto.completar_con_trampa()
                    print("[OK] Estado trampa integrado. El AFD ha sido completado.")
    elif reg.tipo == "AFND":
        valido, errores = auto.validar_estructura()
        if valido:
            print(f"[OK] El AFND '{auto.nombre}' es estructuralmente VALIDO.")
        else:
            print("[ADVERTENCIA] Inconsistencias en el AFND:")
            for e in errores:
                print(f"  - {e}")
    elif reg.tipo in ["APD", "APND"]:
        valido, errores = auto.validar_estructura()
        if valido:
            print(f"[OK] El {reg.tipo} '{auto.nombre}' es estructuralmente VALIDO.")
        else:
            print(f"[ADVERTENCIA] Inconsistencias en el {reg.tipo}:")
            for e in errores:
                print(f"  - {e}")


def convertirAFNDaAFD():
    reg = gestor.obtener_activo()
    if not reg:
        print("[ADVERTENCIA] No hay ningun automata activo.")
        return
    if reg.tipo != "AFND":
        print(f"[ADVERTENCIA] El automata activo es de tipo {reg.tipo}. La conversion requiere un AFND.")
        return

    try:
        afd_gen, equiv = convertidor_afnd.convertir(reg.instancia)
        reg_afd = gestor.registrar(afd_gen, "AFD", f"Conversion de {reg.id}", padre_id=reg.id, equivalencias=equiv)
        print(f"\n[OK] Conversion exitosa mediante Construccion de Subconjuntos.")
        print(f"Se genero el AFD equivalente '{afd_gen.nombre}' y quedo activo con ID: {reg_afd.id}")
        
        # Retroalimentacion: mostrar inmediatamente definicion formal y tabla del AFD generado
        print("\n--- DEFINICION FORMAL DEL AFD GENERADO ---")
        afd_gen.mostrarDefinicion()
        afd_gen.mostrarTablaTransiciones()
    except Exception as e:
        print(f"[ERROR durante la conversion]: {e}")


def mostrarEquivalencias():
    reg = gestor.obtener_activo()
    if not reg or not reg.equivalencias:
        print("[ADVERTENCIA] El automata activo no posee una tabla de equivalencias de subconjuntos.")
        return

    print("\n" + "=" * 52)
    print(f"TABLA DE EQUIVALENCIAS DE MACROESTADOS - {reg.nombre}")
    print("=" * 52)
    print(f"{'Macroestado AFD':<18} | {'Conjunto de Estados AFND':<25}")
    print("-" * 52)
    for macro, conj_str, es_fin in reg.equivalencias:
        marca = "*" if es_fin else " "
        print(f"  {marca} {macro:<14} | {conj_str:<25}")
    print("-" * 52)
    print("Leyenda: * Contiene al menos un estado final del AFND\n")


def simularCadenaIndividual():
    reg = gestor.obtener_activo()
    if not reg:
        print("[ADVERTENCIA] No hay automata activo.")
        return

    cadena = input("Ingrese la cadena a evaluar (presione Enter o 'eps' para vacia): ")
    auto = reg.instancia
    if reg.tipo == "AFD":
        auto.validarCadena(cadena, mostrarTraza=True)
    else:
        auto.evaluar_cadena(cadena, mostrar_traza=True)


def evaluarLote():
    reg = gestor.obtener_activo()
    if not reg:
        print("[ADVERTENCIA] No hay automata activo.")
        return

    ruta = input("Ingrese la ruta del archivo de cadenas (.txt): ").strip()
    if not os.path.exists(ruta):
        print(f"[ERROR] El archivo '{ruta}' no existe.")
        return

    # Retroalimentacion del docente: ofrecer trazas completas por lote
    resp_traza = input("¿Desea mostrar las trazas paso a paso de cada cadena del lote? (s/n): ").strip().lower()
    mostrar_trazas = (resp_traza == "s")

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            cadenas = [linea.strip() for linea in f if linea.strip() and not linea.startswith("#")]
    except OSError as err:
        print(f"[ERROR al leer archivo]: {err}")
        return

    auto = reg.instancia
    print(f"\n{'=' * 65}")
    print(f"EVALUACION DE CADENAS POR LOTE - {reg.tipo}: {auto.nombre}")
    print(f"{'=' * 65}")

    aceptadas = 0
    total = len(cadenas)
    resultados = []

    for idx, cad in enumerate(cadenas, 1):
        if mostrar_trazas:
            print(f"\n--- Evaluando Cadena {idx}/{total}: '{cad}' ---")

        if reg.tipo == "AFD":
            res = auto.validarCadena(cad, mostrarTraza=mostrar_trazas)
            estado_res = "Aceptada" if res else "Rechazada"
        else:
            res = auto.evaluar_cadena(cad, mostrar_traza=mostrar_trazas)
            if res is True:
                estado_res = "Aceptada"
            elif res is False:
                estado_res = "Rechazada"
            else:
                estado_res = "Detenida"

        if res is True:
            aceptadas += 1
        resultados.append((idx, cad, estado_res))

    print(f"\n{'-' * 65}")
    print(f"{'No.':<6} | {'Cadena':<30} | {'Resultado':<15}")
    print(f"{'-' * 65}")
    for idx, cad, estado_res in resultados:
        print(f"{idx:<6} | {cad:<30} | {estado_res:<15}")
    print(f"{'-' * 65}")
    pct = (aceptadas / total * 100) if total > 0 else 0
    print(f"Resumen: {aceptadas}/{total} cadenas aceptadas ({pct:.1f}%)\n")


def consultarHistorial():
    reg = gestor.obtener_activo()
    if not reg:
        print("[ADVERTENCIA] No hay automata activo.")
        return

    auto = reg.instancia
    print(f"\n--- HISTORIAL DE EVALUACIONES: {reg.id} ({reg.nombre}) ---")
    if not auto.historial:
        print("  No hay registros de evaluaciones previas.")
        return

    for idx, reg_eval in enumerate(auto.historial, 1):
        cad = reg_eval.get("cadena", "")
        res = reg_eval.get("resultado", "")
        fin = reg_eval.get("estado_final", "-")
        rama = f" | Rama: {reg_eval['rama_aceptante']}" if "rama_aceptante" in reg_eval else ""
        print(f"  {idx}. Cadena: \"{cad}\" -> {res} | Estado Final: {fin}{rama}")


def ejecutarAnalisisEstructural():
    reg = gestor.obtener_activo()
    if not reg:
        print("[ADVERTENCIA] No hay automata activo.")
        return

    auto = reg.instancia
    if hasattr(auto, "analisisEstructural"):
        auto.analisisEstructural()
    elif hasattr(auto, "analisis_estructural"):
        auto.analisis_estructural()
    else:
        print(f"[INFO] El analisis topologico de accesibilidad aplica para modelos finitos (AFD/AFND).")


def mostrarMenu():
    reg = gestor.obtener_activo()
    info_activo = f"[{reg.id} - {reg.tipo} - {reg.nombre}]" if reg else "[NINGUNO]"
    print("\n" + "=" * 68)
    print(f"   SISTEMA DE AUTOMATAS FINITOS Y DE PILA (FASES 1, 2 Y 3)")
    print(f"   Automata Activo: {info_activo}")
    print("=" * 68)
    print("  1. Cargar automata desde archivo plano (.txt)")
    print("  2. Crear un AFD manualmente")
    print("  3. Crear un AFND manualmente")
    print("  4. Crear un Autómata de Pila (APD o APND) manualmente")
    print("  5. Listar o cambiar automata activo en memoria")
    print("  6. Mostrar definicion formal (séptupla / quíntupla) y tabla")
    print("  7. Validar estructura del automata activo")
    print("  8. Convertir AFND a AFD equivalente (Construccion Subconjuntos)")
    print("  9. Mostrar tabla de equivalencias de macroestados")
    print(" 10. Evaluar una cadena individual con traza paso a paso")
    print(" 11. Evaluar un archivo de cadenas por lote (.txt)")
    print(" 12. Consultar historial de evaluaciones del automata activo")
    print(" 13. Realizar analisis estructural (accesibilidad y lenguaje vacio)")
    print(" 14. Salir")
    print("=" * 68)


def iniciar():
    while True:
        mostrarMenu()
        opcion = input("Seleccione una opcion (1-14): ").strip()
        if opcion == "1":
            cargarArchivo()
        elif opcion == "2":
            crearAFDManual()
        elif opcion == "3":
            crearAFNDManual()
        elif opcion == "4":
            crearPilaManual()
        elif opcion == "5":
            listarYSeleccionar()
        elif opcion == "6":
            mostrarDefinicionYTabla()
        elif opcion == "7":
            validarEstructuraActivo()
        elif opcion == "8":
            convertirAFNDaAFD()
        elif opcion == "9":
            mostrarEquivalencias()
        elif opcion == "10":
            simularCadenaIndividual()
        elif opcion == "11":
            evaluarLote()
        elif opcion == "12":
            consultarHistorial()
        elif opcion == "13":
            ejecutarAnalisisEstructural()
        elif opcion == "14":
            print("\nFinalizando ejecucion del programa.")
            break
        else:
            print("[ERROR] Opcion no valida. Ingrese un numero del 1 al 14.")