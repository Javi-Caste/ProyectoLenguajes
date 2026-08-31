import re
import os
from AFD.AFD import AFD

# Patrones con expresiones regulares para la lectura del archivo
RE_NOMBRE = re.compile(r'^(?:NOMBRE-AFD|NOMBRE)\s*[:=]\s*(.+)$', re.IGNORECASE)
RE_ESTADOS = re.compile(r'^ESTADOS\s*[:=]\s*([a-zA-Z0-9_,\s]+)$', re.IGNORECASE)
RE_ALFABETO = re.compile(r'^ALFABETO-?\s*[:=]\s*([^:=]+)$', re.IGNORECASE)
RE_INICIAL = re.compile(r'^INICIAL\s*[:=]\s*([a-zA-Z0-9_]+)$', re.IGNORECASE)
RE_FINALES = re.compile(r'^FINALES\s*[:=]\s*([a-zA-Z0-9_,\s]*)$', re.IGNORECASE)
RE_SECCION_TRANSICIONES = re.compile(r'^TRANSICIONES\s*:', re.IGNORECASE)
RE_TRANSICION = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*,\s*([^,\s]+)\s*,\s*([a-zA-Z0-9_]+)\s*$')

# Funcion para procesar y cargar un AFD desde un archivo de texto
def cargarAFDDesdeArchivo(rutaArchivo):
    if not os.path.exists(rutaArchivo):
        print(f"[ERROR] El archivo '{rutaArchivo}' no existe.")
        return None

    try:
        with open(rutaArchivo, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
    except Exception as e:
        print(f"[ERROR] No se pudo leer el archivo: {e}")
        return None

    nombre = "AFD_Cargado"
    estadosLista = []
    alfabetoLista = []
    inicialStr = None
    finalesLista = []
    transicionesLista = []
    enSeccionTransiciones = False

    for numLinea, linea in enumerate(lineas, 1):
        lineaLimpia = linea.strip()
        if not lineaLimpia or lineaLimpia.startswith("#"):
            continue

        if not enSeccionTransiciones:
            mNom = RE_NOMBRE.match(lineaLimpia)
            mEst = RE_ESTADOS.match(lineaLimpia)
            mAlf = RE_ALFABETO.match(lineaLimpia)
            mIni = RE_INICIAL.match(lineaLimpia)
            mFin = RE_FINALES.match(lineaLimpia)

            if mNom:
                nombre = mNom.group(1).strip()
            elif mEst:
                estadosLista = [e.strip() for e in mEst.group(1).split(",") if e.strip()]
            elif mAlf:
                alfabetoLista = [s.strip() for s in mAlf.group(1).split(",") if s.strip()]
            elif mIni:
                inicialStr = mIni.group(1).strip()
            elif mFin:
                finalesLista = [f.strip() for f in mFin.group(1).split(",") if f.strip()]
            elif RE_SECCION_TRANSICIONES.match(lineaLimpia):
                enSeccionTransiciones = True
            else:
                print(f"[ADVERTENCIA] Linea {numLinea}: Sintaxis no reconocida -> '{lineaLimpia}'")
        else:
            mTrans = RE_TRANSICION.match(lineaLimpia)
            if mTrans:
                qOrigen, simbolo, qDestino = mTrans.group(1), mTrans.group(2), mTrans.group(3)
                transicionesLista.append((qOrigen, simbolo, qDestino, numLinea))
            else:
                print(f"[ADVERTENCIA] Linea {numLinea}: Formato de transicion invalido -> '{lineaLimpia}'")

    # Creacion del objeto AFD
    nuevoAFD = AFD(nombre)
    nuevoAFD.definirAlfabeto(alfabetoLista)

    for est in estadosLista:
        esIni = (est == inicialStr)
        esFin = (est in finalesLista)
        nuevoAFD.agregarEstado(est, esInicial=esIni, esFinal=esFin)

    # Insercion y validacion de transiciones
    for qOrig, sim, qDest, nLinea in transicionesLista:
        if qOrig not in nuevoAFD.nodos or qDest not in nuevoAFD.nodos:
            print(f"[ERROR] Linea {nLinea}: Estados '{qOrig}' o '{qDest}' no declarados en ESTADOS.")
            continue
        if sim not in nuevoAFD.alfabeto:
            print(f"[ERROR] Linea {nLinea}: Simbolo '{sim}' no pertenece al ALFABETO.")
            continue
        try:
            nuevoAFD.agregarTransicion(qOrig, sim, qDest)
        except ValueError as err:
            print(f"[ERROR No-Determinismo] Linea {nLinea}: {err}")

    print(f"[OK] Archivo cargado correctamente. Automata '{nombre}' creado.")
    return nuevoAFD