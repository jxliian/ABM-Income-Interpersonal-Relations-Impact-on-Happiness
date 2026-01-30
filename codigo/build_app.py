import PyInstaller.__main__
import os
import shutil

# Clean previous builds
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')



# Find Mesa path to include templates
from PyInstaller.utils.hooks import collect_all

# Collect data and hidden imports for mesa and mesa_viz_tornado
mesa_datas, mesa_binaries, mesa_hiddenimports = collect_all('mesa')
mesa_viz_datas, mesa_viz_binaries, mesa_viz_hiddenimports = collect_all('mesa_viz_tornado')

# Combine collected data
all_datas = mesa_datas + mesa_viz_datas
all_hiddenimports = mesa_hiddenimports + mesa_viz_hiddenimports

# Definir la raíz del proyecto relativa a este script (codigo/build_app.py)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define additional data to include
# Format: (source_path, destination_path)
local_datas = [
    (os.path.join(ROOT_DIR, 'web', 'assets'), 'assets'), # Include assets from web/
    (os.path.join(ROOT_DIR, 'documentos_datos', 'data'), 'data'), # Include data from documentos_datos/
    (os.path.join(ROOT_DIR, 'documentos_datos', 'clean_data'), 'clean_data'), # Include clean_data from documentos_datos/
    (os.path.join(ROOT_DIR, 'codigo', 'src'), 'src'), # Include src from codigo/
]

# Construct the --add-data argument
add_data_args = []
sep = ';' if os.name == 'nt' else ':' # Windows uses ;, Linux uses :

# Add local datas
for src, dest in local_datas:
    if os.path.exists(src):
        add_data_args.append(f'--add-data={src}{sep}{dest}')
    else:
        print(f"WARNING: Source path not found: {src}")

# Add collected datas from PyInstaller hooks (already in (src, dest) format, but dest might be relative)
# collect_all ensures datas are (src, dest)
for src, dest in all_datas:
    add_data_args.append(f'--add-data={src}{sep}{dest}')

# PyInstaller arguments
args = [
    os.path.join(ROOT_DIR, 'codigo', 'src', 'main_gui.py'), # Entry point
    '--name=ABM_Happiness_Tool',
    '--onefile', # Single executable
    '--windowed', # No console window (GUI only)
    '--clean',
    '--hidden-import=pandas',
    '--hidden-import=openpyxl',
] + [f'--hidden-import={h}' for h in all_hiddenimports] + add_data_args

print("Running PyInstaller with args:")
# Print first few args to avoid spamming console with hundreds of data files
print(args[:10] + ['... (and many data files)'])

PyInstaller.__main__.run(args)
