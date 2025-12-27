from nicegui import ui, app
import os, secrets, json
from pages import home, login, setup, whitelist, settings

# App is for handling browser storage and session management
# Checks for a 'authenticated' cookie 
@ui.page('/')
async def index_page():
    await ui.context.client.connected()
    # If first time setup not completed, redirect to setup
    if not os.path.exists('data/config.json') or not os.path.exists('data/authorised_numbers.json'):       
        ui.navigate.to('/setup')
        return
        
    # Otherwise redirect to login
    ui.navigate.to('/login')

@ui.page('/setup')
async def setup_page():
    await ui.context.client.connected()
    # Prevent access if already setup
    if os.path.exists('data/config.json') and os.path.exists('data/authorised_numbers.json'):
        ui.navigate.to('/login')
        return
    
    # If authenticated, redirect to home
    if app.storage.tab.get('authenticated', False):
        ui.navigate.to('/login')
        return
    
    # Show setup page
    setup.content()
    
@ui.page('/login')
async def login_page():
    await ui.context.client.connected()   
    # If authenticated, redirect to home
    if app.storage.tab.get('authenticated', False):
        ui.navigate.to('/home')
        return
    
    # Show login page
    login.content()
     
@ui.page('/home')
async def home_page():
    await ui.context.client.connected()
    # If not authenticated, redirect to login
    if not app.storage.tab.get('authenticated', False):
        ui.navigate.to('/login')
        return
       
    # Show home page
    home.content()

@ui.page('/whitelist')
async def number_whitelist_page():
    await ui.context.client.connected()
    # If not authenticated, redirect to login
    if not app.storage.tab.get('authenticated', False):
        ui.navigate.to('/login')
        return
    
    # Show settings page
    whitelist.content()

@ui.page('/settings')
async def settings_page():
    await ui.context.client.connected()
    # If not authenticated, redirect to login
    if not app.storage.tab.get('authenticated', False):
        ui.navigate.to('/login')
        return
    
    # Show settings page
    settings.content()

# Generate/read secret to sign users sessionID cookie
# File doesnt have 3 lines
if not os.path.exists('data/crypt_data.json'): 
    storage_key = secrets.token_urlsafe(128) # Generate a secure random key
    if not os.path.exists('data'): # Create data directory if it doesn't exist
        os.makedirs('data')
    with open('data/crypt_data.json', 'w') as f: # Write the key to file
        # Store data in {'browser_key': '<key>'} (dictionary format)
        f.write(f'{{"browser_key": "{storage_key}"}}')
# File exists 
else:
    with open('data/crypt_data.json', 'r') as f: # Read the key from file
        storage_key = json.load(f)['browser_key']


ui.run(port=8080, 
       title='BluChat', 
       show=False, 
       storage_secret=storage_key)