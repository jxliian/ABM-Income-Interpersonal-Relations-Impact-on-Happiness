import mesa
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
import pandas as pd
import numpy as np
import os
import sys

# --- 1. GESTIÓN DE RUTAS ---
def obtener_ruta_datos(nombre_archivo):
    try:
        dir_script = os.path.dirname(os.path.abspath(__file__))
        dir_raiz = os.path.dirname(dir_script)
        ruta = os.path.join(dir_raiz, 'clean_data', nombre_archivo)
        return ruta
    except Exception as e:
        print(f"Error construyendo ruta: {e}")
        return nombre_archivo

# --- 2. AGENTE CON INTELIGENCIA SOCIAL ---
class SocialAgent(Agent):
    def __init__(self, unique_id, model, happiness, sociability):
        super().__init__(unique_id, model)
        self.happiness = float(happiness)
        self.sociability = float(sociability)
        
        # Definimos un umbral: ¿Qué consideramos "sociable"?
        # Si la sociabilidad es alta (> 5 por ejemplo, depende de tu alpha), busca gente.
        # Ajusta este valor según tus datos reales.
        self.social_threshold = 2.0 

    def update_color(self):
        """Actualiza el color basado en la felicidad actual redondeada."""
        val = int(round(max(0, min(5, self.happiness))))
        color_mapping = {
            0: "Red", 1: "Orange", 2: "Yellow", 
            3: "Green", 4: "LightBlue", 5: "DarkBlue"
        }
        return color_mapping.get(val, "Grey")

    def move_smart(self):
        """
        Movimiento basado en Sociabilidad:
        - Si soy sociable: Prefiero celdas con vecinos.
        - Si soy antisocial: Prefiero celdas vacías.
        """
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        
        # Clasificamos las celdas posibles
        candidates = []
        for step in possible_steps:
            # Contamos agentes en esa celda candidata (usamos get_cell_list_contents)
            occupants = self.model.grid.get_cell_list_contents([step])
            count = len(occupants)
            candidates.append((step, count))
        
        if not candidates:
            return

        # Lógica de decisión
        if self.sociability > self.social_threshold:
            # --- COMPORTAMIENTO GREGARIO (Busca multitud) ---
            # Ordenamos descendente por cantidad de ocupantes
            candidates.sort(key=lambda x: x[1], reverse=True)
            # Intentamos ir a donde haya más gente, pero con un poco de aleatoriedad
            # para no quedar estancados
            best_steps = [c[0] for c in candidates if c[1] >= candidates[0][1]]
        else:
            # --- COMPORTAMIENTO ERMITAÑO (Busca soledad) ---
            # Ordenamos ascendente (preferimos 0 ocupantes)
            candidates.sort(key=lambda x: x[1], reverse=False)
            best_steps = [c[0] for c in candidates if c[1] <= candidates[0][1]]
            
        new_position = self.random.choice(best_steps)
        self.model.grid.move_agent(self, new_position)

    def interact_and_influence(self):
        """
        Calcula la media de felicidad de los vecinos y ajusta la propia.
        La intensidad del cambio depende de la sociabilidad.
        """
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        
        if len(neighbors) > 0:
            avg_happiness = np.mean([a.happiness for a in neighbors])
            
            # Factor de permeabilidad: Cuanto más sociable, más te afecta el entorno.
            # Normalizamos un poco para que el cambio no sea drástico instantáneamente.
            # Supongamos que sociabilidad va de 0 a 10 aprox.
            permeability = min(0.3, self.sociability * 0.05) 
            
            # Fórmula de difusión: Nueva = Vieja + Tasa * (Objetivo - Vieja)
            delta = (avg_happiness - self.happiness) * permeability
            
            self.happiness += delta
            
            # Mantenemos la felicidad en rangos lógicos (0 a 5)
            self.happiness = max(0, min(5, self.happiness))

    def step(self):
        self.move_smart()
        self.interact_and_influence()

# --- 3. MODELO ---
class SocialModel(Model):
    def __init__(self, N, width, height, excel_file_path):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True 

        print(f"Cargando datos extendidos desde: {excel_file_path}")
        
        try:
            # Asumimos que la fila 1 son headers. 
            # Col 0 = Felicidad, Col 1 = Sociabilidad
            df = pd.read_excel(excel_file_path) # Detecta headers automáticamente
            
            # Si el excel no tiene headers y empieza directo con números, usa: header=None
            # Ajuste de seguridad:
            if isinstance(df.iloc[0,0], str): 
                # Parece que leyó headers como datos, recargamos
                pass 
            
            # Extraemos columnas. Ajusta nombres si tus columnas tienen nombres específicos
            # O usamos iloc para ir a lo seguro (columna 0 y columna 1)
            happiness_vals = df.iloc[:, 0].tolist()
            sociability_vals = df.iloc[:, 1].tolist()
            
        except Exception as e:
            print(f"Error leyendo Excel ({e}). Usando datos aleatorios.")
            happiness_vals = np.random.uniform(0, 5, N).tolist()
            sociability_vals = np.random.uniform(0, 5, N).tolist()

        for i in range(self.num_agents):
            # Obtener datos cíclicos si hay menos filas que agentes
            h_val = happiness_vals[i % len(happiness_vals)]
            s_val = sociability_vals[i % len(sociability_vals)]
            
            # Crear agente
            a = SocialAgent(i, self, h_val, s_val)
            self.schedule.add(a)
            
            # Ubicación aleatoria
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.datacollector = DataCollector(
            agent_reporters={"Felicidad": "happiness", "Sociabilidad": "sociability"}
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

# --- 4. VISUALIZACIÓN ---
def agent_portrayal(agent):
    if agent is None: return
    
    # El color cambia dinámicamente en cada paso
    color = agent.update_color()
    
    # El tamaño podría representar la sociabilidad (opcional)
    # radio = 0.5 + (agent.sociability / 10.0) 
    
    return {
        "Shape": "circle", 
        "r": 0.8, 
        "Filled": "true", 
        "Layer": 0, 
        "Color": color,
        # Mostramos info al pasar el mouse
        "text": f"H:{agent.happiness:.1f} S:{agent.sociability:.1f}", 
        "text_color": "black"
    }

def lanzar_servidor(nombre_red, n_agentes, nombre_archivo):
    ruta_archivo = obtener_ruta_datos(nombre_archivo)
    
    # Configuración de la rejilla
    grid = CanvasGrid(agent_portrayal, 30, 30, 600, 600) # 30x30 es mejor para ver interacciones que 50x50

    try:
        server = ModularServer(
            SocialModel,
            [grid],
            f"Dinámica Social: {nombre_red}",
            {"N": n_agentes, "width": 30, "height": 30, "excel_file_path": ruta_archivo}
        )
        server.port = 8521
        print(f"\nIniciando {nombre_red}...")
        server.launch()
    except Exception as e:
        print(f"Error: {e}")

# --- 5. MENÚ ---
if __name__ == "__main__":
    config = {
        '1': {'name': 'Facebook', 'N': 400, 'file': 'model_FB.xlsx'}, # N reducido para mejor visualización
        '2': {'name': 'Instagram', 'N': 267, 'file': 'model_IG.xlsx'},
        '3': {'name': 'X (Twitter)', 'N': 371, 'file': 'model_X.xlsx'}
    }

    print("=== SIMULACIÓN DE DINÁMICA SOCIAL ===")
    print("Los agentes se mueven e influyen según su sociabilidad.")
    print("1) Facebook")
    print("2) Instagram")
    print("3) X")
    
    op = input("Elige: ")
    if op in config:
        lanzar_servidor(config[op]['name'], config[op]['N'], config[op]['file'])
    else:
        print("Opción inválida")