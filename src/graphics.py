import mesa
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.visualization.modules import CanvasGrid, TextElement, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Slider
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

# --- 2. LAYOUT DASHBOARD ---
class DashboardLayout(TextElement):
    def render(self, model):
        return """
        <style>
        .container-fluid {
            display: grid !important;
            grid-template-columns: 360px 1fr;
            grid-template-rows: auto 1fr;
            gap: 15px; padding: 15px; height: 95vh; max-width: 100% !important;
        }
        .navbar { margin-bottom: 0px !important; }
        .chart-container { grid-column: 1; grid-row: 1; width: 100% !important; border: 1px solid #ddd; border-radius: 6px; padding: 8px; background: white;}
        .mesa-canvas { grid-column: 2; grid-row: 1 / span 2; width: 100% !important; height: 100% !important; display: flex; justify-content: center; }
        .mesa-text { grid-column: 1; grid-row: 2; width: 100% !important; height: 100% !important; overflow-y: auto; background: #f9f9f9; border: 1px solid #ccc; border-radius: 6px; padding: 10px; font-family: 'Segoe UI', sans-serif; }
        h4 { margin-top: 0; border-bottom: 2px solid #555; padding-bottom: 5px; }
        .stat-group { background: #fff; border: 1px solid #eee; padding: 8px; margin-bottom: 8px; border-radius: 4px; }
        .stat-row { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 3px; border-bottom: 1px dotted #eee; padding-bottom: 2px;}
        .val { font-weight: bold; }
        </style>
        """

# --- 3. ESTADÍSTICAS EN VIVO ---
class ComparisonStats(TextElement):
    def render(self, model):
        agents = model.schedule.agents
        if not agents: return "Cargando..."
        
        # Clasificación
        v_unhappy = [a for a in agents if a.happiness <= 1.5]
        unhappy   = [a for a in agents if 1.5 < a.happiness <= 2.5]
        neutral   = [a for a in agents if 2.5 < a.happiness <= 3.5]
        happy     = [a for a in agents if 3.5 < a.happiness <= 4.5]
        v_happy   = [a for a in agents if a.happiness > 4.5]
        
        # Cálculo de medias
        def get_mean_inc(ag_list):
            return np.mean([a.effective_income for a in ag_list]) if ag_list else 0

        i_v_unhappy = get_mean_inc(v_unhappy)
        i_unhappy   = get_mean_inc(unhappy)
        i_neutral   = get_mean_inc(neutral)
        i_happy     = get_mean_inc(happy)
        i_v_happy   = get_mean_inc(v_happy)
        
        # Datos globales y validación SMI
        all_incomes = [a.effective_income for a in agents]
        min_detected = min(all_incomes) if all_incomes else 0
        avg_income = np.mean(all_incomes) if all_incomes else 0
        smi_val = model.min_wage

        # Color de validación (Si el mínimo detectado < SMI, algo va mal)
        smi_check_color = "green" if min_detected >= smi_val else "red"

        return f"""
        <h4> ESTADO DE LA RED (Paso {model.schedule.steps})</h4>
        
        <div class='stat-group' style='background: #e3f2fd;'>
             <div class='stat-row'><b>SALARIO MÍNIMO (SMI):</b> <span class='val' style='font-size:14px'>{smi_val}€</span></div>
             <div class='stat-row'>Renta Mínima Detectada: <span class='val' style='color:{smi_check_color}'>{min_detected:.0f}€</span></div>
             <div class='stat-row'>Renta Media Global: <span class='val'>{avg_income:.0f}€</span></div>
             <div style='font-size:10px; color:#666; margin-top:5px;'>(Pulsa <b>Reset</b> tras mover el Slider)</div>
        </div>

        <div class='stat-group'>
            <div class='stat-row' style='margin-bottom:8px'><b>DISTRIBUCIÓN (Población | Sueldo Medio)</b></div>
            
            <div class='stat-row'>
                <span style='color:DarkBlue'>● Muy Feliz (>4):</span> 
                <span class='val'>{len(v_happy)} pax | {i_v_happy:.0f}€</span>
            </div>
            <div class='stat-row'>
                <span style='color:LightGreen'>● Feliz (>3):</span> 
                <span class='val'>{len(happy)} pax | {i_happy:.0f}€</span>
            </div>
            <div class='stat-row'>
                <span style='color:Gold'>● Neutro (=3):</span> 
                <span class='val'>{len(neutral)} pax | {i_neutral:.0f}€</span>
            </div>
            <div class='stat-row'>
                <span style='color:Red'>● Infeliz (2):</span> 
                <span class='val'>{len(unhappy)} pax | {i_unhappy:.0f}€</span>
            </div>
            <div class='stat-row'>
                <span style='color:DarkRed'>● Muy Infeliz (1):</span> 
                <span class='val'>{len(v_unhappy)} pax | {i_v_unhappy:.0f}€</span>
            </div>
        </div>
        """

# --- 4. DATA COLLECTION ---
def get_avg_happiness(model):
    return np.mean([a.happiness for a in model.schedule.agents])

# --- 5. AGENTE ---
class DynamicSocialAgent(Agent):
    def __init__(self, unique_id, model, income_code, happiness_val, sociability_val):
        super().__init__(unique_id, model)
        # 1. Economía
        self.original_income = MAPA_INGRESOS.get(int(income_code), 300)
        
        # APLICAR POLÍTICA DESDE EL INICIO
        smi = getattr(self.model, 'min_wage', 0)
        self.effective_income = max(self.original_income, smi)
        
        # 2. Felicidad
        self.happiness = float(happiness_val)
        self.original_base_happiness = self.happiness 
        self.current_base_happiness = self.happiness  
        
        # Si ya empiezo con subsidio, ajusto mi felicidad base inicial
        if self.effective_income > self.original_income:
            boost = ((self.effective_income - self.original_income) / 1000.0) * 0.8
            self.current_base_happiness = min(5, self.original_base_happiness + boost)
            # También subo la felicidad actual para que se note
            self.happiness = min(5, self.happiness + boost)

        # 3. Sociabilidad
        self.sociability = float(sociability_val) 
        self.social_threshold = 5.0 

    def update_color(self):
        h = self.happiness
        if h <= 1.5: return "DarkRed"
        if h <= 2.5: return "Red"
        if h <= 3.5: return "Gold"
        if h <= 4.5: return "LightGreen"
        return "DarkBlue"

    def apply_economic_policy(self):
        # Leemos el SMI actual del modelo
        smi = self.model.min_wage
        
        # GARANTIZAR SUELDO MÍNIMO
        self.effective_income = max(self.original_income, smi)
        
        # Calcular impacto emocional
        if self.effective_income > self.original_income:
            extra_money = self.effective_income - self.original_income
            # Factor de impacto: +0.8 felicidad por cada 1000€ regalados
            boost = (extra_money / 1000.0) * 0.8 
            self.current_base_happiness = min(5, self.original_base_happiness + boost)
        else:
            self.current_base_happiness = self.original_base_happiness

    def move_logic(self):
        if self.happiness < 2.0:
            if self.random.random() < 0.6: self.move_randomly()
            return
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
        if self.random.random() < 0.05:
            self.move_randomly()

    def emotional_balance(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        social_delta = 0
        if neighbors:
            avg_h = np.mean([n.happiness for n in neighbors])
            social_delta = (avg_h - self.happiness) * 0.05

        personality_delta = (self.current_base_happiness - self.happiness) * 0.1
        life_noise = self.random.uniform(-0.05, 0.05)

        self.happiness += social_delta + personality_delta + life_noise
        self.happiness = max(0, min(5, self.happiness))

    def move_randomly(self):
        x = self.random.randrange(self.model.grid.width)
        y = self.random.randrange(self.model.grid.height)
        self.model.grid.move_agent(self, (x, y))

    def step(self):
        self.apply_economic_policy()
        self.move_logic()
        self.emotional_balance()

# --- 6. MODELO ---
class SocialEvolutionModel(Model):
    def __init__(self, N, width, height, excel_file_path, min_wage=0):
        super().__init__()
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.min_wage = min_wage 
        
        print(f"Cargando datos: {excel_file_path}")
        try:
            df = pd.read_excel(excel_file_path)
            h_vals = df.iloc[:, 0].tolist()
            s_vals = df.iloc[:, 1].tolist()
            if df.shape[1] > 2:
                inc_vals = df.iloc[:, 2].tolist()
            else:
                inc_vals = np.random.randint(1, 11, N)
        except:
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

# --- 7. LANZAMIENTO ---
def agent_portrayal(agent):
    if agent is None: return
    # Formato visual: Si es > 1000 usa "k", si no el número entero.
    txt = f"{agent.effective_income/1000:.1f}k" if agent.effective_income >= 1000 else f"{int(agent.effective_income)}"
    
    return {
        "Shape": "circle", "r": 0.8, "Filled": "true", "Layer": 0, 
        "Color": agent.update_color(),
        "text": txt, "text_color": "white" 
    }

def launch(name, filename, with_slider=False):
    path = get_data_path(filename)
    layout = DashboardLayout()
    chart = ChartModule([{"Label": "Felicidad Global", "Color": "Black"}], canvas_height=200)
    grid = CanvasGrid(agent_portrayal, 30, 30, 600, 600)
    stats = ComparisonStats()

    model_params = {
        "N": 300,
        "width": 30,
        "height": 30,
        "excel_file_path": path,
    }

    if with_slider:
        # Nota: El paso de 100 ayuda a ver cambios más granulares
        model_params["min_wage"] = Slider("Salario Mínimo (SMI)", 750, 0, 7000, 100)
    else:
        model_params["min_wage"] = 0 

    server = ModularServer(
        SocialEvolutionModel,
        [layout, chart, grid, stats], 
        f"Simulación: {name}",
        model_params
    )
    server.port = 8521
    server.launch()

if __name__ == "__main__":
    print("\n=== SIMULADOR DE DINÁMICA SOCIAL ===")
    print("1) Facebook (Estándar)")
    print("2) Instagram (Estándar)")
    print("3) X / Twitter (Estándar)")
    print("4) MODO EXPERIMENTAL: Facebook con Slider de Salario Mínimo")
    
    op = input("\nElige opción: ")
    
    files = {
        '1': ("Facebook", "model_FB.xlsx"), 
        '2': ("Instagram", "model_IG.xlsx"), 
        '3': ("X", "model_X.xlsx")
    }
    
    if op in files:
        launch(files[op][0], files[op][1], with_slider=False)
    elif op == '4':
        print("Iniciando Experimento Económico...")
        print("NOTA: Recuerda pulsar 'Reset' en el navegador tras mover el Slider.")
        launch("Facebook (Política Económica)", "model_FB.xlsx", with_slider=True)
    else:
        print("Opción no válida.")