# agente_felicidad.py
from mesa import Agent
import numpy as np

class AgenteFelicidad(Agent):
    """
    Un agente que busca maximizar su felicidad (H) asignando su tiempo.
    """
    def __init__(self, unique_id, model, alfa, T_total=24):
        super().__init__(unique_id, model)
        # Atributos fijos del agente (Heterogeneidad)
        self.alfa = alfa  # Predisposición materialista/relacional (0 <= alfa <= 1)
        self.T_total = T_total # Restricción temporal (24 horas/día)

        # Variables que cambian
        self.T_R = 8.0     # Tiempo dedicado a relaciones (T_R) - Inicial (ej. 8 horas)
        self.T_E = T_total - self.T_R # Tiempo a bienes económicos (T_E)
        self.H = self.calcular_felicidad() # Nivel de felicidad inicial

    def calcular_felicidad(self):
        """
        Calcula la felicidad usando la función Cobb-Douglas H = (T_E)^alfa * (T_R)^(1-alfa)
        Simplificada a H = (T - T_R)^alfa * T_R^(1-alfa)
        """
        # Aseguramos que el tiempo no sea cero para evitar log(0) o división por cero en modelos más complejos.
        T_E_val = max(0.001, self.T_total - self.T_R)
        T_R_val = max(0.001, self.T_R)

        # Implementación de la fórmula Cobb-Douglas
        return (T_E_val ** self.alfa) * (T_R_val ** (1 - self.alfa))

    def buscar_tr_optimo(self):
        """
        Método de optimización: el agente busca el T_R que maximiza H.
        En este ejemplo, usamos una búsqueda simple (fuerza bruta discreta).
        """
        mejor_H = -1
        mejor_T_R = self.T_R

        # Rango de T_R a probar (discretizado por minutos/horas)
        # Vamos a probar valores de T_R desde 0 hasta T_total en pasos de 0.1 (6 minutos)
        paso = 0.1
        posibles_T_R = np.arange(0, self.T_total + paso, paso)

        for T_R_prueba in posibles_T_R:
            T_E_prueba = self.T_total - T_R_prueba

            # La función Cobb-Douglas es maximizada por el tiempo *peso_del_factor
            # Aquí, solo validamos la restricción temporal
            if T_R_prueba >= 0 and T_E_prueba >= 0:
                H_prueba = (max(0.001, T_E_prueba) ** self.alfa) * (max(0.001, T_R_prueba) ** (1 - self.alfa))

                if H_prueba > mejor_H:
                    mejor_H = H_prueba
                    mejor_T_R = T_R_prueba

        # El agente actualiza sus variables a los valores óptimos
        self.T_R = mejor_T_R
        self.T_E = self.T_total - self.T_R
        self.H = mejor_H

    def step(self):
        """
        El método step define las acciones del agente en cada paso (día/ronda) de la simulación.
        """
        # En cada paso, el agente busca su asignación de tiempo óptima
        self.buscar_tr_optimo()
        # NOTA: Aquí se añadiría la lógica de Redes Sociales (R) en fases posteriores.