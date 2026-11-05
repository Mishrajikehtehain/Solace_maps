import osmnx as ox
import sys
from pathlib import Path

# Link to config.py
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import CAMPUS_POINT, CAMPUS_RADIUS, GRAPH_FILE

def fetch_campus():
    print(f"Fetching walkable network around {CAMPUS_POINT} with {CAMPUS_RADIUS}m radius...")
    
    # Download using exact coordinates instead of name
    G = ox.graph_from_point(CAMPUS_POINT, dist=CAMPUS_RADIUS, network_type='walk')
    
    # Extract to verify
    nodes, edges = ox.graph_to_gdfs(G)
    print(f"Success: Loaded {len(nodes)} nodes and {len(edges)} walking paths.")
    
    # Save the graph
    ox.save_graphml(G, GRAPH_FILE)
    print(f"Graph saved offline to {GRAPH_FILE}")

if __name__ == "__main__":
    fetch_campus()