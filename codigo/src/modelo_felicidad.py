import pandas as pd
import numpy as np
import os
import sys

# --- 1. CÁLCULOS MATEMÁTICOS ---

def calculate_happiness(alpha, factores, horas=8, decimales=2):
    """
    Calcula el nivel de felicidad (Cobb-Douglas) para cada factor.
    """
    # Aseguramos que los factores no sean 0 para evitar errores matemáticos
    factores_seguros = [max(0.1, f) for f in factores]
    
    current_happiness = [
        round(((factor ** alpha * horas ** (1 - alpha)) * 5) / 11, decimales)
        for factor in factores_seguros
    ]
    return current_happiness

def calculate_sociability_from_happiness(happiness_scores, alpha, decimales=2):
    """
    [NUEVA LÓGICA] Teorema de la Resonancia Social Inversa.
    Calcula la Sociabilidad (S) basándose únicamente en la Felicidad (H).
    Fórmula: S = H * (1 + H^alpha)
    """
    sociability_index = []
    
    for h in happiness_scores:
        h_val = max(0, h) # Evitar negativos
        # Aplicamos la fórmula: Felicidad amplificada por la apertura (alpha)
        val = h_val * (1 + (h_val ** (1-alpha)))
        sociability_index.append(round(val, decimales))
        
    return sociability_index

# --- 2. PROCESAMIENTO DE ARCHIVOS ---

def simulated_happiness(alpha, horas, archivo_excel_data, archivo_excel_results):
    """
    Lee datos, calcula Felicidad y Sociabilidad derivada, y guarda TRES columnas:
    Felicidad, Sociabilidad e Ingresos.
    """
    if not os.path.exists(archivo_excel_data):
        print(f"Error: No se encuentra el archivo {archivo_excel_data}")
        return

    df = pd.read_excel(archivo_excel_data)
    
    # --- DETECCIÓN DE DATOS (INGRESOS) ---
    ingresos_raw = []
    
    # 1. Intentamos buscar la columna específica del CIS "P65"
    if "P65" in df.columns:
        print("  -> Columna 'P65' (Ingresos) detectada.")
        ingresos_raw = df["P65"].tolist()
        
    # 2. Si no existe, usamos la lógica de detección automática anterior
    else:
        cols_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
        cols_texto = df.select_dtypes(include=['object', 'string']).columns.tolist()
        
        if len(cols_numericas) > 0 and "id" not in cols_numericas[-1].lower():
            col_usada = cols_numericas[-1]
            ingresos_raw = df[col_usada].tolist()
            print(f"  -> Usando columna numérica alternativa: '{col_usada}'")
            
        elif len(cols_texto) > 0:
            col_usada = cols_texto[-1]
            ingresos_raw = df[col_usada].astype(str).apply(len).tolist()
            print(f"  -> Usando longitud de texto de: '{col_usada}'")
            
        else:
            print("  -> ¡Aviso! No hay datos útiles. Usando simulación aleatoria.")
            np.random.seed(42)
            ingresos_raw = np.random.randint(1, 12, size=len(df)).tolist()

    # --- CÁLCULOS ---
    # Usamos los ingresos detectados para calcular la felicidad
    happiness_score = calculate_happiness(alpha, ingresos_raw, horas=horas)

    # Usamos la felicidad para calcular la sociabilidad
    sociability_score = calculate_sociability_from_happiness(happiness_score, alpha)

    # --- GUARDADO (AHORA CON 3 COLUMNAS) ---
    df_resultado = pd.DataFrame({
        "Nivel_Felicidad": happiness_score,
        "Indice_Sociabilidad": sociability_score,
        "Ingresos": ingresos_raw  # <--- TERCERA COLUMNA AÑADIDA
    })
    
    df_resultado.to_excel(archivo_excel_results, index=False)
    print(f"  Guardado correctamente (con Ingresos) en:\n  {archivo_excel_results}")

# --- 3. MENÚS Y UTILIDADES ---

def pedir_alpha():
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
            print("Debe ser un número válido.")

def elegir_redes(redes):
    print("\n¿Qué redes quieres procesar?")
    print("  1) Facebook")
    print("  2) Instagram")
    print("  3) X")
    print("  4) Todas")

    while True:
        opcion = input("Elige una o varias opciones (ej: 1,2 o 4): ").strip()

        if opcion.lower() in ["4", "todas", "todo"]:
            return redes

        seleccion = set()
        partes = [p.strip() for p in opcion.split(",") if p.strip()]
        valido = True
        
        mapa = {"1": 0, "2": 1, "3": 2}
        
        for p in partes:
            if p not in mapa:
                valido = False; break
            seleccion.add(mapa[p])

        if not partes or not valido:
            print("Opción no válida.")
            continue

        redes_sel = [redes[i] for i in sorted(seleccion)]
        return redes_sel

if __name__ == "__main__":
    # Configuración de Rutas
    SRC_DIR = os.path.dirname(os.path.abspath(__file__))
    # El script está en codigo/src/, subimos dos niveles para el root
    PROJECT_ROOT = os.path.dirname(os.path.dirname(SRC_DIR))
    CLEAN_DATA_DIR = os.path.join(PROJECT_ROOT, "documentos_datos", "clean_data")
    
    if not os.path.exists(CLEAN_DATA_DIR):
        try:
            os.makedirs(CLEAN_DATA_DIR)
        except:
            pass 

    redes = [
        {"nombre": "FaceBook", "input": "3145_data_clean_FB.xlsx", "output": "model_FB.xlsx"},
        {"nombre": "Instagram", "input": "3145_data_clean_IG.xlsx", "output": "model_IG.xlsx"},
        {"nombre": "X", "input": "3145_data_clean_X.xlsx", "output": "model_X.xlsx"},
    ]

    horas = 8.0

    while True:
        print("\n=== MENÚ PRINCIPAL (Felicidad + Sociabilidad + Ingresos) ===")
        print(f"Horas actuales = {horas}")
        print("  1) Ejecutar modelo")
        print("  2) Cambiar horas")
        print("  3) Salir")

        opcion_menu = input("Elige una opción: ").strip()

        if opcion_menu == "1":
            alpha = pedir_alpha()
            redes_a_procesar = elegir_redes(redes)

            for red in redes_a_procesar:
                ruta_input = os.path.join(CLEAN_DATA_DIR, red["input"])
                ruta_output = os.path.join(CLEAN_DATA_DIR, red["output"])

                print(f"\nProcesando {red['nombre']}...")
                simulated_happiness(alpha, horas, ruta_input, ruta_output)

            print("\nProceso completado.")
            break

        elif opcion_menu == "2":
            horas = pedir_horas(horas)

        elif opcion_menu == "3":
            print("Saliendo...")
            break

        else:
            print("Opción no válida.")