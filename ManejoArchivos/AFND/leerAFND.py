import os
import re

from AFND.AFND import AFND
from GestionAutomatas.ResultadoCarga import ResultadoCarga

RE_NOMBRE = re.compile(r'^(?:NOMBRE-AFND|NOMBRE\s+AFND|NOMBRE)\s*(?:[:=]\s*|\s+)(.+)$', re.IGNORECASE)
RE_TIPO = re.compile(r'^TIPO\s*[:=-]\s*AFND$', re.IGNORECASE)
RE_ESTADOS = re.compile(r'^ESTADOS\s*[:=]\s*([a-zA-Z0-9_,\s]+)$', re.IGNORECASE)
RE_ALFABETO = re.compile(r'^ALFABETO-?\s*[:=]\s*([^:=]+)$', re.IGNORECASE)
RE_INICIAL = re.compile(r'^INICIAL\s*[:=]\s*([a-zA-Z0-9_]+)$', re.IGNORECASE)
RE_FINALES = re.compile(r'^FINALES\s*[:=]\s*([a-zA-Z0-9_,\s]*)$', re.IGNORECASE)
RE_SECCION_TRANSICIONES = re.compile(r'^TRANSICIONES\s*:$', re.IGNORECASE)
RE_TRANSICION = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*,\s*([^,\s]+)\s*,\s*(.*)$')


def cargarAFNDDesdeArchivo(ruta_archivo):
    """Parsea y valida un AFND sin efectos de consola."""
    resultado = ResultadoCarga()
    if not os.path.exists(ruta_archivo):
        resultado.errores.append(f"El archivo '{ruta_archivo}' no existe.")
        return resultado
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            lineas = archivo.readlines()
    except OSError as error:
        resultado.errores.append(f"No se pudo leer el archivo: {error}")
        return resultado

    nombre, estados, alfabeto, inicial, finales = "AFND_Cargado", [], [], None, []
    transiciones, en_transiciones = [], False
    for numero, linea in enumerate(lineas, 1):
        limpia = linea.strip()
        if not limpia or limpia.startswith('#'):
            continue
        if not en_transiciones:
            if (match := RE_NOMBRE.match(limpia)):
                nombre = match.group(1).strip()
            elif RE_TIPO.match(limpia):
                pass
            elif limpia.upper().startswith('TIPO'):
                resultado.errores.append(f"Linea {numero}: TIPO debe ser AFND.")
            elif (match := RE_ESTADOS.match(limpia)):
                estados = [valor.strip() for valor in match.group(1).split(',') if valor.strip()]
            elif (match := RE_ALFABETO.match(limpia)):
                alfabeto = [valor.strip() for valor in match.group(1).split(',') if valor.strip()]
            elif (match := RE_INICIAL.match(limpia)):
                inicial = match.group(1).strip()
            elif (match := RE_FINALES.match(limpia)):
                finales = [valor.strip() for valor in match.group(1).split(',') if valor.strip()]
            elif RE_SECCION_TRANSICIONES.match(limpia):
                en_transiciones = True
            else:
                resultado.errores.append(f"Linea {numero}: sintaxis no reconocida -> '{limpia}'")
        elif (match := RE_TRANSICION.match(limpia)):
            origen, simbolo, destinos_raw = match.group(1), match.group(2), match.group(3).strip()
            if simbolo in {'ε', 'lambda', 'eps', 'E'}:
                resultado.errores.append(f"Linea {numero}: transicion epsilon fuera del alcance del AFND.")
            destinos = [] if destinos_raw in {'O', 'Ø', 'vacio', ''} else destinos_raw.split()
            transiciones.append((origen, simbolo, destinos, numero))
        else:
            resultado.errores.append(f"Linea {numero}: formato de transicion invalido -> '{limpia}'")

    if not estados:
        resultado.errores.append("ESTADOS no fue definido o esta vacio.")
    if not alfabeto:
        resultado.errores.append("ALFABETO no fue definido o esta vacio.")
    if inicial not in estados:
        resultado.errores.append("El estado INICIAL debe pertenecer a ESTADOS.")
    for final in finales:
        if final not in estados:
            resultado.errores.append(f"El estado final '{final}' no pertenece a ESTADOS.")
    for origen, simbolo, destinos, numero in transiciones:
        if origen not in estados:
            resultado.errores.append(f"Linea {numero}: estado origen '{origen}' no declarado.")
        if simbolo not in alfabeto:
            resultado.errores.append(f"Linea {numero}: simbolo '{simbolo}' no pertenece a ALFABETO.")
        for destino in destinos:
            if destino not in estados:
                resultado.errores.append(f"Linea {numero}: estado destino '{destino}' no declarado.")
    if resultado.errores:
        return resultado

    afnd = AFND(nombre)
    afnd.definir_alfabeto(alfabeto)
    for estado in estados:
        afnd.agregar_nodo(estado, es_final=estado in finales, es_inicial=estado == inicial)
    for origen, simbolo, destinos, _ in transiciones:
        for destino in destinos:
            afnd.agregar_transicion(origen, simbolo, destino)
    resultado.instancia = afnd
    return resultado
