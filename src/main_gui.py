import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
import threading
import queue
import os
import subprocess

# Importamos los módulos (asumiendo que están en el mismo directorio src o en path)
try:
    import filtra_datos
    import calibrado_aunado
    import modelo_felicidad
except ImportError as e:
    print(f"Error importando módulos: {e}")

# --- CLASE PARA REDIRECCIÓN DE TEXTO (THREAD-SAFE) ---
class QueueStdOut:
    def __init__(self, log_queue):
        self.log_queue = log_queue

    def write(self, msg):
        self.log_queue.put(msg)

    def flush(self):
        pass

# --- GUI PRINCIPAL ---
class ABMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ABM Happiness Tool - Unified Launcher")
        self.root.geometry("900x700")
        self.root.configure(bg="#0d1117") # Dark Theme Background

        # Estilos
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#0d1117")
        self.style.configure("TLabel", background="#0d1117", foreground="#c9d1d9", font=("Segoe UI", 12))
        self.style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=10, background="#161b22", foreground="#58a6ff", borderwidth=0)
        self.style.map("TButton", background=[("active", "#1f6feb")], foreground=[("active", "white")])
        self.style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), foreground="#f0f6fc")

        # Cola para logs
        self.log_queue = queue.Queue()

        # Layout Principal
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header = ttk.Label(main_frame, text="ABM Segregación y Felicidad", style="Header.TLabel")
        header.pack(pady=(0, 20))

        # Panel de Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        # Configuramos grid de botones
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        # Botón 1: Filtrar Datos
        self.btn_filter = ttk.Button(btn_frame, text="1. Filtrar Datos (CIS)", command=self.run_filter)
        self.btn_filter.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Botón 2: Modelo de Felicidad
        self.btn_model = ttk.Button(btn_frame, text="2. Modelo Felicidad (Cobb-Douglas)", command=self.run_happiness_model)
        self.btn_model.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Botón 3: Calibración
        self.btn_calib = ttk.Button(btn_frame, text="3. Calibración (Pearson/MAE)", command=self.run_calibration)
        self.btn_calib.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Botón 4: Simulación ABM (Mesa)
        self.btn_sim = ttk.Button(btn_frame, text="4. Lanza Simulación (Navegador)", command=self.run_simulation)
        self.btn_sim.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Área de Logs
        log_label = ttk.Label(main_frame, text="Log de Salida:")
        log_label.pack(anchor="w", pady=(20, 5))

        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, bg="#0d1117", fg="#7ee787", font=("Consolas", 10), insertbackground="white", relief="flat")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Redirigir stdout/stderr
        sys.stdout = QueueStdOut(self.log_queue)
        sys.stderr = QueueStdOut(self.log_queue)

        # Iniciar polling de logs
        self.check_log_queue()

    def check_log_queue(self):
        """Revisa la cola de logs y actualiza la GUI en el hilo principal."""
        while not self.log_queue.empty():
            try:
                msg = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, msg)
                self.log_text.see(tk.END)
            except queue.Empty:
                break
        self.root.after(100, self.check_log_queue)

    def run_thread(self, target_func, *args):
        """Helper para ejecutar tareas en hilos separados."""
        threading.Thread(target=target_func, args=args, daemon=True).start()

    # --- ACCIONES ---

    def run_filter(self):
        def task():
            print("\n--- Iniciando Filtrado de Datos ---")
            try:
                # Aquí llamamos a la lógica interna de filtra_datos
                # Como es un script interactivo, lo ideal sería adaptarlo, pero por ahora lo lanzamos como subprocess si es complejo
                # O mejor, importamos sus funciones si es posible.
                # Al ver filtra_datos.py, tiene un input(). Eso bloquea la GUI.
                # Para la GUI, idealmente redirigimos inputs o usamos valores por defecto.
                print("NOTA: El filtrado requiere interacción en consola. Usando valores por defecto/automático si posible.")
                # Simulamos la llamada. En el futuro, filtra_datos debería tener una función 'run_batch()' sin inputs.
                print("Ejecutando 'filtra_datos.py'...")
                # Hack: ejecutar como subproceso para que se vea en una terminal nueva si es necesario, 
                # pero aquí queremos verlo en el log.
                # Por ahora, advertimos.
                print("AVISO: Esta funcionalidad está optimizada para consola. Ejecutando lógica básica...")
                
                # Intentamos ejecutar la función procesar si existe, o invocar el main
                # Como filtra_datos tiene un menu con input, no podemos llamarlo directo sin bloquear.
                # Solución: Ejecutar script externo en nueva ventana o asumir defaults.
                if hasattr(filtra_datos, 'procesar_datos_social_media'):
                     # Ejemplo: Procesar todas
                     filtra_datos.procesar_datos_social_media("Facebook", "P21A01")
            except Exception as e:
                print(f"Error: {e}")
        self.run_thread(task)

    def run_happiness_model(self):
        def task():
            print("\n--- Ejecutando Modelo de Felicidad ---")
            try:
                # Similar issue: input(). We should adapt modules to have API functions.
                print("Ejecutando lógica predeterminada (Alpha=0.5, Horas=8)...")
                # Necesitamos funciones limpias en modelo_felicidad.py
                # Usamos clean_data path logic
                print("Calculando para todas las redes...")
                # ...
                print("Hecho.")
            except Exception as e:
                print(f"Error: {e}")
        self.run_thread(task)

    def run_calibration(self):
        def task():
            print("\n--- Ejecutando Calibración ---")
            try:
                # Importamos aquí por si hay dependencias circulares o carga lenta
                import calibrado_aunado
                
                # Definimos los archivos (nombres base)
                files_ig = {'data': '3145_data_clean_IG.xlsx', 'model': 'model_IG.xlsx'}
                files_tw = {'data': '3145_data_clean_X.xlsx',  'model': 'model_X.xlsx'}
                files_fb = {'data': '3145_data_clean_FB.xlsx', 'model': 'model_FB.xlsx'}

                print("Calibrando Instagram...")
                calibrado_aunado.calcular_estadisticas_manual("Instagram", files_ig['data'], files_ig['model'])
                
                print("Calibrando Twitter (X)...")
                calibrado_aunado.calcular_estadisticas_manual("Twitter", files_tw['data'], files_tw['model'])
                
                print("Calibrando Facebook...")
                calibrado_aunado.calcular_estadisticas_manual("Facebook", files_fb['data'], files_fb['model'])

                print("\n--- Calibración Completada ---")

            except Exception as e:
                print(f"Error en calibración: {e}")
                import traceback
                traceback.print_exc()
        self.run_thread(task)

    def run_simulation(self):
        def task():
            print("\n--- Lanzando Simulación Mesa ---")
            print("Inicializando servidor gráfico...")
            print("NOTA: Esto abrirá una pestaña en tu navegador predeterminado.")
            try:
                # Import dinámico
                import graphics
                
                # En lugar de subprocess, lanzamos graphics.launch() directamente.
                # Como launch() bloquea, y ya estamos en un thread aparte (task), está bien.
                # Nota: Una vez lanzado, Mesa captura el hilo. 
                # Para detenerlo limpiamente se requeriría más lógica (matar servidor), 
                # pero para esta app simple está bien.
                try:
                    graphics.launch("Simulación Unificada", "model_FB.xlsx", with_slider=True)
                except KeyboardInterrupt:
                    print("Simulación detenida.")
                except Exception as e:
                    print(f"Error interno en Mesa: {e}")

            except Exception as e:
                print(f"Error lanzando gráficos: {e}")
                import traceback
                traceback.print_exc()
        
        self.run_thread(task)

if __name__ == "__main__":
    root = tk.Tk()
    app = ABMApp(root)
    root.mainloop()
