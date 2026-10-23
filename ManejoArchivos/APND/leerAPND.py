import os
import re

from APND.APND import APND
from GestionAutomatas.ResultadoCarga import ResultadoCarga


RE_CAMPO = re.compile(r"^([A-Z_]+)\s*=\s*(.*)$", re.IGNORECASE)
RE_TRANSICION = re.compile(r"^\s*([^,;|\s]+)\s*,\s*([^,;|\s]+)\s*,\s*([^,;|\s]+)\s*,\s*(.+?)\s*$")
RE_SIMBOLO = re.compile(r"^[^,;|\s]+$")
RE_REEMPLAZO = re.compile(r"^[^,|\s]+$")
REQUERIDOS = {"NOMBRE", "TIPO", "ESTADOS", "ALFABETO", "ALFABETO_PILA", "INICIAL", "INICIAL_PILA", "FINALES"}


def _lista(valor):
    return [item.strip() for item in valor.split(",") if item.strip()]


def _leer_alternativas(texto, numero, resultado):
    alternativas = []
    for alternativa in texto.split("|"):
        partes = [parte.strip() for parte in alternativa.split(",")]
        if len(partes) != 2 or not all(partes):
            resultado.errores.append(f"Línea {numero}: cada alternativa debe tener destino y reemplazo.")
            return None
        destino, reemplazo = partes
        if not RE_SIMBOLO.fullmatch(destino) or not RE_REEMPLAZO.fullmatch(reemplazo):
            resultado.errores.append(f"Línea {numero}: alternativa inválida -> '{alternativa}'.")
            return None
        reemplazo_simbolos = () if reemplazo == APND.EPS else tuple(reemplazo.split(";"))
        if APND.EPS in reemplazo_simbolos or not reemplazo_simbolos and reemplazo != APND.EPS:
            resultado.errores.append(f"Línea {numero}: EPS debe aparecer solo como reemplazo completo.")
            return None
        alternativas.append((destino, reemplazo_simbolos))
    return alternativas


def cargarAPNDDesdeArchivo(ruta_archivo):
    resultado = ResultadoCarga()
    if not os.path.exists(ruta_archivo):
        resultado.errores.append(f"El archivo '{ruta_archivo}' no existe.")
        return resultado
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()
    except OSError as error:
        resultado.errores.append(f"No se pudo leer el archivo: {error}")
        return resultado

    campos, transiciones, en_transiciones = {}, [], False
    encabezado_transiciones = False
    for numero, linea in enumerate(lineas, 1):
        limpia = linea.strip()
        if not limpia or limpia.startswith("#"):
            continue
        if limpia.upper() == "TRANSICIONES:":
            if encabezado_transiciones:
                resultado.errores.append(f"Línea {numero}: encabezado 'TRANSICIONES:' repetido.")
            encabezado_transiciones = True
            en_transiciones = True
            continue
        if not en_transiciones:
            coincidencia = RE_CAMPO.match(limpia)
            if not coincidencia:
                resultado.errores.append(f"Línea {numero}: sintaxis no reconocida -> '{limpia}'")
                continue
            clave, valor = coincidencia.group(1).upper(), coincidencia.group(2).strip()
            if clave not in REQUERIDOS:
                resultado.errores.append(f"Línea {numero}: campo no reconocido '{clave}'.")
            elif clave in campos:
                resultado.errores.append(f"Línea {numero}: campo '{clave}' repetido.")
            else:
                campos[clave] = valor
            continue

        coincidencia = RE_TRANSICION.match(limpia)
        if not coincidencia:
            resultado.errores.append(f"Línea {numero}: transición inválida -> '{limpia}'")
            continue
        origen, entrada, tope, texto_alternativas = coincidencia.groups()
        alternativas = _leer_alternativas(texto_alternativas, numero, resultado)
        if alternativas is None:
            continue
        for destino, reemplazo in alternativas:
            transiciones.append((origen, entrada, tope, destino, reemplazo, numero))

    if not encabezado_transiciones:
        resultado.errores.append("Falta el encabezado obligatorio 'TRANSICIONES:'.")
    faltantes = REQUERIDOS - set(campos)
    if faltantes:
        resultado.errores.append("Campos requeridos ausentes: " + ", ".join(sorted(faltantes)) + ".")
        return resultado
    if campos["TIPO"].upper() != "APND":
        resultado.errores.append("TIPO debe ser APND.")

    estados, alfabeto = _lista(campos["ESTADOS"]), _lista(campos["ALFABETO"])
    gamma, finales = _lista(campos["ALFABETO_PILA"]), _lista(campos["FINALES"])
    if not estados or not alfabeto or not gamma:
        resultado.errores.append("ESTADOS, ALFABETO y ALFABETO_PILA deben ser no vacíos.")
    if len(estados) != len(set(estados)) or len(alfabeto) != len(set(alfabeto)) or len(gamma) != len(set(gamma)):
        resultado.errores.append("Los estados y alfabetos no pueden tener duplicados.")
    if APND.EPS in alfabeto or APND.EPS in gamma:
        resultado.errores.append("EPS no puede declararse en ALFABETO ni ALFABETO_PILA.")
    if campos["INICIAL"] not in estados:
        resultado.errores.append("INICIAL debe pertenecer a ESTADOS.")
    if campos["INICIAL_PILA"] not in gamma:
        resultado.errores.append("INICIAL_PILA debe pertenecer a ALFABETO_PILA.")
    for final in finales:
        if final not in estados:
            resultado.errores.append(f"El estado final '{final}' no pertenece a ESTADOS.")
    for origen, entrada, tope, destino, reemplazo, numero in transiciones:
        if origen not in estados or destino not in estados:
            resultado.errores.append(f"Línea {numero}: origen o destino no declarado.")
        if entrada != APND.EPS and entrada not in alfabeto:
            resultado.errores.append(f"Línea {numero}: entrada '{entrada}' fuera de ALFABETO.")
        if tope not in gamma or any(simbolo not in gamma for simbolo in reemplazo):
            resultado.errores.append(f"Línea {numero}: tope o reemplazo fuera de ALFABETO_PILA.")
    if resultado.errores:
        return resultado

    apnd = APND(campos["NOMBRE"], "APND")
    apnd.definir_alfabeto(alfabeto)
    apnd.definir_alfabeto_pila(gamma)
    apnd.definir_simbolo_inicial_pila(campos["INICIAL_PILA"])
    for estado in estados:
        apnd.agregar_estado(estado, estado == campos["INICIAL"], estado in finales)
    for origen, entrada, tope, destino, reemplazo, _ in transiciones:
        apnd.agregar_transicion(origen, entrada, tope, destino, reemplazo)
    valido, errores = apnd.validar_estructura()
    if not valido:
        resultado.errores.extend(errores)
        return resultado
    resultado.instancia = apnd
    return resultado
