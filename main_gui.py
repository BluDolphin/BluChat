from nicegui import ui, app
import os, secrets
from pages import home, login, settings, setup

# App is for handling browser storage and session management
# Checks for a 'authenticated' cookie 

@ui.page('/')
def login_page():
    if not os.path.exists("data") or not os.path.exists("data/config.txt") or not os.path.exists("data/authorised_numbers.txt"):       
        setup.content()
        return
    
    if app.storage.user.get('authenticated', False):
        ui.navigate.to('/home')
        return
    login.content()
     
@ui.page('/home')
def home_page():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/')
        return
    home.content()

@ui.page('/settings')
def settings_page():
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/')
        return
    settings.content()


# Generate/read storage secret for browser storage
# File Does not exist
if not os.path.exists("data/browser_key.txt"): 
    storage_key = secrets.token_urlsafe(128) # Generate a secure random key
    if not os.path.exists("data"): # Create data directory if it doesn't exist
        os.makedirs("data")
    with open("data/browser_key.txt", "w") as f: # Write the key to file
        f.write(storage_key)
# File exists 
else:
    with open("data/browser_key.txt", "r") as f: # Read the key from file
        storage_key = f.read().strip()


ui.run(port=8080, storage_secret=storage_key, show=False)