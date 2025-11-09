# run.py
from modelo_felicidad import ModeloFelicidad
import matplotlib.pyplot as plt
import pandas as pd

# --- Parámetros de Simulación ---
NUM_AGENTES = 100
MAX_PASOS = 10 # Pasos de simulación (ej. 10 días/rondas)

# --- Ejecución del Modelo ---
modelo = ModeloFelicidad(N_agentes=NUM_AGENTES)

for i in range(MAX_PASOS):
    modelo.step()
    # En este modelo simple, la optimización ocurre en el primer paso, pero en
    # modelos más complejos (con interacciones de red), el proceso continúa.

# --- Obtención y Análisis de Resultados ---
df_modelo = modelo.datacollector.get_model_vars_dataframe()
df_agente = modelo.datacollector.get_agent_vars_dataframe()

print("--- Felicidad Media por Paso ---")
print(df_modelo.head())

print("\n--- Resultados Finales de Agentes (Muestra) ---")
# Obtenemos los datos solo del último paso (Estado final)
df_agente_final = df_agente.loc[df_agente.index.get_level_values('Step') == MAX_PASOS - 1]
print(df_agente_final.head(10))

# --- Visualización (Ejemplo) ---
df_agente_final.hist(column="Felicidad", by="Alfa", bins=10)
plt.suptitle("Distribución de Felicidad por Predisposición (Alfa)")
plt.show()

# También puedes exportar a CSV para análisis en Stata/R
# df_agente_final.to_csv("resultados_abm_felicidad.csv")