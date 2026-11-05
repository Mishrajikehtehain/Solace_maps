import osmnx as ox
import geopandas as gpd
import pandas as pd
import sys
from pathlib import Path

# Link to config.py
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import GRAPH_FILE, DATA_DIR

def apply_shade_to_graph():
    print("Loading graph, shadows, and trees...")
    G = ox.load_graphml(GRAPH_FILE)
    nodes, edges = ox.graph_to_gdfs(G)
    
    # Project edges to a local UTM coordinate system (meters) for accurate math
  # Use GeoPandas native projection to estimate the correct UTM zone for Bhubaneswar
    edges_proj = edges.to_crs(edges.estimate_utm_crs())
    
    # Load shadows and trees
    shadows = gpd.read_file(DATA_DIR / "campus_shadows.geojson")
    trees = gpd.read_file(DATA_DIR / "campus_trees.geojson")
    
    # Project to match the edges' coordinate system
    shadows_proj = shadows.to_crs(edges_proj.crs)
    trees_proj = trees.to_crs(edges_proj.crs)
    
    # Buffer trees by 5 meters to simulate canopy shade width
    trees_proj['geometry'] = trees_proj.buffer(5)
    
    print("Merging shadows and tree canopies...")
    all_shade_geoms = pd.concat([shadows_proj.geometry, trees_proj.geometry])
    total_shade_poly = all_shade_geoms.unary_union
    
    print("Calculating shade coverage for each walking path...")
    def calculate_coverage(edge_geom):
        if not edge_geom.intersects(total_shade_poly):
            return 0.0
        intersection = edge_geom.intersection(total_shade_poly)
        # Ratio of shaded length vs total edge length
        return round(intersection.length / edge_geom.length, 2)
        
    edges_proj['shade_coverage'] = edges_proj['geometry'].apply(calculate_coverage)
    
    # Transfer the calculated shade column back to the original lat/lon edges
    edges['shade_coverage'] = edges_proj['shade_coverage']
    
    # Rebuild and save the updated graph
    G_shaded = ox.graph_from_gdfs(nodes, edges)
    output_file = DATA_DIR / "campus_graph_shaded.graphml"
    ox.save_graphml(G_shaded, output_file)
    print(f"Success: Shaded graph saved to {output_file}")

if __name__ == "__main__":
    apply_shade_to_graph()