import pandas as pd
import numpy as np
import os
import math

# --- 1. GESTIÓN DE RUTAS ---
def obtener_ruta_datos(nombre_archivo):
    """
    Busca el archivo en la carpeta 'clean_data' subiendo un nivel desde 'src'.
    """
    try:
        dir_script = os.path.dirname(os.path.abspath(__file__))
        dir_raiz = os.path.dirname(dir_script)
        ruta = os.path.join(dir_raiz, 'clean_data', nombre_archivo)
        return ruta
    except Exception as e:
        # Fallback si se ejecuta desde otro sitio
        return nombre_archivo

# --- 2. CÁLCULO MATEMÁTICO MANUAL ---
def calcular_estadisticas_manual(nombre_red, archivo_datos, archivo_modelo):
    path_data = obtener_ruta_datos(archivo_datos)
    path_model = obtener_ruta_datos(archivo_modelo)

    print(f"\n{'='*60}")
    print(f"   ANALIZANDO: {nombre_red.upper()}")
    print(f"{'='*60}")

    try:
        if not os.path.exists(path_data) or not os.path.exists(path_model):
            print("  [!] Error: No se encuentran los archivos.")
            return

        # Cargar DataFrames
        df_real = pd.read_excel(path_data)
        df_sim = pd.read_excel(path_model)

        # --- A. SELECCIÓN DE COLUMNAS ---
        # 1. Datos Reales (CIS): Buscamos P69 (Felicidad)
        # Si no existe por nombre, usamos la columna adecuada (normalmente índice 0 o 3)
        if "P69" in df_real.columns:
            data_real = df_real["P69"]
        else:
            # AJUSTE MANUAL: Si tus datos clean tienen la felicidad en col 3, usa iloc[:,3]
            data_real = df_real.iloc[:, 3] 

        # 2. Datos Simulados (Modelo): Buscamos Nivel_Felicidad
        if "Nivel_Felicidad" in df_sim.columns:
            data_sim = df_sim["Nivel_Felicidad"]
        else:
            data_sim = df_sim.iloc[:, 0]

        # --- B. SINCRONIZACIÓN ---
        # Cortamos los arrays para que tengan la misma longitud
        n = min(len(data_real), len(data_sim))
        Y_real = data_real.iloc[:n].values
        Y_sim = data_sim.iloc[:n].values
        
        print(f"  > Muestras procesadas (N): {n}")

        # --- C. CÁLCULO MANUAL DE PEARSON (Paso a Paso) ---
        # 1. Medias
        mean_real = np.mean(Y_real)
        mean_sim = np.mean(Y_sim)

        # 2. Desviaciones (x - media)
        dev_real = Y_real - mean_real
        dev_sim = Y_sim - mean_sim

        # 3. Suma de productos (Numerador)
        sum_products = np.sum(dev_real * dev_sim)

        # 4. Suma de cuadrados (Denominador)
        sum_sq_real = np.sum(dev_real ** 2)
        sum_sq_sim = np.sum(dev_sim ** 2)

        # 5. Fórmula Final
        denom = np.sqrt(sum_sq_real * sum_sq_sim)
        
        if denom != 0:
            pearson_corr = sum_products / denom
        else:
            pearson_corr = 0.0

        # --- D. CÁLCULO DE ERRORES (Argumento de Defensa) ---
        
        # MAE (Mean Absolute Error): Promedio de la diferencia absoluta
        # Fórmula: (1/n) * sum(|real - sim|)
        mae = np.mean(np.abs(Y_real - Y_sim))
        
        # RMSE (Root Mean Squared Error): Raíz del error cuadrático medio
        # Fórmula: sqrt( (1/n) * sum((real - sim)^2) )
        rmse = np.sqrt(np.mean((Y_real - Y_sim) ** 2))

        # --- E. IMPRESIÓN DE RESULTADOS ---
        print(f"\n  [1] CORRELACIÓN (Tendencia)")
        print(f"      R de Pearson:   {pearson_corr:.6f}")
        
        print(f"\n  [2] PRECISIÓN (Errores)")
        print(f"      Error Medio (MAE): {mae:.4f}  <-- (Dato Clave)")
        print(f"      Error RMSE:        {rmse:.4f}")

        # Interpretación para el paper/presentación
        print(f"\n  [3] INTERPRETACIÓN CIENTÍFICA")
        if abs(pearson_corr) < 0.2:
            print("      - La correlación es BAJA. Esto indica que la relación no es lineal.")
            print("        (El dinero no causa felicidad directa y proporcional).")
        
        if mae < 1.0:
            print("      - Sin embargo, el MAE es BAJO (< 1.0).")
            print("        CONCLUSIÓN: El modelo es robusto prediciendo rangos, aunque")
            print("        no capture la variabilidad individual (ruido).")
        else:
            print("      - El error es considerable. Se sugiere revisar parámetros.")

    except Exception as e:
        print(f"  [!] Error crítico: {e}")

# --- 3. CONFIGURACIÓN DE ARCHIVOS ---
files_ig = {'data': '3145_data_clean_IG.xlsx', 'model': 'model_IG.xlsx'}
files_tw = {'data': '3145_data_clean_X.xlsx',  'model': 'model_X.xlsx'}
files_fb = {'data': '3145_data_clean_FB.xlsx', 'model': 'model_FB.xlsx'}

# --- 4. MENÚ ---
def menu():
    while True:
        print("\n" + "-"*40)
        print("   SISTEMA DE CALIBRACIÓN MATEMÁTICA")
        print("-" * 40)
        print("1. Instagram")
        print("2. Twitter (X)")
        print("3. Facebook")
        print("4. EJECUTAR TODO (Reporte Completo)")
        print("5. Salir")
        
        op = input("\nSeleccione opción: ")

        if op == '1':
            calcular_estadisticas_manual("Instagram", files_ig['data'], files_ig['model'])
        elif op == '2':
            calcular_estadisticas_manual("Twitter", files_tw['data'], files_tw['model'])
        elif op == '3':
            calcular_estadisticas_manual("Facebook", files_fb['data'], files_fb['model'])
        elif op == '4':
            calcular_estadisticas_manual("Instagram", files_ig['data'], files_ig['model'])
            calcular_estadisticas_manual("Twitter", files_tw['data'], files_tw['model'])
            calcular_estadisticas_manual("Facebook", files_fb['data'], files_fb['model'])
        elif op == '5':
            print("Saliendo...")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    menu()