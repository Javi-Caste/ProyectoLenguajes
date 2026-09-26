import re
import os
from AFND.AFND import AFND

# Patrones Regex para el analisis sintactico del archivo AFND
RE_NOMBRE = re.compile(r'^(?:NOMBRE-AFND|NOMBRE\s+AFND|NOMBRE)\s*[:=]?\s*(.+)$', re.IGNORECASE)
RE_TIPO = re.compile(r'^TIPO\s*[:=-]\s*([a-zA-Z0-9]+)$', re.IGNORECASE)
RE_ESTADOS = re.compile(r'^ESTADOS\s*[:=]\s*([a-zA-Z0-9_,\s]+)$', re.IGNORECASE)
RE_ALFABETO = re.compile(r'^ALFABETO-?\s*[:=]\s*([^:=]+)$', re.IGNORECASE)
RE_INICIAL = re.compile(r'^INICIAL\s*[:=]\s*([a-zA-Z0-9_]+)$', re.IGNORECASE)
RE_FINALES = re.compile(r'^FINALES\s*[:=]\s*([a-zA-Z0-9_,\s]*)$', re.IGNORECASE)
RE_SECCION_TRANSICIONES = re.compile(r'^TRANSICIONES\s*:', re.IGNORECASE)
RE_TRANSICION = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*,\s*([^,\s]+)\s*,\s*(.*)$')

# Funcion para cargar y parsear un AFND desde un archivo .txt
def cargarAFNDDesdeArchivo(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        print(f"[ERROR] El archivo '{ruta_archivo}' no existe.")
        return None

    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
    except Exception as e:
        print(f"[ERROR] No se pudo leer el archivo: {e}")
        return None

    nombre = "AFND_Cargado"
    estados_lista = []
    alfabeto_lista = []
    inicial_str = None
    finales_lista = []
    transiciones_lista = []
    en_seccion_transiciones = False

    for num_linea, linea in enumerate(lineas, 1):
        linea_limpia = linea.strip()
        if not linea_limpia or linea_limpia.startswith("#"):
            continue

        if not en_seccion_transiciones:
            m_nom = RE_NOMBRE.match(linea_limpia)
            m_tipo = RE_TIPO.match(linea_limpia)
            m_est = RE_ESTADOS.match(linea_limpia)
            m_alf = RE_ALFABETO.match(linea_limpia)
            m_ini = RE_INICIAL.match(linea_limpia)
            m_fin = RE_FINALES.match(linea_limpia)

            if m_nom:
                nombre = m_nom.group(1).strip()
            elif m_tipo:
                pass  # Verificacion informativa del tipo
            elif m_est:
                estados_lista = [e.strip() for e in m_est.group(1).split(",") if e.strip()]
            elif m_alf:
                alfabeto_lista = [s.strip() for s in m_alf.group(1).split(",") if s.strip()]
            elif m_ini:
                inicial_str = m_ini.group(1).strip()
            elif m_fin:
                finales_lista = [f.strip() for f in m_fin.group(1).split(",") if f.strip()]
            elif RE_SECCION_TRANSICIONES.match(linea_limpia):
                en_seccion_transiciones = True
            else:
                print(f"[ADVERTENCIA] Linea {num_linea}: Sintaxis no reconocida -> '{linea_limpia}'")
        else:
            m_trans = RE_TRANSICION.match(linea_limpia)
            if m_trans:
                q_origen = m_trans.group(1).strip()
                simbolo = m_trans.group(2).strip()
                destinos_raw = m_trans.group(3).strip()

                # Deteccion de transiciones epsilon fuera de alcance
                if simbolo in ["ε", "lambda", "eps", "E"]:
                    print(f"[ADVERTENCIA] Linea {num_linea}: Transicion epsilon detectada. Fuera del alcance solicitado.")
                    continue

                # Procesamiento de destinos multiples o vacios (O)
                if destinos_raw in ["O", "Ø", "vacio", ""]:
                    destinos = []
                else:
                    destinos = [d.strip() for d in destinos_raw.split() if d.strip()]

                transiciones_lista.append((q_origen, simbolo, destinos, num_linea))
            else:
                print(f"[ADVERTENCIA] Linea {num_linea}: Formato de transicion invalido -> '{linea_limpia}'")

    # Creacion del objeto AFND
    nuevo_afnd = AFND(nombre)
    nuevo_afnd.definir_alfabeto(alfabeto_lista)

    for est in estados_lista:
        es_ini = (est == inicial_str)
        es_fin = (est in finales_lista)
        nuevo_afnd.agregar_nodo(est, es_final=es_fin, es_inicial=es_ini)

    # Insercion y validacion de transiciones
    for q_orig, sim, lista_destinos, n_linea in transiciones_lista:
        if q_orig not in nuevo_afnd.nodos:
            print(f"[ERROR] Linea {n_linea}: Estado origen '{q_orig}' no declarado en ESTADOS.")
            continue
        if sim not in nuevo_afnd.alfabeto:
            print(f"[ERROR] Linea {n_linea}: Simbolo '{sim}' no pertenece a ALFABETO.")
            continue
        for dest in lista_destinos:
            if dest not in nuevo_afnd.nodos:
                print(f"[ERROR] Linea {n_linea}: Estado destino '{dest}' no declarado en ESTADOS.")
                continue
            nuevo_afnd.agregar_transicion(q_orig, sim, dest)

    print(f"[OK] Archivo cargado correctamente. AFND '{nombre}' instanciado.")
    return nuevo_afnd