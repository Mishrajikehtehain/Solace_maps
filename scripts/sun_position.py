import sys
from pathlib import Path
import datetime
import pytz
from pysolar.solar import get_altitude, get_azimuth

# Link to config.py
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import CAMPUS_POINT

def get_sun_position(year, month, day, hour, minute):
    lat, lon = CAMPUS_POINT
    ist = pytz.timezone('Asia/Kolkata')
    target_time = ist.localize(datetime.datetime(year, month, day, hour, minute))
    
    altitude = get_altitude(lat, lon, target_time)
    azimuth = get_azimuth(lat, lon, target_time)
    
    return altitude, azimuth, target_time

if __name__ == "__main__":
    alt, az, t_time = get_sun_position(2027, 5, 15, 14, 0)
    print(f"Test Sun Altitude: {alt:.2f}°")