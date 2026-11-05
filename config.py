from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# OUTR Coordinates (Lat, Lon) and capture radius in meters
CAMPUS_POINT = (20.268686, 85.840776) 
CAMPUS_RADIUS = 2000 

GRAPH_FILE = DATA_DIR / "campus_graph.graphml"