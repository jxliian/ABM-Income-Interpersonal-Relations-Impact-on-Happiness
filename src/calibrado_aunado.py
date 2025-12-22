import pandas as pd
import numpy as np
import os

def obtener_ruta_datos(nombre_archivo):
    """
    Genera la ruta absoluta al archivo dentro de la carpeta 'clean_data'.
    """
    try:
        dir_script = os.path.dirname(os.path.abspath(__file__))
        dir_raiz = os.path.dirname(dir_script)
        ruta = os.path.join(dir_raiz, 'clean_data', nombre_archivo)
        return ruta
    except Exception as e:
        # Fallback por si acaso
        return os.path.join('clean_data', nombre_archivo)

def calcular_correlacion(nombre_red, archivo_datos_reales, archivo_modelo_simulado):
    """
    Carga los excels y calcula la correlación de Pearson entre
    la REALIDAD (CIS) y la SIMULACIÓN (ABM).
    """
    # Construimos las rutas
    path_data = obtener_ruta_datos(archivo_datos_reales)
    path_model = obtener_ruta_datos(archivo_modelo_simulado)

    print(f"\n--- Analizando: {nombre_red} ---")
    
    try:
        # 1. Verificar existencia
        if not os.path.exists(path_data):
            print(f"  [!] Error: No encuentro el archivo de datos reales: {archivo_datos_reales}")
            return
        if not os.path.exists(path_model):
            print(f"  [!] Error: No encuentro el archivo del modelo: {archivo_modelo_simulado}")
            return

        # 2. Leer Excels
        df_real = pd.read_excel(path_data)
        df_sim = pd.read_excel(path_model)

        # 3. SELECCIÓN DE COLUMNAS (CORREGIDO)
        
        # --- Datos Reales (CIS) ---
        # Buscamos la columna P69 (Felicidad subjetiva). 
        # Si no la encuentra por nombre, usamos la columna 0 (según tu script de filtrado).
        if "P69" in df_real.columns:
            happiness_real = df_real["P69"]
        else:
            happiness_real = df_real.iloc[:, 0] # Asumimos que es la primera

        # --- Datos Simulados (Modelo) ---
        # Buscamos "Nivel_Felicidad". Si no, columna 0.
        if "Nivel_Felicidad" in df_sim.columns:
            happiness_sim = df_sim["Nivel_Felicidad"]
        else:
            happiness_sim = df_sim.iloc[:, 0]

        # 4. LIMPIEZA Y SINCRONIZACIÓN
        # Aseguramos que tengan el mismo tamaño (cortamos al más pequeño)
        min_len = min(len(happiness_real), len(happiness_sim))
        
        # Recortamos
        series_real = happiness_real.iloc[:min_len]
        series_sim = happiness_sim.iloc[:min_len]

        # 5. CÁLCULO DE CORRELACIÓN (Pearson)
        correlation = series_real.corr(series_sim)

        print(f"  > Filas analizadas: {min_len}")
        print(f"  > Correlación de Pearson: {correlation:.6f}")
        
        # Interpretación automática
        if correlation > 0.3:
            print("   CONCLUSIÓN: El modelo tiene una correlación POSITIVA aceptable.")
        elif correlation > 0.1:
            print("   CONCLUSIÓN: Correlación baja. El modelo captura poco la realidad.")
        elif correlation < 0:
            print("   CONCLUSIÓN: Correlación NEGATIVA. El modelo predice lo contrario a la realidad.")
        else:
            print("   CONCLUSIÓN: Sin correlación aparente.")

    except Exception as e:
        print(f"  [!] Ocurrió un error inesperado: {e}")

# --- Definición de Archivos ---
files_ig = {'data': '3145_data_clean_IG.xlsx', 'model': 'model_IG.xlsx'}
files_tw = {'data': '3145_data_clean_X.xlsx',  'model': 'model_X.xlsx'}
files_fb = {'data': '3145_data_clean_FB.xlsx', 'model': 'model_FB.xlsx'}

# --- Menú Principal ---
def menu():
    while True:
        print("\n============================================")
        print("   SISTEMA DE CALIBRADO (Realidad vs Simulación)")
        print("============================================")
        print("1. Calibrar Instagram")
        print("2. Calibrar Twitter (X)")
        print("3. Calibrar Facebook")
        print("4. Calibrar TODAS")
        print("5. Salir")
        
        opcion = input("\nElige opción: ")

        if opcion == '1':
            calcular_correlacion("Instagram", files_ig['data'], files_ig['model'])
        elif opcion == '2':
            calcular_correlacion("Twitter (X)", files_tw['data'], files_tw['model'])
        elif opcion == '3':
            calcular_correlacion("Facebook", files_fb['data'], files_fb['model'])
        elif opcion == '4':
            calcular_correlacion("Instagram", files_ig['data'], files_ig['model'])
            calcular_correlacion("Twitter (X)", files_tw['data'], files_tw['model'])
            calcular_correlacion("Facebook", files_fb['data'], files_fb['model'])
        elif opcion == '5':
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    menu()