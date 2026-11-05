import osmnx as ox
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DATA_DIR
# this part is synthetic and is to be modified later on
def calculate_final_weights():
    print("Loading shaded graph...")
    G = ox.load_graphml(DATA_DIR / "campus_graph_shaded.graphml")
    nodes, edges = ox.graph_to_gdfs(G)

    base_air_temp = 38.0 
    relative_humidity = 65.0 
    time_multiplier = 1.2 

    def assign_surface_temp(row):
        surface = str(row.get('surface', 'asphalt')).lower()
        if 'asphalt' in surface or 'paved' in surface:
            return base_air_temp + 10.0
        elif 'dirt' in surface or 'grass' in surface:
            return base_air_temp + 2.0
        return base_air_temp + 5.0 

    edges['surface_temp_c'] = edges.apply(assign_surface_temp, axis=1)
    edges['water_point_nearby'] = np.random.choice([0, 1], p=[0.9, 0.1], size=len(edges))

    print("Calculating heat score weights...")
    
    def compute_heat_weight(row):
        base_heat = base_air_temp + (0.05 * relative_humidity)
        radiant_penalty = (row['surface_temp_c'] - base_air_temp) * 0.5
        total_raw_heat = (base_heat + radiant_penalty) * time_multiplier
        
        # Safely extract shade coverage (fixes the sequence error)
        shade_cov = row.get('shade_coverage', 0.0)
        if isinstance(shade_cov, pd.Series):
            shade_cov = shade_cov.iloc[0]
        elif isinstance(shade_cov, (list, tuple)):
            shade_cov = shade_cov[0] if len(shade_cov) > 0 else 0.0
        
        try:
            shade_cov = float(shade_cov)
        except (ValueError, TypeError):
            shade_cov = 0.0

        #    
        shade_mitigation = 1.0 - (shade_cov * 0.4) 
        water_relief = 0.85 if row['water_point_nearby'] == 1 else 1.0
        
        # Safely extract length (OSMnx lengths can also sometimes be lists)
        edge_length = row.get('length', 1.0)
        if isinstance(edge_length, pd.Series):
            edge_length = edge_length.iloc[0]
        elif isinstance(edge_length, (list, tuple)):
            edge_length = edge_length[0] if len(edge_length) > 0 else 1.0

        #main part of the programm ie the weight calculations    
        edge_weight = total_raw_heat * shade_mitigation * water_relief * float(edge_length)
        return max(0.1, edge_weight)

    edges['heat_score_weight'] = edges.apply(compute_heat_weight, axis=1)

    G_final = ox.graph_from_gdfs(nodes, edges)
    output_file = DATA_DIR / "campus_graph_final.graphml"
    ox.save_graphml(G_final, output_file)
    print(f"Success: Final routing graph saved to {output_file}")

if __name__ == "__main__":
    calculate_final_weights()