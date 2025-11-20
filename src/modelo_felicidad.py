import pandas as pd
import numpy as np
import os

def calculate_happiness(alpha, factores, horas=8, decimales=0):
    """
    Calcula el nivel de felicidad para cada factor y lo redondea
    al número de decimales especificado.
    'horas' tiene por defecto el valor 8.
    """
    current_happiness = [
        round(((factor ** alpha * horas ** (1 - alpha)) * 5) / 11, decimales)
        for factor in factores
    ]
    return current_happiness

def simulated_happiness(alpha, horas, archivo_excel_data, archivo_excel_results):
    """
    Lee los datos de 'archivo_excel_data', calcula la felicidad y
    guarda el resultado en 'archivo_excel_results'.
    """
    df = pd.read_excel(archivo_excel_data)
    # tercera columna (como en tus scripts originales)
    primer_factores = df.iloc[:, 2].tolist()

    happiness_score = calculate_happiness(alpha, primer_factores, horas=horas)

    df_resultado = pd.DataFrame({"Nivel_Felicidad": happiness_score})
    df_resultado.to_excel(archivo_excel_results, index=False)

    print(f"Se han generado y guardado los niveles de felicidad en:\n  {archivo_excel_results}")

def pedir_alpha():
    """
    Pide un valor alpha al usuario y comprueba que esté entre 0 y 1.
    """
    while True:
        try:
            alpha = float(input("Introduce un valor alpha entre 0 y 1: "))
        except ValueError:
            print("Debe ser un número (usa punto para decimales).")
            continue

        if 0 <= alpha <= 1:
            return alpha
        else:
            print("El valor alpha debe estar entre 0 y 1.")

def pedir_horas(horas_actual):
    """
    Pide un nuevo valor para 'horas'.
    Por defecto es 8, pero puedes cambiarlo.
    """
    while True:
        try:
            entrada = input(
                f"Valor actual de horas = {horas_actual} (por defecto es 8). "
                "Introduce un nuevo valor o pulsa Enter para mantener: "
            ).strip()

            if entrada == "":
                return horas_actual

            horas_nueva = float(entrada)

            if horas_nueva <= 0:
                print("Las horas deben ser un número positivo.")
                continue

            return horas_nueva
        except ValueError:
            print("Debe ser un número (usa punto para decimales).")

def elegir_redes(redes):
    """
    Pregunta al usuario qué redes quiere procesar y
    devuelve una lista filtrada de redes seleccionadas.
    """
    print("\n¿Qué redes quieres procesar?")
    print("  1) Facebook")
    print("  2) Instagram")
    print("  3) X")
    print("  4) Todas")

    while True:
        opcion = input("Elige una o varias opciones (ej: 1,2 o 4): ").strip()

        # Atajos por texto
        if opcion.lower() in ["4", "todas", "todo"]:
            return redes

        seleccion = set()
        partes = [p.strip() for p in opcion.split(",") if p.strip()]

        valido = True
        for p in partes:
            if p not in ["1", "2", "3"]:
                valido = False
                break
            seleccion.add(int(p))

        if not partes or not valido:
            print("Opción no válida. Prueba con 1, 2, 3, 4 o combinaciones tipo 1,3.")
            continue

        redes_sel = [redes[i - 1] for i in sorted(seleccion)]
        return redes_sel

if __name__ == "__main__":
    num_agentes = 3000  # lo mantengo por si lo usas luego

    # Carpeta donde está ESTE fichero (src/)
    SRC_DIR = os.path.dirname(os.path.abspath(__file__))
    # Carpeta raíz del proyecto (un nivel arriba de src/)
    PROJECT_ROOT = os.path.dirname(SRC_DIR)
    # Carpeta clean_data/
    CLEAN_DATA_DIR = os.path.join(PROJECT_ROOT, "clean_data")

    # Configuración de cada red social (solo nombres de ficheros, sin rutas absolutas)
    redes = [
        {
            "nombre": "FaceBook",
            "input": "3145_data_clean_FB.xlsx",
            "output": "model_FB.xlsx",
        },
        {
            "nombre": "Instagram",
            "input": "3145_data_clean_IG.xlsx",
            "output": "model_IG.xlsx",
        },
        {
            "nombre": "X",
            "input": "3145_data_clean_X.xlsx",
            "output": "model_X.xlsx",
        },
    ]

    # Variable horas (por defecto 8)
    horas = 8.0

    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print(f"Horas actuales = {horas} (por defecto es 8)")
        print("  1) Ejecutar modelo de felicidad")
        print("  2) Cambiar valor de horas")
        print("  3) Salir sin hacer nada")

        opcion_menu = input("Elige una opción: ").strip()

        if opcion_menu == "1":
            # Ejecutar modelo
            alpha = pedir_alpha()
            redes_a_procesar = elegir_redes(redes)

            for red in redes_a_procesar:
                ruta_input = os.path.join(CLEAN_DATA_DIR, red["input"])
                ruta_output = os.path.join(CLEAN_DATA_DIR, red["output"])

                print(f"\nProcesando {red['nombre']}...")
                print(f"  Leyendo de : {ruta_input}")
                print(f"  Guardando en: {ruta_output}")

                simulated_happiness(alpha, horas, ruta_input, ruta_output)

            print("\nProceso completado.")
            break

        elif opcion_menu == "2":
            # Cambiar horas
            horas = pedir_horas(horas)

        elif opcion_menu == "3":
            print("Saliendo del programa sin ejecutar el modelo.")
            break

        else:
            print("Opción no válida. Elige 1, 2 o 3.")

