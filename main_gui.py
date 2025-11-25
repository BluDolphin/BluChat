from nicegui import ui, app
import os, secrets
from pages import home, login, settings, setup

# App is for handling browser storage and session management
# Checks for a 'authenticated' cookie 

@ui.page('/')
async def login_page():
    await ui.context.client.connected()
    # If first time setup not completed, redirect to setup
    if not os.path.exists('data/config.txt') or not os.path.exists('data/authorised_numbers.txt'):       
        setup.content()
        return
    
    # If authenticated, redirect to home
    if app.storage.tab.get('authenticated', False):
        ui.navigate.to('/home')
        return
    
    # Show login page
    login.content()
     
@ui.page('/home')
async def home_page():
    await ui.context..connected()
    # If not authenticated, redirect to login
    if not app.storage.tab.get('authenticated', False):
        ui.navigate.to('/')
        return
       
    # Show home page
    home.content()

@ui.page('/settings')
async def settings_page():
    await ui.context.client.connected()
    # If not authenticated, redirect to login
    if not app.storage.tab.get('authenticated', False):
        ui.navigate.to('/')
        return
    
    # Show settings page
    settings.content()

ui.run(port=8080, 
       title='BluChat', 
       show=False)