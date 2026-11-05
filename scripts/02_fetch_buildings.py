import osmnx as ox
import sys
from pathlib import Path

# Link to config.py
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import CAMPUS_POINT, CAMPUS_RADIUS, DATA_DIR

def fetch_buildings():
    print("Fetching building footprints for shadow calculations...")
    
    # Download building polygons using the same coordinate radius
    tags = {'building': True}
    buildings = ox.features_from_point(CAMPUS_POINT, tags=tags, dist=CAMPUS_RADIUS)
    
    # Filter out point data (some tiny structures are just nodes, we only want polygons for shadows)
    buildings = buildings[buildings.geometry.type.isin(['Polygon', 'MultiPolygon'])]
    
    print(f"Success: Loaded {len(buildings)} buildings.")
    
    # Save as GeoJSON for easy offline spatial math
    output_file = DATA_DIR / "campus_buildings.geojson"
    buildings.to_file(output_file, driver="GeoJSON")
    print(f"Buildings saved offline to {output_file}")

if __name__ == "__main__":
    fetch_buildings()