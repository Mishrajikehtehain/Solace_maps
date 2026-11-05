import osmnx as ox
import geopandas as gpd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import CAMPUS_POINT, CAMPUS_RADIUS, DATA_DIR

def fetch_trees():
    print(f"Fetching trees and green spaces within {CAMPUS_RADIUS}m...")
    tags = {
        'natural': ['tree', 'wood', 'scrub'],
        'leisure': 'park'
    }
    
    output_file = DATA_DIR / "campus_trees.geojson"
    
    try:
        trees = ox.features_from_point(CAMPUS_POINT, tags=tags, dist=CAMPUS_RADIUS)
        if len(trees) == 0:
            raise ValueError("Empty data")
        print(f"Success: Loaded {len(trees)} vegetation features.")
        trees.to_file(output_file, driver="GeoJSON")
        
    except Exception as e:
        print("No mapped trees found. Creating an empty fallback file so the pipeline can continue...")
        # Create an empty map file so Step 6 doesn't crash
        empty_gdf = gpd.GeoDataFrame(columns=['geometry'], geometry='geometry', crs="EPSG:4326")
        empty_gdf.to_file(output_file, driver="GeoJSON")
        
    print(f"Trees saved offline to {output_file}")

if __name__ == "__main__":
    fetch_trees()