from nicegui import ui
import os
from pages.theme import frame

def content():
    with frame('Settings'):
        ui.label('Settings').classes('text-2xl mt-2')
    
                    
