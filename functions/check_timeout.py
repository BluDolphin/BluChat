import time
from nicegui import ui, app

TIMEOUT = 120 # 2 minute timeout

# Timeout logic
def check_timeout(reset=False):
    
    print("Checking timeout...")    
    # Check last active time
    last_active = app.storage.tab.get('last_active', 0)
    
    # If time between last active and now exceeds TIMEOUT
    if time.time() - last_active > TIMEOUT:
        app.storage.tab.clear() # Clear session
        ui.navigate.to('/') # Redirect to login
        ui.notify('Session expired', color='red') # Notify user
    elif reset:
        # Update last active time
        app.storage.tab['last_active'] = time.time()
    