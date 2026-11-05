import sys
import numpy as np
import geopandas as gpd
import osmnx as ox
from shapely.affinity import translate
from pathlib import Path

# Import your config and sun function
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DATA_DIR
from sun_position import get_sun_position
def calculate_shadows(altitude, azimuth, default_height=12.0):
    if altitude <= 0:
        print("Nighttime: No shadows to project.")
        return None

    print("Loading buildings...")
    buildings_file = DATA_DIR / "campus_buildings.geojson"
    buildings = gpd.read_file(buildings_file)
    
    # 1. Project to UTM (Meters) so we can calculate distances properly
    buildings_proj = buildings.to_crs(buildings.estimate_utm_crs())
    
    # 2. Math: Shadow Length
    # Convert altitude to radians. Length = Height / tan(Altitude)
    alt_rad = np.radians(altitude)
    shadow_length = default_height / np.tan(alt_rad)
    
    # 3. Math: Shadow Direction (opposite of the sun)
    # Convert compass azimuth to standard mathematical angle, then flip 180 degrees
    math_angle = 90 - azimuth
    shadow_angle_rad = np.radians(math_angle + 180)
    
    # Calculate the X and Y offsets in meters
    dx = shadow_length * np.cos(shadow_angle_rad)
    dy = shadow_length * np.sin(shadow_angle_rad)
    
    print(f"Projecting shadows {shadow_length:.1f}m away at offsets (dx: {dx:.1f}, dy: {dy:.1f})...")
    
    # 4. Generate the shadow polygons
    shadow_geoms = []
    for geom in buildings_proj.geometry:
        # Shift the building footprint
        shifted = translate(geom, xoff=dx, yoff=dy)
        # Create a single shape spanning from the base building to the end of the shadow
        shadow_poly = geom.union(shifted).convex_hull
        shadow_geoms.append(shadow_poly)
        
    # Create a new GeoDataFrame for the shadows
    shadows_proj = gpd.GeoDataFrame(geometry=shadow_geoms, crs=buildings_proj.crs)
    
    # Project back to Latitude/Longitude (EPSG:4326)
    shadows = shadows_proj.to_crs(epsg=4326)
    
    # Save the shadows
    output_file = DATA_DIR / "campus_shadows.geojson"
    shadows.to_file(output_file, driver="GeoJSON")
    print(f"Success: Saved {len(shadows)} shadow polygons to {output_file}")
    
    return shadows

if __name__ == "__main__":
    # Example: Calculate shadows for May 15 at 4:00 PM (16:00)
    alt, az, _ = get_sun_position(2027, 5, 15, 16, 0)
    calculate_shadows(alt, az)