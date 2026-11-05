import osmnx as ox
import networkx as nx
import folium
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DATA_DIR

def generate_route_map(start_lat, start_lon, end_lat, end_lon):
    print("Loading graph and calculating routes...")
    G = ox.load_graphml(DATA_DIR / "campus_graph_final.graphml")
    
    for u, v, k, data in G.edges(keys=True, data=True):
        if 'heat_score_weight' in data: data['heat_score_weight'] = float(data['heat_score_weight'])
        if 'length' in data: data['length'] = float(data['length'])
    
    orig_node = ox.distance.nearest_nodes(G, X=start_lon, Y=start_lat)
    dest_node = ox.distance.nearest_nodes(G, X=end_lon, Y=end_lat)
    
    shortest_path = nx.shortest_path(G, orig_node, dest_node, weight='length')
    coolest_path = nx.shortest_path(G, orig_node, dest_node, weight='heat_score_weight')
    
    # Initialize map at the starting coordinate
    route_map = folium.Map(
        location=[start_lat, start_lon], 
        zoom_start=17, 
        tiles="http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}",
        attr="Google"
    )
    
    # Plot Shortest Path (Red)
    shortest_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in shortest_path]
    folium.PolyLine(shortest_coords, color="red", weight=4, opacity=0.7, tooltip="Shortest Path (Hot)").add_to(route_map)
    
    # Plot Coolest Path (Blue)
    coolest_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in coolest_path]
    folium.PolyLine(coolest_coords, color="blue", weight=5, opacity=0.9, tooltip="Coolest Path (Shaded)").add_to(route_map)
    
    # Add start and end markers
    folium.Marker([start_lat, start_lon], popup="Start", icon=folium.Icon(color="green")).add_to(route_map)
    folium.Marker([end_lat, end_lon], popup="End", icon=folium.Icon(color="black")).add_to(route_map)
    
    output_file = DATA_DIR / "route_comparison.html"
    route_map.save(output_file)
    print(f"Success: Open {output_file} in your web browser to see the visual comparison.")

if __name__ == "__main__":
    start_pt = (20.273824, 85.776182) 
    end_pt = (20.275463, 85.777021)
    generate_route_map(*start_pt, *end_pt)