import os
from AFD.AFD import AFD

# Funcion para evaluar un lote de cadenas desde un archivo de texto
def evaluarArchivoCadenas(afd, rutaArchivo):
    if not os.path.exists(rutaArchivo):
        print(f"[ERROR] El archivo '{rutaArchivo}' no existe.")
        return

    try:
        with open(rutaArchivo, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
    except Exception as e:
        print(f"[ERROR] No se pudo leer el archivo de cadenas: {e}")
        return

    print("\n" + "=" * 60)
    print(f"EVALUACION DE CADENAS POR LOTE - AFD: {afd.nombre}")
    print("=" * 60)
    print(f"{'No.':<5} | {'Cadena':<25} | {'Resultado':<20}")
    print("-" * 60)

    total = 0
    aceptadas = 0

    for idx, linea in enumerate(lineas, 1):
        cadena = linea.strip()
        if linea.startswith("#"):
            continue
        total += 1
        resultado = afd.validarCadena(cadena, mostrarTraza=False)
        if resultado:
            aceptadas += 1
            resTexto = "Aceptada"
        else:
            resTexto = "Rechazada"

        cadenaMostrar = cadena if cadena != "" else "epsilon"
        print(f"{idx:<5} | {cadenaMostrar:<25} | {resTexto:<20}")

    print("-" * 60)
    porcentaje = (aceptadas / total * 100) if total > 0 else 0
    print(f"Resumen: {aceptadas}/{total} cadenas aceptadas ({porcentaje:.1f}%)\n")