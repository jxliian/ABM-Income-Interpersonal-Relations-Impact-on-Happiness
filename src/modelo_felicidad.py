import pandas as pd
import numpy as np
import os

def calculate_happiness(alpha, factores, decimales=0):
    """
    Calcula el nivel de felicidad para cada factor y lo redondea
    al número de decimales especificado.
    """
    current_happiness = [
        round(((factor ** alpha * 8 ** (1 - alpha)) * 5) / 11, decimales)
        for factor in factores
    ]
    return current_happiness

def simulated_happiness(alpha, archivo_excel_data, archivo_excel_results):
    """
    Lee los datos de 'archivo_excel_data', calcula la felicidad y
    guarda el resultado en 'archivo_excel_results'.
    """
    df = pd.read_excel(archivo_excel_data)
    # tercera columna (como en tus scripts originales)
    primer_factores = df.iloc[:, 2].tolist()

    happiness_score = calculate_happiness(alpha, primer_factores)

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

    # 1) Pedimos alpha una única vez
    alpha = pedir_alpha()

    # 2) Preguntamos qué redes procesar
    redes_a_procesar = elegir_redes(redes)

    # 3) Ejecutamos el cálculo sólo para las redes seleccionadas
    for red in redes_a_procesar:
        ruta_input = os.path.join(CLEAN_DATA_DIR, red["input"])
        ruta_output = os.path.join(CLEAN_DATA_DIR, red["output"])

        print(f"\nProcesando {red['nombre']}...")
        print(f"  Leyendo de : {ruta_input}")
        print(f"  Guardando en: {ruta_output}")

        simulated_happiness(alpha, ruta_input, ruta_output)

    print("\nProceso completado.")
