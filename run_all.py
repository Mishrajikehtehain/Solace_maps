import subprocess
import sys

# List of scripts in exact execution order
pipeline = [
    "scripts/01_fetch_graph.py",
    "scripts/02_fetch_buildings.py",
    "scripts/03_fetch_trees.py",
    "scripts/05_project_shadows.py",
    "scripts/06_apply_shade.py"
]

for script in pipeline:
    print(f"\n========== RUNNING: {script} ==========")
    # sys.executable ensures it uses your active venv Python
    result = subprocess.run([sys.executable, script]) 
    
    if result.returncode != 0:
        print(f"\n[!] Pipeline stopped due to an error in {script}.")
        sys.exit(1)

print("\n========== PIPELINE COMPLETE ==========")