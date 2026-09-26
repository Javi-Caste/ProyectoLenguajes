import os

# Funcion para evaluar un lote de cadenas en el AFND desde un archivo de texto
def evaluarArchivoCadenasAFND(afnd, ruta_archivo):
    if not os.path.exists(ruta_archivo):
        print(f"[ERROR] El archivo '{ruta_archivo}' no existe.")
        return

    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
    except Exception as e:
        print(f"[ERROR] No se pudo leer el archivo de cadenas: {e}")
        return

    print("\n" + "=" * 60)
    print(f"EVALUACION DE CADENAS POR LOTE - AFND: {afnd.nombre}")
    print("=" * 60)
    print(f"{'No.':<5} | {'Cadena':<25} | {'Resultado':<20}")
    print("-" * 60)

    total = 0
    aceptadas = 0

    for idx, linea in enumerate(lineas, 1):
        cadena = linea.strip()
        if cadena.startswith("#"):
            continue
        total += 1
        resultado = afnd.evaluar_cadena(cadena, mostrar_traza=False)
        if resultado:
            aceptadas += 1
            res_texto = "Aceptada"
        else:
            res_texto = "Rechazada"

        cad_display = cadena if cadena != "" else "epsilon"
        print(f"{idx:<5} | {cad_display:<25} | {res_texto:<20}")

    print("-" * 60)
    porcentaje = (aceptadas / total * 100) if total > 0 else 0
    print(f"Resumen: {aceptadas}/{total} cadenas aceptadas ({porcentaje:.1f}%)\n")