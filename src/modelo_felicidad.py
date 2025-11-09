# modelo_felicidad.py
from mesa import Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from agente_felicidad import AgenteFelicidad
import numpy as np
import pandas as pd

# Función para recoger datos a nivel de modelo (ej. felicidad media)
def get_felicidad_media(model):
    """Calcula la felicidad media de todos los agentes."""
    agentes_felicidad = [a.H for a in model.schedule.agents]
    return np.mean(agentes_felicidad)

class ModeloFelicidad(Model):
    """
    El modelo principal para la simulación de la felicidad basada en agentes.
    """
    def __init__(self, N_agentes=100, tiempo_total=24):
        self.num_agents = N_agentes
        self.T_total = tiempo_total
        self.schedule = RandomActivation(self) # Activación aleatoria de agentes
        self.running = True # El modelo está activo

        # 1. CREACIÓN DE AGENTES (CALIBRADO)
        # Para el calibrado inicial, usaremos una distribución simple de alfa:
        # 50% Agentes Relacionales (alfa bajo: ej. 0.3)
        # 50% Agentes Materialistas (alfa alto: ej. 0.7)

        for i in range(self.num_agents):
            if i < self.num_agents / 2:
                # Agente Relacional (T_R importa más)
                alfa = 0.3
            else:
                # Agente Materialista (T_E importa más)
                alfa = 0.7

            # Creamos el agente
            a = AgenteFelicidad(i, self, alfa, self.T_total)
            self.schedule.add(a)

        # 2. RECOLECCIÓN DE DATOS
        self.datacollector = DataCollector(
            model_reporters={"Felicidad_Media": get_felicidad_media},
            agent_reporters={
                "Felicidad": "H",
                "Alfa": "alfa",
                "Tiempo_Relaciones": "T_R",
                "Tiempo_Economico": "T_E"
            }
        )
        self.datacollector.collect(self) # Recogemos los datos iniciales

    def step(self):
        """
        Ejecuta un paso de la simulación. Cada paso representa una unidad de tiempo (ej. un día).
        """
        self.schedule.step() # Llama al método step() de cada agente
        self.datacollector.collect(self) # Recoge los datos después de la interacción