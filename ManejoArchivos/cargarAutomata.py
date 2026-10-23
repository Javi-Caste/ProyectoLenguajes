import os
import re

from AFD.AFD import AFD
from AFND.AFND import AFND, es_simbolo_epsilon
from APD.APD import APD
from APND.APND import APND
from GestionAutomatas.ResultadoCarga import ResultadoCarga


TIPOS_VALIDOS = {"AFD", "AFND", "APD", "APND"}
CAMPOS_FINITOS = {"NOMBRE", "TIPO", "ESTADOS", "ALFABETO", "INICIAL", "FINALES"}
CAMPOS_PILA = CAMPOS_FINITOS | {"ALFABETO_PILA", "INICIAL_PILA"}
RE_CAMPO = re.compile(r"^([A-Z_]+)\s*(?:=|:)\s*(.*)$", re.IGNORECASE)
RE_TRANSICION_FINITA = re.compile(r"^\s*([^,\s]+)\s*,\s*([^,\s]+)\s*,\s*(.*?)\s*$")
RE_TRANSICION_APD = re.compile(r"^\s*([^,;|\s]+)\s*,\s*([^,;|\s]+)\s*,\s*([^,;|\s]+)\s*,\s*([^,;|\s]+)\s*,\s*([^,|\s]+)\s*$")
RE_TRANSICION_APND = re.compile(r"^\s*([^,;|\s]+)\s*,\s*([^,;|\s]+)\s*,\s*([^,;|\s]+)\s*,\s*(.+?)\s*$")
RE_SIMBOLO = re.compile(r"^[^,;|\s]+$")
RE_REEMPLAZO = re.compile(r"^[^,|\s]+$")


def _lista(valor):
    return [item.strip() for item in valor.split(",") if item.strip()]


def _leer_archivo(ruta_archivo, resultado):
    if not os.path.exists(ruta_archivo):
        resultado.errores.append(f"El archivo '{ruta_archivo}' no existe.")
        return None
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            return archivo.readlines()
    except OSError as error:
        resultado.errores.append(f"No se pudo leer el archivo: {error}")
        return None


def _leer_campos_y_transiciones(lineas, resultado):
    campos, transiciones = {}, []
    en_transiciones = encabezado_transiciones = False
    for numero, linea in enumerate(lineas, 1):
        limpia = linea.strip()
        if not limpia or limpia.startswith("#"):
            continue
        if limpia.upper() == "TRANSICIONES:":
            if encabezado_transiciones:
                resultado.errores.append(f"Linea {numero}: encabezado 'TRANSICIONES:' repetido.")
            encabezado_transiciones = True
            en_transiciones = True
            continue
        if en_transiciones:
            transiciones.append((numero, limpia))
            continue
        coincidencia = RE_CAMPO.match(limpia)
        if not coincidencia:
            resultado.errores.append(f"Linea {numero}: sintaxis no reconocida -> '{limpia}'")
            continue
        clave, valor = coincidencia.group(1).upper(), coincidencia.group(2).strip()
        if clave in campos:
            resultado.errores.append(f"Linea {numero}: campo '{clave}' repetido.")
        else:
            campos[clave] = valor
    if not encabezado_transiciones:
        resultado.errores.append("Falta el encabezado obligatorio 'TRANSICIONES:'.")
    return campos, transiciones


def _validar_campos(campos, resultado):
    tipo = campos.get("TIPO", "").upper()
    if tipo not in TIPOS_VALIDOS:
        resultado.errores.append("TIPO debe ser AFD, AFND, APD o APND.")
        return None
    resultado.tipo = tipo
    permitidos = CAMPOS_PILA if tipo in {"APD", "APND"} else CAMPOS_FINITOS
    faltantes = permitidos - set(campos)
    if faltantes:
        resultado.errores.append("Campos requeridos ausentes: " + ", ".join(sorted(faltantes)) + ".")
    for campo in sorted(set(campos) - permitidos):
        resultado.errores.append(f"Campo no permitido para {tipo}: '{campo}'.")
    return tipo


def _datos_comunes(campos, tipo, resultado):
    estados, alfabeto = _lista(campos["ESTADOS"]), _lista(campos["ALFABETO"])
    finales = _lista(campos["FINALES"])
    if not estados or not alfabeto:
        resultado.errores.append("ESTADOS y ALFABETO deben ser no vacios.")
    if len(estados) != len(set(estados)) or len(alfabeto) != len(set(alfabeto)):
        resultado.errores.append("ESTADOS y ALFABETO no pueden tener duplicados.")
    if campos["INICIAL"] not in estados:
        resultado.errores.append("INICIAL debe pertenecer a ESTADOS.")
    for final in finales:
        if final not in estados:
            resultado.errores.append(f"El estado final '{final}' no pertenece a ESTADOS.")
    if tipo == "AFND":
        for simbolo in alfabeto:
            if es_simbolo_epsilon(simbolo):
                resultado.errores.append(f"El simbolo '{simbolo}' no puede pertenecer al ALFABETO de un AFND.")
    datos = {"nombre": campos["NOMBRE"], "estados": estados, "alfabeto": alfabeto,
             "inicial": campos["INICIAL"], "finales": finales}
    if tipo in {"APD", "APND"}:
        gamma = _lista(campos["ALFABETO_PILA"])
        if not gamma:
            resultado.errores.append("ALFABETO_PILA debe ser no vacio.")
        if len(gamma) != len(set(gamma)):
            resultado.errores.append("ALFABETO_PILA no puede tener duplicados.")
        if APD.EPS in alfabeto or APD.EPS in gamma:
            resultado.errores.append("EPS no puede declararse en ALFABETO ni ALFABETO_PILA.")
        if campos["INICIAL_PILA"] not in gamma:
            resultado.errores.append("INICIAL_PILA debe pertenecer a ALFABETO_PILA.")
        datos.update({"gamma": gamma, "inicial_pila": campos["INICIAL_PILA"]})
    return datos


def _transiciones_finitas(lineas, tipo, datos, resultado):
    transiciones, vistos = [], set()
    for numero, texto in lineas:
        coincidencia = RE_TRANSICION_FINITA.match(texto)
        if not coincidencia:
            resultado.errores.append(f"Linea {numero}: formato de transicion invalido -> '{texto}'")
            continue
        origen, simbolo, destinos_raw = coincidencia.groups()
        if tipo == "AFD":
            destinos = [destinos_raw] if RE_SIMBOLO.fullmatch(destinos_raw) else []
            if not destinos:
                resultado.errores.append(f"Linea {numero}: un AFD requiere un unico destino valido.")
        else:
            destinos = [] if destinos_raw in {"O", "Ø", "vacio", ""} else destinos_raw.split()
            if es_simbolo_epsilon(simbolo):
                resultado.errores.append(f"Linea {numero}: transicion epsilon fuera del alcance del AFND.")
        if origen not in datos["estados"]:
            resultado.errores.append(f"Linea {numero}: estado origen '{origen}' no declarado.")
        if simbolo not in datos["alfabeto"]:
            resultado.errores.append(f"Linea {numero}: simbolo '{simbolo}' no pertenece a ALFABETO.")
        if tipo == "AFD":
            clave = (origen, simbolo)
            if clave in vistos:
                resultado.errores.append(f"Linea {numero}: no determinismo en delta({origen}, {simbolo}).")
            vistos.add(clave)
        for destino in destinos:
            if destino not in datos["estados"]:
                resultado.errores.append(f"Linea {numero}: estado destino '{destino}' no declarado.")
        transiciones.append((origen, simbolo, destinos))
    return transiciones


def _reemplazo(texto, tipo, numero, resultado):
    eps = APD.EPS if tipo == "APD" else APND.EPS
    reemplazo = () if texto == eps else tuple(texto.split(";"))
    if eps in reemplazo or not reemplazo and texto != eps:
        resultado.errores.append(f"Linea {numero}: EPS debe aparecer solo como reemplazo completo.")
        return None
    return reemplazo


def _transiciones_pila(lineas, tipo, datos, resultado):
    transiciones = []
    for numero, texto in lineas:
        if tipo == "APD":
            if "|" in texto:
                resultado.errores.append(f"Linea {numero}: alternativas '|' no estan permitidas en APD.")
                continue
            coincidencia = RE_TRANSICION_APD.match(texto)
            if not coincidencia:
                resultado.errores.append(f"Linea {numero}: transicion invalida -> '{texto}'")
                continue
            origen, entrada, tope, destino, texto_reemplazo = coincidencia.groups()
            reemplazo = _reemplazo(texto_reemplazo, tipo, numero, resultado)
            alternativas = [] if reemplazo is None else [(destino, reemplazo)]
        else:
            coincidencia = RE_TRANSICION_APND.match(texto)
            if not coincidencia:
                resultado.errores.append(f"Linea {numero}: transicion invalida -> '{texto}'")
                continue
            origen, entrada, tope, texto_alternativas = coincidencia.groups()
            alternativas = []
            for alternativa in texto_alternativas.split("|"):
                partes = [parte.strip() for parte in alternativa.split(",")]
                if len(partes) != 2 or not all(partes) or not RE_SIMBOLO.fullmatch(partes[0]) or not RE_REEMPLAZO.fullmatch(partes[1]):
                    resultado.errores.append(f"Linea {numero}: alternativa invalida -> '{alternativa}'.")
                    alternativas = []
                    break
                reemplazo = _reemplazo(partes[1], tipo, numero, resultado)
                if reemplazo is None:
                    alternativas = []
                    break
                alternativas.append((partes[0], reemplazo))
        for destino, reemplazo in alternativas:
            if origen not in datos["estados"] or destino not in datos["estados"]:
                resultado.errores.append(f"Linea {numero}: origen o destino no declarado.")
            eps = APD.EPS if tipo == "APD" else APND.EPS
            if entrada != eps and entrada not in datos["alfabeto"]:
                resultado.errores.append(f"Linea {numero}: entrada '{entrada}' fuera de ALFABETO.")
            if tope not in datos["gamma"] or any(simbolo not in datos["gamma"] for simbolo in reemplazo):
                resultado.errores.append(f"Linea {numero}: tope o reemplazo fuera de ALFABETO_PILA.")
            transiciones.append((origen, entrada, tope, destino, reemplazo))
    return transiciones


def _construir_finito(tipo, datos, transiciones, resultado):
    automata = AFD(datos["nombre"]) if tipo == "AFD" else AFND(datos["nombre"])
    if tipo == "AFD":
        automata.definirAlfabeto(datos["alfabeto"])
        for estado in datos["estados"]:
            automata.agregarEstado(estado, esInicial=estado == datos["inicial"], esFinal=estado in datos["finales"])
        for origen, simbolo, destinos in transiciones:
            automata.agregarTransicion(origen, simbolo, destinos[0])
        _, errores, faltantes = automata.validarEstructura()
        resultado.advertencias.extend(errores)
        if faltantes:
            resultado.advertencias.append(f"AFD incompleto: {len(faltantes)} transiciones faltantes.")
    else:
        automata.definir_alfabeto(datos["alfabeto"])
        for estado in datos["estados"]:
            automata.agregar_nodo(estado, es_final=estado in datos["finales"], es_inicial=estado == datos["inicial"])
        for origen, simbolo, destinos in transiciones:
            for destino in destinos:
                automata.agregar_transicion(origen, simbolo, destino)
        valido, errores = automata.validar_estructura()
        if not valido:
            resultado.errores.extend(errores)
            return
    resultado.instancia = automata


def _construir_pila(tipo, datos, transiciones, resultado):
    clase = APD if tipo == "APD" else APND
    automata = clase(datos["nombre"], tipo)
    automata.definir_alfabeto(datos["alfabeto"])
    automata.definir_alfabeto_pila(datos["gamma"])
    automata.definir_simbolo_inicial_pila(datos["inicial_pila"])
    for estado in datos["estados"]:
        automata.agregar_estado(estado, estado == datos["inicial"], estado in datos["finales"])
    for origen, entrada, tope, destino, reemplazo in transiciones:
        automata.agregar_transicion(origen, entrada, tope, destino, reemplazo)
    valido, errores = automata.validar_estructura()
    if not valido:
        resultado.errores.extend(errores)
        return
    resultado.instancia = automata


def cargar_automata_desde_archivo(ruta_archivo):
    """Carga AFD, AFND, APD o APND a partir del campo obligatorio TIPO."""
    resultado = ResultadoCarga()
    lineas = _leer_archivo(ruta_archivo, resultado)
    if lineas is None:
        return resultado
    campos, lineas_transicion = _leer_campos_y_transiciones(lineas, resultado)
    tipo = _validar_campos(campos, resultado)
    if tipo is None or resultado.errores:
        return resultado
    datos = _datos_comunes(campos, tipo, resultado)
    transiciones = (_transiciones_finitas(lineas_transicion, tipo, datos, resultado)
                    if tipo in {"AFD", "AFND"}
                    else _transiciones_pila(lineas_transicion, tipo, datos, resultado))
    if resultado.errores:
        return resultado
    if tipo in {"AFD", "AFND"}:
        _construir_finito(tipo, datos, transiciones, resultado)
    else:
        _construir_pila(tipo, datos, transiciones, resultado)
    return resultado
