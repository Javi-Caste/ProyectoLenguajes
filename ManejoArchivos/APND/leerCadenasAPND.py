import os


def evaluarArchivoCadenasAPND(apnd, ruta_archivo, mostrar_traza=False):
    if not os.path.exists(ruta_archivo):
        print(f"[ERROR] El archivo '{ruta_archivo}' no existe.")
        return
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()
    except OSError as error:
        print(f"[ERROR] No se pudo leer el archivo de cadenas: {error}")
        return
    print("\n" + "=" * 65)
    print(f"EVALUACION DE CADENAS POR LOTE - APND: {apnd.nombre}")
    print("=" * 65)
    print(f"{'No.':<5} | {'Cadena':<25} | Resultado")
    print("-" * 65)
    total = aceptadas = 0
    for numero, linea in enumerate(lineas, 1):
        if linea.lstrip().startswith("#"):
            continue
        cadena = linea.strip()
        total += 1
        respuesta = apnd.evaluar_cadena(cadena, mostrar_traza)
        texto = "Aceptada" if respuesta is True else "Rechazada" if respuesta is False else "Detenida/no evaluada"
        aceptadas += respuesta is True
        print(f"{numero:<5} | {cadena or 'epsilon':<25} | {texto}")
    print("-" * 65)
    porcentaje = aceptadas / total * 100 if total else 0
    print(f"Resumen: {aceptadas}/{total} cadenas aceptadas ({porcentaje:.1f}%)\n")
