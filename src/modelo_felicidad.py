import pandas as pd
import numpy as np
import os

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
    Esto asocia a cada nivel de felicidad una sociabilidad necesaria para mantenerla.
    """
    sociability_index = []
    
    for h in happiness_scores:
        h_val = max(0, h) # Evitar negativos
        # Aplicamos la fórmula: Felicidad amplificada por la apertura (alpha)
        val = h_val * (1 + (h_val ** (1-alpha)))
        sociability_index.append(round(val, decimales))
        
    return sociability_index

def simulated_happiness(alpha, horas, archivo_excel_data, archivo_excel_results):
    """
    Lee datos, calcula Felicidad y Sociabilidad derivada, y guarda ambas columnas.
    """
    if not os.path.exists(archivo_excel_data):
        print(f"Error: No se encuentra el archivo {archivo_excel_data}")
        return

    df = pd.read_excel(archivo_excel_data)
    
    # --- 1. DETECCIÓN INTELIGENTE DE DATOS ---
    # Buscamos qué dato usar como 'factor' (Likes o Longitud de texto)
    cols_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    cols_texto = df.select_dtypes(include=['object', 'string']).columns.tolist()
    
    primer_factores = []
    
    if len(cols_numericas) > 0 and "id" not in cols_numericas[-1].lower():
        # Si hay una columna numérica al final, la usamos
        col_usada = cols_numericas[-1]
        primer_factores = df[col_usada].tolist()
        print(f"  -> Calculando basado en datos numéricos: '{col_usada}'")
        
    elif len(cols_texto) > 0:
        # Si solo hay texto, contamos los caracteres de cada celda
        col_usada = cols_texto[-1]
        primer_factores = df[col_usada].astype(str).apply(len).tolist()
        print(f"  -> Calculando basado en longitud de texto de: '{col_usada}'")
        
    else:
        # Caso de emergencia: Generar aleatorios para que no falle
        print("  -> ¡Aviso! No hay datos útiles. Usando simulación aleatoria.")
        np.random.seed(42)
        primer_factores = np.random.randint(10, 500, size=len(df)).tolist()

    # --- 2. CÁLCULO DE FELICIDAD ---
    happiness_score = calculate_happiness(alpha, primer_factores, horas=horas)

    # --- 3. CÁLCULO DE SOCIABILIDAD (Basado en la Felicidad) ---
    sociability_score = calculate_sociability_from_happiness(happiness_score, alpha)

    # --- 4. GUARDADO ---
    # Creamos el DataFrame con las dos columnas juntas
    df_resultado = pd.DataFrame({
        "Nivel_Felicidad": happiness_score,
        "Indice_Sociabilidad": sociability_score
    })
    
    df_resultado.to_excel(archivo_excel_results, index=False)
    print(f"  Guardado correctamente en:\n  {archivo_excel_results}")

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
            print("Debe ser un número válido.")

def elegir_redes(redes):
    """
    Selección de redes para procesar.
    """
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
    PROJECT_ROOT = os.path.dirname(SRC_DIR)
    CLEAN_DATA_DIR = os.path.join(PROJECT_ROOT, "clean_data")
    
    # Crear carpeta si no existe (para evitar errores en primera ejecución)
    if not os.path.exists(CLEAN_DATA_DIR):
        try:
            os.makedirs(CLEAN_DATA_DIR)
        except:
            pass # Si no se puede crear, probablemente ya exista o sea un tema de permisos

    redes = [
        {"nombre": "FaceBook", "input": "3145_data_clean_FB.xlsx", "output": "model_FB.xlsx"},
        {"nombre": "Instagram", "input": "3145_data_clean_IG.xlsx", "output": "model_IG.xlsx"},
        {"nombre": "X", "input": "3145_data_clean_X.xlsx", "output": "model_X.xlsx"},
    ]

    horas = 8.0

    while True:
        print("\n=== MENÚ PRINCIPAL (Felicidad + Sociabilidad) ===")
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