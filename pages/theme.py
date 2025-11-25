from nicegui import ui, app
from contextlib import contextmanager
import time

COLOUR_BG = '0d1331'  # Very dark blue
COLOUR_1 = '151b3e'  # Dark blue
COLOUR_2 = '152851'  # Medium blue

TIMEOUT = 6 # 3 minute timeout

# Timeout logic
def check_timeout(reset=False):
    # If authenticated
    print("Checking timeout...")
    if app.storage.user.get('authenticated', True):
        # Check last active time
        last_active = app.storage.user.get('last_active', 0)
        
        # If time between last active and now exceeds TIMEOUT
        if time.time() - last_active > TIMEOUT:
            app.storage.user.clear() # Clear session
            ui.navigate.to('/') # Redirect to login
            ui.notify('Session expired', color='red') # Notify user
        elif reset:
            # Update last active time
            app.storage.user['last_active'] = time.time()


# context manager for page layout with sidebar and theming
@contextmanager 
def frame(current_page):
    # Remove default padding and margins from the page and body
    ui.add_head_html('''
        <style>
            body { margin: 0; padding: 0; }
            .nicegui-content { padding: 0 !important; margin: 0 !important; max-width: none !important; }
        </style>
    ''')
    
    check_timeout(True)
            
    # Create a full-height row to hold sidebar and main content
    with ui.row().classes('h-screen w-full no-wrap gap-0') as layout_container:
        # Timer to check periodically (In main window to fix navigation)
        # Safe wrapper to ensure layout_container is accessible
        def call_check_timeout():
            with layout_container:
                check_timeout()
        ui.timer(10.0, call_check_timeout)
        
        # Sidebar: COLOUR_1, full height, width 64, padding 4
        with ui.column().style(f'background-color: #{COLOUR_1}').classes('w-64 h-full p-4'):
            # Sidebar Title
            ui.label('Menu').classes('text-xl font-bold mb-4 text-white') 
            
            # Helper function to create navigation links with highlighting
            def nav_link(name, target):
                # Base classes: block for full width, padding, rounded corners
                classes = f'mb-2 w-full block p-2 rounded hover:text-white hover:bg-[#{COLOUR_2}]'
                if name == current_page:
                    # Active style: lighter background, white text
                    classes += f' bg-[#{COLOUR_2}] text-white'
                ui.link(name, target).classes(classes)

            nav_link('Home', '/home')
            nav_link('Settings', '/settings')
        
        # Main Content Area
        with ui.column().style(f'background-color: #{COLOUR_BG}').classes('p-4 w-full h-full text-white'):
            yield  # Pause here to inject content into the main area
