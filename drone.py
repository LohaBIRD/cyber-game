import threading
from pyparrot.Minidrone import Mambo 

# Global variables to hold the drone state
mambo = None
drone_connected = False
is_flying = False  # Lock to prevent overlapping commands if you die twice quickly

def init_drone():
    """Initializes and connects to the drone."""
    global mambo, drone_connected
    
    print("Attempting to connect to Parrot Mambo over Wi-Fi...")
    mambo = Mambo(None, use_wifi=True)
    drone_connected = mambo.connect(num_retries=3)
    
    if drone_connected:
        print("Connected! Waking up sensors (Waiting 4 seconds)...")
        mambo.smart_sleep(4) 
        
        print("Asking for initial state update...")
        mambo.ask_for_state_update()
        mambo.smart_sleep(4) 
    
    print(f"Drone connected: {drone_connected}")
    return drone_connected

def _fly_drone_task():
    """Internal function that handles the actual flight commands."""
    global is_flying
    
    if drone_connected and mambo is not None:
        is_flying = True
        
        print("TAKING OFF!")
        mambo.safe_takeoff(5)
        
        print("Hovering for 6 seconds to stabilize...")
        mambo.smart_sleep(6) 
        
        # --- AGGRESSIVE LANDING LOGIC ---
        print("Forcing state update so it knows it is flying...")
        mambo.ask_for_state_update()
        
        print("Waiting 3 seconds for state packet to return...")
        mambo.smart_sleep(3) 
        
        print("LANDING COMMAND 1!")
        mambo.safe_land(5)
        
        print("Waiting 3 seconds to see if it lands...")
        mambo.smart_sleep(3) 
        
        print("LANDING COMMAND 2 (Backup)!")
        mambo.safe_land(5)
        
        print("Waiting 3 seconds for landing to finish...")
        mambo.smart_sleep(3) 
        
        is_flying = False  # Unlock the drone for the next death
    else:
        print("[Simulated] Drone would take off, wait 6s, and land here.")

def trigger_flight():
    """Spawns a thread so the game doesn't freeze during the flight."""
    global is_flying
    
    if not is_flying:  # Only fly if it isn't already flying
        flight_thread = threading.Thread(target=_fly_drone_task)
        flight_thread.start()
    else:
        print("Drone is already in the air! Ignoring extra death trigger.")

def disconnect_drone():
    """Disconnects the drone safely."""
    if drone_connected and mambo is not None:
        print("Disconnecting drone...")
        mambo.disconnect()