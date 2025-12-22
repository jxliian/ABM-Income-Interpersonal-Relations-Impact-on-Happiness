import mesa
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid, TextElement, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
import pandas as pd
import numpy as np
import os

# --- 1. CONFIGURACIÓN ---
MAPA_INGRESOS = {
    1: 0, 2: 300, 3: 450, 4: 750, 5: 1050, 
    6: 1500, 7: 2100, 8: 2700, 9: 3750, 
    10: 5250, 11: 7000, 98: 0, 99: 0
}

def get_data_path(filename):
    try:
        dir_script = os.path.dirname(os.path.abspath(__file__))
        dir_root = os.path.dirname(dir_script)
        return os.path.join(dir_root, 'clean_data', filename)
    except:
        return filename

# --- 2. LAYOUT "DASHBOARD" (DISEÑO PROFESIONAL) ---
class DashboardLayout(TextElement):
    def render(self, model):
        return """
        <style>
        /* CONTENEDOR PRINCIPAL */
        .container-fluid {
            display: grid !important;
            grid-template-columns: 360px 1fr;
            grid-template-rows: auto 1fr;
            gap: 15px;
            padding: 15px;
            height: 95vh;
            max-width: 100% !important;
        }

        .navbar { margin-bottom: 0px !important; }

        /* ===== GRÁFICO (izquierda arriba) ===== */
        .chart-container {
            grid-column: 1;
            grid-row: 1;
            width: 100% !important;
            background: #ffffff;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 8px;
        }

        /* ===== MAPA (derecha, toda la altura) ===== */
        .mesa-canvas {
            grid-column: 2;
            grid-row: 1 / span 2;
            width: 100% !important;
            height: 100% !important;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        /* ===== ESTADÍSTICAS (izquierda abajo) ===== */
        .mesa-text {
            grid-column: 1;
            grid-row: 2;
            width: 100% !important;
            height: 100% !important;
            overflow-y: auto;
            background: #f9f9f9;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 10px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* ESTILO INTERNO */
        h4 {
            margin-top: 0;
            font-size: 14px;
            font-weight: 700;
            color: #333;
            border-bottom: 2px solid #555;
            padding-bottom: 5px;
        }

        .stat-group {
            background: #fff;
            border: 1px solid #eee;
            padding: 8px;
            margin-bottom: 8px;
            border-radius: 4px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }

        .stat-row {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            margin-bottom: 3px;
        }

        .val { font-weight: bold; }
        .inc-up { color: #2e7d32; }
        .inc-down { color: #c62828; }
        </style>
        """


# --- 3. ESTADÍSTICAS EN VIVO ---
class ComparisonStats(TextElement):
    def render(self, model):
        agents = model.schedule.agents
        if not agents: return "Cargando..."
        
        # Grupos actuales
        happy_group = [a for a in agents if a.happiness >= 3.0]
        unhappy_group = [a for a in agents if a.happiness < 3.0]
        
        # Medias
        inc_happy = np.mean([a.income for a in happy_group]) if happy_group else 0
        inc_unhappy = np.mean([a.income for a in unhappy_group]) if unhappy_group else 0
        
        soc_happy = np.mean([a.sociability for a in happy_group]) if happy_group else 0
        soc_unhappy = np.mean([a.sociability for a in unhappy_group]) if unhappy_group else 0
        
        # Brecha
        gap = inc_happy - inc_unhappy
        gap_fmt = f"+{gap:.0f}" if gap > 0 else f"{gap:.0f}"
        gap_color = "#2e7d32" if gap > 0 else "#c62828"

        return f"""
        <h4> DATOS EN VIVO (Paso {model.schedule.steps})</h4>
        
        <div class='stat-group' style='border-left: 4px solid #1976d2;'>
            <div class='stat-row' style='font-weight:bold; color:#1976d2;'> GRUPO FELIZ (H≥3.0)</div>
            <div class='stat-row'><span>Población:</span> <span class='val'>{len(happy_group)}</span></div>
            <div class='stat-row'><span>Sueldo Medio:</span> <span class='val inc-up'>{inc_happy:.0f} €</span></div>
            <div class='stat-row'><span>Sociabilidad:</span> <span class='val'>{soc_happy:.1f}</span></div>
        </div>

        <div class='stat-group' style='border-left: 4px solid #d32f2f;'>
            <div class='stat-row' style='font-weight:bold; color:#d32f2f;'> GRUPO INFELIZ (H<3.0)</div>
            <div class='stat-row'><span>Población:</span> <span class='val'>{len(unhappy_group)}</span></div>
            <div class='stat-row'><span>Sueldo Medio:</span> <span class='val inc-down'>{inc_unhappy:.0f} €</span></div>
            <div class='stat-row'><span>Sociabilidad:</span> <span class='val'>{soc_unhappy:.1f}</span></div>
        </div>
        
        <div class='stat-group' style='background: #e8f5e9; border: 1px solid #c8e6c9;'>
            <div class='stat-row' style='font-size:13px;'><b> BRECHA SALARIAL:</b></div>
            <div style='text-align:center; font-size:18px; font-weight:bold; color:{gap_color}; margin: 5px 0;'>{gap_fmt} €</div>
            <div style='font-size:10px; color:#555; text-align:center;'>¿El dinero da felicidad en esta red?</div>
        </div>
        """

# --- 4. DATA COLLECTION ---
def get_avg_happiness(model):
    return np.mean([a.happiness for a in model.schedule.agents])

# --- 5. AGENTE ---
class DynamicSocialAgent(Agent):
    def __init__(self, unique_id, model, income_code, happiness_val, sociability_val):
        super().__init__(unique_id, model)
        self.income = MAPA_INGRESOS.get(int(income_code), 300)
        self.happiness = float(happiness_val)
        self.base_happiness = self.happiness # Ancla de personalidad
        self.sociability = float(sociability_val) 
        self.social_threshold = 5.0 

    def update_color(self):
        val = int(round(self.happiness))
        if val <= 2: return "#d32f2f"    # Rojo
        if val == 3: return "#fbc02d"    # Amarillo
        return "#1976d2"                 # Azul

    def move_logic(self):
        # 1. INFELICES: Inquietos, se mudan
        if self.happiness < 2.5:
            if self.random.random() < 0.5: self.move_randomly()
            return

        # 2. SOCIABLES: Buscan gente
        if self.sociability > self.social_threshold:
            neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            best_pos = self.pos
            max_neighbors = -1
            for pos in neighbors:
                count = len(self.model.grid.get_cell_list_contents([pos]))
                if count > max_neighbors:
                    max_neighbors = count
                    best_pos = pos
            if best_pos != self.pos:
                self.model.grid.move_agent(self, best_pos)
            return

        # 3. INTROVERTIDOS: Se quedan quietos
        if self.random.random() < 0.05:
            self.move_randomly()

    def emotional_balance(self):
        # Influencia Social + Personalidad + Ruido
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        social_delta = 0
        if neighbors:
            avg_h = np.mean([n.happiness for n in neighbors])
            social_delta = (avg_h - self.happiness) * 0.05

        personality_delta = (self.base_happiness - self.happiness) * 0.02
        life_noise = self.random.uniform(-0.1, 0.1)

        self.happiness += social_delta + personality_delta + life_noise
        self.happiness = max(0, min(5, self.happiness))

    def move_randomly(self):
        x = self.random.randrange(self.model.grid.width)
        y = self.random.randrange(self.model.grid.height)
        self.model.grid.move_agent(self, (x, y))

    def step(self):
        self.move_logic()
        self.emotional_balance()

# --- 6. MODELO ---
class SocialEvolutionModel(Model):
    def __init__(self, N, width, height, excel_file_path):
        super().__init__()
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        
        print(f"Cargando: {excel_file_path}")
        try:
            df = pd.read_excel(excel_file_path)
            h_vals = df.iloc[:, 0].tolist()
            s_vals = df.iloc[:, 1].tolist()
            if df.shape[1] > 2:
                inc_vals = df.iloc[:, 2].tolist()
            else:
                inc_vals = np.random.randint(1, 11, N)
        except:
            print("Datos no encontrados, aleatorios.")
            h_vals = np.random.uniform(0, 5, N)
            s_vals = np.random.uniform(0, 10, N)
            inc_vals = np.random.randint(1, 11, N)

        for i in range(self.num_agents):
            h = h_vals[i % len(h_vals)]
            s = s_vals[i % len(s_vals)]
            inc = inc_vals[i % len(inc_vals)]
            
            a = DynamicSocialAgent(i, self, inc, h, s)
            self.schedule.add(a)
            
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.datacollector = DataCollector({
            "Felicidad Global": get_avg_happiness
        })

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

# --- 7. LANZADOR ---
def agent_portrayal(agent):
    if agent is None: return
    return {
        "Shape": "circle", "r": 0.8, "Filled": "true", "Layer": 0, 
        "Color": agent.update_color(),
        "text": f"{int(agent.income/1000)}k", "text_color": "white" 
    }

def launch(name, filename):
    path = get_data_path(filename)
    
    # 1. Layout (Estilo Dashboard)
    layout = DashboardLayout()
    
    # 2. Chart (Arriba Izquierda)
    chart = ChartModule([{"Label": "Felicidad Global", "Color": "Black"}], 
                        canvas_height=200, canvas_width=350)
    
    # 3. Grid (Derecha Completa)
    grid = CanvasGrid(agent_portrayal, 30, 30, 600, 600)
    
    # 4. Stats (Abajo Izquierda)
    stats = ComparisonStats()

    # EL ORDEN DE LA LISTA DEFINE LA POSICIÓN EN EL CSS
    # [Layout, Chart, Grid, Stats]
    server = ModularServer(
        SocialEvolutionModel,
        [layout, chart, grid, stats], 
        f"Estudio: {name}",
        {"N": 300, "width": 30, "height": 30, "excel_file_path": path}
    )
    server.port = 8521
    server.launch()

if __name__ == "__main__":
    print("=== DASHBOARD FINAL (DISEÑO GRID) ===")
    print("1) Facebook")
    print("2) Instagram")
    print("3) X (Twitter)")
    
    op = input("Selecciona Red: ")
    files = {'1': ("Facebook", "model_FB.xlsx"), '2': ("Instagram", "model_IG.xlsx"), '3': ("X", "model_X.xlsx")}
    
    if op in files:
        launch(files[op][0], files[op][1])
    else:
        launch("Facebook", "model_FB.xlsx")