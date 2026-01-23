import PyInstaller.__main__
import os
import shutil

# Clean previous builds
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

# Find Mesa path to include templates
import mesa
mesa_path = os.path.dirname(mesa.__file__)
# We need to include the 'visualization/templates' directory
mesa_templates = os.path.join(mesa_path, 'visualization', 'templates')

print(f"Mesa path found: {mesa_path}")

# Defines aditional data to include
# Format: (source_path, destination_path)
datas = [
    (mesa_templates, 'mesa/visualization/templates'), # Include Mesa HTML templates
    ('assets', 'assets'), # Include local assets (images, css)
    ('data', 'data'), # Include initial data
    ('src', 'src'), # Include src for dynamic imports if needed
]

# Construct the --add-data argument
add_data_args = []
sep = ';' if os.name == 'nt' else ':' # Windows uses ;, Linux uses :

for src, dest in datas:
    if os.path.exists(src):
        add_data_args.append(f'--add-data={src}{sep}{dest}')
    else:
        print(f"WARNING: Source path not found: {src}")

# PyInstaller arguments
args = [
    'src/main_gui.py', # Entry point
    '--name=ABM_Happiness_Tool',
    '--onefile', # Single executable
    '--windowed', # No console window (GUI only)
    '--clean',
    '--hidden-import=mesa',
    '--hidden-import=mesa.visualization.modules',
    '--hidden-import=pandas',
    '--hidden-import=openpyxl',
] + add_data_args

print("Running PyInstaller with args:")
print(args)

PyInstaller.__main__.run(args)
