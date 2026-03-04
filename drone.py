# drone.py
import threading
from pyparrot.Minidrone import Mambo 


# Global variables to hold the drone state
mambo = None
drone_connected = False

def init_drone():
    """Initializes and connects to the drone."""
    global mambo, drone_connected
    
    print("Attempting to connect to Parrot Mambo over Wi-Fi...")
    mambo = Mambo(None, use_wifi=True)
    drone_connected = mambo.connect(num_retries=3)
    
    print(f"Drone connected: {drone_connected}")
    return drone_connected

def _fly_drone_task():
    """Internal function that handles the actual flight commands."""
    if drone_connected and mambo is not None:
        print("Drone taking off!")
        mambo.safe_takeoff(5) 
        mambo.smart_sleep(4)  # Hover for 2 seconds
        print("Drone landing!")
        mambo.safe_land(5)
    else:
        print("[Simulated] Drone would take off, wait 2s, and land here.")

def trigger_flight():
    """Spawns a thread so the game doesn't freeze during the flight."""
    flight_thread = threading.Thread(target=_fly_drone_task)
    flight_thread.start()

def disconnect_drone():
    """Disconnects the drone safely."""
    if drone_connected and mambo is not None:
        print("Disconnecting drone...")
        mambo.disconnect()