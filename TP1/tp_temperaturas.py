"""
Trabajo Práctico - Desarrollo de Herramientas de Software
Autor: Agustin Cardetti F
Fecha: Agosto 2025

Descripción:
------------
Este programa procesa un archivo de temperaturas del SMN con formato:

FECHA    TMAX  TMIN  NOMBRE
17082025  14.2  10.0 AEROPARQUE AERO
17082025  15.2   2.3 AZUL AERO
...

Objetivo:
---------
1. Guardar la información en un diccionario de la forma:
   datos[estacion] = {
       "tmax": [lista de Tmax],
       "tmin": [lista de Tmin]
   }

2. Generar un archivo de reporte con:
   - Máxima y mínima registrada en cada estación.
   - Estación con mayor amplitud térmica en un mismo día.
   - Estación con menor amplitud térmica en un mismo día.
   - Máxima diferencia de temperaturas entre estaciones en un mismo día.
   - Mínima diferencia de temperaturas entre estaciones en un mismo día.
"""

from typing import Dict, List, Tuple, Optional


# -----------------------------
# 1) LECTURA DEL ARCHIVO
# -----------------------------
def leer_datos(nombre_archivo: str) -> Dict[str, Dict[str, List[Optional[float]]]]:
    """
    Lee el archivo de temperaturas y devuelve un diccionario con la estructura pedida.

    :param nombre_archivo: ruta al archivo de entrada
    :return: diccionario con datos por estación
    """
    datos = {}

    with open(nombre_archivo, "r") as f:
        lineas = f.readlines()

    # Saltar encabezado (primeras dos líneas)
    for linea in lineas[2:]:
        partes = linea.strip().split()
        if len(partes) < 4:
            continue  # línea malformada

        fecha = partes[0]
        try:
            tmax = float(partes[1])
        except ValueError:
            tmax = None
        try:
            tmin = float(partes[2])
        except ValueError:
            tmin = None
        nombre_estacion = " ".join(partes[3:])  # puede tener espacios

        if nombre_estacion not in datos:
            datos[nombre_estacion] = {"tmax": [], "tmin": [], "fechas": []}

        datos[nombre_estacion]["tmax"].append(tmax)
        datos[nombre_estacion]["tmin"].append(tmin)
        datos[nombre_estacion]["fechas"].append(fecha)

    return datos


# -----------------------------
# 2) FUNCIONES DE ESTADÍSTICAS
# -----------------------------
def max_min_por_estacion(datos) -> Dict[str, Tuple[float, float]]:
    """
    Devuelve el máximo y mínimo registrado por cada estación.
    """
    resultados = {}
    for est, vals in datos.items():
        maximos = [t for t in vals["tmax"] if t is not None]
        minimos = [t for t in vals["tmin"] if t is not None]
        if maximos and minimos:
            resultados[est] = (max(maximos), min(minimos))
    return resultados


def mayor_menor_amplitud(datos) -> Tuple[Tuple[str, str, float], Tuple[str, str, float]]:
    """
    Encuentra la estación y día con mayor y menor amplitud térmica.
    """
    mayor = ("", "", float("-inf"))  # estacion, fecha, amplitud
    menor = ("", "", float("inf"))

    for est, vals in datos.items():
        for i in range(len(vals["fechas"])):
            tmax = vals["tmax"][i]
            tmin = vals["tmin"][i]
            fecha = vals["fechas"][i]
            if tmax is not None and tmin is not None:
                amp = tmax - tmin
                if amp > mayor[2]:
                    mayor = (est, fecha, amp)
                if amp < menor[2]:
                    menor = (est, fecha, amp)

    return mayor, menor


def diferencias_entre_estaciones(datos) -> Tuple[Tuple[str, str, str, str, float], Tuple[str, str, str, str, float]]:
    """
    Calcula la máxima y mínima diferencia de temperaturas entre estaciones en un mismo día.
    """
    fechas = set()
    for est in datos.values():
        fechas.update(est["fechas"])

    mayor = ("", "", "", "", float("-inf"))  # est1, est2, fecha, tipo, dif
    menor = ("", "", "", "", float("inf"))

    for fecha in fechas:
        registros = []
        for est, vals in datos.items():
            if fecha in vals["fechas"]:
                idx = vals["fechas"].index(fecha)
                if vals["tmax"][idx] is not None and vals["tmin"][idx] is not None:
                    registros.append((est, vals["tmax"][idx], vals["tmin"][idx]))

        # Comparar entre estaciones
        for i in range(len(registros)):
            for j in range(i + 1, len(registros)):
                est1, tmax1, tmin1 = registros[i]
                est2, tmax2, tmin2 = registros[j]

                # Diferencia entre Tmax y Tmin de distintas estaciones
                dif = abs(tmax1 - tmin2)

                if dif > mayor[4]:
                    mayor = (est1, est2, fecha, "Tmax-Tmin", dif)
                if dif < menor[4]:
                    menor = (est1, est2, fecha, "Tmax-Tmin", dif)

    return mayor, menor


# -----------------------------
# 3) GENERACIÓN DEL REPORTE
# -----------------------------
def generar_reporte(datos, nombre_reporte: str):
    """
    Genera un archivo de texto con las estadísticas pedidas.
    """
    with open(nombre_reporte, "w", encoding="utf-8") as f:
        f.write("=== REPORTE DE TEMPERATURAS ===\n\n")

        # Máximas y mínimas por estación
        f.write("1) Máximas y mínimas registradas por estación:\n")
        resumen = max_min_por_estacion(datos)
        for est, (tmax, tmin) in resumen.items():
            f.write(f" - {est}: Tmax = {tmax:.1f}°C, Tmin = {tmin:.1f}°C\n")
        f.write("\n")

        # Mayor y menor amplitud
        mayor, menor = mayor_menor_amplitud(datos)
        f.write("2) Mayor amplitud térmica:\n")
        f.write(f" - {mayor[0]} el día {mayor[1]} con {mayor[2]:.1f}°C\n")
        f.write("   Menor amplitud térmica:\n")
        f.write(f" - {menor[0]} el día {menor[1]} con {menor[2]:.1f}°C\n\n")

        # Diferencias entre estaciones
        mayor, menor = diferencias_entre_estaciones(datos)
        f.write("3) Máxima diferencia entre estaciones:\n")
        f.write(f" - Entre {mayor[0]} y {mayor[1]} el día {mayor[2]}: {mayor[4]:.1f}°C ({mayor[3]})\n")
        f.write("   Mínima diferencia entre estaciones:\n")
        f.write(f" - Entre {menor[0]} y {menor[1]} el día {menor[2]}: {menor[4]:.1f}°C ({menor[3]})\n")


# -----------------------------
# 4) PROGRAMA PRINCIPAL
# -----------------------------
if __name__ == "__main__":
    #Modificar las rutas de los archivos según corresponda
    archivo_entrada = 'C:/Users/aguca/AndroidStudioProjects/DHS/TP1/RegistroTemp.txt'
    archivo_salida = "C:/Users/aguca/AndroidStudioProjects/DHS/TP1/reporte_temperaturas.txt"

    datos = leer_datos(archivo_entrada)
    generar_reporte(datos, archivo_salida)

    print(f"Reporte generado en '{archivo_salida}'")

#NOTA: No se modularizo el código en varios archivos para facilitar la entrega y revisión del TP.