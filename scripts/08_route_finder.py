import osmnx as ox
import networkx as nx
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DATA_DIR

def find_best_routes(start_lat, start_lon, end_lat, end_lon):
    print("Loading final routing graph...")
    G = ox.load_graphml(DATA_DIR / "campus_graph_final.graphml")
    
    # Convert GraphML text attributes back to numbers for math operations
    for u, v, k, data in G.edges(keys=True, data=True):
        if 'heat_score_weight' in data:
            data['heat_score_weight'] = float(data['heat_score_weight'])
        if 'length' in data:
            data['length'] = float(data['length'])
    
    # Snap GPS coordinates to the nearest valid walking nodes on the graph
    orig_node = ox.distance.nearest_nodes(G, X=start_lon, Y=start_lat)
    dest_node = ox.distance.nearest_nodes(G, X=end_lon, Y=end_lat)
    
    print(f"Routing from Node {orig_node} to Node {dest_node}...\n")
    
    # 1. Standard Path (Optimized purely for distance)
    shortest_path = nx.shortest_path(G, orig_node, dest_node, weight='length')
    shortest_dist = nx.shortest_path_length(G, orig_node, dest_node, weight='length')
    shortest_heat = sum(min(G.get_edge_data(u, v).values(), key=lambda d: d['heat_score_weight'])['heat_score_weight'] for u, v in zip(shortest_path[:-1], shortest_path[1:]))
    
    # 2. Coolest Path (Optimized for shade and heat reduction)
    coolest_path = nx.shortest_path(G, orig_node, dest_node, weight='heat_score_weight')
    coolest_heat = nx.shortest_path_length(G, orig_node, dest_node, weight='heat_score_weight')
    
    # Calculate actual walking distance for the coolest path natively
    coolest_dist = sum(min(G.get_edge_data(u, v).values(), key=lambda d: d['length'])['length'] for u, v in zip(coolest_path[:-1], coolest_path[1:]))
    
    print("=== ROUTING RESULTS ===")
    print(f"Shortest Path: {shortest_dist:.1f} meters | Heat Score: {shortest_heat:.1f}")
    print(f"Coolest Path:  {coolest_dist:.1f} meters | Heat Score: {coolest_heat:.1f}")
    
    if shortest_path == coolest_path:
        print("\nResult: The shortest path is already the coolest route.")
    else:
        print("\nResult: The heat-optimized algorithm found a more shaded route. It takes a slightly longer walking distance to avoid direct sun exposure.")

if __name__ == "__main__":
    # Test coordinates inside OUTR campus
    start_pt = (20.268756, 85.840829) 
    end_pt = (20.275318, 85.835550)
    
    find_best_routes(*start_pt, *end_pt)