import mesa
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
import pandas as pd
import os
import sys

# --- 1. GESTIÓN DE RUTAS RELATIVAS ---
def obtener_ruta_datos(nombre_archivo):
    """
    Busca el archivo en la carpeta hermana 'clean_data' 
    sin importar en qué PC estemos.
    """
    try:
        # Ubicación de este script (dentro de src)
        dir_script = os.path.dirname(os.path.abspath(__file__))
        # Subir un nivel a la raíz
        dir_raiz = os.path.dirname(dir_script)
        # Bajar a clean_data
        ruta = os.path.join(dir_raiz, 'clean_data', nombre_archivo)
        return ruta
    except Exception as e:
        print(f"Error construyendo la ruta: {e}")
        return nombre_archivo

# --- 2. DEFINICIÓN DEL AGENTE (Común para las 3 redes) ---
class MyAgent(Agent):
    def __init__(self, unique_id, model, happiness, color):
        super().__init__(unique_id, model)
        self.happiness = happiness
        self.color = color

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def step(self):
        self.move()

# --- 3. DEFINICIÓN DEL MODELO (Común para las 3 redes) ---
class MyModel(Model):
    def __init__(self, N, width, height, excel_file_path):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True # Necesario para que el botón Start funcione correctamente en nuevas versiones

        print(f"Cargando datos desde: {excel_file_path}")
        
        try:
            # Leer excel (header=None según tu código original)
            df = pd.read_excel(excel_file_path, header=None)
            happiness_values = df.iloc[:, 0].tolist()
        except FileNotFoundError:
            print(f"ERROR CRÍTICO: No se encontró el archivo: {excel_file_path}")
            # Generar datos dummy para que no crashee el servidor si falta el archivo
            happiness_values = [0] * N 
        except Exception as e:
            print(f"Error leyendo el Excel: {e}")
            happiness_values = [0] * N

        # Mapeo de valores a colores
        color_mapping = {
            0: "Red",
            1: "Orange",
            2: "Yellow",
            3: "Green",
            4: "LightBlue",
            5: "DarkBlue"
        }

        for i in range(self.num_agents):
            # Ciclo por los valores si hay menos datos que agentes
            if len(happiness_values) > 0:
                happiness = happiness_values[i % len(happiness_values)]
            else:
                happiness = 0
            
            color = color_mapping.get(happiness, "Grey")
            
            a = MyAgent(i, self, happiness, color)
            self.schedule.add(a)
            
            # Ubicación aleatoria
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.datacollector = DataCollector(
            agent_reporters={"Pos": "pos"}
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

# --- 4. VISUALIZACIÓN ---
def agent_portrayal(agent):
    if agent is None:
        return
    portrayal = {"Shape": "circle", "r": 0.7, "Filled": "true", "Layer": 0, "Color": agent.color}
    return portrayal

def lanzar_servidor(nombre_red, n_agentes, nombre_archivo, puerto=8521):
    ruta_archivo = obtener_ruta_datos(nombre_archivo)
    
    if not os.path.exists(ruta_archivo):
        print(f"\n ERROR: El archivo '{nombre_archivo}' no existe en la carpeta clean_data.")
        input("Presiona ENTER para volver al menú...")
        return

    print(f"\n>>> Iniciando simulación para: {nombre_red}")
    print(f">>> Agentes: {n_agentes}")
    print(f">>> Archivo: {ruta_archivo}")
    print(">>> Abre tu navegador en http://127.0.0.1:{}/ si no se abre automáticamente.".format(puerto))
    print(">>> Presiona Ctrl+C en esta consola para detener el servidor y volver al menú (o salir).\n")

    grid = CanvasGrid(agent_portrayal, 50, 50, 500, 500)

    try:
        server = ModularServer(
            MyModel,
            [grid],
            f"Modelo Felicidad: {nombre_red}",
            {"N": n_agentes, "width": 50, "height": 50, "excel_file_path": ruta_archivo}
        )
        server.port = puerto
        server.launch()
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
    except Exception as e:
        print(f"Error lanzando el servidor: {e}")

# --- 5. MENÚ PRINCIPAL ---
def menu():
    # Configuración de cada red según tus códigos originales
    config = {
        'ig': {'name': 'Instagram', 'N': 267, 'file': 'model_IG.xlsx'},
        'tw': {'name': 'Twitter (X)', 'N': 371, 'file': 'model_X.xlsx'},
        'fb': {'name': 'Facebook', 'N': 1063, 'file': 'model_FB.xlsx'}
    }

    while True:
        print("\n========================================")
        print("   VISUALIZADOR DE AGENTES (MESA)       ")
        print("========================================")
        print("Si quieres ejecutar uno diferente, sal (Ctrl+C) , y vuelve a ejecutar.")
        print("1. Visualizar Instagram (N=267)")
        print("2. Visualizar Twitter/X (N=371)")
        print("3. Visualizar Facebook  (N=1063)")
        print("4. Ejecutar Secuencia (Una tras otra. Modo Experimental. En trabajo)")
        print("5. Salir")
        
        opcion = input("\nSeleccione una opción (1-5): ")

        if opcion == '1':
            lanzar_servidor(config['ig']['name'], config['ig']['N'], config['ig']['file'])
        
        elif opcion == '2':
            lanzar_servidor(config['tw']['name'], config['tw']['N'], config['tw']['file'])
        
        elif opcion == '3':
            lanzar_servidor(config['fb']['name'], config['fb']['N'], config['fb']['file'])
        
        elif opcion == '4':
            print("\n!!! MODO SECUENCIA !!!")
            print("Se lanzará Instagram. Cuando cierres el servidor (Ctrl+C), se lanzará Twitter, etc.")
            input("Presiona ENTER para comenzar...")
            lanzar_servidor(config['ig']['name'], config['ig']['N'], config['ig']['file'])
            print("\n--- Siguiente: Twitter ---")
            lanzar_servidor(config['tw']['name'], config['tw']['N'], config['tw']['file'])
            print("\n--- Siguiente: Facebook ---")
            lanzar_servidor(config['fb']['name'], config['fb']['N'], config['fb']['file'])
            print("\nSecuencia terminada.")

        elif opcion == '5':
            print("Saliendo...")
            sys.exit()
        
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    # Necesario para evitar problemas con asyncio en algunos entornos de windows/notebooks
    # aunque en script puro de python suele ir bien.
    menu()