import pandas as pd
import os
import sys
import sys

def procesar_datos_social_media(social_media_key, columna_red_social):
    """
    Procesa el archivo de datos, filtra las filas, recodifica una columna 
    y guarda el resultado en un nuevo archivo Excel.
    
    :param social_media_key: Clave para nombrar el archivo de salida (Ej: 'X', 'IG', 'FB').
    :param columna_red_social: El nombre de la columna específica de la red social (Ej: 'P21A02').
    """
    
    # 1. Definir Rutas Portables
    
    if getattr(sys, 'frozen', False):
        # Si es EXE, base es donde está el ejecutable
        # En el EXE, las carpetas data y clean_data suelen estar en la raíz del entorno virtual del EXE
        base_dir = os.path.dirname(sys.executable)
        DATA_FOLDER = 'data'
        CLEAN_DATA_FOLDER = 'clean_data'
    else:
        # Si es Script, calculamos la ruta relativa al archivo para ser robustos
        # El script está ahora en codigo/src/filtra_datos.py, así que subimos dos niveles para el root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(os.path.dirname(script_dir))
        DATA_FOLDER = os.path.join('documentos_datos', 'data')
        CLEAN_DATA_FOLDER = os.path.join('documentos_datos', 'clean_data')
    
    # Uso de os.path.join para crear rutas robustas
    data_path = os.path.join(base_dir, DATA_FOLDER)
    clean_data_path = os.path.join(base_dir, CLEAN_DATA_FOLDER)
    
    # Crear la carpeta clean_data si no existe
    if not os.path.exists(clean_data_path):
        os.makedirs(clean_data_path)
    
    # Ruta del archivo de entrada
    excel_file_name = '3145_data.xlsx'
    excel_file_path = os.path.join(data_path, excel_file_name)
    
    # 2. Especificar Columnas
    
    columnas_base = ["P65", "P69", "P60A"]
    columnas_deseadas = columnas_base + [columna_red_social]
    
    print(f"\n--- Procesando datos para {social_media_key} (Columna: {columna_red_social}) ---")
    
    # 3. Cargar el Archivo y Comprobar su Existencia
    try:
        # Cargar el archivo Excel en un DataFrame
        df = pd.read_excel(excel_file_path, usecols=columnas_deseadas)
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo de datos en la ruta: {excel_file_path}")
        print(f"Asegúrate de que '{excel_file_name}' esté en la carpeta '{DATA_FOLDER}' y de que estés ejecutando el script desde la raíz del proyecto.")
        return

    # 4. Filtrar y Preprocesar
    
    # Nos aseguramos de filtrar valores de 'No sabe/No contesta' (98, 99)
    # y quedarnos solo con usuarios activos (P21Ax == 1) y españoles (P60A == 1)
    try:
        # Filtro de usuarios activos en la red social
        filas_filtradas = df[df[columna_red_social] == 1].copy()
        
        # Filtro de nacionalidad española (opcional pero común en estos estudios)
        if "P60A" in filas_filtradas.columns:
            filas_filtradas = filas_filtradas[filas_filtradas["P60A"] == 1]
            
        # Filtro de ingresos válidos
        filas_filtradas = filas_filtradas[filas_filtradas["P65"] < 90]
        
        # Filtro de felicidad válida
        filas_filtradas = filas_filtradas[filas_filtradas["P69"] < 90]
        
    except KeyError as e:
        print(f"ERROR: No se encontró la columna en el DataFrame: {e}")
        return

    # Recodificar la columna P69 de rango 0-10 a 0-5
    # Nota: El CIS usa 0-10. Nuestra recodificación la mapea a 6 niveles (0 a 5)
    recodificacion_p69 = {
        0:0, 1:0, 2:1, 3:1, 4:2, 5:2, 6:3, 7:3, 8:4, 9:4, 10:5
    }
    filas_filtradas.loc[:, "P69"] = filas_filtradas["P69"].replace(recodificacion_p69)

    # 5. Guardar el Resultado
    
    # Nombre del archivo de salida
    nuevo_excel_file_name = f'3145_data_clean_{social_media_key}.xlsx'
    nuevo_excel_path = os.path.join(clean_data_path, nuevo_excel_file_name)
    
    filas_filtradas.to_excel(nuevo_excel_path, index=False)
    
    print(f"\n Procesamiento completado. Filas finales: {len(filas_filtradas)}")
    print(f" Archivo guardado correctamente en: {nuevo_excel_path}")


# --- FUNCIÓN PRINCIPAL Y MENÚ INTERACTIVO ---

def menu_principal():
    """Muestra un menú interactivo para elegir la red social a procesar."""
    
    opciones = {
        '1': {'key': 'X', 'col': 'P21A02'},
        '2': {'key': 'IG', 'col': 'P21A05'},
        '3': {'key': 'FB', 'col': 'P21A01'}
    }
    
    print("\n========================================================")
    print("      Herramienta de Filtrado de Datos ABM/Felicidad")
    print("========================================================")
    print("Seleccione la red social cuyos datos desea procesar:")
    print("1. X (Anteriormente Twitter)")
    print("2. Instagram (IG)")
    print("3. Facebook (FB)")
    print("0. Salir")
    
    while True:
        eleccion = input("\nIngrese su opción (1, 2, 3 o 0): ").strip()
        
        if eleccion == '0':
            print("Programa finalizado. ¡Hasta luego!")
            break
        elif eleccion in opciones:
            opcion_elegida = opciones[eleccion]
            procesar_datos_social_media(opcion_elegida['key'], opcion_elegida['col'])
        else:
            print("Opción no válida. Por favor, ingrese 1, 2, 3 o 0.")

if __name__ == "__main__":
    menu_principal()