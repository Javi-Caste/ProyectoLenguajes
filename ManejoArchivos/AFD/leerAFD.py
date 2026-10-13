import os
import re

from AFD.AFD import AFD
from GestionAutomatas.ResultadoCarga import ResultadoCarga

RE_NOMBRE = re.compile(r'^(?:NOMBRE-AFD|NOMBRE)\s*(?:[:=]\s*|\s+)(.+)$', re.IGNORECASE)
RE_ESTADOS = re.compile(r'^ESTADOS\s*[:=]\s*([a-zA-Z0-9_,\s]+)$', re.IGNORECASE)
RE_ALFABETO = re.compile(r'^ALFABETO-?\s*[:=]\s*([^:=]+)$', re.IGNORECASE)
RE_INICIAL = re.compile(r'^INICIAL\s*[:=]\s*([a-zA-Z0-9_]+)$', re.IGNORECASE)
RE_FINALES = re.compile(r'^FINALES\s*[:=]\s*([a-zA-Z0-9_,\s]*)$', re.IGNORECASE)
RE_SECCION_TRANSICIONES = re.compile(r'^TRANSICIONES\s*:$', re.IGNORECASE)
RE_TRANSICION = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*,\s*([^,\s]+)\s*,\s*([a-zA-Z0-9_]+)\s*$')


# Parsea y valida un AFD. No imprime ni acepta definiciones con errores.
def cargarAFDDesdeArchivo(rutaArchivo):
    resultado = ResultadoCarga()
    if not os.path.exists(rutaArchivo):
        resultado.errores.append(f"El archivo '{rutaArchivo}' no existe.")
        return resultado
    try:
        with open(rutaArchivo, 'r', encoding='utf-8') as archivo:
            lineas = archivo.readlines()
    except OSError as error:
        resultado.errores.append(f"No se pudo leer el archivo: {error}")
        return resultado

    nombre, estados, alfabeto, inicial, finales = "AFD_Cargado", [], [], None, []
    transiciones, en_transiciones = [], False
    for numero, linea in enumerate(lineas, 1):
        limpia = linea.strip()
        if not limpia or limpia.startswith('#'):
            continue
        if not en_transiciones:
            if (match := RE_NOMBRE.match(limpia)):
                nombre = match.group(1).strip()
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
            transiciones.append((match.group(1), match.group(2), match.group(3), numero))
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
    vistos = set()
    for origen, simbolo, destino, numero in transiciones:
        if origen not in estados or destino not in estados:
            resultado.errores.append(f"Linea {numero}: estados '{origen}' o '{destino}' no declarados.")
        if simbolo not in alfabeto:
            resultado.errores.append(f"Linea {numero}: simbolo '{simbolo}' no pertenece a ALFABETO.")
        clave = (origen, simbolo)
        if clave in vistos:
            resultado.errores.append(f"Linea {numero}: no determinismo en delta({origen}, {simbolo}).")
        vistos.add(clave)
    if resultado.errores:
        return resultado

    afd = AFD(nombre)
    afd.definirAlfabeto(alfabeto)
    for estado in estados:
        afd.agregarEstado(estado, esInicial=estado == inicial, esFinal=estado in finales)
    for origen, simbolo, destino, _ in transiciones:
        afd.agregarTransicion(origen, simbolo, destino)
    _, errores, faltantes = afd.validarEstructura()
    resultado.advertencias.extend(errores)
    if faltantes:
        resultado.advertencias.append(f"AFD incompleto: {len(faltantes)} transiciones faltantes.")
    resultado.instancia = afd
    return resultado
