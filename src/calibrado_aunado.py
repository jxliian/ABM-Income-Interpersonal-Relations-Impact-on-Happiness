import pandas as pd
import numpy as np
import os

def obtener_ruta_datos(nombre_archivo):
    """
    Genera la ruta absoluta al archivo dentro de la carpeta 'clean_data',
    independientemente de en qué PC se ejecute.
    """
    # 1. Obtener la ubicación de ESTE script (dentro de 'src')
    directorio_script = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Subir un nivel para ir a la raíz del proyecto (salir de 'src')
    directorio_raiz = os.path.dirname(directorio_script)
    
    # 3. Construir la ruta hacia la carpeta 'clean_data' y el archivo
    ruta_final = os.path.join(directorio_raiz, 'clean_data', nombre_archivo)
    
    return ruta_final

def calcular_correlacion(nombre_red, archivo_datos, archivo_modelo):
    """
    Carga los excels y calcula la correlación manual.
    """
    # Construimos las rutas dinámicas
    path_data = obtener_ruta_datos(archivo_datos)
    path_model = obtener_ruta_datos(archivo_modelo)

    print(f"\n--- Procesando: {nombre_red} ---")
    print(f"Buscando datos en: {path_data}")

    try:
        # Verificar existencia
        if not os.path.exists(path_data):
            print(f" Error: No se encuentra el archivo de datos: {archivo_datos}")
            return
        if not os.path.exists(path_model):
            print(f" Error: No se encuentra el archivo del modelo: {archivo_modelo}")
            return

        # Leer Excels
        df1 = pd.read_excel(path_data)
        df2 = pd.read_excel(path_model)

        # Seleccionar columnas (Datos: col 3 [índice 2], Modelo: col 1 [índice 0])
        happiness_data = df1.iloc[:, 2]
        happiness_model = df2.iloc[:, 0]

        # --- LÓGICA MATEMÁTICA ---
        mean_data = happiness_data.mean()
        mean_model = happiness_model.mean()

        deviation_data = happiness_data - mean_data
        deviation_model = happiness_model - mean_model

        sum_of_products = (deviation_data * deviation_model).sum()

        sum_of_squares_data = (deviation_data ** 2).sum()
        sum_of_squares_model = (deviation_model ** 2).sum()

        sqrt_product = np.sqrt(sum_of_squares_data * sum_of_squares_model)

        if sqrt_product != 0:
            correlation = sum_of_products / sqrt_product
            print(f" El coeficiente de correlación para {nombre_red} es: {correlation:.6f}")
        else:
            print(f" No se puede calcular para {nombre_red} (división por cero).")

    except Exception as e:
        print(f" Ocurrió un error inesperado en {nombre_red}: {e}")

# --- Definición de Archivos (Solo los nombres, ya no rutas completas) ---
files_ig = {
    'data': '3145_data_clean_IG.xlsx',
    'model': 'model_IG.xlsx'
}

files_tw = {
    'data': '3145_data_clean_X.xlsx',
    'model': 'model_X.xlsx'
}

files_fb = {
    'data': '3145_data_clean_FB.xlsx',
    'model': 'model_FB.xlsx'
}

# --- Menú Principal ---
def menu():
    while True:
        print("\n============================================")
        print("   CALIBRACIÓN DE MODELOS (Rutas Relativas) ")
        print("============================================")
        print("1. Calibrar Instagram")
        print("2. Calibrar Twitter (X)")
        print("3. Calibrar Facebook")
        print("4. Calibrar TODAS las redes")
        print("5. Salir")
        
        opcion = input("\nSeleccione una opción (1-5): ")

        if opcion == '1':
            calcular_correlacion("Instagram", files_ig['data'], files_ig['model'])
        
        elif opcion == '2':
            calcular_correlacion("Twitter (X)", files_tw['data'], files_tw['model'])
        
        elif opcion == '3':
            calcular_correlacion("Facebook", files_fb['data'], files_fb['model'])
        
        elif opcion == '4':
            print("\nIniciando calibración completa...")
            calcular_correlacion("Instagram", files_ig['data'], files_ig['model'])
            calcular_correlacion("Twitter (X)", files_tw['data'], files_tw['model'])
            calcular_correlacion("Facebook", files_fb['data'], files_fb['model'])
        
        elif opcion == '5':
            print("Saliendo...")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    menu()